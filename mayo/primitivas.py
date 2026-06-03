import cv2 as cv
import numpy as np 

img = np.ones((500,500,3), np.uint8)*150 

# --------- Transformación (ESCALA) ----------
S = np.array([[1.2, 0],
              [0, 1.2]])

def transformar(p):
    p = np.array([[p[0]],
                  [p[1]]])
    pt = S @ p
    return int(pt[0][0]), int(pt[1][0])

# --------- Centro ----------
centro = (200, 200)
centro_t = transformar(centro)

# --------- Pétalos ----------
petalos = [
    (200,150),
    (200,250),
    (150,200),
    (250,200),
    (165,165),
    (235,165),
    (165,235),
    (235,235)
]

for p in petalos:
    pt = transformar(p)
    cv.circle(img, pt, 30, (0,0,255), -1)

# --------- Centro de la flor ----------
cv.circle(img, centro_t, 35, (0,255,255), -1)

# --------- Tallo ----------
p1 = transformar((200,235))
p2 = transformar((200,350))
cv.line(img, p1, p2, (0,200,0), 8)

# --------- Hoja izquierda ----------
cv.circle(img, transformar((170,320)), 25, (0,180,0), -1)

# --------- Hoja derecha ----------
cv.circle(img, transformar((230,320)), 25, (0,180,0), -1)

cv.imshow('img', img)
cv.waitKey(0)
cv.destroyAllWindows()