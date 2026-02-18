from ultralytics import YOLO

model = YOLO('yolov8n.pt')

results = model.train(
    data='/home/user/Documents/krabs/eyecar_track/code/my_data.yaml', 
    epochs=50,
    imgsz=640,
    device='cpu',  # <--- КРИТИЧЕСКОЕ ИЗМЕНЕНИЕ
    project='eyecar_1',
    name='version_1'
)