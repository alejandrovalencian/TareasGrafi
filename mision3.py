import cv2
import numpy as np

# Cargar la imagen
img = cv2.imread("microfilm.jpg")

# =========================================
# RECORTE CENTRAL
# =========================================

# Recorte sugerido del centro (200x200)
recorte = img[900:1100, 900:1100]

alto, ancho = recorte.shape[:2]

# =========================================
# MÉTODO 1: MODO RAW (Vecino más cercano)
# =========================================

factor = 5

nuevo_ancho = ancho * factor
nuevo_alto = alto * factor

# Crear nueva imagen grande
escala_raw = np.zeros((nuevo_alto, nuevo_ancho, 3), dtype=np.uint8)

for y in range(nuevo_alto):
    for x in range(nuevo_ancho):

        # Mapear al píxel original
        origen_x = int(x / factor)
        origen_y = int(y / factor)

        escala_raw[y, x] = recorte[origen_y, origen_x]

cv2.imshow("Modo RAW", escala_raw)

# =========================================
# MÉTODO 2: MODO OPENCV
# =========================================

escala_opencv = cv2.resize(
    recorte,
    None,
    fx=5,
    fy=5,
    interpolation=cv2.INTER_CUBIC
)

cv2.imshow("Modo OpenCV", escala_opencv)

cv2.waitKey(0)
cv2.destroyAllWindows()
