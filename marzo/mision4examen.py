import cv2
import numpy as np

img = cv2.imread('m4_ruido.png')

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

bajo = np.array([80,100,100])
alto = np.array([100,255,255])

mascara = cv2.inRange(hsv,bajo,alto)

# guardar imagen
cv2.imwrite("m4_mascara.png", mascara)

cv2.imshow("original", img)
cv2.imshow("mascara cyan", mascara)

cv2.waitKey(0)
cv2.destroyAllWindows()