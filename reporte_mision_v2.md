# Reporte de Misión: Graficación Táctica II
**Agente Especial:** [Jorge Alejandro Valencia Nuñez / 24120404]

---
## Evidencias
### Misión 1
- Imagen recuperada x50: ![Resultado Mision 1](imagenes/m1_recuperado_x50.png)
- Imagen recuperada x50 + 20: ![Resultado Mision 1](imagenes/m1_recuperado_x50_mas20.png)
- Código:
```python
import cv2
import numpy as np

img = cv2.imread("m1_oscura.png", cv2.IMREAD_GRAYSCALE)

# TODO MODO RAW:
img_int = img.astype(np.int32)
h, w = img.shape

recuperada = np.zeros((h, w), dtype=np.int32)

for y in range(h):
    for x in range(w):
        recuperada[y, x] = img_int[y, x] * 50

recuperada = np.clip(recuperada, 0, 255).astype(np.uint8)
cv2.imwrite("m1_recuperado_x50.png", recuperada)


# TODO SEGUNDA FASE (RAW):
recuperada2 = recuperada.astype(np.int32)

for y in range(h):
    for x in range(w):
        recuperada2[y, x] += 20

recuperada2 = np.clip(recuperada2, 0, 255).astype(np.uint8)
cv2.imwrite("m1_recuperado_x50_mas20.png", recuperada2)


# TODO MODO VECTORIZADO (opcional):
vec = np.clip(img.astype(np.int32) * 50 + 20, 0, 255).astype(np.uint8)
cv2.imwrite("m1_recuperado_vec.png", vec)
```  

### Misión 2
- QR reconstruido: ![Resultado Mision 2](imagenes/m2_qr_reconstruido.png)
- Código:
```python
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
```  

### Misión 3
- Sello forjado: ![Resultado Mision 3](imagenes/m3_sello_forjado_v2.png)
- Código:
```python
import cv2
import numpy as np
import math

# Lienzo base
img = np.zeros((600, 600, 3), dtype=np.uint8)
img[:] = (40, 20, 20)  # BGR


cx, cy = 300, 300


cv2.circle(img, (cx, cy), 170, (0, 255, 255), 3)

cv2.circle(img, (cx, cy), 110, (0, 255, 255), 2)

cv2.rectangle(img, (250, 260), (350, 340), (0, 0, 255), -1)


cv2.line(img, (0, 0), (600, 600), (255, 255, 255), 2)
cv2.line(img, (600, 0), (0, 600), (255, 255, 255), 2)

radio = 140
for i in range(8):
    angulo = 2 * math.pi * i / 8
    x = int(cx + radio * math.cos(angulo))
    y = int(cy + radio * math.sin(angulo))
    cv2.circle(img, (x, y), 8, (0, 255, 0), -1)

cv2.putText(img, "SECTOR-9", (200, 560),
            cv2.FONT_HERSHEY_SIMPLEX, 1,
            (255, 255, 255), 2, cv2.LINE_AA)

cv2.imwrite("m3_sello_forjado_v2.png", img)
```  

### Misión 4
- Máscara Cyan: ![Resultado Mision 4](imagenes/m4_suavizada.png)
- Código:
```python
import cv2
import numpy as np


img = cv2.imread("m4_ruido.png")


kernel = np.ones((3,3), np.float32) / 9
img_suavizada = cv2.filter2D(img, -1, kernel)


cv2.imwrite("m4_suavizada.png", img_suavizada)


hsv = cv2.cvtColor(img_suavizada, cv2.COLOR_BGR2HSV)


lower_cyan = np.array([80, 100, 100])
upper_cyan = np.array([100, 255, 255])


mask = cv2.inRange(hsv, lower_cyan, upper_cyan)


cv2.imwrite("m4_mask_cyan.png", mask)
```  

### Misión 5
- Evidencia tricolor: ![Resultado Mision 5](imagenes/m5_tricolor.png)
- Mensaje recuperado: ![Resultado Mision 5](imagenes/m5_mensaje.png)
- Código:
```python
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
```  

---
## Análisis del Analista (Reflexiones Finales)

1. **Operadores puntuales (M1):** ¿Qué diferencia visual hay entre recuperar con multiplicación (x50) y recuperar con suma (+50)? ¿Cuál preserva mejor el contraste del texto?
> *[La multiplicación (x50) hace que los valores de la imagen se escalen, entonces las partes claras se vuelven mucho más claras y las oscuras siguen siendo oscuras, por eso el contraste se mantiene mejor. En cambio la suma (+50) solo aumenta el brillo general, pero puede “lavar” la imagen y hacer que el texto se vea menos definido. En mi opinion, la multiplicación preserva mejor el contraste, aun que aveces puede saturar demasiado.]*

2. **Transformaciones geométricas (M2):** ¿Por qué es importante escoger el centro correcto al rotar una imagen con `getRotationMatrix2D`?
> *[Es importante porque la rotación se hace alrededor de ese punto. Si el centro no es el correcto, la imagen puede desplazarse o incluso salirse del encuadre. Por ejemplo, si no usas el centro real de la imagen, el objeto principal puede quedar cortado o en una posicion rara. Entonces elegir bien el centro asegura que la rotacion sea mas precisa.]*

3. **Convolución (M4):** ¿Por qué un filtro promedio puede ayudar a reducir falsos positivos antes de segmentar por HSV, y qué desventaja tiene sobre los bordes del texto?
> *[El filtro promedio suaviza la imagen, eliminando ruido y pequeñas variaciones de color, lo que ayuda a que la segmentacion en HSV sea mas estable y no detecte cosas que no son. Pero la desventaja es que tambien difumina los bordes, entonces el texto puede perder nitidez y volverse menos claro, afectando la detección correcta.]*

4. **Canales (M5):** ¿Por qué separar canales puede revelar información que en la imagen a color “no se ve” a simple vista?
> *[Porque cada canal (rojo, verde, azul) guarda distinta informacion de intensidad. A veces un objeto o texto resalta mas en un canal especifico que en la imagen completa. Al separarlos, puedes notar diferencias que antes no eran tan obvias, como contrastes o detalles ocultos. Esto ayuda mucho en analisis de imagenes aunque no siempre es tan evidente al inicio.]*