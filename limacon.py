import numpy as np
import cv2

# Definir los parámetros iniciales
width, height = 1000, 1000
img = np.zeros((height, width, 3), dtype=np.uint8)  # Fondo negro

# Parámetros de la curva de Limacon
a, b = 150, 100
k1 = 0.7
k2 = 1.2
k3 = 2
k4 = 4

theta_increment = 0.05
max_theta = 2 * np.pi

# Centros (4 cuadrantes)
center1 = (width // 4, height // 4)
center2 = (3 * width // 4, height // 4)
center3 = (width // 4, 3 * height // 4)
center4 = (3 * width // 4, 3 * height // 4)

theta = 0

while True:

    for t in np.arange(0, theta, theta_increment):

        # ---- Curva 1 ----
        r = a + b * np.cos(k1 * t)
        x = int(center1[0] + r * np.cos(t))
        y = int(center1[1] + r * np.sin(t))
        cv2.circle(img, (x-2, y-2), 5, (255, 255, 255), -1)

        # ---- Curva 2 ----
        r = a + b * np.cos(k2 * t)
        x = int(center2[0] + r * np.cos(t))
        y = int(center2[1] + r * np.sin(t))
        cv2.circle(img, (x-2, y-2), 5, (255, 0, 0), -1)

        # ---- Curva 3 ----
        r = a + b * np.cos(k3 * t)
        x = int(center3[0] + r * np.cos(t))
        y = int(center3[1] + r * np.sin(t))
        cv2.circle(img, (x-2, y-2), 5, (0, 255, 0), -1)

        # ---- Curva 4 ----
        r = a + b * np.cos(k4 * t)
        x = int(center4[0] + r * np.cos(t))
        y = int(center4[1] + r * np.sin(t))
        cv2.circle(img, (x-2, y-2), 5, (0, 0, 255), -1)

    cv2.imshow("Parametric Animation", img)

    theta += theta_increment

    # Cerrar con ESC o con la X
    if cv2.waitKey(30) & 0xFF == 27 or \
       cv2.getWindowProperty("Parametric Animation", cv2.WND_PROP_VISIBLE) < 1:
        break

cv2.destroyAllWindows()