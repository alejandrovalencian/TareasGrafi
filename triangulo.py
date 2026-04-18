import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math

# Variables globales para rotación con mouse
rot_x = 0
rot_y = 0
last_x = 0
last_y = 0
dragging = False


def mouse_button(window, button, action, mods):
    global dragging
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            dragging = True
        elif action == glfw.RELEASE:
            dragging = False


def cursor_position(window, xpos, ypos):
    global last_x, last_y, rot_x, rot_y, dragging

    if dragging:
        dx = xpos - last_x
        dy = ypos - last_y

        rot_y += dx * 0.5
        rot_x += dy * 0.5

    last_x = xpos
    last_y = ypos


def draw_pyramid(t):
    speed = 8  # 🔥 velocidad de colores

    r = (math.sin(t * speed) + 1) / 2
    g = (math.sin(t * speed + 2) + 1) / 2
    b = (math.sin(t * speed + 4) + 1) / 2

    glBegin(GL_TRIANGLES)

    # Cara frontal
    glColor3f(r, 0, 0)
    glVertex3f(0, 0.5, 0)
    glColor3f(0, g, 0)
    glVertex3f(-0.5, -0.5, 0.5)
    glColor3f(0, 0, b)
    glVertex3f(0.5, -0.5, 0.5)

    # Cara derecha
    glColor3f(r, g, 0)
    glVertex3f(0, 0.5, 0)
    glColor3f(0, g, b)
    glVertex3f(0.5, -0.5, 0.5)
    glColor3f(r, 0, b)
    glVertex3f(0.5, -0.5, -0.5)

    # Cara trasera
    glColor3f(r, 0, b)
    glVertex3f(0, 0.5, 0)
    glColor3f(0, g, b)
    glVertex3f(0.5, -0.5, -0.5)
    glColor3f(r, g, 0)
    glVertex3f(-0.5, -0.5, -0.5)

    # Cara izquierda
    glColor3f(0, g, 0)
    glVertex3f(0, 0.5, 0)
    glColor3f(r, g, 0)
    glVertex3f(-0.5, -0.5, -0.5)
    glColor3f(0, 0, b)
    glVertex3f(-0.5, -0.5, 0.5)

    glEnd()

    # 🔥 Base con colores dinámicos
    glBegin(GL_QUADS)

    glColor3f(r, g, b)
    glVertex3f(-0.5, -0.5, 0.5)

    glColor3f(0, g, b)
    glVertex3f(0.5, -0.5, 0.5)

    glColor3f(r, 0, b)
    glVertex3f(0.5, -0.5, -0.5)

    glColor3f(r, g, 0)
    glVertex3f(-0.5, -0.5, -0.5)

    glEnd()


def main():
    global rot_x, rot_y

    if not glfw.init():
        return

    window = glfw.create_window(1500, 1000, "Pirámide 3D con Mouse", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    # Eventos de mouse
    glfw.set_cursor_pos_callback(window, cursor_position)
    glfw.set_mouse_button_callback(window, mouse_button)

    # Activar profundidad
    glEnable(GL_DEPTH_TEST)

    # Proyección perspectiva
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1500/1000, 0.1, 50.0)

    glMatrixMode(GL_MODELVIEW)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        t = glfw.get_time()

        glLoadIdentity()

        # Cámara
        glTranslatef(0.0, 0.0, -3)

        # Rotación con mouse
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)

        draw_pyramid(t)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()