import cv2
import numpy as np
import math

# Cargar imagen
img = cv2.imread('qr_rotado.jpg')

alto, ancho = img.shape[:2]

# Centro de rotación
cx = 250
cy = 250

# Ángulo de rotación (corregir -45 grados)
theta = math.radians(-45)

# =========================================
# MÉTODO 1: MODO RAW (TRIGONOMETRÍA)
# =========================================

# Crear imagen vacía
destino = np.zeros_like(img)

for y in range(alto):
    for x in range(ancho):

        # Coordenadas relativas al centro
        xr = x - cx
        yr = y - cy

        # Aplicar rotación inversa
        x_origen = int(xr * math.cos(theta) - yr * math.sin(theta) + cx)
        y_origen = int(xr * math.sin(theta) + yr * math.cos(theta) + cy)

        if 0 <= x_origen < ancho and 0 <= y_origen < alto:
            destino[y, x] = img[y_origen, x_origen]

cv2.imshow("Modo RAW", destino)


# =========================================
# MÉTODO 2: MODO OPENCV
# =========================================

# Matriz de rotación
M = cv2.getRotationMatrix2D((cx, cy), -45, 1)

# Aplicar rotación
rotada = cv2.warpAffine(img, M, (ancho, alto))

cv2.imshow("Modo OpenCV", rotada)

cv2.waitKey(0)
cv2.destroyAllWindows()
5