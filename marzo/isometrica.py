import cv2
import numpy as np

# Crear lienzo blanco
img = np.ones((500, 500, 3), dtype=np.uint8) * 255

# Tamaño y posición
size = 120
x, y = 200, 320
dx, dy = size//2, -size//2

# Cara frontal
A = (x, y)
B = (x+size, y)
C = (x+size, y-size)
D = (x, y-size)

# Cara trasera
A2 = (A[0]+dx, A[1]+dy)
B2 = (B[0]+dx, B[1]+dy)
C2 = (C[0]+dx, C[1]+dy)
D2 = (D[0]+dx, D[1]+dy)

# 🎨 COLORES SÓLIDOS (BGR)
verde = (60, 160, 60)     # arriba
marron_frente = (60, 100, 150)
marron_lado = (40, 80, 120)

# ---------- CARAS ----------
# Cara superior (verde)
cv2.fillPoly(img, [np.array([D, C, C2, D2])], verde)

# Cara frontal (marrón)
cv2.fillPoly(img, [np.array([A, B, C, D])], marron_frente)

# Cara lateral (marrón más oscuro)
cv2.fillPoly(img, [np.array([B, C, C2, B2])], marron_lado)

# ---------- CONTORNOS ----------
edges = [
    (A,B),(B,C),(C,D),(D,A),
    (A2,B2),(B2,C2),(C2,D2),(D2,A2),
    (A,A2),(B,B2),(C,C2),(D,D2)
]

for p1, p2 in edges:
    cv2.line(img, p1, p2, (0,0,0), 2)

# Mostrar
cv2.imshow("Cubo Minecraft Simple", img)
cv2.waitKey(0)
cv2.destroyAllWindows()