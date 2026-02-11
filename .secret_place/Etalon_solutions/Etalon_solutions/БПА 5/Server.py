import requests


class Server:
    def __init__(self):
        self.base_url = "http://172.16.65.50:8000"

    def send_points(self, points: list) -> bool:
        ans = requests.post(f"{self.base_url}/points", json=points)
        if ans.status_code != 200:
            return False
        return ans.json()["status"] == "OK"

    def get_points(self) -> list:
        ans = requests.get(f"{self.base_url}/points")
        if ans.status_code != 200:
            return []
        return ans.json()["detail"]

    def send_task(self, tasks: list) -> bool:
        ans = requests.post(f"{self.base_url}/task", json=tasks)
        print(ans.json())
        if ans.status_code != 200:
            return False
        return ans.json()["status"] == "OK"

    def get_task(self) -> list:
        ans = requests.get(f"{self.base_url}/task")
        if ans.status_code != 200:
            return []
        return ans.json()["detail"]

    def visit_point(self, number) -> list:
        ans = requests.post(f"{self.base_url}/point?number={number}")
        if ans.status_code != 200:
            return []
        return ans.json()["status"]