import cv2
import numpy as np

# Webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Tamaño del bloque de pixeles
PIXELS = 8          # cuantos pixeles reales se analizan
SCALE = 60          # cuanto se agranda cada pixel

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Mostrar webcam normal
    cv2.imshow("Webcam", frame)

    # Tomar zona central
    h, w, _ = frame.shape
    cx, cy = w // 2, h // 2
    roi = frame[
        cy - PIXELS//2 : cy + PIXELS//2,
        cx - PIXELS//2 : cx + PIXELS//2
    ]

    # Crear imagen ampliada
    zoom = np.zeros((PIXELS*SCALE, PIXELS*SCALE, 3), dtype=np.uint8)

    for y in range(PIXELS):
        for x in range(PIXELS):
            color = roi[y, x]
            y1, y2 = y*SCALE, (y+1)*SCALE
            x1, x2 = x*SCALE, (x+1)*SCALE

            zoom[y1:y2, x1:x2] = color

            # Texto RGB
            r, g, b = int(color[2]), int(color[1]), int(color[0])
            text = f"{r},{g},{b}"

            cv2.putText(
                zoom, text,
                (x1+5, y1+35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255,255,255),
                1
            )

    # Dibujar cuadrícula
    for i in range(PIXELS):
        cv2.line(zoom, (0, i*SCALE), (PIXELS*SCALE, i*SCALE), (0,0,0), 1)
        cv2.line(zoom, (i*SCALE, 0), (i*SCALE, PIXELS*SCALE), (0,0,0), 1)

    cv2.imshow("Zoom de Pixeles RGB", zoom)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
