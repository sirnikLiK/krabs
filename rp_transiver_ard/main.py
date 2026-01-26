import serial
import serial.tools.list_ports
import time

# 1. Выводим список всех доступных портов
ports = list(serial.tools.list_ports.comports())

if not ports:
    print("Устройства не найдены. Проверь кабель!")
    exit()

print("Доступные порты:")
for i, p in enumerate(ports):
    print(f"[{i}] {p.device} - {p.description}")

# 2. Выбор порта пользователем
try:
    idx = int(input("Введите номер порта (например, 0): "))
    selected_port = ports[idx].device
except (ValueError, IndexError):
    print("Ошибка выбора.")
    exit()

# 3. Подключение
try:
    ser = serial.Serial(selected_port, 9600, timeout=1)
    time.sleep(2) # Ждем инициализацию
    print(f"Подключено к {selected_port}. Жми 'w' для отправки или 'q' для выхода.")

    while True:
        cmd = input("Команда: ").strip().lower()
        if cmd == 'w':
            ser.write(b'w')
            print("Отправлено: w")
        elif cmd == 'q':
            break
except Exception as e:
    print(f"Ошибка: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Соединение закрыто.") 