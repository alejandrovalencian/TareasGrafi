import cv2
import numpy as np

img = cv2.imread("m1_oscura.png", cv2.IMREAD_GRAYSCALE)

# TODO MODO RAW:
img_int = img.astype(np.int32)
h, w = img.shape

recuperada = np.zeros((h, w), dtype=np.int32)

for y in range(h):
    for x in range(w):
        recuperada[y, x] = img_int[y, x] * 50

recuperada = np.clip(recuperada, 0, 255).astype(np.uint8)
cv2.imwrite("m1_recuperado_x50.png", recuperada)


# TODO SEGUNDA FASE (RAW):
recuperada2 = recuperada.astype(np.int32)

for y in range(h):
    for x in range(w):
        recuperada2[y, x] += 20

recuperada2 = np.clip(recuperada2, 0, 255).astype(np.uint8)
cv2.imwrite("m1_recuperado_x50_mas20.png", recuperada2)


# TODO MODO VECTORIZADO (opcional):
vec = np.clip(img.astype(np.int32) * 50 + 20, 0, 255).astype(np.uint8)
cv2.imwrite("m1_recuperado_vec.png", vec)