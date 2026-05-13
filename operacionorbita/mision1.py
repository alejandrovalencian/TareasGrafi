#!/usr/bin/env python3

from __future__ import annotations

import sys

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

WINDOW_TITLE = "Mision 1"

CAM_DISTANCE = 5.0
ANGLE_SPEED = 0.6

_quadric = None


def draw_sphere(radius=1.0):

    global _quadric

    if _quadric is None:

        _quadric = gluNewQuadric()

        gluQuadricDrawStyle(
            _quadric,
            GLU_FILL
        )

    gluSphere(
        _quadric,
        radius,
        40,
        24
    )


def render_normal(angle):

    glMatrixMode(GL_MODELVIEW)

    glLoadIdentity()

    glRotatef(
        -angle,
        0.0,
        1.0,
        0.0
    )

    glTranslatef(
        0.0,
        0.0,
        -CAM_DISTANCE
    )

    glColor3f(
        1.0,
        0.5,
        0.3
    )

    draw_sphere()


def render_variant(angle):

    glMatrixMode(GL_MODELVIEW)

    glLoadIdentity()

    glTranslatef(
        0.0,
        0.0,
        -CAM_DISTANCE
    )

    glRotatef(
        angle,
        0.0,
        1.0,
        0.0
    )

    glColor3f(
        0.3,
        1.0,
        0.4
    )

    draw_sphere()


def main():

    if not glfw.init():

        sys.exit(1)

    glfw.window_hint(
        glfw.CONTEXT_VERSION_MAJOR,
        2
    )

    glfw.window_hint(
        glfw.CONTEXT_VERSION_MINOR,
        1
    )

    window = glfw.create_window(
        800,
        600,
        WINDOW_TITLE,
        None,
        None
    )

    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)

    mode = 1

    angle = 0.0

    def on_key(win, key, scancode, action, mods):

        nonlocal mode

        if action != glfw.PRESS:
            return

        if key == glfw.KEY_1:
            mode = 1

        elif key == glfw.KEY_2:
            mode = 2

        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(
                win,
                True
            )

    glfw.set_key_callback(
        window,
        on_key
    )

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
            50.0,
            width / float(height),
            0.1,
            100.0
        )

        if mode == 1:

            render_normal(angle)

        else:

            render_variant(angle)

        angle += ANGLE_SPEED

        glfw.swap_buffers(window)

        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()