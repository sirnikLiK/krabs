import serial
import time

# --- НАСТРОЙКИ ---
SERIAL_PORT = '/dev/ttyACM0' 
BAUD_RATE = 9600

try:
    # Инициализация порта
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    # Важно: даем Arduino 2 секунды на перезагрузку после открытия порта
    time.sleep(2) 
    print(f"✅ Подключено к {SERIAL_PORT}")
    print("Вводи команду (например: W, A, S, D или 90) и жми Enter.")
    print("Для выхода введи 'exit'")
except Exception as e:
    print(f"❌ Ошибка Serial: {e}")
    ser = None

if ser:
    try:
        while True:
            # Ждем ввод пользователя в терминале
            user_input = input("Команда >> ").strip()

            if user_input.lower() == 'exit':
                break

            if user_input:
                # Добавляем символ новой строки \n, чтобы Arduino поняла конец команды
                data_to_send = f"{user_input}\n"
                ser.write(data_to_send.encode())
                
                print(f"📤 Отправлено в порт: {user_input}")

    except KeyboardInterrupt:
        print("\n🛑 Завершение работы...")
    finally:
        ser.close()
        print("🔌 Порт закрыт.")