import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt, gluNewQuadric, gluCylinder, gluSphere
import sys

# ------------------ CÁMARA ------------------
camera_pos = [4.0, 3.0, 8.0]
camera_target = [0.0, 1.0, 0.0]
camera_up = [0.0, 1.0, 0.0]

camera_speed = 0.2
keys = {}

# ------------------ MOUSE ------------------
mouse_pressed = False
last_mouse_x = 0
last_mouse_y = 0

# ------------------ INIT ------------------
def init():
    glClearColor(0.5, 0.8, 1.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, 1200/800, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

# ------------------ DIBUJO ------------------
def draw_trunk():
    glPushMatrix()
    glColor3f(0.6, 0.3, 0.1)
    glRotatef(-90, 1, 0, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.3, 0.3, 2.0, 32, 32)
    glPopMatrix()

def draw_foliage():
    glPushMatrix()
    glColor3f(0.1, 0.8, 0.1)
    glTranslatef(0.0, 2.0, 0.0)
    quadric = gluNewQuadric()
    gluSphere(quadric, 1.0, 32, 32)

    glColor3f(1, 0, 0)
    glTranslatef(0.0, 1.0, 0.0)
    gluSphere(quadric, 1.0, 32, 32)
    glPopMatrix()

def draw_foliage2():
    glPushMatrix()
    glColor3f(0.1, 0.6, 0.0)
    glTranslatef(0.0, 2.5, 0.0)
    quadric = gluNewQuadric()
    gluSphere(quadric, 1.0, 32, 32)
    glPopMatrix()

def draw_ground():
    glBegin(GL_QUADS)
    glColor3f(0.3, 0.3, 0.3)
    glVertex3f(-10, 0, 10)
    glVertex3f(10, 0, 10)
    glVertex3f(10, 0, -10)
    glVertex3f(-10, 0, -10)
    glEnd()

def draw_scene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
              camera_target[0], camera_target[1], camera_target[2],
              camera_up[0], camera_up[1], camera_up[2])

    draw_ground()
    draw_trunk()
    draw_foliage()
    draw_foliage2()

    glfw.swap_buffers(window)

# ------------------ INPUT ------------------
def process_input():
    global camera_pos

    if keys.get(glfw.KEY_W):
        camera_pos[2] -= camera_speed
    if keys.get(glfw.KEY_S):
        camera_pos[2] += camera_speed
    if keys.get(glfw.KEY_A):
        camera_pos[0] -= camera_speed
    if keys.get(glfw.KEY_D):
        camera_pos[0] += camera_speed
    if keys.get(glfw.KEY_SPACE):
        camera_pos[1] += camera_speed
    if keys.get(glfw.KEY_LEFT_SHIFT):
        camera_pos[1] -= camera_speed

def key_callback(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        keys[key] = True
    elif action == glfw.RELEASE:
        keys[key] = False

# ------------------ MOUSE ------------------
def mouse_button_callback(window, button, action, mods):
    global mouse_pressed

    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            mouse_pressed = True
        elif action == glfw.RELEASE:
            mouse_pressed = False

def cursor_callback(window, xpos, ypos):
    global last_mouse_x, last_mouse_y, camera_pos

    if mouse_pressed:
        dx = xpos - last_mouse_x
        dy = ypos - last_mouse_y

        sensibilidad = 0.01

        # mover como si arrastraras la escena
        camera_pos[0] -= dx * sensibilidad
        camera_pos[2] += dy * sensibilidad

    last_mouse_x = xpos
    last_mouse_y = ypos

# ------------------ MAIN ------------------
def main():
    global window

    if not glfw.init():
        sys.exit()

    window = glfw.create_window(1200, 800, "Mover con Mouse (Drag)", None, None)
    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    init()

    while not glfw.window_should_close(window):
        process_input()
        draw_scene()
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()