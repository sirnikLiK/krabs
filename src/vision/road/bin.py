import cv2 as cv
import numpy as np

# --- Object Detection Template Matching ---
# This script uses reference images (ref1.png, ref2.png) to identify objects 
# in the video feed by comparing them to detected contours.

# --- Load Reference Images ---
# These images are the "ground truth" to look for.
ref1 = cv.imread('ref1.png')
ref2 = cv.imread('ref2.png')

# Resize references to 64x64 if they exist
# A fixed size is crucial for pixel-by-pixel comparison (absdiff)
if ref1 is not None:
    ref1 = cv.resize(ref1, (64, 64))
if ref2 is not None:
    ref2 = cv.resize(ref2, (64, 64))

# Open default camera (index 1 often refers to external USB cam)
cap = cv.VideoCapture(1)
 
while(True):
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    copyf = frame.copy()
        
    # --- Preprocessing & Contour Detection ---
    # Convert to HSV color space for better color segmentation
    frameHSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV) 
    # Blur to reduce noise
    frameBlur = cv.blur(frameHSV, (5, 5))
    # Create a binary mask for the target color range (Greenish/Yelllowish?)
    mask = cv.inRange(frameBlur, (0,143,124), (212,245,207))
    
    # Morphological operations to clean up the mask
    maskEr = cv.erode(mask, None, iterations=2) # Remove small noise
    maskDil = cv.dilate(mask, None, iterations=4) # Connect broken parts
    
    # Find contours in the mask
    contours, _ = cv.findContours(maskDil, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    
    if contours:
        # Sort contours by area (largest first) and take the biggest one
        contours = sorted(contours, key=cv.contourArea, reverse=True)
        cv.drawContours(frame, contours[0], -1, (255,0,255), 3)
        
        # Get Bounding Box of the largest contour
        (x,y,w,h) = cv.boundingRect(contours[0])
        cv.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
        
        # Extract Region of Interest (ROI) - the potential object
        roImg = copyf[y:y+h, x:x+w]
        
        # Resize detected object
        # Resize detected detected ROI to fixed 64x64 for comparison
        try:
            roImgResized = cv.resize(roImg, (64, 64))
            
            best_match = "None"
            max_similarity = -1

            # --- Template Matching / Comparison ---
            # Compare with ref1
            if ref1 is not None:
                # Calculate absolute difference between ROI and Reference
                diff1 = cv.absdiff(roImgResized, ref1)
                # Count the number of 'similar' pixels (difference < 30)
                less_than_30_1 = np.less(diff1, 30)
                match_count_1 = np.sum(less_than_30_1)
                
                # Check if this is the best match so far
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
