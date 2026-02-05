from ultralytics import YOLO
model = YOLO("/home/stefano/Documents/ATS_nto (copy)/src/detection/models/best.pt")
model.export(format="torchscript") # Создаст файл best.torchscript