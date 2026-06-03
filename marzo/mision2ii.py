import cv2
import numpy as np

mitad1 = cv2.imread("m2_mitad1.png")
mitad2 = cv2.imread("m2_mitad2.png")

lienzo = np.full((400, 400, 3), 255, dtype=np.uint8)

h1, w1 = mitad1.shape[:2]


dx, dy = -50, -50  

M1 = np.float32([[1, 0, dx],
                 [0, 1, dy]])

mitad1_corr = cv2.warpAffine(mitad1, M1, (w1, h1))


lienzo[0:h1, 0:w1] = mitad1_corr

h2, w2 = mitad2.shape[:2]
centro = (w2 // 2, h2 // 2)

M2 = cv2.getRotationMatrix2D(centro, 180, 1)
mitad2_corr = cv2.warpAffine(mitad2, M2, (w2, h2))

lienzo[h1:h1+h2, 0:w2] = mitad2_corr


cv2.imwrite("m2_qr_reconstruido.png", lienzo)