from ultralytics import YOLO
import cv2
import time

# --- CONFIG ---
MODEL_PATH = "runs/detect/yolo_nto_train/weights/best.pt" # Path to your trained model
# MODEL_PATH = "yolov8n.pt" # Or use default for testing
CONF_THRESHOLD = 0.5

def main():
    # Load model
    try:
        model = YOLO(MODEL_PATH)
        print(f"Loaded model: {MODEL_PATH}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # Open camera
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    if not cap.isOpened():
        print("Error opening camera")
        return

    print("Press 'q' to exit")

    while True:
        ret, frame = cap.read()
        if not ret: break

        # Inference
        results = model(frame, stream=True, verbose=False)

        # Process results
        for r in results:
            boxes = r.boxes
            for box in boxes:
                conf = float(box.conf[0])
                if conf < CONF_THRESHOLD:
                    continue
                
                # Bounding Box
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Class Name
                cls = int(box.cls[0])
                label = f"{model.names[cls]} {conf:.2f}"

                # Draw
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow("YOLO Inference", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
