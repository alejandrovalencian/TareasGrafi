import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math

rotation = 0.0
eye_mode = 0  # 0=uno, 1=dos, 2=cuadrícula, 3=círculo

# --- FUNCIÓN AUXILIAR PARA EVITAR USAR GLUT ---
def draw_sphere(radius, slices, stacks):
    """Dibuja una esfera sólida usando GLU (Seguro para Windows)"""
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluSphere(quadric, radius, slices, stacks)
    gluDeleteQuadric(quadric)
# ----------------------------------------------

def draw_eye():
    """Dibuja un ojo completo"""
    glPushMatrix()
    
    glColor3f(0.85, 0.67, 0.65)
    glPushMatrix()
    glTranslatef(0.7, 0, 0)
    draw_sphere(0.54, 30, 30)
    glPopMatrix()

    glColor3f(1, 1, 1)
    glPushMatrix()
    glTranslatef(0.56, 0, 0)
    draw_sphere(0.6, 30, 30)
    glPopMatrix()
    
    glColor3f(0 , 0, 1)
    glPushMatrix()
    glTranslatef(0.49, 0, 0)
    draw_sphere(0.55, 30, 30)
    glPopMatrix()

    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(0.3, 0, 0)
    draw_sphere(0.4, 30, 30)
    glPopMatrix()
    
    glPopMatrix()

def draw_one_eye():
    """Un solo ojo"""
    draw_eye()

def draw_two_eyes():
    """Dos ojos como cara"""
    glPushMatrix()
    glTranslatef(-1.2, 0, 0)
    draw_eye()
    draw_eye()
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, -1.5, 0)
    draw_eye()
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 1.5, 0)
    draw_eye()
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(1.2, 0, 0)
    draw_eye()
    glPopMatrix()

def draw_grid_eyes():
    """Cuadrícula de ojos"""
    for row in range(3):
        for col in range(3):
            x = (col - 1) * 1.8
            y = (row - 1) * 1.8
            glPushMatrix()
            glTranslatef(x, y, 0)
            glScalef(0.5, 0.5, 0.5)
            draw_eye()
            glPopMatrix()

def draw_circle_eyes():
    """Círculo de ojos (araña)"""
    num_eyes = 100
    radius = 2
    
    for i in range(num_eyes):
        angle = i * (360.0 / num_eyes)
        rad = math.radians(angle)
        
        x = radius * math.cos(rad)
        y = radius * math.sin(rad)
        
        glPushMatrix()
        glTranslatef(x, y, 0)
        glRotatef(angle + 90, 0, 0, 1)
        glScalef(0.4, 0.4, 0.4)
        draw_eye()
        glPopMatrix()

def draw_eyes():
    """Dibuja según el modo actual"""
    if eye_mode == 0:
        draw_one_eye()
    elif eye_mode == 1:
        draw_two_eyes()
    elif eye_mode == 2:
        draw_grid_eyes()
    elif eye_mode == 3:
        draw_circle_eyes()

def setup_lighting():
    """Configura iluminación básica"""
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    
    light_position = [2.0, 3.0, 2.0, 1.0]
    light_ambient = [0.4, 0.4, 0.4, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)

def key_callback(window, key, scancode, action, mods):
    """Cambiar entre modos con teclas"""
    global eye_mode
    
    if action == glfw.PRESS:
        if key == glfw.KEY_1:
            eye_mode = 0
            print("Modo: UN OJO")
        elif key == glfw.KEY_2:
            eye_mode = 1
            print("Modo: DOS OJOS (cara)")
        elif key == glfw.KEY_3:
            eye_mode = 2
            print("Modo: CUADRÍCULA 3x3")
        elif key == glfw.KEY_4:
            eye_mode = 3
            print("Modo: CÍRCULO (araña)")

def main():
    global rotation
    
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Múltiples Ojos (Sin GLUT)", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    glClearColor(0.54, 0.72, 0.84, 1.0)
    setup_lighting()

    print("=" * 50)
    print("CONTROLES:")
    print("  1 - Un ojo")
    print("  2 - Dos ojos (cara)")
    print("  3 - Cuadrícula 3x3")
    print("  4 - Círculo (araña)")
    print("=" * 50)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(30, 800/600, 0.1, 100.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -8)  # Más lejos para ver todos
        
        rotation += 0.3
        glRotatef(rotation, 0, 1, 0)
        glRotatef(20, 1, 0, 0)
        
        draw_eyes()
        
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()