import cv2 as cv
import numpy as np

# Cargar la imagen en escala de grises
img = cv.imread('frutas.png', 0)

# Obtener el tamaño de la imagen
x, y = img.shape

# Crear una imagen vacía para el cizallamiento
sheared_img = np.zeros((x, y), dtype=np.uint8)

# Definir el factor de cizallamiento
shear_factor_x = 0.5

# Aplicar el cizallamiento en el eje x
for i in range(x):
    for j in range(y):
        new_x = i
        new_y = int(j + shear_factor_x * i)
        if 0 <= new_x < x and 0 <= new_y < y:
            sheared_img[new_x, new_y] = img[i, j]

# Mostrar la imagen original y la cizallada
cv.imshow('Imagen Original', img)
cv.imshow('Imagen Cizallada (modo raw)', sheared_img)
cv.waitKey(0)
cv.destroyAllWindows()