import cv2
import dlib
import os
import xml.etree.ElementTree as pars

dir = "/home/stefano/Documents/ATS_nto/ped_detect"
image = []
labels = []

imgnames = os.listdir(dir + '/img')

for imgname in imgnames:
    img = cv2.imread(dir + '/img/' + imgname)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    image.append(img)

    onlyfilename = imgname.split(".")[0]
    e = pars.parse(dir + '/labels/' + onlyfilename + '.xml')
    root = e.getroot()
    object= root.find("object")
    object=object.find("bndbox")
    xmin = int(object.find("xmin").text)
    ymin = int(object.find("ymin").text)
    xmax = int(object.find("xmax").text)
    ymax = int(object.find("ymax").text)
    labels.append([dlib.rectangle(left=xmin, top=ymin, right=xmax, bottom=ymax)])
  
options = dlib.simple_object_detector_training_options()
options.be_verbose = True
detector = dlib.train_simple_object_detector(image, labels, options)

detector.save("tld.svm")
print("Training finished. Detector saved to tld.svm")