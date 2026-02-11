import cv2
import numpy as np
import json
from collections import deque

from typing import List

from Server import Server

server = Server()
biggest_num = 0

with open("./lines.json", "r") as f:
    lines = json.load(f)

graph = {
    "6": [("10", "STRAIGHT"), ("9", "LEFT")],
    "7": [("15", "RIGHT")],
    "8": [("7", "RIGHT"), ("10", "LEFT")],
    "9": [("13", "RIGHT"), ("16", "LEFT")],
    "10": [("14", "LEFT")],
    "11": [("9", "RIGHT"), ("7", "STRAIGHT")],
    "13": [("11", "RIGHT")],
    "14": [("16", "STRAIGHT"), ("8", "LEFT")],
    "15": [("8", "RIGHT"), ("13", "STRAIGHT")],
    "16": [("6", "LEFT")]
}


class DamagePoint:
    def __init__(self, x, y, damage_type, visit_count, number):
        self.x: int = x
        self.y: int = y
        self.damage_type = damage_type
        self.visit_count: int = visit_count
        self.number: int = number

    def get_zone(self):
        nearest_zone = None
        min_distance = 1e9
        percent_position = 0

        for zone_id, points in lines.items():
            points = np.array(points)
            distances = np.linalg.norm(points - np.array((self.x, self.y)), axis=1)
            min_idx = np.argmin(distances)
            min_dist = distances[min_idx]

            if min_dist < min_distance:
                min_distance = min_dist
                nearest_zone = zone_id
                percent_position = (min_idx / (len(points) - 1)) * 100

        return nearest_zone, float(round(percent_position, 2))

    def json(self):
        return {"type": self.damage_type, "number": self.number, "count": self.visit_count, "x": self.x, "y": self.y}


def find_shortest_path(start, target):
    queue = deque([(start, [], None)])
    visited = set()

    while queue:
        current_zone, path, last_direction = queue.popleft()

        if current_zone == target:
            return path + [current_zone]

        if current_zone in visited:
            continue
        visited.add(current_zone)

        for neighbor, direction in graph.get(current_zone, []):
            if neighbor not in visited:
                queue.append((neighbor, path + [current_zone], direction))

    return []


def find_all_points(zone, damage_points):
    data = []
    for point in damage_points:
        if point.get_zone()[0] == zone:
            data.append((point.number, point.get_zone()[1]))

    return [f"{dt[0]}" for dt in sorted(data, key=lambda x: x[1])]


def find_optimal_route(start, targets):
    print(targets)
    targets = set(targets)
    visited = []
    current_zone = start
    route = [current_zone]

    while targets:
        best_next_zone = None
        best_path = None
        min_turns = 1e9

        for target in targets:
            path = find_shortest_path(current_zone, target)
            turns = len(path)

            if turns < min_turns:
                min_turns = turns
                best_next_zone = target
                best_path = path

        if best_next_zone:
            route.extend(best_path[1:])
            for pt in find_all_points(best_next_zone, damage_points):
                visited.append((len(route), pt))
            targets.remove(best_next_zone)
            current_zone = best_next_zone

    path = find_shortest_path(current_zone, stop_zone)
    route.extend(path[1:])

    return route, visited


def send_all_points(points: List[DamagePoint]):
    data = []
    for point in points:
        data.append(point.json())
    if server.send_points(data):
        print("Data was sent to server!")
    else:
        print("Error in sanding data!")


image_path = "./image.jpg"
image = cv2.imread(image_path)
image = cv2.resize(image, (815, 600))
original_image = image.copy()
damage_points = []


def draw_points():
    global image
    image = original_image.copy()

    for idx, point in enumerate(damage_points):
        cv2.circle(image, (point.x, point.y), 5, (0, 0, 255), -1)
        text = f"{point.damage_type}/{point.visit_count}/{point.number}"
        cv2.putText(image, text, (point.x - 20, point.y - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imshow("Map", image)


def update_points():
    global damage_points, biggest_num
    damage_points = []
    server_points = server.get_points()
    biggest_num = 0
    for point in server_points:
        biggest_num = max(biggest_num, point["number"])
        damage_points.append(DamagePoint(point["x"], point["y"], point["type"], point["count"], point["number"]))
    draw_points()


update_points()

robot_zone = None
stop_zone = None
freeze_zone = None


def mouse_callback(event, x, y, flags, param):
    global damage_points, robot_zone, biggest_num, stop_zone, freeze_zone

    if event == cv2.EVENT_LBUTTONDOWN:
        for i, point in enumerate(damage_points):
            if abs(point.x - x) < 10 and abs(point.y - y) < 10:
                print(f"Удаление точки: {point.damage_type}")
                del damage_points[i]
                draw_points()
                send_all_points(damage_points)
                return

        damage_type = input("Тип повреждения: ")

        damage_point = DamagePoint(x, y, damage_type, 0, biggest_num + 1)
        biggest_num += 1
        damage_points.append(damage_point)
        send_all_points(damage_points)
        draw_points()

    elif event == cv2.EVENT_RBUTTONDOWN:
        if not robot_zone:
            robot_zone, _ = DamagePoint(x, y, 0, 0, 0).get_zone()
            print(f"Робот установлен в зону {robot_zone}")
            freeze_zone = input("Зона для взятия проб: ")
            print("Нажмите на точку остановки")
        else:
            stop_zone, _ = DamagePoint(x, y, 0, 0, 0).get_zone()
        if robot_zone and stop_zone:
            plan_robot_route()


def plan_robot_route():
    if not robot_zone:
        print("Зона робота не установлена.")
        return

    target_zones = {dp.get_zone()[0] for dp in damage_points}
    if not target_zones:
        print("Точек нет")
        return

    route, visited = find_optimal_route(robot_zone, target_zones)
    vis_cnt = 0

    task = []

    for i in range(len(route) - 1):
        for neighbor, action in graph.get(route[i], []):
            if neighbor == route[i + 1]:
                task.append(action)
                while vis_cnt < len(visited) and i + 1 == visited[vis_cnt][0] - 1:
                    if freeze_zone == visited[vis_cnt][1]:
                        pass
                    else:
                        task.append(visited[vis_cnt][1])
                    vis_cnt += 1
                break
    task.append("f")
    print(task)
    print(visited)
    server.send_task(task)


def main():
    draw_points()
    cv2.setMouseCallback("Map", mouse_callback)

    while True:
        key = cv2.waitKey(1) & 0xFF
        update_points()
        if key == 27:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
