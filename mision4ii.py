import cv2
import numpy as np


img = cv2.imread("m4_ruido.png")


kernel = np.ones((3,3), np.float32) / 9
img_suavizada = cv2.filter2D(img, -1, kernel)


cv2.imwrite("m4_suavizada.png", img_suavizada)


hsv = cv2.cvtColor(img_suavizada, cv2.COLOR_BGR2HSV)


lower_cyan = np.array([80, 100, 100])
upper_cyan = np.array([100, 255, 255])


mask = cv2.inRange(hsv, lower_cyan, upper_cyan)


cv2.imwrite("m4_mask_cyan.png", mask)