import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math

# -------- ROTACIÓN --------
rot_x = 0
rot_y = 0
lastX, lastY = 400, 300
dragging = False

def mouse_button_callback(window, button, action, mods):
    global dragging
    if button == glfw.MOUSE_BUTTON_LEFT:
        dragging = (action == glfw.PRESS)

def cursor_callback(window, xpos, ypos):
    global lastX, lastY, rot_x, rot_y, dragging

    if dragging:
        dx = xpos - lastX
        dy = ypos - lastY

        rot_y += dx * 0.3
        rot_x += dy * 0.3

    lastX, lastY = xpos, ypos

# -------- IRIS VERDE --------
def draw_iris():
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(61):
        angle = 2 * math.pi * i / 60
        x = math.cos(angle)
        y = math.sin(angle)

        glColor3f(0.0, 0.6, 0.1)   # verde oscuro
        glVertex3f(0.35*x, 0.35*y, 0)

        glColor3f(0.5, 1.0, 0.5)   # verde claro
        glVertex3f(0.15*x, 0.15*y, 0)
    glEnd()

# -------- OJO --------
def draw_eye():
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)

    # 👁️ ESCLERA BLANCO PURO
    glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
    glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1, 1, 1, 1])
    glMaterialf(GL_FRONT, GL_SHININESS, 120)
    gluSphere(quad, 1.0, 60, 60)

    # 🟢 IRIS
    glPushMatrix()
    glTranslatef(0, 0, 0.99)
    glDisable(GL_LIGHTING)
    draw_iris()
    glEnable(GL_LIGHTING)
    glPopMatrix()

    # 🧿 PUPILA
    glMaterialfv(GL_FRONT, GL_DIFFUSE, [0, 0, 0, 1])
    glPushMatrix()
    glTranslatef(0, 0, 1.0)
    gluSphere(quad, 0.15, 40, 40)
    glPopMatrix()

    # ✨ BRILLO
    glMaterialfv(GL_FRONT, GL_DIFFUSE, [1, 1, 1, 1])
    glPushMatrix()
    glTranslatef(0.2, 0.2, 1.1)
    gluSphere(quad, 0.05, 20, 20)
    glPopMatrix()

# -------- MAIN --------
def main():
    if not glfw.init():
        return

    window = glfw.create_window(1600, 1250, "Ojo Blanco Realista", None, None)
    glfw.make_context_current(window)

    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)

    # 💡 LUZ CONTROLADA (clave para blanco real)
    glLightfv(GL_LIGHT0, GL_POSITION, [5, 5, 5, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1])

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 800/600, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)

        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)

        draw_eye()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()