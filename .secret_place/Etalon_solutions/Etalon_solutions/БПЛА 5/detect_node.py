import rospy
from sensor_msgs.msg import Image
from std_srvs.srv import Empty, EmptyResponse
import cv2
from cv_bridge import CvBridge
from rospy import Service
import numpy as np
import base64
import requests
import paho.mqtt.client as mqtt
from time import time
from io import BytesIO

MQTT_BROKER = "172.16.65.70"
MQTT_PORT = 1883
SERVER_URL = "http://172.16.65.50:8000"

def array_to_bytes(x: np.ndarray) -> bytes:
    np_bytes = BytesIO()
    np.save(np_bytes, x, allow_pickle=True)
    return np_bytes.getvalue()

def bytes_to_array(b: bytes) -> np.ndarray:
    np_bytes = BytesIO(b)
    return np.load(np_bytes, allow_pickle=True)

class CheckClient:
    def __init__(self, team_num, client_type):
        self.team_num = team_num
        self.client_type = client_type
        if client_type == 'car':
            self.topic_type = 'accelerometer'
        elif client_type == 'copter':
            self.topic_type = 'image'

        self._output = None

        self._client = mqtt.Client()
        self._client.on_connect = self.__on_connect
        self._client.on_message = self.__on_message

        self._client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self._client.loop_start()

    def __on_connect(self, client, userdata, flags, rc):
        client.subscribe(f"{self.client_type}/{self.team_num}/{self.topic_type}/response")

    def __on_message(self, client, userdata, msg):
        if self.client_type == 'car':
            self._output = msg.payload.decode()
        elif self.client_type == 'copter':
            self._output = bytes_to_array(msg.payload)

    def send(self, data=None):
        if self.client_type == 'car':
            data = 'get_sample'
        elif self.client_type == 'copter':
            data = array_to_bytes(data)

        self._client.publish(f"{self.client_type}/{self.team_num}/{self.topic_type}/request", data)

    def get_output(self):
        start_time = time()
        while time() - start_time < 20:
            if self._output is not None:
                break
        out = self._output
        self._output = None
        return out

rospy.init_node("detect_node")
bridge = CvBridge()
client = CheckClient(1, 'copter')

def send_image_to_server(original_image, processed_image):
    # Кодируем исходное изображение в JPEG
    _, buffer_orig = cv2.imencode('.jpg', original_image)
    # Кодируем обработанное изображение в JPEG
    _, buffer_proc = cv2.imencode('.jpg', processed_image)
    
    # Конвертируем в base64
    img_orig_base64 = base64.b64encode(buffer_orig).decode('utf-8')
    img_proc_base64 = base64.b64encode(buffer_proc).decode('utf-8')
    
    # Отправляем на сервер
    response = requests.post(
        f"{SERVER_URL}/images",
        json={
            "original": img_orig_base64,
            "processed": img_proc_base64
        }
    )
    return response.status_code == 200

def detect_handler(request):
    global bridge
    
    image_msg = rospy.wait_for_message("/pioneer_max_camera/image_raw", Image)
    try:
        cv_image = bridge.imgmsg_to_cv2(image_msg, "bgr8")
        client.send(cv_image)
        output = client.get_output()
        
        if output is not None:
            send_image_to_server(cv_image, output)
        
    except Exception as e:
        print(f"Ошибка в detect_handler: {str(e)}")
    return EmptyResponse()

detect_server = Service("/get_photo", Empty, detect_handler)
rospy.spin()