import cv2
import numpy as np

img = cv2.imread('m1_oscura.png', cv2.IMREAD_GRAYSCALE)

if img is not None:
    alto, ancho = img.shape
    
    img_raw = np.zeros((alto, ancho), dtype=np.uint8)

    for y in range(alto):
        for x in range(ancho):

            pixel_ofuscado = int(img[y, x])

            pixel_recuperado = pixel_ofuscado * 50

            img_raw[y, x] = np.clip(pixel_recuperado, 0, 255)

    img_vectorizada = np.clip(img * 50, 0, 255).astype(np.uint8)

    cv2.imwrite('m1_revelada_raw.png', img_raw)
    cv2.imwrite('m1_revelada_numpy.png', img_vectorizada)
    
    print("Desencriptación exitosa!")
    
else:
    print("Error")