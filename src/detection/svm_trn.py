import cv2
import dlib
import os
import xml.etree.ElementTree as pars

# --- SVM Detector Trainer ---
# Purpose: Trains a dlib simple object detector (HOG + SVM) using 
# a dataset of images and XML annotations (Pascal VOC format).

dir = "/home/stefano/Documents/ATS_nto/ped_detect"
image = []
labels = []

imgnames = os.listdir(dir + '/img')

for imgname in imgnames:
    img = cv2.imread(dir + '/img/' + imgname)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    image.append(img)

    # Parse XML annotation
    onlyfilename = imgname.split(".")[0]
    e = pars.parse(dir + '/labels/' + onlyfilename + '.xml')
    root = e.getroot()
    object= root.find("object")
    object=object.find("bndbox")
    
    # Get bounding box coordinates
    xmin = int(object.find("xmin").text)
    ymin = int(object.find("ymin").text)
    xmax = int(object.find("xmax").text)
    ymax = int(object.find("ymax").text)
    
    # Check for invalid coordinates (sometimes xmin > xmax etc)
    # The original code just appends, let's document it relies on correct XMLs.
    labels.append([dlib.rectangle(left=xmin, top=ymin, right=xmax, bottom=ymax)])
  
options = dlib.simple_object_detector_training_options()
options.be_verbose = True
# Train the SVM
detector = dlib.train_simple_object_detector(image, labels, options)

detector.save("tld.svm")
print("Training finished. Detector saved to tld.svm")