import sys
print("Script started at top level...")
sys.stdout.flush()
import cv2
import numpy as np
import os
import sys

def get_color_name(bgr_color):
    """Simple heuristic to convert BGR to a basic color name."""
    b, g, r = [int(c) for c in bgr_color]
    
    # Check for neutrals first
    avg = (r + g + b) / 3
    if abs(r - avg) < 15 and abs(g - avg) < 15 and abs(b - avg) < 15:
        if avg < 60: return "Black"
        if avg > 200: return "White"
        return "Gray"
    
    # Primary/Secondary
    if r > g + 20 and r > b + 20:
        if b > 80: return "Purple/Violet"
        return "Red"
    if g > r + 20 and g > b + 20: return "Green"
    if b > r + 20 and b > g + 20: return "Blue"
    
    # Specific color for beetroot-violet
    if r > 100 and b > 100 and g < 100: return "Purple/Violet"
    
    return "Unknown"

def process_wheel(image_path, output_path='output_nuts.jpg'):
    print(f"Step 0: Starting processing for {image_path}...")
    sys.stdout.flush()
    img_orig = cv2.imread(image_path)
    if img_orig is None:
        print(f"Error: Could not read image {image_path}")
        return

    # Resize for faster processing if image is huge
    max_dim = 1200
    h_orig, w_orig = img_orig.shape[:2]
    if max(h_orig, w_orig) > max_dim:
        scale = max_dim / max(h_orig, w_orig)
        img = cv2.resize(img_orig, (0, 0), fx=scale, fy=scale)
    else:
        scale = 1.0
        img = img_orig.copy()

    display_img = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # --- 1. Wheel Detection ---
    edges = cv2.Canny(blurred, 30, 100)
    kernel_close = np.ones((5, 5), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_close)
    
    contours_wheel, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    wheel_ellipse = None
    max_area = 0
    
    for cnt in sorted(contours_wheel, key=cv2.contourArea, reverse=True):
        area = cv2.contourArea(cnt)
        if area < 5000: continue 
        if len(cnt) >= 20:
            ellipse = cv2.fitEllipse(cnt)
            (xc, yc), (d1, d2), angle = ellipse
            if min(d1, d2) / max(d1, d2) > 0.4:
                if area > max_area:
                    max_area = area
                    wheel_ellipse = ellipse

    if wheel_ellipse is None:
        print("No wheel detected.")
        return

    (xc, yc), (d1, d2), angle = wheel_ellipse
    wheel_radius = max(d1, d2) / 2
    print(f"Step 1: Wheel detected. Radius: {wheel_radius:.2f}")
    sys.stdout.flush()
    
    # --- 2. Advanced Nut Detection (Hub ROI) ---
    hub_radius_factor = 0.5
    hub_mask = np.zeros(img.shape[:2], dtype=np.uint8)
    cv2.ellipse(hub_mask, ((xc, yc), (d1*hub_radius_factor, d2*hub_radius_factor), angle), 255, -1)
    
    print("Step 2: Processing thresholds...")
    thresh_a = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                    cv2.THRESH_BINARY_INV, 15, 2)
    _, thresh_b = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
    thresh_c = np.uint8(np.absolute(laplacian))
    _, thresh_c = cv2.threshold(thresh_c, 20, 255, cv2.THRESH_BINARY)

    print("Step 3: Combining thresholds...")
    combined_thresh = cv2.bitwise_or(thresh_a, thresh_b)
    combined_thresh = cv2.bitwise_or(combined_thresh, thresh_c)
    combined_thresh = cv2.bitwise_and(combined_thresh, hub_mask)
    
    kernel_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    combined_thresh = cv2.morphologyEx(combined_thresh, cv2.MORPH_OPEN, kernel_clean)
    
    nut_contours, _ = cv2.findContours(combined_thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Step 4: Found {len(nut_contours)} candidate contours.")
    sys.stdout.flush()
    
    unique_nuts = []
    # Sort candidates by area for efficient deduplication
    for cnt in sorted(nut_contours, key=cv2.contourArea, reverse=True):
        area = cv2.contourArea(cnt)
        # Nut size limits relative to wheel
        if area < (wheel_radius * 0.04)**2 * np.pi or area > (wheel_radius * 0.18)**2 * np.pi:
            continue
            
        (nx, ny), nr = cv2.minEnclosingCircle(cnt)
        
        # Deduplicate
        is_dup = False
        for unx, uny, unr, ucnt in unique_nuts:
            if np.hypot(nx - unx, ny - uny) < (nr + unr) * 0.7:
                is_dup = True
                break
        if not is_dup:
            unique_nuts.append((int(nx), int(ny), int(nr), cnt))

    # --- 3. Classification & Color ---
    nut_data = []
    for nx, ny, nr, cnt in unique_nuts:
        # Avoid image edges
        if nx-nr < 0 or ny-nr < 0 or nx+nr >= img.shape[1] or ny+nr >= img.shape[0]: continue
        
        # Color
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [cnt], -1, 255, -1)
        # Dilate mask slightly for better color sampling
        mask = cv2.dilate(mask, np.ones((3,3), np.uint8))
        color_bgr = cv2.mean(img, mask=mask)[:3]
        color_name = get_color_name(color_bgr)
        
        # Classification: LOCAL INTENSITY MINIMUM check
        # Compare center intensity (the potential hole) to the ring intensity (nut surface)
        roi_gray = gray[ny-nr:ny+nr, nx-nr:nx+nr]
        if roi_gray.size == 0: continue
        h_r, w_r = roi_gray.shape
        center_val = np.mean(roi_gray[int(h_r*0.35):int(h_r*0.65), int(w_r*0.35):int(w_r*0.65)])
        
        # Sample ring area (surface)
        ring_mask = np.zeros(roi_gray.shape, dtype=np.uint8)
        cv2.circle(ring_mask, (int(w_r/2), int(h_r/2)), int(nr), 255, -1)
        cv2.circle(ring_mask, (int(w_r/2), int(h_r/2)), int(nr*0.5), 0, -1)
        ring_val = cv2.mean(roi_gray, mask=ring_mask)[0]
        
        # If center is darker than ring by a relative margin, it's a Hex-Hole
        # Increased sensitivity since the user says all are hex-holes
        is_hex = center_val < ring_val * 0.9 or center_val < 100
        
        nut_data.append({
            'pos': (nx, ny),
            'radius': nr,
            'type': "Hex-Hole" if is_hex else "Solid",
            'color': color_name
        })

    # --- 4. Visualization ---
    cv2.ellipse(display_img, wheel_ellipse, (0, 255, 0), 3)
    # Output Hub ROI for debug
    cv2.ellipse(display_img, ((xc, yc), (d1*hub_radius_factor, d2*hub_radius_factor), angle), (128, 128, 128), 1)

    for nut in nut_data:
        # Use contrasting colors for drawing
        draw_color = (255, 0, 0) if nut['type'] == "Hex-Hole" else (0, 0, 255)
        nx_p, ny_p = int(nut['pos'][0]), int(nut['pos'][1])
        nr_p = int(nut['radius'])
        
        cv2.circle(display_img, (nx_p, ny_p), nr_p, draw_color, 2)
        cv2.putText(display_img, f"{nut['color']} {nut['type'][0]}", 
                    (nx_p-20, ny_p-nr_p-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    # Print summary
    print(f"--- Final Analysis for {os.path.basename(image_path)} ---")
    print(f"Total Nuts Found: {len(nut_data)}")
    for i, n in enumerate(nut_data):
        print(f"  Nut {i+1}: {n['color']} ({n['type']})")
    
    cv2.imwrite(output_path, display_img)
    print(f"Result saved to {output_path}")

if __name__ == "__main__":
    test_img = '20260216_161006.jpg'
    if os.path.exists(test_img):
        process_wheel(test_img)
    else:
        print(f"Image not found: {test_img}")
