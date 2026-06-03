"""
=============================================================
  PROYECTO 2 — CIUDAD 3D CON OpenGL + MediaPipe
  Materia: Graficación
  Control: dos manos via webcam

"""

import os, sys, math, time
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("GLOG_minloglevel", "3")

import glfw
import cv2
import numpy as np
import mediapipe as mp
from OpenGL.GL import *
from OpenGL.GLU import *

# ─── MediaPipe Tasks API ──────────────────────────────────────
BaseOptions       = mp.tasks.BaseOptions
HandLandmarker    = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "hand_landmarker.task")

HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (5,9),(9,10),(10,11),(11,12),
    (9,13),(13,14),(14,15),(15,16),
    (13,17),(0,17),(17,18),(18,19),(19,20),
]

# ─── Estado de cámara ────────────────────────────────────────
angle_x, angle_y = 20.0, 0.0
zoom             = -18.0
pan_x, pan_y     = 0.0, -1.0
prev_right       = None
prev_left        = None

# ─── Cuádrica reutilizable (se crea una vez en main) ─────────
quadric = None


# ══════════════════════════════════════════════════════════════
#  PRIMITIVAS DE DIBUJO
# ══════════════════════════════════════════════════════════════

def draw_box(w, h, d, r, g, b):
    """Caja centrada en el origen, dimensiones w×h×d, color RGB."""
    hx, hy, hz = w/2, h/2, d/2
    faces = [
        # frente
        ((0,0,1),  [(-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]),
        # atrás
        ((0,0,-1), [(-hx,-hy,-hz),(-hx,hy,-hz),(hx,hy,-hz),(hx,-hy,-hz)]),
        # izquierda
        ((-1,0,0), [(-hx,-hy,-hz),(-hx,-hy,hz),(-hx,hy,hz),(-hx,hy,-hz)]),
        # derecha
        ((1,0,0),  [(hx,-hy,-hz),(hx,hy,-hz),(hx,hy,hz),(hx,-hy,hz)]),
        # arriba
        ((0,1,0),  [(-hx,hy,-hz),(-hx,hy,hz),(hx,hy,hz),(hx,hy,-hz)]),
        # abajo
        ((0,-1,0), [(-hx,-hy,-hz),(hx,-hy,-hz),(hx,-hy,hz),(-hx,-hy,hz)]),
    ]
    glBegin(GL_QUADS)
    for normal, verts in faces:
        shade = 0.6 + 0.4 * abs(normal[1]) + 0.2 * abs(normal[2])
        glColor3f(r*shade, g*shade, b*shade)
        for v in verts:
            glVertex3f(*v)
    glEnd()


def draw_pyramid(base, height, r, g, b):
    """Pirámide de base cuadrada base×base, altura height."""
    hb = base / 2
    apex = (0, height, 0)
    sides = [
        [(-hb,0,hb), (hb,0,hb),  apex],
        [(hb,0,hb),  (hb,0,-hb), apex],
        [(hb,0,-hb), (-hb,0,-hb),apex],
        [(-hb,0,-hb),(-hb,0,hb), apex],
    ]
    glBegin(GL_TRIANGLES)
    for i, tri in enumerate(sides):
        shade = 0.7 + 0.1*i
        glColor3f(r*shade, g*shade, b*shade)
        for v in tri:
            glVertex3f(*v)
    glEnd()
    # base
    glBegin(GL_QUADS)
    glColor3f(r*0.5, g*0.5, b*0.5)
    glVertex3f(-hb,0,-hb); glVertex3f(hb,0,-hb)
    glVertex3f(hb,0,hb);   glVertex3f(-hb,0,hb)
    glEnd()


def draw_cylinder_gl(radius, height, slices=16):
    """Cilindro usando GLU."""
    gluCylinder(quadric, radius, radius, height, slices, 1)
    # tapa inferior
    glPushMatrix()
    glRotatef(180, 1, 0, 0)
    gluDisk(quadric, 0, radius, slices, 1)
    glPopMatrix()
    # tapa superior
    glPushMatrix()
    glTranslatef(0, 0, height)
    gluDisk(quadric, 0, radius, slices, 1)
    glPopMatrix()


def draw_cone_gl(base_r, height, slices=16):
    gluCylinder(quadric, base_r, 0.0, height, slices, 1)
    glPushMatrix()
    glRotatef(180, 1, 0, 0)
    gluDisk(quadric, 0, base_r, slices, 1)
    glPopMatrix()


def draw_sphere_gl(radius, slices=16):
    gluSphere(quadric, radius, slices, slices//2)


# ══════════════════════════════════════════════════════════════
#  OBJETOS DE LA CIUDAD
# ══════════════════════════════════════════════════════════════

def draw_ground():
    """
    Suelo con calles, banquetas y jardines.

    Layout (coordenadas mundo):
      Calles principales: franjas de 2 u de ancho en X=-2..0 y Z=-2..0
      Banquetas:          franja de 0.5 u a cada lado de la calle
      Jardines:           cuadrantes verdes entre bloques de ciudad
      Resto:              asfalto gris oscuro base
    """
    SIZE = 25          # mitad del tamaño total del suelo
    STREET_W  = 2.0    # ancho de cada calle principal
    SIDEW_W   = 0.5    # ancho de banqueta
    Y = 0.0            # altura del suelo

    # ── 1. BASE: césped verde oscuro (todo el suelo) ──────────
    glBegin(GL_QUADS)
    glColor3f(0.22, 0.48, 0.18)
    glVertex3f(-SIZE, Y, -SIZE)
    glVertex3f( SIZE, Y, -SIZE)
    glVertex3f( SIZE, Y,  SIZE)
    glVertex3f(-SIZE, Y,  SIZE)
    glEnd()

    # ── 2. JARDINES: cuadrantes con hierba más clara ──────────
    # Cuatro bloques principales de jardín (entre las calles)
    garden_blocks = [
        # (x0, z0, x1, z1)
        (-SIZE,  -SIZE,  -3,   -3),   # SO
        (   3,   -SIZE,  SIZE, -3),   # SE
        (-SIZE,     3,  -3,   SIZE),  # NO
        (   3,      3,  SIZE, SIZE),  # NE
    ]
    glBegin(GL_QUADS)
    for x0, z0, x1, z1 in garden_blocks:
        glColor3f(0.28, 0.58, 0.22)
        glVertex3f(x0, Y+0.01, z0)
        glVertex3f(x1, Y+0.01, z0)
        glVertex3f(x1, Y+0.01, z1)
        glVertex3f(x0, Y+0.01, z1)
    glEnd()

    # Flores/manchas en jardines (pequeños quads de colores)
    import math
    flower_seed = [
        (-18,-18),(-14,-20),(-20,-12),(-10,-16),(-16,-8),
        ( 10,-18),( 16,-14),( 20,-20),( 12,-10),( 18,-8),
        (-18, 10),(-12, 16),(-20, 18),(-8,  12),(-16, 20),
        ( 10, 10),( 18, 14),( 12, 20),( 20, 10),( 8,  18),
    ]
    flower_colors = [
        (1.0,0.2,0.2),(1.0,0.85,0.1),(0.9,0.5,0.9),
        (1.0,0.55,0.1),(0.4,0.8,1.0)
    ]
    glBegin(GL_QUADS)
    for i,(fx,fz) in enumerate(flower_seed):
        cr,cg,cb = flower_colors[i % len(flower_colors)]
        glColor3f(cr, cg, cb)
        glVertex3f(fx-0.25, Y+0.02, fz-0.25)
        glVertex3f(fx+0.25, Y+0.02, fz-0.25)
        glVertex3f(fx+0.25, Y+0.02, fz+0.25)
        glVertex3f(fx-0.25, Y+0.02, fz+0.25)
    glEnd()

    # ── 3. BANQUETAS: gris claro a los lados de las calles ────
    SW = STREET_W / 2   # mitad del ancho de calle
    SB = SW + SIDEW_W   # borde exterior de banqueta

    sidewalk_strips = [
        # banquetas calle horizontal (a lo largo de Z)
        (-SIZE, -SB,    SIZE, -SW),   # norte de calle horizontal
        (-SIZE,  SW,    SIZE,  SB),   # sur  de calle horizontal
        # banquetas calle vertical (a lo largo de X)
        (-SB,  -SIZE,  -SW,   SIZE),  # oeste de calle vertical
        ( SW,  -SIZE,   SB,   SIZE),  # este  de calle vertical
    ]
    glBegin(GL_QUADS)
    glColor3f(0.72, 0.72, 0.70)
    for x0,z0,x1,z1 in sidewalk_strips:
        glVertex3f(x0, Y+0.015, z0)
        glVertex3f(x1, Y+0.015, z0)
        glVertex3f(x1, Y+0.015, z1)
        glVertex3f(x0, Y+0.015, z1)
    glEnd()

    # ── 4. CALLES: asfalto gris oscuro ────────────────────────
    street_quads = [
        # calle horizontal (eje X, franja en Z)
        (-SIZE, -SW,  SIZE,  SW),
        # calle vertical   (eje Z, franja en X)
        (-SW,  -SIZE,  SW,  SIZE),
    ]
    glBegin(GL_QUADS)
    glColor3f(0.22, 0.22, 0.22)
    for x0,z0,x1,z1 in street_quads:
        glVertex3f(x0, Y+0.02, z0)
        glVertex3f(x1, Y+0.02, z0)
        glVertex3f(x1, Y+0.02, z1)
        glVertex3f(x0, Y+0.02, z1)
    glEnd()

    # ── 5. LÍNEAS DISCONTINUAS en el centro de cada calle ─────
    glBegin(GL_QUADS)
    glColor3f(0.95, 0.88, 0.2)   # amarillo
    dash_len  = 1.5
    gap_len   = 1.0
    stripe_w  = 0.08
    period    = dash_len + gap_len
    pos = -SIZE
    while pos < SIZE:
        end = pos + dash_len
        # línea central horizontal
        glVertex3f(pos, Y+0.03, -stripe_w)
        glVertex3f(end, Y+0.03, -stripe_w)
        glVertex3f(end, Y+0.03,  stripe_w)
        glVertex3f(pos, Y+0.03,  stripe_w)
        # línea central vertical
        glVertex3f(-stripe_w, Y+0.03, pos)
        glVertex3f( stripe_w, Y+0.03, pos)
        glVertex3f( stripe_w, Y+0.03, end)
        glVertex3f(-stripe_w, Y+0.03, end)
        pos += period
    glEnd()

    # ── 6. CRUCE: bloque sólido gris en la intersección ───────
    glBegin(GL_QUADS)
    glColor3f(0.28, 0.28, 0.28)
    glVertex3f(-SW, Y+0.025, -SW)
    glVertex3f( SW, Y+0.025, -SW)
    glVertex3f( SW, Y+0.025,  SW)
    glVertex3f(-SW, Y+0.025,  SW)
    glEnd()

    # ── 7. PASO PEATONAL: rayas blancas en el cruce ───────────
    glBegin(GL_QUADS)
    glColor3f(0.95, 0.95, 0.95)
    stripe_count = 4
    sw2 = SW - 0.1
    for i in range(stripe_count):
        sx = -sw2 + i * (2*sw2 / stripe_count)
        ex = sx + (2*sw2 / stripe_count) * 0.5
        # paso horizontal (norte-sur)
        glVertex3f(sx, Y+0.04, -SB)
        glVertex3f(ex, Y+0.04, -SB)
        glVertex3f(ex, Y+0.04, -SW)
        glVertex3f(sx, Y+0.04, -SW)
        glVertex3f(sx, Y+0.04,  SW)
        glVertex3f(ex, Y+0.04,  SW)
        glVertex3f(ex, Y+0.04,  SB)
        glVertex3f(sx, Y+0.04,  SB)
        # paso vertical (este-oeste)
        glVertex3f(-SB, Y+0.04, sx)
        glVertex3f(-SW, Y+0.04, sx)
        glVertex3f(-SW, Y+0.04, ex)
        glVertex3f(-SB, Y+0.04, ex)
        glVertex3f( SW, Y+0.04, sx)
        glVertex3f( SB, Y+0.04, sx)
        glVertex3f( SB, Y+0.04, ex)
        glVertex3f( SW, Y+0.04, ex)
    glEnd()


def draw_building(x, z, w, h, d, r, g, b, t, scale_pulse=False):
    """Edificio: cuerpo + ventanas."""
    glPushMatrix()
    glTranslatef(x, h/2, z)
    # Escalado pulsante (animación)
    if scale_pulse:
        s = 1.0 + 0.025 * math.sin(t * 1.5)
        glScalef(s, s, s)
    draw_box(w, h, d, r, g, b)
    # Ventanas (líneas de quads amarillos)
    rows = max(1, int(h/1.2))
    cols = max(1, int(w/0.8))
    ww, wh = 0.25, 0.25
    glColor3f(1.0, 0.95, 0.5)
    glBegin(GL_QUADS)
    for row in range(rows):
        wy = -h/2 + 0.6 + row*1.1
        for col in range(cols):
            wx = -w/2 + 0.45 + col*0.85
            glVertex3f(wx,     wy,    d/2+0.01)
            glVertex3f(wx+ww,  wy,    d/2+0.01)
            glVertex3f(wx+ww,  wy+wh, d/2+0.01)
            glVertex3f(wx,     wy+wh, d/2+0.01)
    glEnd()
    glPopMatrix()


def draw_house(x, z, t=0, wall_r=0.92, wall_g=0.88, wall_b=0.78,
               roof_r=0.20, roof_g=0.45, roof_b=0.72):
    """Casa con paredes y techo piramidal, colores configurables."""
    glPushMatrix()
    glTranslatef(x, 0, z)
    # Cuerpo
    glPushMatrix()
    glTranslatef(0, 0.75, 0)
    draw_box(1.8, 1.5, 1.8, wall_r, wall_g, wall_b)
    glPopMatrix()
    # Techo
    glPushMatrix()
    glTranslatef(0, 1.5, 0)
    draw_pyramid(2.0, 1.0, roof_r, roof_g, roof_b)
    glPopMatrix()
    # Puerta
    glPushMatrix()
    glTranslatef(0, 0.35, 0.91)
    draw_box(0.3, 0.7, 0.02, 0.35, 0.20, 0.10)
    glPopMatrix()
    glPopMatrix()


def draw_tree(x, z):
    """Árbol: tronco cilíndrico + copa cónica."""
    glPushMatrix()
    glTranslatef(x, 0, z)
    # Tronco
    glColor3f(0.4, 0.25, 0.1)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_cylinder_gl(0.12, 1.0, 10)
    glPopMatrix()
    # Copa
    glColor3f(0.15, 0.65, 0.2)
    glPushMatrix()
    glTranslatef(0, 1.0, 0)
    glRotatef(-90, 1, 0, 0)
    draw_cone_gl(0.65, 1.5, 12)
    glPopMatrix()
    # Segunda copa
    glColor3f(0.2, 0.75, 0.25)
    glPushMatrix()
    glTranslatef(0, 1.8, 0)
    glRotatef(-90, 1, 0, 0)
    draw_cone_gl(0.45, 1.1, 12)
    glPopMatrix()
    glPopMatrix()


def draw_lamp_post(x, z):
    """Poste de luz: cilindro + esfera."""
    glPushMatrix()
    glTranslatef(x, 0, z)
    # Poste
    glColor3f(0.5, 0.5, 0.5)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_cylinder_gl(0.07, 3.0, 8)
    glPopMatrix()
    # Brazo
    glPushMatrix()
    glTranslatef(0.3, 3.0, 0)
    draw_box(0.6, 0.07, 0.07, 0.5, 0.5, 0.5)
    glPopMatrix()
    # Luz
    glPushMatrix()
    glTranslatef(0.6, 2.85, 0)
    glColor3f(1.0, 1.0, 0.6)
    draw_sphere_gl(0.15, 8)
    glPopMatrix()
    glPopMatrix()


def draw_fountain(t):
    """Fuente central: base + anillos (toro aproximado) + agua animada."""
    glPushMatrix()
    # Base
    glColor3f(0.55, 0.55, 0.65)
    glPushMatrix()
    glTranslatef(0, 0.15, 0)
    draw_cylinder_gl(1.2, 0.3, 24)
    glPopMatrix()
    # Borde
    glColor3f(0.6, 0.6, 0.7)
    for a in range(0, 360, 15):
        ra = math.radians(a)
        px = 1.2 * math.cos(ra)
        pz = 1.2 * math.sin(ra)
        glPushMatrix()
        glTranslatef(px, 0.45, pz)
        draw_sphere_gl(0.12, 8)
        glPopMatrix()
    # Columna central
    glColor3f(0.7, 0.7, 0.8)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_cylinder_gl(0.12, 1.2, 12)
    glPopMatrix()
    # Agua (arco de partículas animadas)
    glColor3f(0.3, 0.6, 1.0)
    glPointSize(4.0)
    glBegin(GL_POINTS)
    for i in range(16):
        a  = math.radians(i * 22.5)
        ph = t * 2.5 + i * 0.4
        r  = 0.3 + 0.5 * abs(math.sin(ph))
        ht = 0.5 + 0.8 * abs(math.sin(ph))
        glVertex3f(r*math.cos(a), 1.2 + ht, r*math.sin(a))
    glEnd()
    glPointSize(1.0)
    glPopMatrix()


def draw_car(x, z, angle_y_car, r, g, b):
    """Auto simple: carrocería + ruedas."""
    glPushMatrix()
    glTranslatef(x, 0.3, z)
    glRotatef(angle_y_car, 0, 1, 0)
    # Carrocería baja
    draw_box(1.6, 0.4, 0.8, r, g, b)
    # Cabina
    glPushMatrix()
    glTranslatef(0, 0.35, 0)
    draw_box(0.9, 0.35, 0.75, r*0.8, g*0.8, b*0.8)
    glPopMatrix()
    # Ruedas (4)
    glColor3f(0.15, 0.15, 0.15)
    for wx, wz in [(-0.55,-0.42),(0.55,-0.42),(-0.55,0.42),(0.55,0.42)]:
        glPushMatrix()
        glTranslatef(wx, -0.18, wz)
        glRotatef(90, 0, 1, 0)
        draw_cylinder_gl(0.18, 0.12, 10)
        glPopMatrix()
    glPopMatrix()


def draw_balloon(x, z, y_offset, t):
    """Globo aerostático: esfera grande + cesta."""
    glPushMatrix()
    glTranslatef(x, 5.0 + y_offset, z)
    # Esfera del globo
    glColor3f(1.0, 0.3, 0.3)
    draw_sphere_gl(0.8, 16)
    # Rayas
    glColor3f(1.0, 1.0, 0.2)
    for i in range(8):
        a = math.radians(i*45)
        glPushMatrix()
        glRotatef(i*45, 0, 1, 0)
        glBegin(GL_LINES)
        for lat in range(-8, 9):
            la = math.radians(lat*10)
            glVertex3f(0.81*math.cos(la)*math.cos(math.radians(5)),
                       0.81*math.sin(la),
                       0.81*math.cos(la)*math.sin(math.radians(5)))
        glEnd()
        glPopMatrix()
    # Cuerdas
    glColor3f(0.6, 0.4, 0.2)
    glBegin(GL_LINES)
    for a in [0, 90, 180, 270]:
        ra = math.radians(a)
        glVertex3f(0.5*math.cos(ra), -0.8, 0.5*math.sin(ra))
        glVertex3f(0.15*math.cos(ra), -1.4, 0.15*math.sin(ra))
    glEnd()
    # Cesta
    glPushMatrix()
    glTranslatef(0, -1.5, 0)
    draw_box(0.35, 0.25, 0.35, 0.55, 0.35, 0.15)
    glPopMatrix()
    glPopMatrix()


def draw_sun_moon(t):
    """Sol/luna que orbita en el cielo."""
    angle = t * 20.0
    r     = 16.0
    sx    = r * math.cos(math.radians(angle))
    sy    = 8.0 + 4.0 * math.sin(math.radians(angle * 0.5))
    sz    = r * math.sin(math.radians(angle))
    glPushMatrix()
    glTranslatef(sx, sy, sz)
    glColor3f(1.0, 0.95, 0.3)
    draw_sphere_gl(0.9, 16)
    # Halo
    glColor3f(1.0, 0.85, 0.1)
    for i in range(8):
        a = math.radians(i*45 + angle*3)
        glPushMatrix()
        glRotatef(i*45 + angle*3, 0, 0, 1)
        draw_box(0.1, 0.9, 0.05, 1.0, 0.85, 0.1)
        glPopMatrix()
    glPopMatrix()


def draw_plane(t):
    """Avión que orbita la ciudad."""
    angle = t * 25.0
    r     = 14.0
    px    = r * math.cos(math.radians(angle))
    pz    = r * math.sin(math.radians(angle))
    py    = 7.0
    glPushMatrix()
    glTranslatef(px, py, pz)
    glRotatef(angle + 90, 0, 1, 0)   # mira hacia donde vuela
    # Cuerpo
    glColor3f(0.9, 0.9, 0.9)
    draw_box(1.8, 0.3, 0.3, 0.9, 0.9, 0.9)
    # Alas
    glColor3f(0.7, 0.7, 0.75)
    glPushMatrix()
    glTranslatef(0, 0, 0)
    draw_box(0.4, 0.08, 1.6, 0.7, 0.7, 0.75)
    glPopMatrix()
    # Cola
    glColor3f(0.8, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(-0.75, 0.22, 0)
    draw_box(0.25, 0.45, 0.05, 0.8, 0.1, 0.1)
    glPopMatrix()
    glPopMatrix()


def draw_cloud(x, z, y, t):
    """Nube (3 esferas) que se desplaza."""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.95, 0.95, 0.98)
    for ox, oy, r in [(0,0,0.7),(-0.6,-.15,0.5),(0.65,-.1,0.52)]:
        glPushMatrix()
        glTranslatef(ox, oy, 0)
        draw_sphere_gl(r, 12)
        glPopMatrix()
    glPopMatrix()


def draw_traffic_light(x, z):
    """Semáforo: poste + caja + 3 luces."""
    glPushMatrix()
    glTranslatef(x, 0, z)
    # Poste
    glColor3f(0.4, 0.4, 0.4)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_cylinder_gl(0.06, 2.8, 8)
    glPopMatrix()
    # Caja
    glPushMatrix()
    glTranslatef(0, 3.0, 0)
    draw_box(0.2, 0.55, 0.18, 0.15, 0.15, 0.15)
    # Luces R/Y/G
    for oy, cr, cg, cb in [(0.18,1,0,0),(0,1,0.85,0),(-0.18,0,0.8,0)]:
        glPushMatrix()
        glTranslatef(0, oy, 0.1)
        glColor3f(cr, cg, cb)
        draw_sphere_gl(0.055, 8)
        glPopMatrix()
    glPopMatrix()
    glPopMatrix()


def draw_bench(x, z, angle=0):
    """Banca de parque."""
    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(angle, 0, 1, 0)
    # Asiento
    glColor3f(0.55, 0.35, 0.15)
    glPushMatrix()
    glTranslatef(0, 0.42, 0)
    draw_box(1.0, 0.08, 0.38, 0.55, 0.35, 0.15)
    glPopMatrix()
    # Respaldo
    glPushMatrix()
    glTranslatef(0, 0.65, -0.15)
    draw_box(1.0, 0.35, 0.06, 0.55, 0.35, 0.15)
    glPopMatrix()
    # Patas
    glColor3f(0.3, 0.2, 0.1)
    for px in [-0.4, 0.4]:
        glPushMatrix()
        glTranslatef(px, 0.2, 0)
        draw_box(0.06, 0.42, 0.06, 0.3, 0.2, 0.1)
        glPopMatrix()
    glPopMatrix()


# ══════════════════════════════════════════════════════════════
#  RENDER DE TODA LA CIUDAD
# ══════════════════════════════════════════════════════════════

def render_city(t):
    draw_ground()

    # ── EDIFICIOS (14) con escalado pulsante en pares ──
    buildings = [
        # x,   z,    w,   h,    d,    r,    g,    b,    pulse
        # --- bloque norte ---
        (-8,  -8,  2.0,  8.0, 2.0, 0.50, 0.55, 0.65, True),
        (-5,  -9,  2.0,  5.5, 2.0, 0.60, 0.45, 0.40, False),
        (-11, -7,  2.0,  6.5, 2.0, 0.40, 0.50, 0.60, True),
        ( 7,  -8,  2.0,  9.0, 2.0, 0.65, 0.55, 0.45, False),
        ( 10, -7,  2.0,  5.0, 2.0, 0.55, 0.60, 0.50, True),
        ( 4,  -11, 2.0,  7.0, 2.0, 0.45, 0.48, 0.62, False),
        # --- bloque sur ---
        (-8,   8,  2.0,  6.0, 2.0, 0.50, 0.58, 0.55, True),
        ( 8,   8,  2.0,  8.5, 2.0, 0.62, 0.50, 0.48, False),
        # --- nuevos edificios ---
        (-13,  0,  2.0, 10.5, 2.0, 0.35, 0.42, 0.68, True),
        ( 13,  0,  2.0,  7.5, 2.0, 0.70, 0.48, 0.38, False),
        ( 0,  -14, 2.0, 11.0, 2.0, 0.42, 0.52, 0.58, True),
        ( 0,   13, 2.0,  6.0, 2.0, 0.58, 0.62, 0.44, False),
        (-5,   10, 2.0,  9.0, 2.0, 0.48, 0.45, 0.65, True),
        ( 5,   10, 2.0,  5.0, 2.0, 0.65, 0.52, 0.42, False),
    ]
    for bx,bz,bw,bh,bd,br,bg,bb,bp in buildings:
        draw_building(bx, bz, bw, bh, bd, br, bg, bb, t, bp)

    # ── CASAS (4) con colores variados ──
    houses = [
        # x,   z,   wall_r wall_g wall_b  roof_r roof_g roof_b
        (-3, -4,  0.95, 0.90, 0.75,  0.80, 0.18, 0.18),  # crema / rojo
        ( 3, -4,  0.70, 0.88, 0.78,  0.20, 0.45, 0.72),  # verde menta / azul
        (-3,  4,  0.88, 0.78, 0.95,  0.55, 0.30, 0.12),  # lila / marrón
        ( 3,  4,  0.98, 0.85, 0.65,  0.18, 0.55, 0.30),  # durazno / verde
    ]
    for hx, hz, wr, wg, wb, rr, rg, rb in houses:
        draw_house(hx, hz, t, wr, wg, wb, rr, rg, rb)

    # ── ÁRBOLES (6) ──
    for tx, tz in [(-1,-7),(1,-7),(-1,7),(1,7),(-6,0),(6,0)]:
        draw_tree(tx, tz)

    # ── POSTES DE LUZ (4) ──
    for lx, lz in [(-4,-4),(4,-4),(-4,4),(4,4)]:
        draw_lamp_post(lx, lz)

    # ── SEMÁFOROS (2) ──
    draw_traffic_light(-2, -2)
    draw_traffic_light( 2,  2)

    # ── BANCAS (2) ──
    draw_bench(-1.5, -1.2, 30)
    draw_bench( 1.5,  1.2, 210)

    # ── AUTO ROJO — translación en Z (loop) ──
    car_z = -12 + (t * 3.0) % 24   # va de -12 a +12 y repite
    draw_car(-5.5, car_z - 12, 0, 0.85, 0.15, 0.15)

    # ── AUTO AZUL — translación en X (loop, sentido contrario) ──
    car_x = 12 - (t * 2.5) % 24
    draw_car(car_x - 12, 5.5, 90, 0.15, 0.25, 0.80)

    # ── GLOBO — translación Y oscilante ──
    balloon_y = 2.0 * math.sin(t * 0.6)
    draw_balloon(-2, -2, balloon_y, t)

    # ── SOL/LUNA orbital ──
    draw_sun_moon(t)

    # ── AVIÓN orbital ──
    draw_plane(t)

    # ── NUBES (2) — translación X en loop ──
    cloud_x = -15 + (t * 1.5) % 30
    draw_cloud(cloud_x, -5, 9.0, t)
    draw_cloud(cloud_x - 12, 6, 8.0, t)


# ══════════════════════════════════════════════════════════════
#  MEDIAPIPE — procesar manos
# ══════════════════════════════════════════════════════════════

def process_hands(results, w, h):
    global angle_x, angle_y, zoom, pan_x, pan_y
    global prev_right, prev_left

    if not results.hand_landmarks:
        prev_right = None
        prev_left  = None
        return []

    all_kp = []
    for idx, hand_lm in enumerate(results.hand_landmarks):
        handedness = "Left"
        if results.handedness and idx < len(results.handedness):
            handedness = results.handedness[idx][0].category_name

        kp = [(int(lm.x*w), int(lm.y*h)) for lm in hand_lm]
        if len(kp) < 21:
            continue

        thumb  = kp[4]
        index  = kp[8]
        pinch  = math.hypot(index[0]-thumb[0], index[1]-thumb[1])
        nx, ny = index[0]/w, index[1]/h

        if handedness == "Right":
            if prev_right is not None:
                dx = (nx - prev_right[0]) * 120
                dy = (ny - prev_right[1]) * 120
                angle_y += dx
                angle_x += dy
            zoom = -5.0 - (pinch/w) * 30.0
            zoom = max(-40.0, min(-3.0, zoom))
            prev_right = (nx, ny)
        else:
            if prev_left is not None:
                dx = (nx - prev_left[0]) * 6
                dy = (ny - prev_left[1]) * 6
                pan_x += dx
                pan_y -= dy
            prev_left = (nx, ny)

        all_kp.append((kp, pinch))
    return all_kp


def draw_hand_overlay(frame, kp, pinch):
    for pt in kp:
        cv2.circle(frame, pt, 4, (0,200,255), cv2.FILLED)
    for c in HAND_CONNECTIONS:
        cv2.line(frame, kp[c[0]], kp[c[1]], (0,255,120), 2)
    if len(kp) >= 21:
        th, ix = kp[4], kp[8]
        cv2.line(frame, th, ix, (0,80,255), 2)
        mid = ((th[0]+ix[0])//2, (th[1]+ix[1])//2)
        cv2.putText(frame, f"{int(pinch)}px", mid,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,80,255), 2)


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

def main():
    global quadric

    if not os.path.exists(MODEL_PATH):
        print("="*60)
        print(f"ERROR: Falta el modelo '{MODEL_PATH}'")
        print("Descárgalo con:")
        print("  wget https://storage.googleapis.com/mediapipe-models/"
              "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task")
        print("="*60)
        sys.exit(1)

    if not glfw.init():
        print("No se pudo inicializar GLFW"); sys.exit(1)

    W, H = 1920, 1080
    window = glfw.create_window(W, H, "Ciudad 3D — Control con Manos", None, None)
    if not window:
        glfw.terminate(); sys.exit(1)

    glfw.make_context_current(window)
    glViewport(0, 0, W, H)

    # OpenGL config
    glClearColor(0.53, 0.81, 0.98, 1.0)   # cielo azul
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

    # Iluminación básica
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION,  [5.0, 10.0, 5.0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,   [1.0,  1.0, 0.9, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,   [0.35, 0.35, 0.35, 1.0])
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(55, W/H, 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW)

    # Cuádrica global
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)

    # MediaPipe
    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.IMAGE,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara"); glfw.terminate(); sys.exit(1)

    t0 = time.perf_counter()

    with HandLandmarker.create_from_options(options) as landmarker:
        while not glfw.window_should_close(window):
            if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
                break

            t = time.perf_counter() - t0

            # ── Captura + MediaPipe ──
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                fh, fw = frame.shape[:2]
                mp_img  = mp.Image(image_format=mp.ImageFormat.SRGB,
                                   data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                results = landmarker.detect(mp_img)
                hand_data = process_hands(results, fw, fh)

                if hand_data:
                    for kp, pinch in hand_data:
                        draw_hand_overlay(frame, kp, pinch)

                # HUD
                hud = [
                    "MANO DER: rotar vista",
                    "PINZA DER: zoom",
                    "MANO IZQ: mover camara",
                    "ESC: salir",
                ]
                for i, txt in enumerate(hud):
                    cv2.putText(frame, txt, (10, 22+i*22),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)
                cv2.imshow("MediaPipe — Camara", frame)
                cv2.waitKey(1)

            # ── Render 3D ──
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            # Cámara con gluLookAt + pan + zoom
            cd = abs(zoom)
            eye_x = cd*0.0 + pan_x
            eye_y = cd*0.35 + pan_y
            eye_z = cd
            gluLookAt(eye_x, eye_y, eye_z,
                      pan_x, pan_y, 0,
                      0, 1, 0)

            glRotatef(angle_x, 1, 0, 0)
            glRotatef(angle_y, 0, 1, 0)

            render_city(t)

            glfw.swap_buffers(window)
            glfw.poll_events()

    gluDeleteQuadric(quadric)
    cap.release()
    cv2.destroyAllWindows()
    glfw.terminate()


if __name__ == "__main__":
    main()