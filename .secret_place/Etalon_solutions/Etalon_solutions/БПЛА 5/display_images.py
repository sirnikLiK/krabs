import cv2
import numpy as np
import requests
import base64
import time

SERVER_URL = "http://172.16.65.50:8000"

def base64_to_image(base64_string):
    # Декодируем base64 строку в байты
    img_data = base64.b64decode(base64_string)
    # Преобразуем байты в numpy массив
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def main():
    # URL сервера
    
    while True:
        try:
            # Получаем данные с сервера
            response = requests.get(f"{SERVER_URL}/images")
            data = response.json()
            
            if data["status"] == "OK" and data["detail"] is not None:
                # Получаем изображения
                original_img = base64_to_image(data["detail"]["original"])
                processed_img = base64_to_image(data["detail"]["processed"])
                
                # Создаем окно с двумя изображениями рядом
                combined = np.hstack((original_img, processed_img))
                
                # Показываем изображения
                cv2.imshow("Original and Processed Images", combined)
                
                # Ждем нажатия клавиши (1 мс)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            # Небольшая задержка перед следующим запросом
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(1)  # Ждем секунду перед повторной попыткой
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 