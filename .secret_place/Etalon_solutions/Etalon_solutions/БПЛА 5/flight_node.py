#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from rospy import ServiceProxy
from std_srvs.srv import Empty
from gs_flight import FlightController, CallbackEvent
from gs_board import BoardManager
from gs_navigation import NavigationManager
import requests

SERVER_URL = "http://172.16.65.50:8000"
PIXEL_CONST = 0.0067

rospy.init_node("flight_test_node")  # инициализируем узел

# получаем координаты стартовой точки
nav = NavigationManager()
HOME_POINT = nav.lps.position()
HOME_POINT.z += 1.0
HOME_POINT = [HOME_POINT.x, HOME_POINT.y, HOME_POINT.z]

coordinates = [
    HOME_POINT
]

run = True # переменная отвечающая за работу программы
position_number = 0 # счетчик пройденных точек

once = False # переменная отвечающая за первое вхождение в начало программы

def get_copter_task():
    ans = requests.get(f"{SERVER_URL}/copter_task")
    if ans.status_code != 200:
        return None
    return ans.json()["detail"]

def callback(event): # функция обработки событий Автопилота
    global ap
    global run
    global coordinates
    global position_number
    global detect_client

    event = event.data
    if event == CallbackEvent.ENGINES_STARTED: # блок обработки события запуска двигателя
        print("engine started")
        ap.takeoff() # отдаем команду взлета
    elif event == CallbackEvent.TAKEOFF_COMPLETE: # блок обработки события завершения взлета
        print("takeoff complete")
        position_number = 0
        ap.goToLocalPoint(coordinates[position_number][0], coordinates[position_number][1], coordinates[position_number][2]) # отдаем команду полета в точку
    elif event == CallbackEvent.POINT_REACHED: # блок обработки события достижения точки
        print(f"point {position_number} reached")
        position_number += 1 # наращиваем счетчик точек
        if position_number < len(coordinates): # проверяем количество текущее количество точек с количеством точек в полетном задании
            ap.goToLocalPoint(coordinates[position_number][0], coordinates[position_number][1], coordinates[position_number][2]) # отдаем команду полета в точку
        elif position_number == len(coordinates):
            detect_client()
            ap.goToLocalPoint(*HOME_POINT)
        else:
            ap.landing() # отдаем команду посадки
    elif event == CallbackEvent.COPTER_LANDED: # блок обработки события приземления
        print("finish programm")
        run = False # прекращем программу

detect_client = ServiceProxy("/get_photo", Empty) # клиент сервиса распознавания
board = BoardManager() # создаем объект бортового менеджера
ap = FlightController(callback) # создаем объект управления полета

while not rospy.is_shutdown() and run:
    if board.runStatus() and not once: # проверка подключения RPi к Пионеру
        print("start programm")
        while True:
            task = get_copter_task()
            if task is not None:
                coordinates.append([task["x"] * PIXEL_CONST, task["y"] * PIXEL_CONST, HOME_POINT[2]])
                break
        ap.preflight() # отдаем команду выполнения предстартовой подготовки
        once = True
    pass