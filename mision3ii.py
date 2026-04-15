import cv2
import numpy as np
import math

# Lienzo base
img = np.zeros((600, 600, 3), dtype=np.uint8)
img[:] = (40, 20, 20)  # BGR


cx, cy = 300, 300


cv2.circle(img, (cx, cy), 170, (0, 255, 255), 3)

cv2.circle(img, (cx, cy), 110, (0, 255, 255), 2)

cv2.rectangle(img, (250, 260), (350, 340), (0, 0, 255), -1)


cv2.line(img, (0, 0), (600, 600), (255, 255, 255), 2)
cv2.line(img, (600, 0), (0, 600), (255, 255, 255), 2)

radio = 140
for i in range(8):
    angulo = 2 * math.pi * i / 8
    x = int(cx + radio * math.cos(angulo))
    y = int(cy + radio * math.sin(angulo))
    cv2.circle(img, (x, y), 8, (0, 255, 0), -1)

cv2.putText(img, "SECTOR-9", (200, 560),
            cv2.FONT_HERSHEY_SIMPLEX, 1,
            (255, 255, 255), 2, cv2.LINE_AA)

cv2.imwrite("m3_sello_forjado_v2.png", img)