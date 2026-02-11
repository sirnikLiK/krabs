import rospy
from sensor_msgs.msg import Image
from std_srvs.srv import Empty, EmptyResponse
import cv2
from cv_bridge import CvBridge
from rospy import Service
import numpy as np

rospy.init_node("detect_node")  # инициализируем узел
bridge = CvBridge()  # создаем объект преобразования сообщений ROS в OpenCV

weights_path = "yolov4-tiny-obj_best.weights"
config_path = "yolov4-tiny-obj.cfg"

net = cv2.dnn.readNet(config_path, weights_path)
yolo_model = cv2.dnn.DetectionModel(net)
all_object = []

# Выдает самый веротяный объект на изображении
def get_most_probable_class(class_ids, confidences):
    if len(class_ids) == 0 or len(confidences) == 0:
        return None
    most_probable_index = np.argmax(confidences)
    return class_ids[most_probable_index]

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
        most_class = get_most_probable_class(class_ids, scores)
        if (most_class is None) or (len(all_object) == 0):
            all_object.append(most_class)
        elif most_class == all_object[-1]:
            all_object.append(None)
        else:
            all_object.append(most_class)

        if all_object[-1] is not None:
            print(f"Обнаруженный тип повреждения: {all_object[-1]}")
    except:
        pass
    return EmptyResponse()

detect_server = Service("/get_photo", Empty, detect_handler)  # создаем сервис для получения фотографии
rospy.spin()