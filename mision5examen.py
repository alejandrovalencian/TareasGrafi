import cv2
import numpy as np
import math

lienzo = np.zeros((500,500,3), dtype=np.uint8)

t = 0

while t <= 6.28:

    x = 250 + 150 * math.sin(3*t)
    y = 250 + 150 * math.sin(2*t)

    x = int(x)
    y = int(y)

    cv2.circle(lienzo,(x,y),1,(255,255,255),-1)

    t += 0.01

# guardar imagen
cv2.imwrite("m5_curva.png", lienzo)

cv2.imshow("curva", lienzo)
cv2.waitKey(0)
cv2.destroyAllWindows()