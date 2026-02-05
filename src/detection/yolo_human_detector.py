from ultralytics import YOLO
# from roboflow import download_dataset
import cv2

model = YOLO("/home/stefano/Documents/ATS_nto (copy)/src/detection/models/best.pt")


cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    results = model(frame, verbose=False)
    
    filtered_boxes = []
    conf_threshold = 0.5
    for box in results[0].boxes:
        if box.conf.item() > conf_threshold:
            filtered_boxes.append(box)
    
    num_objects = len(filtered_boxes)
    
    results[0].boxes = filtered_boxes
    annotated_frame = results[0].plot()
    cv2.putText(
        annotated_frame,
        f"Count humans: {num_objects}",
        (10, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        2,
        (0, 0, 255),
        2,
    )
    
    cv2.imshow("Finds peoples", annotated_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()