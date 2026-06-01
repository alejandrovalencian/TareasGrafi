"""
=============================================================
  DEMO PROCEDURAL — GRAFICACIÓN  |  Tema: FÚTBOL
  Tecnologías: Python 3 · NumPy · OpenCV
=============================================================

  ESCENAS (timeline 60 s, 6 bloques × 10 s)
  ─────────────────────────────────────────
  0  Credits / Intro   — cancha + pelota pulsante + texto
  1  Lissajous Ball    — pelota sigue curva de Lissajous
  2  Rosa Polar        — curva rosa polar (vista aérea)
  3  Spirograph Kick   — hipotrocoide + epicicloide + parábola
  4  Partículas Estadio— confeti + luces + ola sinusoidal
  5  Fuego de Gol      — heatmap + "GOOOL" pulsante

  CURVAS PARAMÉTRICAS (6 distintas)
  ────────────────────────────────────
  1. Lissajous animada          (scene 1)
  2. Rosa polar r=cos(k·θ)      (scene 2)
  3. Círculo (tiro de esquina)  (scene 2)
  4. Hipotrocoide               (scene 3)
  5. Epicicloide                (scene 3)
  6. Sinusoide de ola           (scene 4)

  TRANSFORMACIONES (2 explícitas con matrices afines 2×3)
  ────────────────────────────────────────────────────────
  • Rotación 2-D  → curva Lissajous + pelota (scene 1)
  • Escala        → zoom pulsante en spirograph (scene 3)
  • Composición addWeighted → transiciones de escena
  • Espejo (flip) → texto en créditos (scene 0)

  POST-FX
  ─────────────────────────────────────────────────────
  • Viñeta radial   (todas las escenas)
  • Scanlines retro (todas las escenas)
  • Posterize       (todas las escenas)
=============================================================
"""

import time
import math
import numpy as np
import cv2

# ─── Parámetros globales ───────────────────────────────────
W, H     = 800, 600
FPS      = 30
DURATION = 40.0

WHITE  = (255, 255, 255)
YELLOW = (0,   220, 240)


# ══════════════════════════════════════════════════════════
#  UTILIDADES
# ══════════════════════════════════════════════════════════

def clamp01(x):
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)

def smoothstep(a, b, x):
    x = clamp01((x - a) / (b - a))
    return x * x * (3 - 2 * x)

def hsv_to_bgr(h, s, v):
    hsv = np.uint8([[[int(h) % 180, int(np.clip(s,0,255)), int(np.clip(v,0,255))]]])
    return tuple(int(x) for x in cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0])

def poly_param(fx, fy, t0, t1, n, cx, cy, sx, sy):
    ts = np.linspace(t0, t1, n, dtype=np.float32)
    xs = fx(ts) * sx + cx
    ys = fy(ts) * sy + cy
    return np.round(np.stack([xs, ys], 1)).astype(np.int32).reshape((-1, 1, 2))

def apply_affine(pts_nx2, M):
    """Aplica transformación afín 2×3 a un array Nx2."""
    ones = np.ones((len(pts_nx2), 1), dtype=np.float32)
    hom  = np.hstack([pts_nx2.astype(np.float32), ones])
    return (M @ hom.T).T.astype(np.int32)

def rotation_matrix_2d(cx, cy, angle):
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s, cx*(1-c)+cy*s],
                     [s,  c, cy*(1-c)-cx*s]], dtype=np.float32)

def scale_matrix_2d(cx, cy, sx, sy):
    return np.array([[sx,  0, cx*(1-sx)],
                     [ 0, sy, cy*(1-sy)]], dtype=np.float32)

def background_hsv_gradient(img, t, hue0=10, hue1=140):
    hsv = np.zeros((H, W, 3), np.uint8)
    ys  = np.linspace(0, 1, H, dtype=np.float32)
    hue = (hue0 + (hue1-hue0)*ys + 10*np.sin(t*0.4+ys*2)).astype(np.float32)
    hsv[:,:,0] = np.clip(hue, 0, 179).astype(np.uint8)[:,None]
    hsv[:,:,1] = 200
    hsv[:,:,2] = (40 + 120*(1-ys)).astype(np.uint8)[:,None]
    img[:] = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


# ══════════════════════════════════════════════════════════
#  POST-FX
# ══════════════════════════════════════════════════════════

def post_vignette(img, strength=0.72):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (xx - W*0.5)/(W*0.5)
    ny = (yy - H*0.5)/(H*0.5)
    mask = np.clip(1.0 - strength*(nx*nx+ny*ny), 0, 1)
    return (img.astype(np.float32)*mask[...,None]).astype(np.uint8)

def post_scanlines(img, strength=0.14):
    out = img.astype(np.float32)
    y   = np.arange(H, dtype=np.float32)
    m   = 1.0 - strength*(0.5+0.5*np.sin(2*np.pi*y/3.0))
    out *= m[:,None,None]
    return np.clip(out, 0, 255).astype(np.uint8)

def post_posterize(img, q=24):
    return ((img//max(1,q))*max(1,q)).astype(np.uint8)


# ══════════════════════════════════════════════════════════
#  FONDOS
# ══════════════════════════════════════════════════════════

def draw_grass_bg(img):
    sw = W // 8
    c  = [(34,139,34),(45,160,45)]
    for i in range(8):
        cv2.rectangle(img, (i*sw,0), ((i+1)*sw,H), c[i%2], -1)

def draw_stadium_bg(img, t):
    img[:] = (10,10,20)
    for r in range(320, 0, -20):
        v = int(18 + 55*(1-r/320)*(0.8+0.2*math.sin(t)))
        cv2.circle(img, (W//2,H//2), r, (v, v+8, v), -1)

def draw_field_lines(img, alpha=0.45):
    ov = img.copy()
    cv2.rectangle(ov,(80,55),(W-80,H-55),WHITE,2)
    cv2.line(ov,(W//2,55),(W//2,H-55),WHITE,1)
    cv2.circle(ov,(W//2,H//2),72,WHITE,1)
    cv2.circle(ov,(W//2,H//2),3,WHITE,-1)
    cv2.rectangle(ov,(80,H//2-70),(210,H//2+70),WHITE,2)
    cv2.rectangle(ov,(W-210,H//2-70),(W-80,H//2+70),WHITE,2)
    cv2.addWeighted(img,1-alpha,ov,alpha,0,img)


# ══════════════════════════════════════════════════════════
#  PELOTA DE FÚTBOL (primitivas + rotación afín)
# ══════════════════════════════════════════════════════════

def draw_ball(img, cx, cy, r, angle=0.0):
    r = max(4, int(r))
    cv2.circle(img,(int(cx),int(cy)),r,(255,255,255),-1,cv2.LINE_AA)
    cv2.circle(img,(int(cx),int(cy)),r,(180,180,180), 1,cv2.LINE_AA)
    M = rotation_matrix_2d(cx, cy, angle)
    def penta(pcx, pcy, rr, rot):
        pts = [[pcx+rr*math.cos(rot+2*math.pi*k/5-math.pi/2),
                pcy+rr*math.sin(rot+2*math.pi*k/5-math.pi/2)] for k in range(5)]
        return np.array(pts, dtype=np.float32)
    p0 = apply_affine(penta(cx,cy,r*0.38,angle),M)
    cv2.fillPoly(img,[p0.reshape(-1,1,2)],(30,30,30))
    for k in range(5):
        a   = angle+2*math.pi*k/5-math.pi/2
        ps  = apply_affine(penta(cx+r*0.68*math.cos(a),cy+r*0.68*math.sin(a),r*0.22,angle+math.pi/5),M)
        cv2.fillPoly(img,[ps.reshape(-1,1,2)],(30,30,30))


# ══════════════════════════════════════════════════════════
#  ESCENAS
# ══════════════════════════════════════════════════════════

# ── Escena 0: Credits ─────────────────────────────────────
def scene_credits(img, t):
    draw_grass_bg(img)
    draw_field_lines(img, alpha=0.55)
    # Pelota pulsante en el centro
    pulse = 1.0 + 0.12*math.sin(t*3.0)
    draw_ball(img, W//2, H//2, 40*pulse, t*1.2)
    # Sombra + título
    for dx,dy,col in [(3,3,(0,50,0)),(0,0,WHITE)]:
        cv2.putText(img,"GRAFICACION",(W//2-185+dx,148+dy),
                    cv2.FONT_HERSHEY_DUPLEX,1.45,col,3,cv2.LINE_AA)
    for dx,dy,col in [(2,2,(0,50,0)),(0,0,YELLOW)]:
        cv2.putText(img,"Demo Procedural: FUTBOL",(W//2-225+dx,198+dy),
                    cv2.FONT_HERSHEY_SIMPLEX,0.88,col,2,cv2.LINE_AA)
    # TRANSFORMACIÓN: espejo horizontal del subtítulo
    sub = np.zeros((38,420,3),np.uint8)
    cv2.putText(sub,"OpenCV + NumPy + Matematicas",(5,26),
                cv2.FONT_HERSHEY_SIMPLEX,0.65,(180,255,180),1,cv2.LINE_AA)
    flip = cv2.flip(sub,1)  # espejo horizontal
    blend = 0.45+0.45*math.sin(t*1.6)
    roi   = img[H-78:H-40, W//2-210:W//2+210]
    cv2.addWeighted(roi,1-blend,flip,blend,0,roi)
    img[H-78:H-40,W//2-210:W//2+210] = roi


# ── Escena 1: Lissajous Ball ──────────────────────────────
def scene_lissajous(img, t):
    draw_stadium_bg(img, t)
    draw_field_lines(img, alpha=0.35)
    # Curva Lissajous
    a = 3.0+0.5*math.sin(t*0.5)
    b = 2.0+0.5*math.cos(t*0.7)
    delta = math.pi/2+0.3*math.sin(t*0.4)
    pts = poly_param(lambda x:np.sin(a*x+delta),lambda x:np.sin(b*x),
                     0,2*math.pi,900,W//2,H//2,280,200)
    # TRANSFORMACIÓN 1: rotación afín de la curva completa
    M   = rotation_matrix_2d(W//2,H//2,t*0.25)
    rot = apply_affine(pts.reshape(-1,2),M).reshape(-1,1,2)
    col = hsv_to_bgr(int(30+20*math.sin(t*0.9)),230,240)
    cv2.polylines(img,[rot],False,col,2,cv2.LINE_AA)
    # Pelota en la curva
    ph = (t*0.4)%(2*math.pi)
    braw = np.array([[math.sin(a*ph+delta)*280+W//2,
                      math.sin(b*ph)*200+H//2]],dtype=np.float32)
    bp   = apply_affine(braw,M)[0]
    draw_ball(img,bp[0],bp[1],22,t*4.0)
    # Estela con arrowedLine
    ph2  = ph-0.22
    praw = np.array([[math.sin(a*ph2+delta)*280+W//2,
                      math.sin(b*ph2)*200+H//2]],dtype=np.float32)
    pp   = apply_affine(praw,M)[0]
    cv2.arrowedLine(img,(int(pp[0]),int(pp[1])),(int(bp[0]),int(bp[1])),
                    YELLOW,2,cv2.LINE_AA,tipLength=0.4)
    cv2.putText(img,"Lissajous (rotacion afin)",(20,35),
                cv2.FONT_HERSHEY_SIMPLEX,0.65,(180,255,180),1,cv2.LINE_AA)


# ── Escena 2: Rosa Polar ──────────────────────────────────
def scene_rose_polar(img, t):
    background_hsv_gradient(img,t,hue0=42,hue1=80)
    draw_grass_bg(img)
    draw_field_lines(img, alpha=0.55)
    # Rosa polar r=cos(5θ)
    k = 5; th0 = t*0.5
    pts = poly_param(lambda th:np.cos(k*th)*np.cos(th+th0),
                     lambda th:np.cos(k*th)*np.sin(th+th0),
                     0,2*math.pi,1400,W//2,H//2,225,225)
    col = hsv_to_bgr(int(50+30*math.sin(t*0.6)),240,255)
    cv2.polylines(img,[pts],False,col,2,cv2.LINE_AA)
    # Curva: círculos en las 4 esquinas (tiros de esquina)
    for i,(ccx,ccy) in enumerate([(80,55),(W-80,55),(80,H-55),(W-80,H-55)]):
        r = int(40+28*math.sin(t*1.6+i))
        cv2.circle(img,(ccx,ccy),max(1,r),(200,255,200),1,cv2.LINE_AA)
    draw_ball(img,W//2,H//2,28,-t*2.0)
    cv2.putText(img,"Rosa Polar  r=cos(5*theta)",(20,35),
                cv2.FONT_HERSHEY_SIMPLEX,0.65,WHITE,1,cv2.LINE_AA)


# ── Escena 3: Spirograph Kick ─────────────────────────────
def scene_spirograph(img, t):
    draw_stadium_bg(img, t)
    # Hipotrocoide
    R,r,d = 8.0,3.0,5.0; w=(R-r)/r
    pts_h = poly_param(lambda x:(R-r)*np.cos(x)+d*np.cos(w*x+0.3*np.sin(t*0.7)),
                       lambda x:(R-r)*np.sin(x)-d*np.sin(w*x+0.3*np.cos(t*0.6)),
                       0,14*math.pi,1600,W//2,H//2,28,28)
    # TRANSFORMACIÓN 2: escala afín pulsante
    sf  = 1.0+0.4*math.sin(t*1.1)
    Ms  = scale_matrix_2d(W//2,H//2,sf,sf)
    phs = apply_affine(pts_h.reshape(-1,2),Ms).reshape(-1,1,2)
    cv2.polylines(img,[phs],False,
                  (240,240,240),2,cv2.LINE_AA)  # Blanco grisáceo

    # Epicicloide
    R2,r2=5.0,3.0
    pts_e = poly_param(lambda x:(R2+r2)*np.cos(x)-r2*np.cos((R2+r2)/r2*x),
                       lambda x:(R2+r2)*np.sin(x)-r2*np.sin((R2+r2)/r2*x),
                       0,6*math.pi,800,W//2,H//2,22,22)
    pes = apply_affine(pts_e.reshape(-1,2),Ms).reshape(-1,1,2)
    cv2.polylines(img,[pes],False,
                  (225,225,225),2,cv2.LINE_AA)  # Gris claro

    # Parábola del "chutazo"
    ph = (t*0.7)%(2*math.pi)
    bx = int(90+(W-180)*(ph/(2*math.pi)))
    by = int(H*0.6-210*math.sin(ph))
    draw_ball(img,bx,by,20,t*6.0)
    for s in range(1,6):
        p2=ph-s*0.15
        if p2<0: continue
        ex=int(90+(W-180)*(p2/(2*math.pi)))
        ey=int(H*0.6-210*math.sin(p2))
        cv2.circle(img,(ex,ey),max(1,5-s),(230,230,230),-1)

    img[:] = post_scanlines(img,0.15)
    cv2.putText(img,"Hipotrocoide + Epicicloide  (escala afin)",(20,35),
                cv2.FONT_HERSHEY_SIMPLEX,0.6,(235,235,235),1,cv2.LINE_AA)

# ── Escena 4: Fuego de Gol ────────────────────────────────
def scene_fire(img, t, state):
    heat=state["heat"]; rf=state["rng"]
    heat[:]=(heat*0.93).astype(np.float32)
    n=1600
    xs=rf.integers(0,W,n); ys=rf.integers(int(H*0.80),H,n)
    heat[ys,xs]+=rf.random(n)*(0.9+0.5*math.sin(t*2.2))
    heat[:]=cv2.GaussianBlur(heat,(0,0),2.5)
    heat[:-2,:]=heat[2:,:]; heat[-2:,:]*=0
    h_c=(20-20*np.clip(heat,0,1)).astype(np.uint8)
    s_c=(230-90*np.clip(heat,0,1)).astype(np.uint8)
    v_c=(50+205*np.clip(heat,0,1)).astype(np.uint8)
    img[:]=cv2.cvtColor(np.dstack([h_c,s_c,v_c]).astype(np.uint8),cv2.COLOR_HSV2BGR)
    cv2.rectangle(img,(0,int(H*0.84)),(W,H),(8,8,8),-1)
    sx=rf.integers(0,W,200); sy=rf.integers(int(H*0.50),int(H*0.88),200)
    img[sy,sx]=(255,255,255)
    pulse=1.0+0.18*math.sin(t*4.0)
    fsc=2.8*pulse; txt="GOOOL!!!"
    (tw,th),_=cv2.getTextSize(txt,cv2.FONT_HERSHEY_DUPLEX,fsc,4)
    tx=(W-tw)//2; ty=(H-th)//2+int(H*0.08)
    cv2.putText(img,txt,(tx+4,ty+4),cv2.FONT_HERSHEY_DUPLEX,fsc,(0,0,0),6,cv2.LINE_AA)
    cv2.putText(img,txt,(tx,ty),cv2.FONT_HERSHEY_DUPLEX,fsc,
                hsv_to_bgr(int(30+20*math.sin(t*3)),255,255),4,cv2.LINE_AA)
    img[:]=cv2.GaussianBlur(img,(0,0),0.5)

# ── Escena 5: Partículas Estadio ──────────────────────────
def scene_particles(img, t, rng):
    draw_stadium_bg(img, t)
    # Luces de tribuna (ellipse + line)
    for i in range(12):
        ax  = int(W*i/12)+30
        bri = int(160+80*math.sin(t*2+i*0.6))
        col = hsv_to_bgr(int(40+i*5),180,bri)
        cv2.ellipse(img,(ax,28),(18,7),0,0,360,col,-1,cv2.LINE_AA)
        cv2.line(img,(ax,28),(ax,56),col,1,cv2.LINE_AA)
    # Confeti
    n=800; base=np.arange(n,dtype=np.float32)
    xs=(base*13.7+rng.random(n)*W)%W
    ys=(base*7.3 +rng.random(n)*H+t*42)%H
    xs=(xs+60*np.sin(ys/40+t*1.8))%W
    for j in range(0,n,4):
        cv2.circle(img,(int(xs[j]),int(ys[j])),3,
                   hsv_to_bgr(int((base[j]*3.7+t*30)%180),230,240),-1)
    # Curva: sinusoide "ola del estadio"
    amp=32+18*math.sin(t*1.3)
    wpts=np.array([[[x,int(H*0.82+amp*math.sin(0.025*x+t*3))]]
                   for x in range(0,W,4)],dtype=np.int32)
    cv2.polylines(img,[wpts],False,YELLOW,3,cv2.LINE_AA)
    img[:]=cv2.GaussianBlur(img,(0,0),1.0)
    cv2.putText(img,"Estadio: particulas + ola sinusoidal",(20,35),
                cv2.FONT_HERSHEY_SIMPLEX,0.65,(255,255,200),1,cv2.LINE_AA)





# ══════════════════════════════════════════════════════════
#  RENDER DISPATCHER
# ══════════════════════════════════════════════════════════

def render_scene(buf, sid, t, rng, fs):
    if   sid==0: scene_credits(buf,t)
    elif sid==1: scene_lissajous(buf,t)
    elif sid==2: scene_rose_polar(buf,t)
    elif sid==3: scene_spirograph(buf,t)
    elif sid==4: scene_fire(buf,t,fs)
    else:        scene_particles(buf,t,rng)


# ══════════════════════════════════════════════════════════
#  TIMELINE
# ══════════════════════════════════════════════════════════

def timeline(t, rng, bufA, bufB, fs):
    block = int(min(5,max(0,t//5)))
    t_in  = t - block*8
    render_scene(bufA,block,t,rng,fs)
    frame = bufA
    if block<5 and t_in>=8.8:
        render_scene(bufB,block+1,t,rng,fs)
        a     = smoothstep(8.8,10.0,t_in)
        frame = cv2.addWeighted(bufA,1-a,bufB,a,0)
        flash = smoothstep(9.5,10.0,t_in)
        if flash>0:
            frame=cv2.addWeighted(frame,1.0,np.full_like(frame,255),0.15*flash,0)
    fin  = smoothstep(0.0,1.5,t)
    fout = 1.0-smoothstep(DURATION-1.5,DURATION,t)
    f    = fin*fout
    if f<0.999:
        frame=(frame.astype(np.float32)*f).astype(np.uint8)
    return frame


# ══════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════

def main():
    rng  = np.random.default_rng(42)
    bufA = np.zeros((H,W,3),np.uint8)
    bufB = np.zeros((H,W,3),np.uint8)
    fs   = {"heat":np.zeros((H,W),np.float32),"rng":np.random.default_rng(999)}

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter("demo_futbol.mp4", fourcc, FPS, (W,H))

    total = int(DURATION*FPS)
    t0    = time.perf_counter()
    for i in range(total):
        t     = i/FPS
        frame = timeline(t,rng,bufA,bufB,fs)
        frame = post_vignette(frame,0.72)
        frame = post_scanlines(frame,0.14)
        frame = post_posterize(frame,24)
        writer.write(frame)
        cv2.imshow("Demo Procedural FUTBOL  (ESC para salir)",frame)
        if cv2.waitKey(1)&0xFF==27:
            break
    writer.release()
    cv2.destroyAllWindows()
    print(f"Listo! Tiempo: {time.perf_counter()-t0:.1f}s | demo_futbol.mp4 guardado")

if __name__=="__main__":
    main()