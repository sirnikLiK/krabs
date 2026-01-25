import cv2 as cv
import numpy as np

# Load reference images
ref1 = cv.imread('ref1.png')
ref2 = cv.imread('ref2.png')

# Resize references to 64x64 if they exist
if ref1 is not None:
    ref1 = cv.resize(ref1, (64, 64))
if ref2 is not None:
    ref2 = cv.resize(ref2, (64, 64))

cap = cv.VideoCapture(1)
 
while(True):
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    copyf = frame.copy()
        
    frameHSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV) 
    frameBlur = cv.blur(frameHSV, (5, 5))
    mask = cv.inRange(frameBlur, (0,143,124), (212,245,207))
    maskEr = cv.erode(mask, None, iterations=2)
    maskDil = cv.dilate(mask, None, iterations=4)
    contours, _ = cv.findContours(maskDil, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    
    if contours:
        contours = sorted(contours, key=cv.contourArea, reverse=True)
        cv.drawContours(frame, contours[0], -1, (255,0,255), 3)
        (x,y,w,h) = cv.boundingRect(contours[0])
        cv.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
        roImg = copyf[y:y+h, x:x+w]
        
        # Resize detected object
        try:
            roImgResized = cv.resize(roImg, (64, 64))
            
            best_match = "None"
            max_similarity = -1

            # Compare with ref1
            if ref1 is not None:
                # Calculate absolute difference
                diff1 = cv.absdiff(roImgResized, ref1)
                # Count pixels with small difference (e.g. less than 30 intensity difference)
                less_than_30_1 = np.less(diff1, 30)
                match_count_1 = np.sum(less_than_30_1)
                
                if match_count_1 > max_similarity:
                    max_similarity = match_count_1
                    best_match = "1"

            # Compare with ref2
            if ref2 is not None:
                diff2 = cv.absdiff(roImgResized, ref2)
                less_than_30_2 = np.less(diff2, 30)
                match_count_2 = np.sum(less_than_30_2)
                
                if match_count_2 > max_similarity:
                    max_similarity = match_count_2
                    best_match = "2"
            
            # Draw result text
            cv.putText(frame, f"Match: {best_match}", (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv.imshow("roImg", roImgResized)
            
        except Exception as e:
            print(f"Error processing ROI: {e}")

        cv.imshow("contours", frame)
    cv.imshow("mask", mask)
    #cv.imshow("maskEr", maskEr)
    #cv.imshow("maskDil", maskDil)
    if cv.waitKey(1)==ord("q"):
        break
cap.release()
cv.destroyAllWindows()
