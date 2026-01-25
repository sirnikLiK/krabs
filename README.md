# ATS_nto - Autonomous Transport System Project

This project contains various computer vision modules for an autonomous vehicle or traffic simulation.

## Project Structure

### 1. `road_detect/` - Lane Detection
*   **`road_dtct.py`**: Main script for lane detection using sliding window and polynomial fitting.
*   **`bin.py`**: Helper script (likely for object/sign detection using template matching).

### 2. `trf_detect/` - Traffic Sign Detection
*   **`bin.py`**: Detects traffic signs by comparing contours against reference images (`ref1.png`, `ref2.png`).
*   **`extrmums.py`**: Utility to find optimal H/S/V color thresholds for detection using trackbars.

### 3. `trf_lgt/` - Traffic Light Detection
*   **`trf.py`**: Detects traffic light state (Red/Yellow/Green) by analyzing specific image regions.
*   **`trf_test.py`**: A traffic light simulator (Tkinter) to test the detector.
*   **`hw.py`**: Simple hardware camera test.

### 4. `ped_detect/` - Pedestrian/Object Detection
*   **`main.py`**: Runs a trained SVM Object Detector on the video feed.
*   **`svm_trn.py`**: Script to train the SVM detector using images and XML labels.