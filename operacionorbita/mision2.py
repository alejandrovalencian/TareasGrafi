#!/usr/bin/env python3

from __future__ import annotations

import math
import glfw

from OpenGL.GL import *
from OpenGL.GLU import *

angle = 0.0
mode = 1

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


def render_scene(radius):

    global angle

    glMatrixMode(GL_MODELVIEW)

    glLoadIdentity()

    a = math.radians(angle)

    cam_x = radius * math.sin(a)
    cam_z = radius * math.cos(a)

    gluLookAt(
        cam_x,
        0.0,
        cam_z,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0
    )

    glColor3f(
        1.0,
        0.9,
        0.3
    )

    draw_sphere()


def on_key(window, key, scancode, action, mods):

    global mode

    if action != glfw.PRESS:
        return

    if key == glfw.KEY_1:
        mode = 1

    elif key == glfw.KEY_2:
        mode = 2

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


glfw.init()

window = glfw.create_window(
    800,
    600,
    "Mision 2",
    None,
    None
)

glfw.make_context_current(window)

glfw.set_key_callback(window, on_key)

glEnable(GL_DEPTH_TEST)

while not glfw.window_should_close(window):

    width, height = glfw.get_framebuffer_size(window)

    glViewport(0, 0, width, height)

    glClearColor(0.08, 0.08, 0.12, 1.0)

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

    if mode == 1:

        render_scene(3.0)

    else:

        render_scene(8.0)

    angle += 0.6

    glfw.swap_buffers(window)

    glfw.poll_events()

glfw.terminate()