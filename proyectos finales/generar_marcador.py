"""
Generador de Marcador ArUco
Crea el marcador ArUco ID 0 del diccionario DICT_4X4_50
para usarlo en el proyecto de Realidad Aumentada
"""

import cv2
import numpy as np

# Obtener el diccionario DICT_4X4_50 (el mismo que usa ciudad_ar.py)
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

# Generar la imagen del marcador ID 0 con tamaño 400x400 píxeles
img = cv2.aruco.generateImageMarker(dictionary, 0, 400)

# Crear un canvas blanco de 480x480
canvas = np.full((480, 480), 255, dtype=np.uint8)

# Colocar el marcador en el centro del canvas
canvas[40:440, 40:440] = img

# Guardar la imagen
cv2.imwrite("marcador_aruco_id0.png", canvas)

print("✓ Marcador generado: marcador_aruco_id0.png")
print("  Tamaño: 480x480 píxeles")
print("  ID: 0")
print("  Diccionario: DICT_4X4_50")
print("\nInstrucciones:")
print("  1. Imprime la imagen en papel (se recomienda 10x10 cm mínimo)")
print("  2. O muéstrala en pantalla con una resolución alta")
print("  3. Apunta la cámara hacia el marcador al ejecutar ciudad_ar.py")