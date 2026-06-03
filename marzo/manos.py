import cv2
import mediapipe as mp
import math

# Configuración de la nueva Tasks API
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode



# 1. Crear las opciones del detector (Reemplaza a mp_hands.Hands)
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='hand_landmarker.task'),
    running_mode=VisionRunningMode.IMAGE, # IMAGE mode funciona igual que el process() anterior
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

# Conexiones de la mano para dibujar (Reemplaza a mp_hands.HAND_CONNECTIONS)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),       # Pulgar
    (0, 5), (5, 6), (6, 7), (7, 8),       # Índice
    (5, 9), (9, 10), (10, 11), (11, 12),  # Medio
    (9, 13), (13, 14), (14, 15), (15, 16),# Anular
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20) # Meñique
]

# Captura de video
cap = cv2.VideoCapture(0)
distancia=0
# 2. Inicializar el detector usando un bloque 'with'
with HandLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convertir imagen a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 3. La nueva API requiere que envolvamos la imagen en un objeto mp.Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        # Detectar manos
        results = landmarker.detect(mp_image)
        
        # Dibujar los puntos clave y conexiones
        # En la nueva API, los resultados están en 'hand_landmarks'
        if results.hand_landmarks:
            for hand_landmarks in results.hand_landmarks:
                h, w, c = frame.shape
                
                # Extraer coordenadas a píxeles
                keypoints = []
                for landmark in hand_landmarks:
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    keypoints.append((cx, cy))
                    # Dibujar el punto
                    cv2.circle(frame, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
                    
                # Dibujar las conexiones (líneas)
                for connection in HAND_CONNECTIONS:
                    start_idx = connection[0]
                    end_idx = connection[1]
                    cv2.line(frame, keypoints[start_idx], keypoints[end_idx], (0, 255, 0), 2)

                    
                if len(keypoints) >= 9: 
                    x1, y1 = keypoints[4]
                    x2, y2 = keypoints[8]
                    
                    # 1. Dibujar la línea y los puntos
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    cv2.circle(frame, (x1, y1), 8, (0, 0, 255), cv2.FILLED)
                    cv2.circle(frame, (x2, y2), 8, (0, 0, 255), cv2.FILLED)
                    
                    # 2. Calcular la longitud de la línea (distancia)
                    distancia = math.hypot(x2 - x1, y2 - y1)
                    
                    # 3. Encontrar el punto medio para colocar el texto
                    cx_medio, cy_medio = (x1 + x2) // 2, (y1 + y2) // 2
                    
                    # 4. Mostrar el valor en la pantalla (convertido a entero)
                    cv2.putText(frame, f"{int(distancia)} px", (cx_medio, cy_medio), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

        cv2.circle(frame, (200,200), int(distancia), (21,34,234), -1)            
        # Mostrar la imagen
        cv2.imshow("Salida", frame)

        # Salir con 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()