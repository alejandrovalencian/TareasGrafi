import cv2
import numpy as np

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

img = cv2.aruco.generateImageMarker(dictionary, 0, 400)

canvas = np.full((480, 480), 255, dtype=np.uint8)

canvas[40:440, 40:440] = img

cv2.imwrite("marcador_aruco_id0.png", canvas)

print("Marcador generado")