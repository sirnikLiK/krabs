import requests

SERVER_URL = "http://172.16.65.50:8000"

def send_start_command():
    try:
        response = requests.post(f"{SERVER_URL}/start", json={"value": True})
        if response.status_code == 200:
            print("Команда старта успешно отправлена")
            return True
        else:
            print(f"Ошибка при отправке команды: {response.status_code}")
            return False
    except Exception as e:
        print(f"Ошибка при отправке команды: {e}")
        return False

def main():
    print("Ожидание ввода команды 'start'...")
    while True:
        command = input("Введите команду: ").strip().lower()
        if command == "start":
            if send_start_command():
                print("Программа завершена")
                break
        elif command == "exit":
            print("Программа завершена")
            break
        else:
            print("Неизвестная команда. Используйте 'start' или 'exit'")

if __name__ == "__main__":
    main() 