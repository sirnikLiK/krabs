import cv2
import numpy as np
import sys
from trackbars import *
class AikarDetector:
    def __init__(self):
        self.detected = False
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.area = 0
        self.aspect_ratio = 0
        self.coordinates = (0, 0)
        self.size = (0, 0)
        self.lower_hsv = np.array([0, 0, 200])
        self.upper_hsv = np.array([20, 30, 255])
        self.min_area = 5000
        self.min_ratio = 3.0
        self.max_ratio = 6.0
        self.track = Trackbar('Settings')

    def create_trackbars(self):
        self.track.create_trackbars()
    
    def get_params(self):
        params = self.track.get_params()
        self.lower_hsv = params['lower_hsv']
        self.upper_hsv = params['upper_hsv']
        self.min_area = params['min_area']
        self.min_ratio = params['min_ratio']
        self.max_ratio = params['max_ratio']
    
    def detect(self, frame):
        self.get_params()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.detected = False
        self.x = self.y = self.width = self.height = self.area = 0
        self.aspect_ratio = 0
        self.coordinates = (0, 0)
        self.size = (0, 0)
        
        best_contour = None
        best_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if area > self.min_area:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / float(h) if h > 0 else 0
                
                if self.min_ratio <= aspect_ratio <= self.max_ratio:
                    if area > best_area:
                        best_area = area
                        best_contour = contour
                        self.x, self.y, self.width, self.height = x, y, w, h
                        self.area = area
                        self.aspect_ratio = aspect_ratio
        
        if best_contour is not None:
            self.detected = True
            self.coordinates = (self.x, self.y)
            self.size = (self.width, self.height)
        
        return mask, best_contour
    
    def draw_result(self, frame, contour):
        display = frame.copy()
        
        if self.detected and contour is not None:
            cv2.rectangle(display, (self.x, self.y), 
                         (self.x + self.width, self.y + self.height), 
                         (0, 255, 0), 3)
            
            cv2.putText(display, f"{self.x}\t{self.y}\t{self.area:.0f}", 
                       (self.x, self.y + self.height + 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 1)
        else:
            pass
        
        return display
    
    def get_results(self):
        return {
            'detected': self.detected,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'area': self.area,
            'aspect_ratio': self.aspect_ratio,
            'coordinates': self.coordinates,
            'size': self.size
        }

def process_image(image_path):
    frame = cv2.imread(image_path)
    
    if frame is None:
        return None
    detector = AikarDetector()
    detector.create_trackbars()

    while True:
        mask, contour = detector.detect(frame)
        display = detector.draw_result(frame, contour)
        cv2.imshow('Mask', mask)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        if key == ord('r'):
            results = detector.get_results()
            print(results)
    cv2.destroyAllWindows()
    print
    return detector

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        pass

    ret, frame = cap.read()

    detector = AikarDetector()
    detector.create_trackbars()
    mask, contour = detector.detect(frame)
    display = detector.draw_result(frame, contour)

    while True:
        ret, frame = cap.read()

        mask, contour = detector.detect(frame)
        display = detector.draw_result(frame, contour)
        
        # Сохраняем последние кадры
        last_display = display.copy()
        last_mask = mask.copy()
        
        # Преобразуем маску в цветное изображение для совмещения
        mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        
        # Совмещаем изображения горизонтально
        combined = np.hstack((display, mask_colored))
        last_combined = combined.copy()
        
        # Отображение совмещенного изображения
        cv2.imshow('AIKAR Detection + Mask (Combined)', combined)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            detector.print_results()
            break
        elif key == ord('s'):
            detector.print_results()
            results = detector.get_results()
            print(f"\nРезультаты:")
            print(results)
        elif key == ord('r'):
            detector.track.reset_trackbars()
            print("Параметры сброшены")
        elif key == ord('c'):
            cv2.imwrite('aikar_frame.png', display)
            cv2.imwrite('aikar_mask.png', mask)
            cv2.imwrite('aikar_combined.png', combined)
            print("Кадры сохранены: aikar_frame.png, aikar_mask.png, aikar_combined.png")
    
    cap.release()
    cv2.destroyAllWindows()
