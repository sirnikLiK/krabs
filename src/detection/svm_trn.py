import cv2
import dlib
import os
import xml.etree.ElementTree as pars
import numpy as np

base_dir = "/home/stefano/Documents/ATS_nto/src/detection"
img_dir = os.path.join(base_dir, 'output_frames')
label_dir = os.path.join(base_dir, 'labels_test')

images, labels = [], []
all_ratios, temp_data = [], []

MIN_AREA = 450 

print("Шаг 1: Анализ геометрии объектов...")
for img_name in os.listdir(img_dir):
    file_id = os.path.splitext(img_name)[0]
    xml_path = os.path.join(label_dir, file_id + '.xml')
    if not os.path.exists(xml_path): continue

    try:
        root = pars.parse(xml_path).getroot()
        img_boxes = []
        for obj in root.findall("object"):
            bbox = obj.find("bndbox")
            xmin, ymin = int(bbox.find("xmin").text), int(bbox.find("ymin").text)
            xmax, ymax = int(bbox.find("xmax").text), int(bbox.find("ymax").text)
            w, h = xmax - xmin, ymax - ymin
            
            if (w * h) >= MIN_AREA and h > 0:
                all_ratios.append(w / h)
                img_boxes.append([xmin, ymin, xmax, ymax])
        if img_boxes:
            temp_data.append({'name': img_name, 'boxes': img_boxes})
    except: continue

if not all_ratios:
    print("Объекты не найдены."); exit()

# Вычисляем целевое соотношение сторон
target_ratio = np.median(all_ratios)
print(f"Целевое соотношение (W/H): {target_ratio:.2f}")

print("Шаг 2: Коррекция боксов и загрузка...")
for item in temp_data:
    final_boxes = []
    for b in item['boxes']:
        xmin, ymin, xmax, ymax = b
        w, h = xmax - xmin, ymax - ymin
        
        # Вычисляем, какой должна быть ширина при текущей высоте для target_ratio
        new_w = h * target_ratio
        delta_w = (new_w - w) / 2
        
        # Корректируем границы (центрируем)
        xmin_corr = int(xmin - delta_w)
        xmax_corr = int(xmax + delta_w)
        
        # Добавляем в список (dlib сам отсечет, если выйдет за границы кадра)
        final_boxes.append(dlib.rectangle(left=xmin_corr, top=ymin, right=xmax_corr, bottom=ymax))
    
    if final_boxes:
        img = cv2.imread(os.path.join(img_dir, item['name']))
        if img is not None:
            images.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            labels.append(final_boxes)

print(f"Подготовлено изображений: {len(images)}")

if len(images) > 0:
    options = dlib.simple_object_detector_training_options()
    options.be_verbose = True
    options.add_left_right_image_flips = True # Отражения для увеличения базы
    options.C = 1.0 # Баланс между точностью и переобучением
    
    # Если картинки очень большие, dlib может "скушать" всю оперативку. 
    # В этом случае можно добавить options.upsample_limit = 0
    
    try:
        print("Начинаю обучение (это может занять время)...")
        detector = dlib.train_simple_object_detector(images, labels, options)
        detector.save("tld.svm")
        print("--- Успех! Модель сохранена в tld.svm ---")
    except RuntimeError as e:
        print(f"Dlib всё еще недоволен: {e}")