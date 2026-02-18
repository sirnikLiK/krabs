import cv2
import numpy as np

def detect_any_wheel(frame):
    h, w = frame.shape[:2]
    
    start_x = max(0, (w - 640) // 2)
    start_y = max(0, (h - 480) // 2)
    
    img = frame[start_y:start_y + 480, start_x:start_x + 640] # обрезка кадра
    #img = cv2.resize(frame, (640, 480)) #масштабирование
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    edged = cv2.Canny(blurred, 20, 80)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dilated = cv2.dilate(edged, kernel, iterations=2)
    closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        for cnt in sorted(contours, key=cv2.contourArea, reverse=True)[:10]:
            area = cv2.contourArea(cnt)
            if area < 1500: continue

            bx, by, bw, bh = cv2.boundingRect(cnt)
            aspect_ratio = float(bw) / bh
            
            if 0.6 < aspect_ratio < 1.5:
                rect_area = bw * bh
                solidity = float(area) / rect_area
                if solidity > 0.3: 
                    cv2.rectangle(img, (bx, by), (bx + bw, by + bh), (0, 255, 0), 2)
    return img

def main():
    
    source = 0
    cap = cv2.VideoCapture(source)
    if not cap.isOpened(): return

    while True:
        ret, frame = cap.read()
        if not ret:
            if source.endswith(('.png', '.jpg', '.jpeg')): cv2.waitKey(0)
            break
        
        result = detect_any_wheel(frame)
        cv2.imshow("Detection", result)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()