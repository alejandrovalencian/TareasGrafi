import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt
import sys

def init():
    glClearColor(0.5, 0.8, 1.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, 1.0, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def draw_cube():
    glBegin(GL_QUADS)
    glColor3f(0.8, 0.5, 0.2)

    glVertex3f(-1, 0, 1)
    glVertex3f(1, 0, 1)
    glVertex3f(1, 1, 1)
    glVertex3f(-1, 1, 1)

    glVertex3f(-1, 0, -1)
    glVertex3f(1, 0, -1)
    glVertex3f(1, 1, -1)
    glVertex3f(-1, 1, -1)

    glVertex3f(-1, 0, -1)
    glVertex3f(-1, 0, 1)
    glVertex3f(-1, 1, 1)
    glVertex3f(-1, 1, -1)

    glVertex3f(1, 0, -1)
    glVertex3f(1, 0, 1)
    glVertex3f(1, 1, 1)
    glVertex3f(1, 1, -1)

    glColor3f(0.9, 0.6, 0.3)
    glVertex3f(-1, 1, -1)
    glVertex3f(1, 1, -1)
    glVertex3f(1, 1, 1)
    glVertex3f(-1, 1, 1)

    glColor3f(0.6, 0.4, 0.2)
    glVertex3f(-1, 0, -1)
    glVertex3f(1, 0, -1)
    glVertex3f(1, 0, 1)
    glVertex3f(-1, 0, 1)
    glEnd()

def draw_roof():
    glBegin(GL_TRIANGLES)
    glColor3f(0.9, 0.1, 0.1)

    glVertex3f(-1, 1, 1)
    glVertex3f(1, 1, 1)
    glVertex3f(0, 2, 0)

    glVertex3f(-1, 1, -1)
    glVertex3f(1, 1, -1)
    glVertex3f(0, 2, 0)

    glVertex3f(-1, 1, -1)
    glVertex3f(-1, 1, 1)
    glVertex3f(0, 2, 0)

    glVertex3f(1, 1, -1)
    glVertex3f(1, 1, 1)
    glVertex3f(0, 2, 0)
    glEnd()

def draw_ground():
    glBegin(GL_QUADS)
    glColor3f(0.3, 0.3, 0.3)

    glVertex3f(-10, 0, 10)
    glVertex3f(10, 0, 10)
    glVertex3f(10, 0, -10)
    glVertex3f(-10, 0, -10)
    glEnd()

def draw_house():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(4, 3, 8,
              0, 1, 0,
              0, 1, 0)

    draw_ground()

    # ---- INCLINACIÓN REAL ----
    glPushMatrix()

    glTranslatef(0, 1, 0)      # centro
    glRotatef(45, 1, 0, 0)     # inclinar sobre eje X 🔥
    glTranslatef(0, -1, 0)

    draw_cube()
    draw_roof()

    glPopMatrix()
    # -------------------------

    glfw.swap_buffers(window)

def main():
    global window

    if not glfw.init():
        sys.exit()

    window = glfw.create_window(800, 600, "Casa INCLINADA", None, None)
    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)
    glViewport(0, 0, 800, 600)
    init()

    while not glfw.window_should_close(window):
        draw_house()
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()