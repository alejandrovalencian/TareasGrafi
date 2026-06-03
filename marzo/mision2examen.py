import cv2
import numpy as np

mitad1 = cv2.imread('m2_mitad1.png')
mitad2 = cv2.imread('m2_mitad2.png')

# lienzo
lienzo = np.zeros((400,400,3), dtype=np.uint8)

# ----- mitad 1 -----
h1, w1 = mitad1.shape[:2]

M1 = np.float32([
    [1,0,0],
    [0,1,0]
])

mitad1_movida = cv2.warpAffine(mitad1, M1, (400,400))

lienzo[0:h1,0:w1] = mitad1_movida[0:h1,0:w1]

# ----- mitad 2 -----
h2, w2 = mitad2.shape[:2]

centro = (w2//2, h2//2)

M2 = cv2.getRotationMatrix2D(centro,180,1)

mitad2_rotada = cv2.warpAffine(mitad2,M2,(w2,h2))

lienzo[400-h2:400,0:w2] = mitad2_rotada

# guardar imagen
cv2.imwrite("m2_resultado.png", lienzo)

cv2.imshow("QR reconstruido", lienzo)
cv2.waitKey(0)
cv2.destroyAllWindows()