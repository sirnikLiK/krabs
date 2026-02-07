import cv2
import numpy as np
import math
import serial
import time

# --- НАСТРОЙКИ ---
SERIAL_PORT = '/dev/ttyACM0' 
BAUD_RATE = 9600
IMG_SIZE = (360, 200)
CENTER_X = IMG_SIZE[0] // 2 

# !!! ГЛАВНАЯ НАСТРОЙКА !!!
# Если робот едет слишком близко к правой линии -> УВЕЛИЧЬ это число (поставь 200, 220)
# Если робот едет слишком близко к левой линии -> УМЕНЬШИ это число
LANE_WIDTH = 210  

# Сколько кадров помнить линию, если она исчезла (для пунктира)
MEMORY_FRAMES = 10 

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2) 
    print(f"✅ Подключено к {SERIAL_PORT}")
except Exception as e:
    print(f"❌ Ошибка Serial: {e}"); ser = None

cap = cv2.VideoCapture(0)

# Перспектива (подстрой src под свою камеру, если линии кривые)
src = np.float32([[10, 190], [350, 190], [270, 110], [90, 110]])
dst = np.float32([[80, 200], [280, 200], [280, 0], [80, 0]])
M = cv2.getPerspectiveTransform(src, dst)
Minv = cv2.getPerspectiveTransform(dst, src)

# Переменные памяти (храним последние найденные линии)
last_l_fit = None
last_r_fit = None
lost_l_counter = 0
lost_r_counter = 0
last_sent_data = ""
last_servo_val = 90

while True:
    ret, frame = cap.read()
    if not ret: break
        
    frame = cv2.resize(frame, IMG_SIZE)
    
    # 1. HLS фильтр (белый цвет)
    hls = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)
    mask = cv2.inRange(hls, np.array([0, 150, 0]), np.array([180, 255, 255]))
    
    # Морфология (убираем шум)
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    warped = cv2.warpPerspective(mask, M, IMG_SIZE)
    bev_debug = cv2.cvtColor(warped, cv2.COLOR_GRAY2BGR)

    # 2. Поиск линий (Гистограмма)
    histogram = np.sum(warped[int(warped.shape[0]/2):,:], axis=0)
    midpoint = int(histogram.shape[0]/2)
    
    # Ищем базы линий
    leftx_base = np.argmax(histogram[:midpoint])
    rightx_base = np.argmax(histogram[midpoint:]) + midpoint

    # Проверяем, есть ли там вообще пиксели (защита от пустых мест)
    left_detected_now = histogram[leftx_base] > 50
    right_detected_now = histogram[rightx_base] > 50

    # Скользящие окна
    nz = warped.nonzero()
    ny, nx = np.array(nz[0]), np.array(nz[1])
    l_inds, r_inds = [], []
    win_h, margin = 20, 50
    cur_l, cur_r = leftx_base, rightx_base

    for w in range(9):
        y_low, y_high = warped.shape[0]-(w+1)*win_h, warped.shape[0]-w*win_h
        
        if left_detected_now:
            l_idx = ((ny >= y_low) & (ny < y_high) & (nx >= cur_l-margin) & (nx < cur_l+margin)).nonzero()[0]
            l_inds.append(l_idx)
            if len(l_idx) > 20: cur_l = int(np.mean(nx[l_idx]))

        if right_detected_now:
            r_idx = ((ny >= y_low) & (ny < y_high) & (nx >= cur_r-margin) & (nx < cur_r+margin)).nonzero()[0]
            r_inds.append(r_idx)
            if len(r_idx) > 20: cur_r = int(np.mean(nx[r_idx]))

    try:
        ploty = np.linspace(0, warped.shape[0]-1, 20)
        l_fit, r_fit = None, None

        # --- ЛОГИКА ПАМЯТИ (Для прерывистых линий) ---
        
        # Обработка ЛЕВОЙ линии
        if l_inds:
            l_inds_concat = np.concatenate(l_inds)
            if len(l_inds_concat) > 50:
                l_fit = np.polyfit(ny[l_inds_concat], nx[l_inds_concat], 2)
                last_l_fit = l_fit # Обновляем память
                lost_l_counter = 0
        
        # Если левой линии сейчас нет, но в памяти она свежая -> берем из памяти
        if l_fit is None and last_l_fit is not None and lost_l_counter < MEMORY_FRAMES:
            l_fit = last_l_fit
            lost_l_counter += 1
        elif l_fit is None:
            lost_l_counter += 1

        # Обработка ПРАВОЙ линии
        if r_inds:
            r_inds_concat = np.concatenate(r_inds)
            if len(r_inds_concat) > 50:
                r_fit = np.polyfit(ny[r_inds_concat], nx[r_inds_concat], 2)
                last_r_fit = r_fit # Обновляем память
                lost_r_counter = 0

        if r_fit is None and last_r_fit is not None and lost_r_counter < MEMORY_FRAMES:
            r_fit = last_r_fit
            lost_r_counter += 1
        elif r_fit is None:
            lost_r_counter += 1

        # --- РАСЧЕТ ЦЕНТРА ---
        
        if l_fit is not None and r_fit is not None:
            # Видим ОБЕ линии (или помним обе) -> Идеальный центр
            center_fit = (l_fit + r_fit) / 2
            
            # (Опционально) Можно подправлять LANE_WIDTH автоматически, если видим обе
            # real_width = (r_fit[2] - l_fit[2])
            # LANE_WIDTH = int(real_width) 
            
        elif r_fit is not None:
            # Видим только ПРАВУЮ -> Отступаем влево на LANE_WIDTH
            center_fit = r_fit.copy()
            center_fit[2] -= (LANE_WIDTH / 2) # Делим на 2, чтобы попасть в центр
            
            # Но если мы хотим ехать ровно посередине между линиями, 
            # координата центра = Правая - (Половина ширины дороги)
            # В данном коде LANE_WIDTH - это полная ширина дороги.
            # Поэтому центр будет: r_fit - (LANE_WIDTH / 2)
            # Исправляем логику для точности:
            l_fit_simulated = r_fit.copy()
            l_fit_simulated[2] -= LANE_WIDTH
            center_fit = (l_fit_simulated + r_fit) / 2
            
        elif l_fit is not None:
            # Видим только ЛЕВУЮ (пунктир появился) -> Отступаем вправо
            r_fit_simulated = l_fit.copy()
            r_fit_simulated[2] += LANE_WIDTH
            center_fit = (l_fit + r_fit_simulated) / 2
            
        else:
            raise ValueError("All lines lost")

        # --- УПРАВЛЕНИЕ ---
        y_bottom = float(warped.shape[0] - 1)
        y_ahead = y_bottom - 60

        x_center_bottom = center_fit[0]*y_bottom**2 + center_fit[1]*y_bottom + center_fit[2]
        x_center_ahead = center_fit[0]*y_ahead**2 + center_fit[1]*y_ahead + center_fit[2]

        offset_error = x_center_bottom - CENTER_X
        angle_deg = math.degrees(math.atan2(x_center_ahead - x_center_bottom, y_bottom - y_ahead))

        # P-регулятор
        target_servo = int(90 + angle_deg + (offset_error * 0.4))
        
        # Сглаживание
        servo_val = int(last_servo_val * 0.7 + target_servo * 0.3)
        servo_val = max(50, min(130, servo_val))
        last_servo_val = servo_val

        # Отправка
        data_to_send = f"1;{servo_val}\n"
        if ser and data_to_send != last_sent_data:
            ser.write(data_to_send.encode())
            last_sent_data = data_to_send
            print(f"Angle: {servo_val} | Offset: {int(offset_error)} | Using Memory: L={lost_l_counter}, R={lost_r_counter}")

        # --- ОТРИСОВКА ---
        road_canvas = np.zeros_like(frame)
        
        # Рисуем линии, если они есть (или в памяти)
        if l_fit is not None:
            l_x = l_fit[0]*ploty**2 + l_fit[1]*ploty + l_fit[2]
            cv2.polylines(road_canvas, [np.int32(np.transpose(np.vstack([l_x, ploty])))], False, (0, 255, 255), 3) # Желтая левая
            
        if r_fit is not None:
            r_x = r_fit[0]*ploty**2 + r_fit[1]*ploty + r_fit[2]
            cv2.polylines(road_canvas, [np.int32(np.transpose(np.vstack([r_x, ploty])))], False, (0, 0, 255), 3) # Красная правая

        # Рисуем центр (синяя)
        c_x = center_fit[0]*ploty**2 + center_fit[1]*ploty + center_fit[2]
        cv2.polylines(road_canvas, [np.int32(np.transpose(np.vstack([c_x, ploty])))], False, (255, 255, 0), 4)

        overlay = cv2.warpPerspective(road_canvas, Minv, IMG_SIZE)
        frame = cv2.addWeighted(frame, 1, overlay, 0.6, 0)

    except Exception:
        cv2.putText(frame, "SEARCHING...", (10, 50), 1, 2, (0, 0, 255), 2)
        if ser: ser.write(b"1;90\n")

    cv2.imshow("Dual Lane Memory", np.hstack((frame, bev_debug)))
    if cv2.waitKey(1) == ord('q'): break

if ser: ser.close()
cap.release()
cv2.destroyAllWindows()