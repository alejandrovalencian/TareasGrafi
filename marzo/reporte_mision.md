# Reporte de Misión: Graficación Táctica
**Agente Especial:** [Jorge Alejandro Valencia Nuñez / 24120404]

---

## Evidencias de Misión

---

### Misión 1

```python
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
```  
![Resultado Mision 1](imagenes/m1_revelada_numpy.png)
  
### Mision 2
```python
import cv2
import numpy as np

mitad1 = cv2.imread('m2_mitad1.png')
mitad2 = cv2.imread('m2_mitad2.png')

lienzo = np.zeros((400,400,3), dtype=np.uint8)

# mitad 1
h1, w1 = mitad1.shape[:2]

M1 = np.float32([
    [1,0,0],
    [0,1,0]
])

mitad1_movida = cv2.warpAffine(mitad1, M1, (400,400))
lienzo[0:h1,0:w1] = mitad1_movida[0:h1,0:w1]

# mitad 2
h2, w2 = mitad2.shape[:2]

centro = (w2//2, h2//2)

M2 = cv2.getRotationMatrix2D(centro,180,1)

mitad2_rotada = cv2.warpAffine(mitad2,M2,(w2,h2))

lienzo[400-h2:400,0:w2] = mitad2_rotada

cv2.imwrite("m2_resultado.png", lienzo)

cv2.imshow("QR reconstruido", lienzo)
cv2.waitKey(0)
cv2.destroyAllWindows()
```
![Resultado Mision 2](imagenes/m2_resultado.png)

### Mision 3
```python
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
```
![Resultado Mision 3](imagenes/m3_sello_forjado.png)

### Mision 4
```python
import cv2
import numpy as np

img = cv2.imread('m4_ruido.png')

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

bajo = np.array([80,100,100])
alto = np.array([100,255,255])

mascara = cv2.inRange(hsv,bajo,alto)

# guardar imagen
cv2.imwrite("m4_mascara.png", mascara)

cv2.imshow("original", img)
cv2.imshow("mascara cyan", mascara)

cv2.waitKey(0)
cv2.destroyAllWindows()
```
![Resultado Mision 4](imagenes/m4_mascara.png)


### Mision 5
```python
import cv2
import numpy as np
import math

lienzo = np.zeros((500,500,3), dtype=np.uint8)

t = 0

while t <= 6.28:

    x = 250 + 150 * math.sin(3*t)
    y = 250 + 150 * math.sin(2*t)

    x = int(x)
    y = int(y)

    cv2.circle(lienzo,(x,y),1,(255,255,255),-1)

    t += 0.01

# guardar imagen
cv2.imwrite("m5_curva.png", lienzo)

cv2.imshow("curva", lienzo)
cv2.waitKey(0)
cv2.destroyAllWindows()
```
![Resultado Mision 5](imagenes/m5_curva.png)

##  Análisis del Analista (Reflexiones Finales)

1. **Sobre los Operadores Puntuales (Misión 1):** Matemáticamente, ¿qué pasaría si en lugar de multiplicar por 50, hubieras sumado 50 a cada píxel oscuro? ¿Se revelaría el texto igual de claro o la imagen perdería contraste?
> *[Si en lugar de multiplicar se sumara 50 a cada píxel, todos los valores aumentarían de forma similar. Esto no cambiaría mucho la diferencia entre píxeles claros y oscuros, por lo que el contraste seguiría siendo bajo. Al multiplicar los valores se amplifica la diferencia de intensidades y el texto oculto se vuelve más visible.]*

2. **Sobre el Espacio HSV (Misión 4):** ¿Por qué el modelo de color BGR es ineficiente para la Recuperación de Información cuando buscamos "todos los tonos de azul celeste", y por qué el modelo HSV resuelve este problema con una sola variable?
> *[En el modelo BGR el color depende de tres canales diferentes, por lo que encontrar un color específico requiere analizar combinaciones de los tres valores. En cambio, en HSV el matiz (Hue) representa directamente el tipo de color, lo que permite detectar todos los tonos de un color usando solo un rango en esa variable.]*

3. **Sobre Ecuaciones Paramétricas (Misión 5):** ¿Por qué las ecuaciones paramétricas (usando el parámetro t) son mejores para dibujar formas cerradas y complejas en graficación por computadora que usar la clásica función $y=f(x)$?
> *[Las ecuaciones paramétricas permiten calcular las coordenadas x e y al mismo tiempo usando un parámetro t. Esto facilita dibujar curvas complejas o cerradas que no pueden representarse fácilmente con una función y=f(x), ya que algunas curvas pueden tener varios valores de y para un mismo x.]*
