import cv2
from flask import Flask, Response
import time

app = Flask(__name__)

def find_camera():
    # Проверяем индексы от 0 до 5
    for index in range(6):
        print(f"Проверка камеры на индексе {index}...")
        cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
        if cap.isOpened():
            # Пробуем считать один кадр, чтобы убедиться, что она не "мертвая"
            ret, frame = cap.read()
            if ret:
                print(f" УРА! Камера найдена на индексе {index}")
                return cap
            cap.release()
    return None

# Автоматический поиск при старте
camera = find_camera()

def gen_frames():
    if camera is None:
        return
    
    # Оптимизация для USB-камеры
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    while True:
        # Сбрасываем старый кадр из буфера для уменьшения пинга
        camera.grab()
        success, frame = camera.retrieve()
        
        if not success:
            print("Потеря связи с камерой...")
            break
        
        # Сжатие
        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 35])
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    if camera:
        return "<html><body style='background:#111; color:white; text-align:center;'>"\
               "<h1>Камера работает!</h1><img src='/video_feed' style='border:2px solid red;'></body></html>"
    else:
        return "<h1>Камера не найдена! Проверь USB-разъем.</h1>"

if __name__ == '__main__':
    if camera is None:
        print("!!! ОШИБКА: Ни одна камера не ответила. Попробуй переткнуть USB.")
    else:
        # threaded=True критически важен, чтобы поток не зависал
        app.run(host='0.0.0.0', port=5000, threaded=True)