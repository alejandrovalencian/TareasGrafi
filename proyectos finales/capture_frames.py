"""
capture_frames.py
─────────────────
Genera la carpeta renders/ con:
  • 1 captura PNG representativa por escena (6 imágenes)
  • Copia del video final si ya existe

Uso:
    python capture_frames.py

Requiere haber ejecutado demo_futbol.py al menos una vez (para que exista
demo_futbol.mp4), aunque puede correr de forma independiente para
generar solo las capturas.
"""

import os
import shutil
import math
import numpy as np
import cv2

# ── Importamos todo desde demo_futbol.py ───────────────────────────────────
from demo_futbol import (
    W, H, FPS,
    scene_credits, scene_lissajous, scene_rose_polar,
    scene_spirograph, scene_fire, scene_particles,
    post_vignette, post_scanlines, post_posterize,
)

# ── Configuración ──────────────────────────────────────────────────────────
OUTPUT_DIR = "renders"

# Tiempo representativo dentro de cada escena (en segundos globales)
# Se elige un punto donde la curva/efecto ya está bien formado
SCENE_SNAPSHOTS = [
    (0, 3.5,  "scene_0_credits"),
    (1, 9.0,  "scene_1_lissajous"),
    (2, 15.0, "scene_2_rosa_polar"),
    (3, 23.0, "scene_3_spirograph"),
    (4, 32.0, "scene_4_fuego_gol"),
    (5, 38.5, "scene_5_particulas"),
]


def render_snapshot(scene_id: int, t: float, rng, fs: dict) -> np.ndarray:
    """Renderiza un único frame para la escena indicada en el tiempo t."""
    buf = np.zeros((H, W, 3), np.uint8)

    if   scene_id == 0: scene_credits(buf, t)
    elif scene_id == 1: scene_lissajous(buf, t)
    elif scene_id == 2: scene_rose_polar(buf, t)
    elif scene_id == 3: scene_spirograph(buf, t)
    elif scene_id == 4: scene_fire(buf, t, fs)
    else:               scene_particles(buf, t, rng)

    # Aplicar post-FX igual que en el render principal
    buf = post_vignette(buf, 0.72)
    buf = post_scanlines(buf, 0.14)
    buf = post_posterize(buf, 24)
    return buf


def main():
    # Crear directorio de salida
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"[capture_frames] Carpeta de salida: ./{OUTPUT_DIR}/\n")

    rng = np.random.default_rng(42)

    # Estado del fuego (necesita algunos frames de calentamiento)
    fs = {"heat": np.zeros((H, W), np.float32), "rng": np.random.default_rng(999)}

    # Pre-calentar la simulación de fuego para que se vea bien en el snapshot
    buf_warmup = np.zeros((H, W, 3), np.uint8)
    for _ in range(60):      # ~2 segundos simulados
        scene_fire(buf_warmup, 30.0, fs)

    for scene_id, t_snap, filename in SCENE_SNAPSHOTS:
        print(f"  Escena {scene_id} — t={t_snap:.1f}s → {filename}.png")
        frame = render_snapshot(scene_id, t_snap, rng, fs)

        # Etiqueta con número de escena en la esquina superior derecha
        label = f"Escena {scene_id}"
        cv2.putText(frame, label, (W - 130, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

        out_path = os.path.join(OUTPUT_DIR, f"{filename}.png")
        cv2.imwrite(out_path, frame)
        print(f"    Guardado: {out_path}")

    # Copiar el video si existe
    video_src = "demo_futbol.mp4"
    video_dst = os.path.join(OUTPUT_DIR, "demo_futbol.mp4")
    if os.path.exists(video_src):
        shutil.copy2(video_src, video_dst)
        print(f"\n  Video copiado a: {video_dst}")
    else:
        print(f"\n  AVISO: Video '{video_src}' no encontrado.")
        print("     Ejecuta primero 'python demo_futbol.py' para generarlo.")

    print(f"\n[capture_frames] Listo! {len(SCENE_SNAPSHOTS)} capturas guardadas en ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    main()