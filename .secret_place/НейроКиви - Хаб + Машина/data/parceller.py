import cv2
cap = cv2.VideoCapture('./output17.avi')
i = 0
while True:
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    if i % 15 == 0:
    	cv2.imwrite(f'./images/vid9-{i}.png', frame)
    i += 1

cap.release()
cv2.destroyAllWindows()
