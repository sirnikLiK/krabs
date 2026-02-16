import cv2
import numpy as np

def detect_wheels(image_path, output_path='output.jpg'):
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image at {image_path}")
        return

    # Create copies for visualization
    hough_viz = img.copy()
    ellipse_viz = img.copy()

    # Preprocessing for Hough
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    # 1. Hough Circle Transform (Method "Khafa"/Hough)
    # Refined parameters to reduce noise
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=200,
                               param1=100, param2=80, minRadius=50, maxRadius=300)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            cv2.circle(hough_viz, (i[0], i[1]), i[2], (0, 255, 0), 2)
            cv2.circle(hough_viz, (i[0], i[1]), 2, (0, 0, 255), 3)
            print(f"Hough Circle detected at ({i[0]}, {i[1]}) with radius {i[2]}")
    else:
        print("No Hough circles detected.")

    # 2. Ellipse Fitting (Better for angled circles)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Expanded range for green rim to catch shadowed wheel
    lower_green = np.array([30, 40, 40])
    upper_green = np.array([90, 255, 255])
    
    mask = cv2.inRange(hsv, lower_green, upper_green)
    # Better cleaning
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 300: # Slightly lower threshold
            continue
            
        if len(cnt) >= 20: # Slightly more points for stable fit
            ellipse = cv2.fitEllipse(cnt)
            (xc, yc), (d1, d2), angle = ellipse
            
            # Additional filtering: wheels are usually roughly circular but angled
            ratio = min(d1, d2) / max(d1, d2)
            if ratio < 0.4: # Filter very elongated shapes
                continue

            cv2.ellipse(ellipse_viz, ellipse, (255, 0, 0), 2)
            cv2.circle(ellipse_viz, (int(xc), int(yc)), 2, (0, 0, 255), 3)
            print(f"Ellipse detected at ({int(xc)}, {int(yc)}) with axes ({int(d1)}, {int(d2)}) at angle {angle:.2f}")

    # Combine results for display
    combined = np.hstack((hough_viz, ellipse_viz))
    cv2.imwrite(output_path, combined)
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    detect_wheels('/home/stefano/Documents/test/photo_2026-02-16_20-28-45.jpg')
