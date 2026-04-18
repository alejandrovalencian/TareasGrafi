import cv2
import numpy as np

# =========================
# 1. GENERACIÓN
# =========================

# Imagen con ruido (300x700)
img = np.random.randint(0, 256, (300, 700, 3), dtype=np.uint8)

# Texto oculto (alto en G, bajo en B y R)
texto = "MENSAJE SECRETO"
pos = (50, 150)

# Color: (B, G, R) → fuerte en G
color_trampa = (20, 255, 20)

cv2.putText(img, texto, pos, cv2.FONT_HERSHEY_SIMPLEX,
            2, color_trampa, 3, cv2.LINE_AA)

# Guardar evidencia
cv2.imwrite("m5_tricolor.png", img)


# =========================
# 2. RECUPERACIÓN
# =========================

# Separar canales
b, g, r = cv2.split(img)

# Pruebas
solo_g = g
diff_gb = cv2.absdiff(g, b)
diff_rg = cv2.absdiff(r, g)

# Normalizar (opcional pero ayuda mucho)
diff_gb_norm = cv2.normalize(diff_gb, None, 0, 255, cv2.NORM_MINMAX)

# Umbral para hacer visible el texto
_, mask = cv2.threshold(diff_gb_norm, 50, 255, cv2.THRESH_BINARY)

# Guardar mejor resultado
cv2.imwrite("m5_mensaje.png", mask)