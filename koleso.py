import cv2
import numpy as np

def detect_precise_v2(image_path):
    img = cv2.imread(image_path)
    if img is None: return
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 2)
    edged = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours: return
    wheel_cnt = max(contours, key=cv2.contourArea)
    (x, y), radius = cv2.minEnclosingCircle(wheel_cnt)
    center = (int(x), int(y))
    radius = int(radius)

    hub_r = int(radius * 0.25)
    y1, y2 = max(0, center[1]-hub_r), min(img.shape[0], center[1]+hub_r)
    x1, x2 = max(0, center[0]-hub_r), min(img.shape[1], center[0]+hub_r)
    hub_crop = img[y1:y2, x1:x2].copy()
    

    hub_gray = cv2.cvtColor(hub_crop, cv2.COLOR_BGR2GRAY)
    hub_gray = cv2.medianBlur(hub_gray, 5)

    crop_h, crop_w = hub_gray.shape
    crop_center_coords = (crop_w // 2, crop_h // 2)

    dead_zone_radius = int(hub_r * 0.4)

    # Параметры Hough
    min_dist = int(hub_r * 0.6)
    min_r = int(hub_r * 0.1)
    max_r = int(hub_r * 0.4)

    bolts = cv2.HoughCircles(
        hub_gray, 
        cv2.HOUGH_GRADIENT, 
        dp=1.2, 
        minDist=min_dist,
        param1=600, 
        param2=8, 
        minRadius=min_r, 
        maxRadius=max_r
    )

    bolt_count = 0
    if bolts is not None:
        bolts = np.round(bolts[0, :]).astype("int")
        for (bx, by, br) in bolts:
            dist_from_center = np.sqrt((bx - crop_center_coords[0])**2 + (by - crop_center_coords[1])**2)

            if dist_from_center > dead_zone_radius:
                bolt_count += 1
                cv2.circle(hub_crop, (bx, by), br, (0, 255, 0), 2)
                cv2.circle(hub_crop, (bx, by), 2, (0, 0, 255), -1)

    cv2.circle(img, center, radius, (255, 0, 0), 2)
    cv2.circle(img, center, hub_r, (0, 255, 255), 2)

    cv2.circle(hub_crop, crop_center_coords, dead_zone_radius, (255, 0, 0), 1)

    cv2.imshow("1. Wheel Detection", img)
    cv2.imshow("2. Hub Bolts (Filtered)", hub_crop)
    print(f"Изображение {image_path}: Найдено болтов: {bolt_count}")
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()

detect_precise_v2('image.png')
detect_precise_v2('image3.png')
