import cv2 
import numpy as np

# Leer la imagen
img = cv2.imread('frutas.png')

# Convertir la imagen al espacio de color HSV
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Rango 1 de rojo
lower_red1 = np.array([50, 100, 100])
upper_red1 = np.array([85, 255, 255])

# Rango 2 de rojo
lower_red2 = np.array([50, 100, 100])
upper_red2 = np.array([85, 255, 255])

# Crear máscaras
mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

# Unir las dos máscaras
mask = mask1 + mask2

# Aplicar la máscara
result = cv2.bitwise_and(img, img, mask=mask)

# Mostrar resultados
cv2.imshow("Imagen Original", img)
cv2.imshow("Color Rojo Detectado", result)
cv2.waitKey(0)
cv2.destroyAllWindows()
