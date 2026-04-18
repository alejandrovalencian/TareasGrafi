import cv2
import numpy as np

lienzo = np.zeros((500,500,3), dtype=np.uint8)

# color azul oscuro
lienzo[:] = (50,20,20)

# circulo amarillo
cv2.circle(lienzo,(250,250),100,(0,255,255),3)

# rectangulo rojo
cv2.rectangle(lienzo,(200,200),(300,300),(0,0,255),-1)

# diagonales
cv2.line(lienzo,(0,0),(500,500),(255,255,255),2)
cv2.line(lienzo,(500,0),(0,500),(255,255,255),2)

# guardar
cv2.imwrite("m3_sello_forjado.png", lienzo)

cv2.imshow("sello", lienzo)
cv2.waitKey(0)
cv2.destroyAllWindows()