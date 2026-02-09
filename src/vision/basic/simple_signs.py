import cv2
import numpy as np

def detect_sign(frame):
    """
    Detects blue signs and classifies shape: Triangle, Square, Circle.
    """
    # HSV for Blue Signs
    # Adjust for your specific sign color (e.g. might be darker blue)
    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([140, 255, 255])
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_shape = "none"
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1000: # Min area filter
            perimeter = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * perimeter, True)
            
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w)/h
            
            shape_name = "unknown"
            
            if len(approx) == 3:
                shape_name = "triangle"
            elif len(approx) == 4:
                # Check if square or rectangle
                if 0.95 <= aspect_ratio <= 1.05:
                    shape_name = "square"
                else:
                    shape_name = "rectangle"
            elif len(approx) > 8:
                shape_name = "circle"
            
            detected_shape = shape_name
            
            cv2.drawContours(frame, [approx], 0, (0, 255, 0), 2)
            cv2.putText(frame, shape_name, (x, y - 10), 0, 0.5, (0, 255, 0), 2)
            
    return detected_shape, frame

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        shape, frame = detect_sign(frame)
        
        cv2.imshow("Simple Sign Detection", frame)
        if cv2.waitKey(1) == ord('q'): break
        
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
