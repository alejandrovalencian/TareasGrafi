"""
=============================================================
  CIUDAD 3D CON REALIDAD AUMENTADA — ArUco + OpenCV + OpenGL
  Materia: Graficación
 
=============================================================
"""

import sys
import math
import time

import cv2
import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *


# ─── Configuración ArUco ─────────────────────────────────────
CAMERA_INDEX    = 0
MARKER_LENGTH_M = 0.10          # tamaño físico del marcador (metros)
ARUCO_DICT      = cv2.aruco.DICT_4X4_50
MARKER_ID       = 0
MODEL_SCALE     = 0.04          # factor de escala de la ciudad

WINDOW_TITLE    = "Ciudad AR — ArUco + OpenGL"
ZNEAR, ZFAR     = 0.01, 100.0

# ─── Tamaño de ventana deseado ───────────────────────────────
WIN_W, WIN_H    = 1280, 720     # ← cambia aquí el tamaño que quieras

# ─── Estado global ───────────────────────────────────────────
rotation   = 0.0     # rotación manual con teclado
quadric    = None
texture_id = None
t0         = time.perf_counter()


# ══════════════════════════════════════════════════════════════
#  CÁMARA SINTÉTICA (cuando no hay calibración real)
# ══════════════════════════════════════════════════════════════

def default_camera_matrix(width, height):
    f  = float(max(width, height))
    cx = width  / 2.0
    cy = height / 2.0
    return np.array([[f, 0, cx],
                     [0, f, cy],
                     [0, 0,  1]], dtype=np.float64)


# ══════════════════════════════════════════════════════════════
#  DETECTOR ArUco
# ══════════════════════════════════════════════════════════════

def make_detector():
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    params     = cv2.aruco.DetectorParameters()
    if hasattr(cv2.aruco, "ArucoDetector"):
        return cv2.aruco.ArucoDetector(dictionary, params), dictionary
    return None, dictionary


def detect_marker(gray, detector, dictionary):
    if detector is not None:
        corners, ids, _ = detector.detectMarkers(gray)
    else:
        corners, ids, _ = cv2.aruco.detectMarkers(gray, dictionary)

    if ids is None:
        return None
    for i, mid in enumerate(ids.flatten()):
        if mid == MARKER_ID:
            return corners[i]
    return None


# ══════════════════════════════════════════════════════════════
#  ESTIMACIÓN DE POSE (solvePnP)
# ══════════════════════════════════════════════════════════════

def marker_object_points(size):
    s = size / 1.0
    return np.array([[-s,  s, 0],
                     [ s,  s, 0],
                     [ s, -s, 0],
                     [-s, -s, 0]], dtype=np.float32)


def estimate_pose(corners, camera_matrix):
    image_points  = corners.reshape(-1, 2).astype(np.float32)
    object_points = marker_object_points(MARKER_LENGTH_M)
    ok, rvec, tvec = cv2.solvePnP(
        object_points, image_points,
        camera_matrix, np.zeros((5, 1), dtype=np.float64)
    )
    return (rvec, tvec) if ok else (None, None)


# ══════════════════════════════════════════════════════════════
#  MATRICES OpenGL
# ══════════════════════════════════════════════════════════════

def projection_matrix_from_camera(K, width, height):
    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]
    P = np.zeros((4, 4), dtype=np.float32)
    P[0, 0] =  2 * fx / width
    P[1, 1] =  2 * fy / height
    P[0, 2] =  (width  - 2 * cx) / width
    P[1, 2] =  (2 * cy - height)  / height
    P[2, 2] = -(ZFAR + ZNEAR) / (ZFAR - ZNEAR)
    P[2, 3] = -1.0
    P[3, 2] = -(2 * ZFAR * ZNEAR) / (ZFAR - ZNEAR)
    return P


def modelview_matrix(rvec, tvec):
    R, _ = cv2.Rodrigues(rvec)
    M    = np.eye(4, dtype=np.float32)
    M[:3, :3] = R
    M[:3,  3] = tvec.flatten()
    # Conversión OpenCV → OpenGL:
    # En OpenCV  Y apunta abajo  y Z apunta hacia la cámara.
    # En OpenGL  Y apunta arriba y Z apunta hacia el espectador.
    # Invertir Y y Z coloca la ciudad ENCIMA del marcador con Y hacia arriba.
    cv_to_gl = np.array([[ 1,  0,  0, 0],
                         [ 0, -1,  0, 0],
                         [ 0,  0, -1, 0],
                         [ 0,  0,  0, 1]], dtype=np.float32)
    return (cv_to_gl @ M).T


# ══════════════════════════════════════════════════════════════
#  FONDO (frame de cámara como textura)
# ══════════════════════════════════════════════════════════════

def upload_camera_texture(frame):
    global texture_id
    rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb  = cv2.flip(rgb, 0)
    h, w = rgb.shape[:2]
    if texture_id is None:
        texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0,
                 GL_RGB, GL_UNSIGNED_BYTE, rgb)


def draw_background(width, height):
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix(); glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix(); glLoadIdentity()
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glColor3f(1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(0,     0)
    glTexCoord2f(1, 0); glVertex2f(width, 0)
    glTexCoord2f(1, 1); glVertex2f(width, height)
    glTexCoord2f(0, 1); glVertex2f(0,     height)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)


# ══════════════════════════════════════════════════════════════
#  PRIMITIVAS DE DIBUJO (de tu proyecto original)
# ══════════════════════════════════════════════════════════════

def draw_box(w, h, d, r, g, b):
    hx, hy, hz = w/2, h/2, d/2
    faces = [
        ((0,0, 1), [(-hx,-hy, hz),( hx,-hy, hz),( hx, hy, hz),(-hx, hy, hz)]),
        ((0,0,-1), [(-hx,-hy,-hz),(-hx, hy,-hz),( hx, hy,-hz),( hx,-hy,-hz)]),
        ((-1,0,0), [(-hx,-hy,-hz),(-hx,-hy, hz),(-hx, hy, hz),(-hx, hy,-hz)]),
        (( 1,0,0), [( hx,-hy,-hz),( hx, hy,-hz),( hx, hy, hz),( hx,-hy, hz)]),
        ((0, 1,0), [(-hx, hy,-hz),(-hx, hy, hz),( hx, hy, hz),( hx, hy,-hz)]),
        ((0,-1,0), [(-hx,-hy,-hz),( hx,-hy,-hz),( hx,-hy, hz),(-hx,-hy, hz)]),
    ]
    glBegin(GL_QUADS)
    for normal, verts in faces:
        shade = 0.6 + 0.4*abs(normal[1]) + 0.2*abs(normal[2])
        glColor3f(r*shade, g*shade, b*shade)
        for v in verts:
            glVertex3f(*v)
    glEnd()


def draw_pyramid(base, height, r, g, b):
    hb   = base / 2
    apex = (0, height, 0)
    sides = [
        [(-hb,0, hb),( hb,0, hb), apex],
        [( hb,0, hb),( hb,0,-hb), apex],
        [( hb,0,-hb),(-hb,0,-hb), apex],
        [(-hb,0,-hb),(-hb,0, hb), apex],
    ]
    glBegin(GL_TRIANGLES)
    for i, tri in enumerate(sides):
        shade = 0.7 + 0.1*i
        glColor3f(r*shade, g*shade, b*shade)
        for v in tri:
            glVertex3f(*v)
    glEnd()
    glBegin(GL_QUADS)
    glColor3f(r*0.5, g*0.5, b*0.5)
    glVertex3f(-hb,0,-hb); glVertex3f(hb,0,-hb)
    glVertex3f( hb,0, hb); glVertex3f(-hb,0, hb)
    glEnd()


def _get_quadric():
    global quadric
    if quadric is None:
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
    return quadric


def draw_cylinder_gl(radius, height, slices=12):
    q = _get_quadric()
    gluCylinder(q, radius, radius, height, slices, 1)
    glPushMatrix(); glRotatef(180,1,0,0); gluDisk(q, 0, radius, slices, 1); glPopMatrix()
    glPushMatrix(); glTranslatef(0,0,height); gluDisk(q, 0, radius, slices, 1); glPopMatrix()


def draw_cone_gl(base_r, height, slices=12):
    q = _get_quadric()
    gluCylinder(q, base_r, 0.0, height, slices, 1)
    glPushMatrix(); glRotatef(180,1,0,0); gluDisk(q, 0, base_r, slices, 1); glPopMatrix()


def draw_sphere_gl(radius, slices=12):
    gluSphere(_get_quadric(), radius, slices, slices//2)


# ══════════════════════════════════════════════════════════════
#  OBJETOS DE LA CIUDAD (escala ~1 = MARKER_LENGTH_M)
#  Todo el mundo está en espacio del marcador:
#    X: derecha, Y: arriba, Z: hacia cámara (sale del marcador)
#  El suelo (Y=0) coincide con el plano del marcador.
# ══════════════════════════════════════════════════════════════

def draw_ground_mini():
    """Piso cuadriculado debajo de la ciudad."""
    S = 5.0
    Y = 0.0
    # Base gris oscuro
    glBegin(GL_QUADS)
    glColor3f(0.22, 0.22, 0.22)
    glVertex3f(-S, Y, -S); glVertex3f(S, Y, -S)
    glVertex3f( S, Y,  S); glVertex3f(-S, Y,  S)
    glEnd()
    # Cuadrícula verde (jardines)
    glBegin(GL_QUADS)
    glColor3f(0.22, 0.48, 0.18)
    for qx, qz in [(-3,-3),(-3,1),(1,-3),(1,1)]:
        glVertex3f(qx,   Y+0.01, qz)
        glVertex3f(qx+2, Y+0.01, qz)
        glVertex3f(qx+2, Y+0.01, qz+2)
        glVertex3f(qx,   Y+0.01, qz+2)
    glEnd()
    # Calle central
    glBegin(GL_QUADS)
    glColor3f(0.28, 0.28, 0.28)
    glVertex3f(-S, Y+0.02, -0.6); glVertex3f(S, Y+0.02, -0.6)
    glVertex3f( S, Y+0.02,  0.6); glVertex3f(-S, Y+0.02,  0.6)
    glVertex3f(-0.6, Y+0.02, -S); glVertex3f(0.6, Y+0.02, -S)
    glVertex3f( 0.6, Y+0.02,  S); glVertex3f(-0.6, Y+0.02,  S)
    glEnd()


def draw_building_mini(x, z, w, h, d, r, g, b, t, pulse=False):
    glPushMatrix()
    glTranslatef(x, h/2, z)
    if pulse:
        s = 1.0 + 0.025 * math.sin(t * 1.5)
        glScalef(s, s, s)
    draw_box(w, h, d, r, g, b)
    # Ventanas
    rows = max(1, int(h/1.2))
    cols = max(1, int(w/0.8))
    glColor3f(1.0, 0.95, 0.5)
    glBegin(GL_QUADS)
    for row in range(rows):
        wy = -h/2 + 0.6 + row*1.1
        for col in range(cols):
            wx = -w/2 + 0.45 + col*0.85
            glVertex3f(wx,      wy,      d/2+0.01)
            glVertex3f(wx+0.25, wy,      d/2+0.01)
            glVertex3f(wx+0.25, wy+0.25, d/2+0.01)
            glVertex3f(wx,      wy+0.25, d/2+0.01)
    glEnd()
    glPopMatrix()


def draw_house_mini(x, z,
                    wr=0.92, wg=0.88, wb=0.78,
                    rr=0.20, rg=0.45, rb=0.72):
    glPushMatrix()
    glTranslatef(x, 0, z)
    # Cuerpo
    glPushMatrix(); glTranslatef(0, 0.75, 0)
    draw_box(1.8, 1.5, 1.8, wr, wg, wb)
    glPopMatrix()
    # Techo
    glPushMatrix(); glTranslatef(0, 1.5, 0)
    draw_pyramid(2.0, 1.0, rr, rg, rb)
    glPopMatrix()
    # Puerta
    glPushMatrix(); glTranslatef(0, 0.35, 0.91)
    draw_box(0.3, 0.7, 0.02, 0.35, 0.20, 0.10)
    glPopMatrix()
    glPopMatrix()


def draw_tree_mini(x, z):
    glPushMatrix()
    glTranslatef(x, 0, z)
    # Tronco
    glColor3f(0.4, 0.25, 0.1)
    glPushMatrix(); glRotatef(-90,1,0,0)
    draw_cylinder_gl(0.12, 1.0, 10)
    glPopMatrix()
    # Copa inferior
    glColor3f(0.15, 0.65, 0.2)
    glPushMatrix(); glTranslatef(0, 1.0, 0); glRotatef(-90,1,0,0)
    draw_cone_gl(0.65, 1.5, 12)
    glPopMatrix()
    # Copa superior
    glColor3f(0.2, 0.75, 0.25)
    glPushMatrix(); glTranslatef(0, 1.8, 0); glRotatef(-90,1,0,0)
    draw_cone_gl(0.45, 1.1, 12)
    glPopMatrix()
    glPopMatrix()


def draw_lamp_post_mini(x, z):
    glPushMatrix()
    glTranslatef(x, 0, z)
    glColor3f(0.5, 0.5, 0.5)
    glPushMatrix(); glRotatef(-90,1,0,0)
    draw_cylinder_gl(0.07, 3.0, 8)
    glPopMatrix()
    glPushMatrix(); glTranslatef(0.3, 3.0, 0)
    draw_box(0.6, 0.07, 0.07, 0.5, 0.5, 0.5)
    glPopMatrix()
    glPushMatrix(); glTranslatef(0.6, 2.85, 0)
    glColor3f(1.0, 1.0, 0.6)
    draw_sphere_gl(0.15, 8)
    glPopMatrix()
    glPopMatrix()


def draw_car_mini(x, z, angle_car, r, g, b):
    glPushMatrix()
    glTranslatef(x, 0.3, z)
    glRotatef(angle_car, 0, 1, 0)
    draw_box(1.6, 0.4, 0.8, r, g, b)
    glPushMatrix(); glTranslatef(0, 0.35, 0)
    draw_box(0.9, 0.35, 0.75, r*0.8, g*0.8, b*0.8)
    glPopMatrix()
    glColor3f(0.15, 0.15, 0.15)
    for wx, wz in [(-0.55,-0.42),(0.55,-0.42),(-0.55,0.42),(0.55,0.42)]:
        glPushMatrix(); glTranslatef(wx, -0.18, wz); glRotatef(90,0,1,0)
        draw_cylinder_gl(0.18, 0.12, 10)
        glPopMatrix()
    glPopMatrix()


def draw_balloon_mini(t):
    y_off = 2.0 * math.sin(t * 0.6)
    glPushMatrix()
    glTranslatef(1.5, 4.0 + y_off, 1.5)
    glColor3f(1.0, 0.3, 0.3)
    draw_sphere_gl(0.6, 14)
    glColor3f(0.6, 0.4, 0.2)
    glBegin(GL_LINES)
    for a in [0, 90, 180, 270]:
        ra = math.radians(a)
        glVertex3f(0.4*math.cos(ra), -0.6, 0.4*math.sin(ra))
        glVertex3f(0.1*math.cos(ra), -1.1, 0.1*math.sin(ra))
    glEnd()
    glPushMatrix(); glTranslatef(0, -1.2, 0)
    draw_box(0.3, 0.2, 0.3, 0.55, 0.35, 0.15)
    glPopMatrix()
    glPopMatrix()


def draw_cloud_mini(x, z, y, t):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.95, 0.95, 0.98)
    for ox, oy, r in [(0,0,0.55),(-0.45,-0.12,0.4),(0.5,-0.08,0.42)]:
        glPushMatrix(); glTranslatef(ox, oy, 0)
        draw_sphere_gl(r, 10)
        glPopMatrix()
    glPopMatrix()


def draw_sun_mini(t):
    angle = t * 20.0
    r = 6.0
    sx = r * math.cos(math.radians(angle))
    sy = 5.0 + 2.0 * math.sin(math.radians(angle * 0.5))
    sz = r * math.sin(math.radians(angle))
    glPushMatrix()
    glTranslatef(sx, sy, sz)
    glColor3f(1.0, 0.95, 0.3)
    draw_sphere_gl(0.5, 12)
    glPopMatrix()


# ══════════════════════════════════════════════════════════════
#  RENDER COMPLETO DE LA MINI-CIUDAD
# ══════════════════════════════════════════════════════════════

def render_mini_city(t):
    """
    Dibuja el bloque de ciudad en coordenadas del marcador.
    MODEL_SCALE ya aplicado en la transformación padre (draw_scene).
    El suelo Y=0 queda sobre el marcador.
    """
    draw_ground_mini()

    # ── 3 EDIFICIOS ──────────────────────────────────────────
    buildings = [
        # x,    z,    w,   h,   d,    r,    g,    b,   pulse
        (-3.0, -3.0, 2.0, 8.0, 2.0, 0.50, 0.55, 0.65, True),
        ( 2.5, -3.0, 2.0, 5.5, 2.0, 0.60, 0.45, 0.40, False),
        (-3.0,  2.5, 2.0, 6.5, 2.0, 0.40, 0.50, 0.60, True),
    ]
    for bx,bz,bw,bh,bd,br,bg,bb,bp in buildings:
        draw_building_mini(bx, bz, bw, bh, bd, br, bg, bb, t, bp)

    # ── 2 CASAS ──────────────────────────────────────────────
    draw_house_mini(-1.0, -1.5, 0.95, 0.90, 0.75, 0.80, 0.18, 0.18)
    draw_house_mini( 1.5,  1.5, 0.70, 0.88, 0.78, 0.20, 0.45, 0.72)

    # ── 2 ÁRBOLES ────────────────────────────────────────────
    draw_tree_mini(-1.0,  1.5)
    draw_tree_mini( 1.5, -1.5)

    # ── POSTE ────────────────────────────────────────────────
    draw_lamp_post_mini(0.5, -0.8)

    # ── AUTO ROJO — translación en Z ─────────────────────────
    car_z = -4.5 + (t * 2.0) % 9.0
    draw_car_mini(-0.5, car_z - 4.5, 0, 0.85, 0.15, 0.15)

    # ── AUTO AZUL — translación en X ─────────────────────────
    car_x = 4.0 - (t * 1.8) % 8.0
    draw_car_mini(car_x - 4.0, 0.5, 90, 0.15, 0.25, 0.80)

    # ── GLOBO oscilante ──────────────────────────────────────
    draw_balloon_mini(t)

    # ── NUBES ────────────────────────────────────────────────
    cloud_x = -6.0 + (t * 0.8) % 12.0
    draw_cloud_mini(cloud_x, -2, 7.0, t)
    draw_cloud_mini(cloud_x - 5, 3, 6.5, t)

    # ── SOL ──────────────────────────────────────────────────
    draw_sun_mini(t)


# ══════════════════════════════════════════════════════════════
#  ESCENA 3D SOBRE EL MARCADOR
# ══════════════════════════════════════════════════════════════

def setup_lighting():
    glDisable(GL_LIGHTING)
    glDisable(GL_COLOR_MATERIAL)


def draw_scene(rvec, tvec, camera_matrix, width, height, t):
    global rotation

    projection = projection_matrix_from_camera(camera_matrix, width, height)
    modelview  = modelview_matrix(rvec, tvec)

    glMatrixMode(GL_PROJECTION)
    glLoadMatrixf(projection)

    glMatrixMode(GL_MODELVIEW)
    glLoadMatrixf(modelview)

    setup_lighting()

    glScalef(MODEL_SCALE, MODEL_SCALE, MODEL_SCALE)
    glRotatef(90, 1, 0, 0)
    glRotatef(rotation, 0, 0, 1)

    render_mini_city(t)


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

def main():
    global MODEL_SCALE, rotation

    # ── Cámara ───────────────────────────────────────────────
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        sys.exit(1)

    # ── Forzar resolución de captura ─────────────────────────
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  WIN_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WIN_H)

    ret, frame = cap.read()
    if not ret:
        print("No se pudo leer un frame.")
        cap.release()
        sys.exit(1)

    # Usar WIN_W / WIN_H como dimensiones canónicas.
    # Si la cámara no soporta esa resolución, el frame se escala abajo.
    w, h = WIN_W, WIN_H
    camera_matrix = default_camera_matrix(w, h)

    detector, dictionary = make_detector()

    # ── GLFW / OpenGL ─────────────────────────────────────────
    if not glfw.init():
        print("No se pudo inicializar GLFW.")
        sys.exit(1)

    window = glfw.create_window(w, h, WINDOW_TITLE, None, None)
    if not window:
        glfw.terminate()
        sys.exit(1)

    glfw.make_context_current(window)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)

    # ── Teclado ──────────────────────────────────────────────
    def key_callback(win, key, scancode, action, mods):
        global MODEL_SCALE, rotation
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(win, True)
        elif key == glfw.KEY_EQUAL:
            MODEL_SCALE *= 1.15
        elif key == glfw.KEY_MINUS:
            MODEL_SCALE /= 1.15
        elif key == glfw.KEY_LEFT:
            rotation -= 15
        elif key == glfw.KEY_RIGHT:
            rotation += 15

    glfw.set_key_callback(window, key_callback)

    # ── HUD en frame de cámara ────────────────────────────────
    hud_lines = [
        "Apunta la camara al marcador ArUco ID=0",
        "+/-: escalar ciudad    <-/->: rotar",
        "ESC: salir",
    ]

    t0 = time.perf_counter()

    # ── Bucle principal ───────────────────────────────────────
    while not glfw.window_should_close(window):
        t = time.perf_counter() - t0

        ret, frame = cap.read()
        if not ret:
            continue

        # Escalar frame al tamaño de ventana si la cámara devuelve
        # una resolución distinta a WIN_W x WIN_H
        fh, fw = frame.shape[:2]
        if fw != w or fh != h:
            frame = cv2.resize(frame, (w, h))

        # Detección ArUco
        gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners = detect_marker(gray, detector, dictionary)

        # HUD en la ventana de cámara
        hud_frame = frame.copy()
        for i, line in enumerate(hud_lines):
            cv2.putText(hud_frame, line, (10, 22 + i*22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1)

        if corners is not None:
            cv2.aruco.drawDetectedMarkers(hud_frame, [corners])
            cv2.putText(hud_frame, "Marcador detectado!", (10, h - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 80), 2)
        else:
            cv2.putText(hud_frame, "Buscando marcador...", (10, h - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 80, 255), 2)

        cv2.imshow("AR — Camara", hud_frame)
        cv2.waitKey(1)

        # Render OpenGL
        glViewport(0, 0, w, h)
        upload_camera_texture(frame)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_background(w, h)

        if corners is not None:
            rvec, tvec = estimate_pose(corners, camera_matrix)
            if rvec is not None:
                draw_scene(rvec, tvec, camera_matrix, w, h, t)

        glfw.swap_buffers(window)
        glfw.poll_events()

    # ── Limpieza ──────────────────────────────────────────────
    global quadric
    if quadric:
        gluDeleteQuadric(quadric)
    cap.release()
    cv2.destroyAllWindows()
    glfw.terminate()


if __name__ == "__main__":
    main()