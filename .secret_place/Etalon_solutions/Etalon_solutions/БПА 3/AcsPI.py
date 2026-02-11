import paho.mqtt.client as mqtt
import time
import numpy as np
from io import BytesIO

MQTT_BROKER = "172.16.65.72"
MQTT_PORT = 1883


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
        start_time = time.time()
        while time.time() - start_time < 20:
            if self._output is not None:
                break
        out = self._output
        self._output = None
        return out