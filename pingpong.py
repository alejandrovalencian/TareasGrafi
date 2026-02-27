import cv2 as cv
import numpy as np

img = np.ones((500,500,3), np.uint8)*255

x = 250
dx = 5

for i in range(400):

    img = np.ones((500,500,3), np.uint8)*255

    # mover pelota
    x = x + dx

    # rebote izquierda y derecha
    if x <= 20 or x >= 480:
        dx = -dx

    # paletas fijas
    cv.rectangle(img, (10,200), (20,300), (234,56,100), -1)
    cv.rectangle(img, (480,200), (490,300), (234,56,100), -1)

    # pelota
    cv.circle(img, (x,250), 20, (0,0,255), -1)

    cv.imshow('img', img)
    cv.waitKey(70)

cv.imshow('img', img)
cv.waitKey(0)
cv.destroyAllWindows()