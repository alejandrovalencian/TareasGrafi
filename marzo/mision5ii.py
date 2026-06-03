import cv2
import numpy as np


img = np.random.randint(0, 256, (300, 700, 3), dtype=np.uint8)


texto = "MENSAJE SECRETO"
pos = (50, 150)


color_trampa = (20, 255, 20)

cv2.putText(img, texto, pos, cv2.FONT_HERSHEY_SIMPLEX,
            2, color_trampa, 3, cv2.LINE_AA)


cv2.imwrite("m5_tricolor.png", img)



b, g, r = cv2.split(img)


solo_g = g
diff_gb = cv2.absdiff(g, b)
diff_rg = cv2.absdiff(r, g)


diff_gb_norm = cv2.normalize(diff_gb, None, 0, 255, cv2.NORM_MINMAX)


_, mask = cv2.threshold(diff_gb_norm, 50, 255, cv2.THRESH_BINARY)


cv2.imwrite("m5_mensaje.png", mask)