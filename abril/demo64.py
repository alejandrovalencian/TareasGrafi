import cv2
import numpy as np
import math


def main():
    # Tamaño de la "Demo 64" -> 640x480
    ancho = 640
    alto = 480

    # Centro de la imagen
    cx, cy = ancho // 2, alto // 2

    # Parámetros de la curva de Lissajous
    A = 200  # amplitud en x
    B = 150  # amplitud en y
    a = 3    # frecuencia en x
    b = 2    # frecuencia en y
    delta = math.pi / 2  # desfase

    # Lista para guardar la trayectoria (estela)
    trayectoria = []
    longitud_max_trayectoria = 1500

    frame = 0

    cv2.namedWindow("Demo 64 - Animacion Parametrica", cv2.WINDOW_AUTOSIZE)

    while True:
        # Imagen negra (3 canales BGR)
        img = np.zeros((alto, ancho, 3), dtype=np.uint8)

        # Parámetro t que avanza con el tiempo
        t = frame * 0.03  # cambia esta constante para hacer la animacion mas rapida o lenta

        # Ecuaciones paramétricas de Lissajous
        x = cx + A * math.sin(a * t + delta)
        y = cy + B * math.sin(b * t)

        px, py = int(x), int(y)

        # Guardar punto actual en la trayectoria
        trayectoria.append((px, py))
        if len(trayectoria) > longitud_max_trayectoria:
            trayectoria.pop(0)

        # Dibujar la trayectoria como líneas conectadas
        for i in range(1, len(trayectoria)):
            cv2.line(
                img,
                trayectoria[i - 1],
                trayectoria[i],
                (0, 255, 255),  # amarillo
                1,
                cv2.LINE_AA,
            )

        # Dibujar el punto actual
        cv2.circle(img, (px, py), 6, (0, 0, 255), -1)

        

        # Mostrar frame
        cv2.imshow("Demo 64 - Animacion Parametrica", img)

        # Esperar ~16 ms (aprox 60 fps) y leer tecla
        key = cv2.waitKey(16) & 0xFF
        if key == 27 or key == ord("q"):  # ESC o 'q'
            break

        frame += 1

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()