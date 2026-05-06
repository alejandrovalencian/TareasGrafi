import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
# 1. ELIMINAMOS la importación de GLUT

rotation = 0.0

def draw_sphere(radius, slices=30, stacks=30):
    """Función auxiliar para dibujar esferas usando GLU en lugar de GLUT"""
    quad = gluNewQuadric()
    gluSphere(quad, radius, slices, stacks)
    gluDeleteQuadric(quad) # Limpiamos memoria

def draw_eye():
    """Dibuja el ojo usando nuestra nueva función draw_sphere"""
    glPushMatrix()
    
    # Primera esfera (roja) a la izquierda
    glColor3f(0.85, 0.67, 0.65)  # Rojo
    glPushMatrix()
    glTranslatef(0.7, 0, 0)
    draw_sphere(0.54) # 2. CAMBIAMOS glutSolidSphere por draw_sphere
    glPopMatrix()

    glColor3f(1, 1, 1)  # Blanco
    glPushMatrix()
    glTranslatef(0.56, 0, 0)
    draw_sphere(0.6)
    glPopMatrix()
    
    # Segunda esfera (azul) a la derecha
    glColor3f(0.84, 0.85, 0.92)  # Azul
    glPushMatrix()
    glTranslatef(0.49, 0, 0)
    draw_sphere(0.55)
    glPopMatrix()

    glColor3f(0, 0, 0)  # Negro
    glPushMatrix()
    glTranslatef(0.3, 0, 0)
    draw_sphere(0.4)
    glPopMatrix()
    
    glPopMatrix()

def setup_lighting():
    """Configura iluminación básica"""
    #glEnable(GL_LIGHTING)
    #glEnable(GL_LIGHT0)
    #glEnable(GL_DEPTH_TEST)
    #glEnable(GL_COLOR_MATERIAL)
    
    light_position = [1.0, 1.0, 1.0, 0.2]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

def main():
    global rotation
    
    # 3. ELIMINAMOS glutInit()
    
    if not glfw.init():
        return

    window = glfw.create_window(1900, 1300, "Dos Esferas Simples", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    glClearColor(0.54, 0.72, 0.84, 1.0)
    setup_lighting()

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 800/600, 0.1, 100.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -5)
        
        # Rotar la escena
        rotation += 0.5
        glRotatef(rotation, 0, 1, 0)
        
        draw_eye()
        
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()