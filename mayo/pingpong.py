import cv2 as cv
import numpy as np

img = np.ones((500,500,3), np.uint8)*255

x = 250
y = 250
dx = 5
dy = 5

for i in range(400):

    img = np.ones((500,500,3), np.uint8)*255

    # mover pelota
    x = x + dx
    y = y + dy

    # rebote izquierda y derecha
    if x <= 20 or x >= 480:
        dx = -dx

    # rebote arriba y abajo
    if y <= 20 or y >= 480:
        dy = -dy

    # dibujar pelota
    cv.circle(img, (x,y), 20, (0,0,255), -1)

    cv.imshow('img', img)
    cv.waitKey(70)

cv.imshow('img', img)
cv.waitKey(0)
cv.destroyAllWindows()