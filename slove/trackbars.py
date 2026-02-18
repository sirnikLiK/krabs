import cv2
import numpy as np

class Trackbar:
    def __init__(self, window_name='Settings'):
        self.window_name = window_name
        
        # Параметры по умолчанию
        self.lower_hsv = np.array([0, 0, 200])
        self.upper_hsv = np.array([20, 30, 255])
        self.min_area = 5000
        self.min_ratio = 3.0
        self.max_ratio = 6.0
    
    def create_trackbars(self):
        """Создание трекбаров в окне"""
        cv2.namedWindow(self.window_name)
        
        # HSV нижние границы
        cv2.createTrackbar('Low H', self.window_name, 0, 180, lambda x: None)
        cv2.createTrackbar('Low S', self.window_name, 0, 255, lambda x: None)
        cv2.createTrackbar('Low V', self.window_name, 200, 255, lambda x: None)
        
        # HSV верхние границы
        cv2.createTrackbar('High H', self.window_name, 20, 180, lambda x: None)
        cv2.createTrackbar('High S', self.window_name, 30, 255, lambda x: None)
        cv2.createTrackbar('High V', self.window_name, 255, 255, lambda x: None)
        
        # Параметры фильтрации
        cv2.createTrackbar('Min Area', self.window_name, 5000, 50000, lambda x: None)
        cv2.createTrackbar('Min Ratio', self.window_name, 30, 100, lambda x: None)
        cv2.createTrackbar('Max Ratio', self.window_name, 60, 100, lambda x: None)
    
    def get_params(self):
        """Получение текущих параметров с трекбаров"""
        self.lower_hsv = np.array([
            cv2.getTrackbarPos('Low H', self.window_name),
            cv2.getTrackbarPos('Low S', self.window_name),
            cv2.getTrackbarPos('Low V', self.window_name)
        ])
        
        self.upper_hsv = np.array([
            cv2.getTrackbarPos('High H', self.window_name),
            cv2.getTrackbarPos('High S', self.window_name),
            cv2.getTrackbarPos('High V', self.window_name)
        ])
        
        self.min_area = cv2.getTrackbarPos('Min Area', self.window_name)
        self.min_ratio = cv2.getTrackbarPos('Min Ratio', self.window_name) / 10.0
        self.max_ratio = cv2.getTrackbarPos('Max Ratio', self.window_name) / 10.0
        
        return {
            'lower_hsv': self.lower_hsv,
            'upper_hsv': self.upper_hsv,
            'min_area': self.min_area,
            'min_ratio': self.min_ratio,
            'max_ratio': self.max_ratio
        }
    
    def reset_trackbars(self):
        """Сброс трекбаров к значениям по умолчанию"""
        cv2.setTrackbarPos('Low H', self.window_name, 0)
        cv2.setTrackbarPos('Low S', self.window_name, 0)
        cv2.setTrackbarPos('Low V', self.window_name, 200)
        cv2.setTrackbarPos('High H', self.window_name, 20)
        cv2.setTrackbarPos('High S', self.window_name, 30)
        cv2.setTrackbarPos('High V', self.window_name, 255)
        cv2.setTrackbarPos('Min Area', self.window_name, 5000)
        cv2.setTrackbarPos('Min Ratio', self.window_name, 30)
        cv2.setTrackbarPos('Max Ratio', self.window_name, 60)
    
    def set_params(self, params):
        """Установка параметров на трекбарах"""
        cv2.setTrackbarPos('Low H', self.window_name, params['lower_hsv'][0])
        cv2.setTrackbarPos('Low S', self.window_name, params['lower_hsv'][1])
        cv2.setTrackbarPos('Low V', self.window_name, params['lower_hsv'][2])
        cv2.setTrackbarPos('High H', self.window_name, params['upper_hsv'][0])
        cv2.setTrackbarPos('High S', self.window_name, params['upper_hsv'][1])
        cv2.setTrackbarPos('High V', self.window_name, params['upper_hsv'][2])
        cv2.setTrackbarPos('Min Area', self.window_name, params['min_area'])
        cv2.setTrackbarPos('Min Ratio', self.window_name, int(params['min_ratio'] * 10))
        cv2.setTrackbarPos('Max Ratio', self.window_name, int(params['max_ratio'] * 10))


# Функции для использования без класса
def create_detection_trackbars(window_name='Settings'):
    """Создать трекбары для детекции"""
    manager = Trackbar(window_name)
    manager.create_trackbars()
    return manager


def get_detection_params(window_name='Settings'):
    """Получить параметры с трекбаров"""
    lower_hsv = np.array([
        cv2.getTrackbarPos('Low H', window_name),
        cv2.getTrackbarPos('Low S', window_name),
        cv2.getTrackbarPos('Low V', window_name)
    ])
    
    upper_hsv = np.array([
        cv2.getTrackbarPos('High H', window_name),
        cv2.getTrackbarPos('High S', window_name),
        cv2.getTrackbarPos('High V', window_name)
    ])
    
    min_area = cv2.getTrackbarPos('Min Area', window_name)
    min_ratio = cv2.getTrackbarPos('Min Ratio', window_name) / 10.0
    max_ratio = cv2.getTrackbarPos('Max Ratio', window_name) / 10.0
    
    return {
        'lower_hsv': lower_hsv,
        'upper_hsv': upper_hsv,
        'min_area': min_area,
        'min_ratio': min_ratio,
        'max_ratio': max_ratio
    }


def reset_detection_trackbars(window_name='Settings'):
    """reset"""
    cv2.setTrackbarPos('Low H', window_name, 0)
    cv2.setTrackbarPos('Low S', window_name, 0)
    cv2.setTrackbarPos('Low V', window_name, 200)
    cv2.setTrackbarPos('High H', window_name, 20)
    cv2.setTrackbarPos('High S', window_name, 30)
    cv2.setTrackbarPos('High V', window_name, 255)
    cv2.setTrackbarPos('Min Area', window_name, 5000)
    cv2.setTrackbarPos('Min Ratio', window_name, 30)
    cv2.setTrackbarPos('Max Ratio', window_name, 60)