import cv2
import time
from wheel_analysis import WheelAnalysis

def main():
    print("--- SERVICE CENTER SYSTEM ---")
    
    analyzer = WheelAnalysis()
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # 1. Detect Wheel
        wheel_rect = analyzer.detect_wheel(frame)
        
        if wheel_rect:
            x, y, w, h = wheel_rect
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Crop wheel
            wheel_img = frame[y:y+h, x:x+w]
            
            if wheel_img.size > 0:
                # 2. Classify
                w_type = analyzer.classify_wheel(wheel_img)
                cv2.putText(frame, f"Type: {w_type}", (x, y-10), 0, 0.7, (255, 0, 0), 2)
                
                # 3. Find Bolts
                bolts = analyzer.find_bolts(wheel_img)
                
                bolt_count = 0
                hole_count = 0
                
                for (bx, by, btype) in bolts:
                    # Draw relative to wheel rect
                    abs_x, abs_y = x + bx, y + by
                    color = (0, 255, 0) if btype == 'bolt' else (0, 0, 255)
                    cv2.circle(frame, (abs_x, abs_y), 5, color, -1)
                    
                    if btype == 'bolt': bolt_count += 1
                    else: hole_count += 1
                
                info_text = f"Bolts: {bolt_count} | Holes: {hole_count}"
                cv2.putText(frame, info_text, (x, y+h+25), 0, 0.6, (255, 255, 255), 1)

        cv2.imshow("Service Center", frame)
        if cv2.waitKey(1) == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
