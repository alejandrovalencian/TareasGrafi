import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

rotation = 0.0
light_mode = 0  # 0=Básica, 1=Múltiple, 2=Direccional, 3=Spotlight, 4=Colores

def draw_two_spheres():
    """Dibuja dos esferas simples formando un ojo"""
    glPushMatrix()
   
    # Esclerótica (blanco)
    glColor3f(1.0, 1.0, 1.0)
    glPushMatrix()
    glTranslatef(0.56, 0, 0)
    glutSolidSphere(0.6, 40, 40)
    glPopMatrix()
    
    # Iris (azul grisáceo)
    glColor3f(0.84, 0.85, 0.92)
    glPushMatrix()
    glTranslatef(0.49, 0, 0)
    glutSolidSphere(0.55, 35, 35)
    glPopMatrix()
    
    # Parte rosada del iris
    glColor3f(0.85, 0.67, 0.65)
    glPushMatrix()
    glTranslatef(0.7, 0, 0)
    glutSolidSphere(0.54, 35, 35)
    glPopMatrix()

    # Pupila (negro)
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0.3, 0, 0)
    glutSolidSphere(0.4, 30, 30)
    glPopMatrix()
    
    glPopMatrix()

def setup_lighting_basic():
    """
    MODO 0: LUZ BÁSICA
    - Una sola luz posicional blanca
    - Iluminación simple y uniforme
    """
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glDisable(GL_LIGHT1)
    glDisable(GL_LIGHT2)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    
    # Luz blanca básica arriba a la derecha
    light_position = [3.0, 2.0, 3.0, 1.0]  # W=1.0 → Luz posicional
    light_diffuse = [1.0, 1.0, 1.0, 1.0]   # Blanco
    light_ambient = [0.3, 0.3, 0.3, 1.0]   # Ambiente gris claro
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)

def setup_lighting_multiple():
    """
    MODO 1: LUCES MÚLTIPLES
    - Luz principal (blanca) desde arriba
    - Luz de relleno (azul suave) desde atrás
    - Luz de acento (naranja) lateral
    Simula un estudio fotográfico profesional
    """
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    
    # LIGHT0: Luz principal (Key Light)
    # Arriba adelante, blanca brillante
    light0_position = [3.0, 4.0, 3.0, 1.0]
    light0_diffuse = [1.0, 1.0, 1.0, 1.0]    # Blanco brillante
    light0_ambient = [0.2, 0.2, 0.2, 1.0]    # Ambiente suave
    light0_specular = [1.0, 1.0, 1.0, 1.0]   # Brillos blancos
    
    glLightfv(GL_LIGHT0, GL_POSITION, light0_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light0_diffuse)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light0_ambient)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light0_specular)
    
    # LIGHT1: Luz de relleno (Fill Light)
    # Atrás izquierda, azul suave
    light1_position = [-2.0, 1.0, -3.0, 1.0]
    light1_diffuse = [0.3, 0.4, 0.6, 1.0]    # Azul suave
    light1_ambient = [0.1, 0.1, 0.2, 1.0]    # Ambiente azulado
    
    glLightfv(GL_LIGHT1, GL_POSITION, light1_position)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diffuse)
    glLightfv(GL_LIGHT1, GL_AMBIENT, light1_ambient)
    
    # LIGHT2: Luz de acento (Rim Light)
    # Lateral derecha, naranja cálida
    light2_position = [4.0, 0.0, 1.0, 1.0]
    light2_diffuse = [0.9, 0.6, 0.3, 1.0]    # Naranja cálido
    
    glLightfv(GL_LIGHT2, GL_POSITION, light2_position)
    glLightfv(GL_LIGHT2, GL_DIFFUSE, light2_diffuse)

def setup_lighting_directional():
    """
    MODO 2: LUZ DIRECCIONAL
    - Como la luz del sol (infinita)
    - Todos los rayos son paralelos
    - W = 0.0 indica que es direccional
    Útil para simular luz solar o luz muy lejana
    """
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glDisable(GL_LIGHT1)
    glDisable(GL_LIGHT2)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    
    # Dirección de la luz (no posición)
    # W = 0.0 → Luz direccional (como el sol)
    light_direction = [1.0, -1.0, 1.0, 0.0]  # ¡W=0.0!
    light_diffuse = [1.0, 0.95, 0.8, 1.0]    # Amarillo cálido (sol)
    light_ambient = [0.4, 0.4, 0.4, 1.0]     # Ambiente más fuerte
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_direction)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)

def setup_lighting_spotlight():
    """
    MODO 3: SPOTLIGHT (Foco)
    - Luz cónica concentrada
    - Como un reflector de teatro
    - Tiene dirección, ángulo y atenuación
    """
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glDisable(GL_LIGHT1)
    glDisable(GL_LIGHT2)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    
    # Posición del foco (arriba)
    light_position = [0.0, 4.0, 2.0, 1.0]
    light_diffuse = [1.0, 1.0, 1.0, 1.0]
    light_ambient = [0.1, 0.1, 0.1, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    
    # Dirección hacia donde apunta el foco (hacia el objeto)
    spot_direction = [0.0, -1.0, -0.5]  # Apunta hacia abajo y adelante
    
    # Ángulo del cono (30 grados)
    spot_cutoff = 30.0
    
    # Concentración del haz (0=difuso, 128=muy concentrado)
    spot_exponent = 20.0
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, spot_direction)
    glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, spot_cutoff)
    glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, spot_exponent)
    
    # Atenuación (cómo disminuye con la distancia)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.01)

def setup_lighting_colored():
    """
    MODO 4: LUCES DE COLORES
    - Múltiples luces con colores diferentes
    - Crea efectos artísticos/dramáticos
    Útil para escenas nocturnas, discotecas, efectos especiales
    """
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    
    # LIGHT0: Luz roja (izquierda)
    light0_position = [-3.0, 1.0, 2.0, 1.0]
    light0_diffuse = [1.0, 0.2, 0.2, 1.0]    # Rojo intenso
    glLightfv(GL_LIGHT0, GL_POSITION, light0_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light0_diffuse)
    
    # LIGHT1: Luz verde (derecha)
    light1_position = [3.0, 1.0, 2.0, 1.0]
    light1_diffuse = [0.2, 1.0, 0.3, 1.0]    # Verde brillante
    glLightfv(GL_LIGHT1, GL_POSITION, light1_position)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diffuse)
    
    # LIGHT2: Luz azul (arriba)
    light2_position = [0.0, 3.0, 0.0, 1.0]
    light2_diffuse = [0.3, 0.3, 1.0, 1.0]    # Azul intenso
    glLightfv(GL_LIGHT2, GL_POSITION, light2_position)
    glLightfv(GL_LIGHT2, GL_DIFFUSE, light2_diffuse)
    
    # Ambiente muy oscuro para resaltar colores
    light_ambient = [0.05, 0.05, 0.05, 1.0]
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)

def setup_lighting():
    """Selecciona el modo de iluminación según light_mode"""
    if light_mode == 0:
        setup_lighting_basic()
    elif light_mode == 1:
        setup_lighting_multiple()
    elif light_mode == 2:
        setup_lighting_directional()
    elif light_mode == 3:
        setup_lighting_spotlight()
    elif light_mode == 4:
        setup_lighting_colored()

def draw_light_indicators():
    """Dibuja pequeñas esferas mostrando la posición de las luces"""
    glDisable(GL_LIGHTING)
    
    if light_mode == 0:
        # Luz básica
        glColor3f(1.0, 1.0, 0.0)
        glPushMatrix()
        glTranslatef(3.0, 2.0, 3.0)
        glutWireSphere(0.1, 8, 8)
        glPopMatrix()
    
    elif light_mode == 1:
        # Múltiples luces
        glColor3f(1.0, 1.0, 1.0)  # Blanca
        glPushMatrix()
        glTranslatef(3.0, 4.0, 3.0)
        glutWireSphere(0.1, 8, 8)
        glPopMatrix()
        
        glColor3f(0.3, 0.4, 0.6)  # Azul
        glPushMatrix()
        glTranslatef(-2.0, 1.0, -3.0)
        glutWireSphere(0.1, 8, 8)
        glPopMatrix()
        
        glColor3f(0.9, 0.6, 0.3)  # Naranja
        glPushMatrix()
        glTranslatef(4.0, 0.0, 1.0)
        glutWireSphere(0.1, 8, 8)
        glPopMatrix()
    
    elif light_mode == 3:
        # Spotlight
        glColor3f(1.0, 1.0, 0.0)
        glPushMatrix()
        glTranslatef(0.0, 4.0, 2.0)
        glutWireSphere(0.15, 8, 8)
        glPopMatrix()
    
    elif light_mode == 4:
        # Luces de colores
        glColor3f(1.0, 0.0, 0.0)  # Roja
        glPushMatrix()
        glTranslatef(-3.0, 1.0, 2.0)
        glutWireSphere(0.1, 8, 8)
        glPopMatrix()
        
        glColor3f(0.0, 1.0, 0.0)  # Verde
        glPushMatrix()
        glTranslatef(3.0, 1.0, 2.0)
        glutWireSphere(0.1, 8, 8)
        glPopMatrix()
        
        glColor3f(0.0, 0.5, 1.0)  # Azul
        glPushMatrix()
        glTranslatef(0.0, 3.0, 0.0)
        glutWireSphere(0.1, 8, 8)
        glPopMatrix()
    
    glEnable(GL_LIGHTING)

def draw_text_info():
    """Muestra información del modo de iluminación"""
    modes = [
        "0: LUZ BÁSICA - Una luz blanca simple",
        "1: LUCES MÚLTIPLES - Key + Fill + Rim",
        "2: LUZ DIRECCIONAL - Como el sol (infinita)",
        "3: SPOTLIGHT - Foco concentrado",
        "4: LUCES DE COLORES - RGB artístico"
    ]
    
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)
    # Nota: Para texto necesitarías glutBitmapCharacter o una librería de texto
    glEnable(GL_LIGHTING)

def key_callback(window, key, scancode, action, mods):
    """Manejo de teclado para cambiar modos"""
    global light_mode
    
    if action == glfw.PRESS:
        if key == glfw.KEY_0:
            light_mode = 0
            print("\n>>> MODO 0: LUZ BÁSICA")
            print("Una luz posicional blanca simple")
        elif key == glfw.KEY_1:
            light_mode = 1
            print("\n>>> MODO 1: LUCES MÚLTIPLES")
            print("Key Light (blanca) + Fill (azul) + Rim (naranja)")
        elif key == glfw.KEY_2:
            light_mode = 2
            print("\n>>> MODO 2: LUZ DIRECCIONAL")
            print("Luz infinita como el sol (W=0)")
        elif key == glfw.KEY_3:
            light_mode = 3
            print("\n>>> MODO 3: SPOTLIGHT")
            print("Foco concentrado con ángulo de 30°")
        elif key == glfw.KEY_4:
            light_mode = 4
            print("\n>>> MODO 4: LUCES DE COLORES")
            print("Roja (izq) + Verde (der) + Azul (arriba)")
        
        setup_lighting()

def main():
    global rotation
    
    glutInit()
    
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Tipos de Iluminación OpenGL", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    glClearColor(0.54, 0.72, 0.84, 1.0)
    setup_lighting()
    
    # Configurar material para brillos
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 100.0)

    print("=" * 60)
    print("MODOS DE ILUMINACIÓN EN OPENGL")
    print("=" * 60)
    print("Presiona las teclas numéricas para cambiar:")
    print("  0 - Luz Básica")
    print("  1 - Luces Múltiples (3 luces)")
    print("  2 - Luz Direccional (sol)")
    print("  3 - Spotlight (foco)")
    print("  4 - Luces de Colores (RGB)")
    print("=" * 60)

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
        glRotatef(20, 1, 0, 0)
        
        draw_two_spheres()
        draw_light_indicators()
        
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()