import rospy
from sensor_msgs.msg import Image
from std_srvs.srv import Empty, EmptyResponse
from std_srvs.srv import Trigger, TriggerResponse
import cv2
from cv_bridge import CvBridge
from rospy import Service
import numpy as np
from gs_navigation import NavigationManager
import requests

SERVER_URL = "http://172.16.65.50:8000"

PIXEL_CONST = 0.0067

rospy.init_node("detect_node")  # инициализируем узел
# Инициализирует NavigationManager для получения координат
nav = NavigationManager()
bridge = CvBridge()  # создаем объект преобразования сообщений ROS в OpenCV

weights_path = "yolov4-tiny-obj_best.weights"
config_path = "yolov4-tiny-obj.cfg"

net = cv2.dnn.readNet(config_path, weights_path)
yolo_model = cv2.dnn.DetectionModel(net)
all_object = []

# Выдает самый веротяный объект на изображении и координаты центра объекта относительно центра изображения с камеры
def get_most_probable_class(class_ids, confidences, boxes, image_shape):
    if len(class_ids) == 0 or len(confidences) == 0 or len(boxes) == 0:
        return None, None, None  # Если объекты не найдены, возвращаем (None, None, None)

    # Находим индекс максимальной уверенности
    most_probable_index = np.argmax(confidences)

    # Получаем соответствующий class_id и box
    class_id = class_ids[most_probable_index]
    box = boxes[most_probable_index]

    # Рассчитываем центр рамки
    x, y, w, h = box  # Координаты рамки: (x, y, ширина, высота)
    box_center_x = x + w / 2
    box_center_y = y + h / 2

    # Рассчитываем центр изображения
    image_height, image_width = image_shape
    image_center_x = image_width / 2
    image_center_y = image_height / 2

    # Рассчитываем смещение центра рамки относительно центра изображения
    center_offset_x = box_center_x - image_center_x
    center_offset_y = box_center_y - image_center_y
    center_offset = (center_offset_x, center_offset_y)

    return class_id, center_offset

# Переводит смещение из пикселей в метры
def convert_pixels_to_meters(pixel_offset_x, pixel_offset_y, camera_height, camera_fov_h, camera_fov_v):
    # Переводим углы обзора из градусов в радианы
    fov_h_rad = np.radians(camera_fov_h)
    fov_v_rad = np.radians(camera_fov_v)
    
    # Рассчитываем фокусные расстояния камеры в пикселях
    focal_length_h = camera_height / np.tan(fov_h_rad / 2)
    focal_length_v = camera_height / np.tan(fov_v_rad / 2)
    
    # Переводим смещение из пикселей в метры
    x_meters = (pixel_offset_x * camera_height) / focal_length_h
    y_meters = (pixel_offset_y * camera_height) / focal_length_v
    
    return x_meters, y_meters

# Создает словарь с классом и смещением
def create_dict(class_id, object_offset, number):
    global nav
    if class_id is None:
        return None
    else:
        position = nav.lps.position()
        object_offset_x, object_offset_y = convert_pixels_to_meters(
            *object_offset, 
            position.z, 
            62.2, 
            48.8
        )
        return {
            "type": class_id,
            "number": number,
            "count" : 0,
            "x": (object_offset_x + position.x) / PIXEL_CONST,
            "y": (object_offset_y + position.y) / PIXEL_CONST
        }

def send_points(points):
    ans = requests.post(f"{SERVER_URL}/points", json=points)
    if ans.status_code != 200:
        return False
    return ans.json()["status"] == "OK"

# Считает количество элементов в списке, которые не равны None.
def count_not_none(all_objects):
   return len(list(filter(lambda x: x is not None, all_objects)))
    

def detect_handler(request):
    global bridge
    global yolo_model
    global all_object
    
    image_msg = rospy.wait_for_message("/pioneer_max_camera/image_raw", Image)
    try:
        cv_image = bridge.imgmsg_to_cv2(image_msg, "bgr8")
        class_ids, scores, boxes = yolo_model.detect(cv_image, 0.6, 0.4)
        most_class, object_offset = get_most_probable_class(
            class_ids, 
            scores, 
            boxes, 
            cv_image.shape
        )
        object_dict = create_dict(
            most_class,
            object_offset,
            count_not_none(all_object)
        )
        if (object_dict is None) or (len(all_object) == 0):
            all_object.append(object_dict)
        elif all_object[-1] is None:
            all_object.append(object_dict)
        elif object_dict["type"] == all_object[-1]["type"]:
            all_object.append(None)
        else:
            all_object.append(object_dict)

        if all_object[-1] is not None:
            print(f"Обнаруженный тип повреждения: {all_object[-1]}")
    except:
        pass
    return EmptyResponse()

def send_points_handler(request):
    global all_object
    send_points(all_object)
    return EmptyResponse()

send_points_server = Service("/send_points", Empty, send_points_handler)  # создаем сервис для отправки точек
detect_server = Service("/get_photo", Empty, detect_handler)  # создаем сервис для получения фотографии

rospy.spin()