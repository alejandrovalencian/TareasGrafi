#!/usr/bin/env python3

import glfw

from OpenGL.GL import *
from OpenGL.GLU import *

angle = 0.0

quadric = None


def draw_sphere():

    global quadric

    if quadric is None:
        quadric = gluNewQuadric()

    gluSphere(
        quadric,
        1.0,
        40,
        40
    )


def setup_light():

    glEnable(GL_LIGHTING)

    glEnable(GL_LIGHT0)

    glEnable(GL_COLOR_MATERIAL)

    glColorMaterial(
        GL_FRONT_AND_BACK,
        GL_AMBIENT_AND_DIFFUSE
    )

    ambient = [
        0.2,
        0.2,
        0.2,
        1.0
    ]

    diffuse = [
        1.0,
        1.0,
        1.0,
        1.0
    ]

    glLightfv(
        GL_LIGHT0,
        GL_AMBIENT,
        ambient
    )

    glLightfv(
        GL_LIGHT0,
        GL_DIFFUSE,
        diffuse
    )


def render_scene():

    global angle

    glMatrixMode(GL_MODELVIEW)

    glLoadIdentity()

    glTranslatef(
        0.0,
        0.0,
        -5.0
    )

    light_position = [
        2.0,
        3.0,
        2.0,
        1.0
    ]

    glLightfv(
        GL_LIGHT0,
        GL_POSITION,
        light_position
    )

    glRotatef(
        angle,
        0.0,
        1.0,
        0.0
    )

    glColor3f(
        0.3,
        0.7,
        1.0
    )

    draw_sphere()


glfw.init()

window = glfw.create_window(
    800,
    600,
    "Mision 3",
    None,
    None
)

glfw.make_context_current(window)

glEnable(GL_DEPTH_TEST)

setup_light()

while not glfw.window_should_close(window):

    width, height = glfw.get_framebuffer_size(window)

    glViewport(
        0,
        0,
        width,
        height
    )

    glClearColor(
        0.08,
        0.08,
        0.12,
        1.0
    )

    glClear(
        GL_COLOR_BUFFER_BIT |
        GL_DEPTH_BUFFER_BIT
    )

    glMatrixMode(GL_PROJECTION)

    glLoadIdentity()

    gluPerspective(
        45.0,
        width / float(height),
        0.1,
        100.0
    )

    render_scene()

    angle += 0.6

    glfw.swap_buffers(window)

    glfw.poll_events()

glfw.terminate()