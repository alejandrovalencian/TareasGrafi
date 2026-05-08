import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math

rotation = 0.0
light_mode = 0  # 0=Básica, 1=Múltiple, 2=Direccional, 3=Spotlight, 4=Colores

# --- FUNCIONES AUXILIARES PARA EVITAR USAR GLUT ---

def draw_sphere(radius, slices, stacks):
    """Dibuja una esfera sólida usando GLU (Seguro para Windows)"""
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluSphere(quadric, radius, slices, stacks)
    gluDeleteQuadric(quadric)

def draw_wire_sphere(radius, slices, stacks):
    """Dibuja una esfera de alambre usando GLU (Para los indicadores de luz)"""
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_LINE) # Modo alambre
    gluSphere(quadric, radius, slices, stacks)
    gluDeleteQuadric(quadric)

# --------------------------------------------------

def draw_two_spheres():
    """Dibuja las esferas formando el ojo"""
    glPushMatrix()
    
    # Esclerótica (blanco)
    glColor3f(1.0, 1.0, 1.0)
    glPushMatrix()
    glTranslatef(0.56, 0, 0)
    draw_sphere(0.6, 40, 40)
    glPopMatrix()
    
    # Iris (azul grisáceo)
    glColor3f(0.84, 0.85, 0.92)
    glPushMatrix()
    glTranslatef(0.49, 0, 0)
    draw_sphere(0.55, 35, 35)
    glPopMatrix()
    
    # Parte rosada del iris
    glColor3f(0.85, 0.67, 0.65)
    glPushMatrix()
    glTranslatef(0.7, 0, 0)
    draw_sphere(0.54, 35, 35)
    glPopMatrix()

    # Pupila (negro)
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0.3, 0, 0)
    draw_sphere(0.4, 30, 30)
    glPopMatrix()
    
    glPopMatrix()

# --- CONFIGURACIONES DE ILUMINACIÓN ---

def setup_lighting_basic():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glDisable(GL_LIGHT1)
    glDisable(GL_LIGHT2)
    
    light_position = [3.0, 2.0, 3.0, 1.0]
    light_diffuse = [1.0, 1.0, 1.0, 1.0]
    light_ambient = [0.3, 0.3, 0.3, 1.0]
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)

def setup_lighting_multiple():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0); glEnable(GL_LIGHT1); glEnable(GL_LIGHT2)
    
    glLightfv(GL_LIGHT0, GL_POSITION, [3.0, 4.0, 3.0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    
    glLightfv(GL_LIGHT1, GL_POSITION, [-2.0, 1.0, -3.0, 1.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.3, 0.4, 0.6, 1.0])
    
    glLightfv(GL_LIGHT2, GL_POSITION, [4.0, 0.0, 1.0, 1.0])
    glLightfv(GL_LIGHT2, GL_DIFFUSE, [0.9, 0.6, 0.3, 1.0])

def setup_lighting_directional():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glDisable(GL_LIGHT1); glDisable(GL_LIGHT2)
    
    # W=0.0 es clave para luz direccional (como el sol)
    light_direction = [1.0, -1.0, 1.0, 0.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_direction)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.95, 0.8, 1.0])

def setup_lighting_spotlight():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glDisable(GL_LIGHT1); glDisable(GL_LIGHT2)
    
    light_position = [0.0, 4.0, 2.0, 1.0]
    spot_direction = [0.0, -1.0, -0.5]
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, spot_direction)
    glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 30.0) # Ángulo del cono
    glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 20.0)

def setup_lighting_colored():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0); glEnable(GL_LIGHT1); glEnable(GL_LIGHT2)
    
    glLightfv(GL_LIGHT0, GL_POSITION, [-3.0, 1.0, 2.0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.2, 0.2, 1.0]) # Rojo
    
    glLightfv(GL_LIGHT1, GL_POSITION, [3.0, 1.0, 2.0, 1.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.2, 1.0, 0.3, 1.0]) # Verde
    
    glLightfv(GL_LIGHT2, GL_POSITION, [0.0, 3.0, 0.0, 1.0])
    glLightfv(GL_LIGHT2, GL_DIFFUSE, [0.3, 0.3, 1.0, 1.0]) # Azul

def setup_lighting():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    if light_mode == 0: setup_lighting_basic()
    elif light_mode == 1: setup_lighting_multiple()
    elif light_mode == 2: setup_lighting_directional()
    elif light_mode == 3: setup_lighting_spotlight()
    elif light_mode == 4: setup_lighting_colored()

def draw_light_indicators():
    """Dibuja pequeñas esferas de alambre donde están las luces"""
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 0.0)
    
    if light_mode == 0:
        glPushMatrix(); glTranslatef(3.0, 2.0, 3.0); draw_wire_sphere(0.1, 8, 8); glPopMatrix()
    elif light_mode == 1:
        glPushMatrix(); glTranslatef(3.0, 4.0, 3.0); draw_wire_sphere(0.1, 8, 8); glPopMatrix()
        glPushMatrix(); glTranslatef(-2.0, 1.0, -3.0); draw_wire_sphere(0.1, 8, 8); glPopMatrix()
    elif light_mode == 4:
        glColor3f(1, 0, 0); glPushMatrix(); glTranslatef(-3.0, 1.0, 2.0); draw_wire_sphere(0.1, 8, 8); glPopMatrix()
        glColor3f(0, 1, 0); glPushMatrix(); glTranslatef(3.0, 1.0, 2.0); draw_wire_sphere(0.1, 8, 8); glPopMatrix()
        glColor3f(0, 0, 1); glPushMatrix(); glTranslatef(0.0, 3.0, 0.0); draw_wire_sphere(0.1, 8, 8); glPopMatrix()
    
    glEnable(GL_LIGHTING)

def key_callback(window, key, scancode, action, mods):
    global light_mode
    if action == glfw.PRESS:
        if glfw.KEY_0 <= key <= glfw.KEY_4:
            light_mode = key - glfw.KEY_0
            print(f"Cambio a Modo de Luz: {light_mode}")
            setup_lighting()

def main():
    global rotation
    
    # Inicializar GLFW
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Tipos de Iluminacion OpenGL (Sin GLUT)", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    # Configuración inicial de OpenGL
    glClearColor(0.1, 0.1, 0.1, 1.0) # Fondo oscuro para ver mejor las luces
    setup_lighting()
    
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 100.0)

    print("Controles: Teclas 0, 1, 2, 3, 4 para cambiar modos de iluminacion.")

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 800/600, 0.1, 100.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -5)
        
        rotation += 0.5
        glRotatef(rotation, 0, 1, 0)
        glRotatef(20, 1, 0, 0)
        
        draw_two_spheres()
        draw_light_indicators()
        
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()