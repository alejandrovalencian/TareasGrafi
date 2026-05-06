import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

rotation = 0.0

def draw_sphere(radius, slices=30, stacks=30):
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)  # Misión 2
    gluSphere(quad, radius, slices, stacks)
    gluDeleteQuadric(quad)

# 🔥 Misión 3: función de materiales
def set_material(ambient, diffuse, specular, shininess, face=GL_FRONT):
    glMaterialfv(face, GL_AMBIENT, ambient)
    glMaterialfv(face, GL_DIFFUSE, diffuse)
    glMaterialfv(face, GL_SPECULAR, specular)
    glMaterialf(face, GL_SHININESS, shininess)

def draw_eye():
    glPushMatrix()

    # Piel (difuso cálido, especular suave)
    glPushMatrix()
    set_material(
        ambient=[0.85, 0.67, 0.65, 1.0],
        diffuse=[0.85, 0.67, 0.65, 1.0],
        specular=[0.2, 0.2, 0.2, 1.0],
        shininess=10
    )
    glTranslatef(0.7, 0, 0)
    draw_sphere(0.54)
    glPopMatrix()

    # Esclerótica (blanco brillante)
    glPushMatrix()
    set_material(
        ambient=[1.0, 1.0, 1.0, 1.0],
        diffuse=[1.0, 1.0, 1.0, 1.0],
        specular=[1.0, 1.0, 1.0, 1.0],
        shininess=80
    )
    glTranslatef(0.56, 0, 0)
    draw_sphere(0.6)
    glPopMatrix()

    # Iris (brillo medio)
    glPushMatrix()
    set_material(
        ambient=[0.84, 0.85, 0.92, 1.0],
        diffuse=[0.84, 0.85, 0.92, 1.0],
        specular=[0.4, 0.4, 0.4, 1.0],
        shininess=32
    )
    glTranslatef(0.49, 0, 0)
    draw_sphere(0.55)
    glPopMatrix()

    # Pupila (sin brillo)
    glPushMatrix()
    set_material(
        ambient=[0.0, 0.0, 0.0, 1.0],
        diffuse=[0.0, 0.0, 0.0, 1.0],
        specular=[0.0, 0.0, 0.0, 1.0],
        shininess=5
    )
    glTranslatef(0.3, 0, 0)
    draw_sphere(0.4)
    glPopMatrix()

    glPopMatrix()

def setup_lighting():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)

    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 2.0, 1.0])

def main():
    global rotation

    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Ojo 3D - Misión 3", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    glClearColor(0.54, 0.72, 0.84, 1.0)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 800/600, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -5)

        setup_lighting()

        rotation += 0.5
        glRotatef(rotation, 0, 1, 0)

        draw_eye()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()