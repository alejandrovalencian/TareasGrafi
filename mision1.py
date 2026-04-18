import cv2
import numpy as np

# Crear lienzo negro de 800x600
width = 800
height = 600
img = np.zeros((height, width, 3), dtype=np.uint8)

# Dibujar el cuadro rojo (OBJETIVO) en la esquina superior izquierda
cv2.rectangle(img, (0,0), (120,50), (0,0,255), -1)
cv2.putText(img, "OBJETIVO", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

# ==============================
# TRASLACION
# ==============================

tx = 300  # mover 300 a la derecha
ty = 200  # mover 200 hacia abajo

# Matriz de traslación
M = np.float32([
    [1, 0, tx],
    [0, 1, ty]
])

# Aplicar transformación
img_trasladada = cv2.warpAffine(img, M, (width, height))

# Mostrar
cv2.imshow("Original", img)
cv2.imshow("Trasladada", img_trasladada)

cv2.waitKey(0)
cv2.destroyAllWindows()
