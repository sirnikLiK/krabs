# -*- coding: utf-8 -*-
import cv2
import numpy
## TODO: Допишите импорт библиотек, которые собираетесь использовать


def find_markers(image) -> list:
    img = cv2.resize(image, (480, 270))
    binimg = cv2.inRange(img, (0, 0, 0), (55, 55, 55))
    contours, _ = cv2.findContours(binimg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    kubs = 0
    lines = []
    for j in range(len(contours)):
        (x, y, w, h) = cv2.boundingRect(contours[j])
        if w > 40 and h > 40:
            kubs += 1
            marker = img[y:y + h, x:x + w]
            bmarker = cv2.inRange(marker, (0, 0, 0), (55, 55, 55))
            bmarker = cv2.inRange(bmarker, 0, 0)
            bmarker = cv2.erode(bmarker, None, iterations=2)
            bmarker = cv2.dilate(bmarker, None, iterations=3)
            contours1, _ = cv2.findContours(bmarker, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours1 = sorted(contours1, key=cv2.contourArea, reverse=True)
            (mx1, my1, mx2, my2) = 600, 600, 0, 0
            for k in range(len(contours1)):
                (x1, y1, w1, h1) = cv2.boundingRect(contours1[k])
                if w1 > 30 or h1 > 30:
                    mx1, my1 = min(x1, mx1), min(y1, my1)
                    mx2, my2 = max(x1 + w1, mx2), max(y1 + h1, my2)
            cuted = bmarker[my1:my2, mx1:mx2]
            if numpy.sum(cuted) > 490000:
                lines.append(3)
            elif 490001 > numpy.sum(cuted) > 290000:
                lines.append(2)
            else:
                lines.append(1)
    """
        Функция для поиска маркировок грузов на изображении и подсчета количества цветных полос на них.

        Входные данные: изображение (bgr), прочитано cv2.imread
        Выходные данные: список из количества цветных полос на маркировках в порядке возрастания
                         на одной маркировке от 0 до 3 полос

        Примеры вывода:
            [1, 3, 3] - 3 маркировки, на одном из них 1 цветная полоса, на двух других по 3 полосы

            [2] - 1 маркировки, на нем 2 цветные полоски

            [] - маркеры не найдены или отсутствуют цветные полосы

    """
    # Алгоритм проверки будет вызывать функцию find_markers,
    # остальные функции должны вызываться из неё.

    ## TODO: Отредактируйте эту функцию по своему усмотрению.
    result = lines[:]

    return result
