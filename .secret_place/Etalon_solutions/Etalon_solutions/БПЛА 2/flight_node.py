#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from rospy import ServiceProxy
from std_srvs.srv import Empty, Trigger
from gs_flight import FlightController, CallbackEvent
from gs_board import BoardManager
from gs_navigation import NavigationManager

rospy.init_node("flight_test_node")  # инициализируем узел

# получаем координаты стартовой точки
nav = NavigationManager()
HOME_POINT = nav.lps.position()
HOME_POINT.z += 1.0
HOME_POINT = [HOME_POINT.x, HOME_POINT.y, HOME_POINT.z]

coordinates = [ # массив координат точек
    HOME_POINT,
    ... # необходимо вставить замеренные точки в формате [x, y, z]
    HOME_POINT
]

run = True # переменная отвечающая за работу программы
position_number = 0 # счетчик пройденных точек

def callback(event): # функция обработки событий Автопилота
    global ap
    global run
    global coordinates
    global position_number
    global detect_client
    global stat_client

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
        detect_client()
        position_number += 1 # наращиваем счетчик точек
        if position_number < len(coordinates): # проверяем количество текущее количество точек с количеством точек в полетном задании
            ap.goToLocalPoint(coordinates[position_number][0], coordinates[position_number][1], coordinates[position_number][2]) # отдаем команду полета в точку
        else:
            ap.landing() # отдаем команду посадки
    elif event == CallbackEvent.COPTER_LANDED: # блок обработки события приземления
        print("finish programm")
        run = False # прекращем программу
        response = stat_client()
        print(f"Кол-во поврежденных участков {response.message}")

detect_client = ServiceProxy("/get_photo", Empty) # клиент сервиса распознавания
stat_client = ServiceProxy("/get_stat", Trigger)
board = BoardManager() # создаем объект бортового менеджера
ap = FlightController(callback) # создаем объект управления полета

once = False # переменная отвечающая за первое вхождение в начало программы

while not rospy.is_shutdown() and run:
    if board.runStatus() and not once: # проверка подлкючения RPi к Пионеру
        print("start programm")
        ap.preflight() # отдаем команду выполенения предстартовой подготовки
        once = True
    pass