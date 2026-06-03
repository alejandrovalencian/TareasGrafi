import sys
import cv2
import glfw
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *

CAMERA_INDEX = 0

MARKER_LENGTH_M = 0.10

ARUCO_DICT = cv2.aruco.DICT_4X4_50

MARKER_ID = 0

MODEL_SCALE = 0.05

WINDOW_TITLE = "RA ArUco + OpenGL"

ZNEAR = 0.01
ZFAR = 100.0


def default_camera_matrix(width, height):
    f = float(max(width, height))
    cx = width / 2.0
    cy = height / 2.0

    return np.array([
        [f, 0, cx],
        [0, f, cy],
        [0, 0, 1]
    ], dtype=np.float64)


def make_detector():
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)

    params = cv2.aruco.DetectorParameters()

    if hasattr(cv2.aruco, "ArucoDetector"):
        detector = cv2.aruco.ArucoDetector(dictionary, params)
        return detector, dictionary

    return None, dictionary


def detect_marker(gray, detector, dictionary):

    if detector is not None:
        corners, ids, _ = detector.detectMarkers(gray)
    else:
        corners, ids, _ = cv2.aruco.detectMarkers(
            gray,
            dictionary
        )

    if ids is None:
        return None

    for i, marker_id in enumerate(ids.flatten()):

        if marker_id == MARKER_ID:
            return corners[i]

    return None


def marker_object_points(size):

    s = size / 2.0

    return np.array([
        [-s,  s, 0],
        [ s,  s, 0],
        [ s, -s, 0],
        [-s, -s, 0]
    ], dtype=np.float32)


def estimate_pose(corners, camera_matrix):

    image_points = corners.reshape(-1, 2).astype(np.float32)

    object_points = marker_object_points(MARKER_LENGTH_M)

    success, rvec, tvec = cv2.solvePnP(
        object_points,
        image_points,
        camera_matrix,
        np.zeros((5, 1), dtype=np.float64)
    )

    if not success:
        return None, None

    return rvec, tvec


def projection_matrix_from_camera(K, width, height):

    fx = K[0, 0]
    fy = K[1, 1]

    cx = K[0, 2]
    cy = K[1, 2]

    P = np.zeros((4, 4), dtype=np.float32)

    P[0, 0] = 2 * fx / width
    P[1, 1] = 2 * fy / height

    P[0, 2] = (width - 2 * cx) / width
    P[1, 2] = (2 * cy - height) / height

    P[2, 2] = -(ZFAR + ZNEAR) / (ZFAR - ZNEAR)
    P[2, 3] = -1

    P[3, 2] = -(2 * ZFAR * ZNEAR) / (ZFAR - ZNEAR)

    return P


def modelview_matrix(rvec, tvec):

    R, _ = cv2.Rodrigues(rvec)

    M = np.eye(4, dtype=np.float32)

    M[:3, :3] = R
    M[:3, 3] = tvec.flatten()

    cv_to_gl = np.array([
        [1, 0, 0, 0],
        [0,-1, 0, 0],
        [0, 0,-1, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

    M = cv_to_gl @ M

    return M.T


quadric = None


def draw_sphere(radius):

    global quadric

    if quadric is None:
        quadric = gluNewQuadric()

    gluSphere(quadric, radius, 32, 32)


def setup_lighting():

    glEnable(GL_LIGHTING)

    glEnable(GL_LIGHT0)

    glEnable(GL_COLOR_MATERIAL)

    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glLightfv(GL_LIGHT0, GL_POSITION, (1, 1, 1, 0))

    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))

    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1))


texture_id = None


def upload_camera_texture(frame):

    global texture_id

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    frame = cv2.flip(frame, 0)

    h, w = frame.shape[:2]

    if texture_id is None:
        texture_id = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, texture_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGB,
        w,
        h,
        0,
        GL_RGB,
        GL_UNSIGNED_BYTE,
        frame
    )


def draw_background(width, height):

    glDisable(GL_DEPTH_TEST)

    glDisable(GL_LIGHTING)

    glMatrixMode(GL_PROJECTION)

    glPushMatrix()

    glLoadIdentity()

    glOrtho(0, width, 0, height, -1, 1)

    glMatrixMode(GL_MODELVIEW)

    glPushMatrix()

    glLoadIdentity()

    glEnable(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, texture_id)

    glColor3f(1, 1, 1)

    glBegin(GL_QUADS)

    glTexCoord2f(0, 0)
    glVertex2f(0, 0)

    glTexCoord2f(1, 0)
    glVertex2f(width, 0)

    glTexCoord2f(1, 1)
    glVertex2f(width, height)

    glTexCoord2f(0, 1)
    glVertex2f(0, height)

    glEnd()

    glDisable(GL_TEXTURE_2D)

    glPopMatrix()

    glMatrixMode(GL_PROJECTION)

    glPopMatrix()

    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)


rotation = 0


def draw_3d_object():

    global rotation

    glPushMatrix()

    glTranslatef(0, 0, MODEL_SCALE * 0.5)

    glRotatef(rotation, 0, 1, 0)

    glColor3f(0.2, 0.8, 1.0)

    draw_sphere(MODEL_SCALE)

    glPopMatrix()


def draw_scene(rvec, tvec, camera_matrix, width, height):

    projection = projection_matrix_from_camera(
        camera_matrix,
        width,
        height
    )

    modelview = modelview_matrix(rvec, tvec)

    glMatrixMode(GL_PROJECTION)

    glLoadMatrixf(projection)

    glMatrixMode(GL_MODELVIEW)

    glLoadMatrixf(modelview)

    setup_lighting()

    draw_3d_object()


def main():

    global MODEL_SCALE
    global rotation

    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print("No se pudo abrir la cámara")
        return

    ret, frame = cap.read()

    if not ret:
        return

    h, w = frame.shape[:2]

    camera_matrix = default_camera_matrix(w, h)

    detector, dictionary = make_detector()

    if not glfw.init():
        return

    window = glfw.create_window(
        w,
        h,
        WINDOW_TITLE,
        None,
        None
    )

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    glClearColor(0.2, 0.2, 0.2, 1)

    glEnable(GL_DEPTH_TEST)

    def key_callback(window, key, scancode, action, mods):

        global MODEL_SCALE
        global rotation

        if action != glfw.PRESS:
            return

        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

        elif key == glfw.KEY_EQUAL:
            MODEL_SCALE *= 1.1

        elif key == glfw.KEY_MINUS:
            MODEL_SCALE /= 1.1

        elif key == glfw.KEY_LEFT:
            rotation -= 10

        elif key == glfw.KEY_RIGHT:
            rotation += 10

    glfw.set_key_callback(window, key_callback)

    while not glfw.window_should_close(window):

        ret, frame = cap.read()

        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        corners = detect_marker(
            gray,
            detector,
            dictionary
        )

        glViewport(0, 0, w, h)

        upload_camera_texture(frame)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        draw_background(w, h)

        if corners is not None:

            rvec, tvec = estimate_pose(
                corners,
                camera_matrix
            )

            if rvec is not None:

                draw_scene(
                    rvec,
                    tvec,
                    camera_matrix,
                    w,
                    h
                )

        glfw.swap_buffers(window)

        glfw.poll_events()

    cap.release()

    glfw.terminate()


if __name__ == "__main__":
    main()