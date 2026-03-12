import cv2
import numpy as np

img = cv2.imread('m1_oscura.png', cv2.IMREAD_GRAYSCALE)

# modo RAW
# recore con un for y multiplica por 50
img_raw = np.zeros_like(img)
alto, ancho = img.shape

for y in range(alto):
    for x in range(ancho):
        # aqui se multiplica por 50 y se usa np.clip para no pasar de 255
        img_raw[y, x] = np.clip(img[y, x] * 50, 0, 255)

# modo OPENCV
# usa la magia de la vectorizacion
img_opencv = cv2.multiply(img, 50)

# guardar las imagenes para qu puedas ver el texto revelado
cv2.imwrite('revelado_raw.png', img_raw)
cv2.imwrite('revelado_opencv.png', img_opencv)