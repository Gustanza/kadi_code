# John & Vedastina - WEDDING v2 - black & cream/gold 3D flowers (ekadi Ekadi_109, 3020x3652)
# Same blueprint as Latifa Hellen v3 / Hafidh & Lamlaty; layout adapted from LATIFAH HELLEN/sources/build_v3.py
# run: ~/.haflaway/venv/bin/python build_v2.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "John_&_Vedastina_v2_final_02.png"
PREV = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/8d5d143e-4e6d-4e7a-9c03-6fcc9b8f790b/scratchpad/john_v2_prev.jpg"

src = cv2.imread(HERE + "/blueprint_black_gold.jpg"); H, W = src.shape[:2]
boxes = [(1050,690,1970,870),(1120,925,1900,1008),(900,1135,2120,1300),(790,1405,2240,1580),(1150,1685,1890,1765),
         (1050,1885,1975,1985),(680,2290,2330,2465),(680,2540,2050,2620),(680,2700,1300,2782),(1040,2820,2060,2905),
         (1380,3505,1640,3615)]
bg = cv2.medianBlur(src, 41)
m = np.zeros((H, W), np.uint8)
for x1, y1, x2, y2 in boxes:
    d = src[y1:y2, x1:x2].astype(int).max(axis=2) - bg[y1:y2, x1:x2].astype(int).max(axis=2)
    m[y1:y2, x1:x2] = np.where((d > 28) | (src[y1:y2, x1:x2].max(axis=2) > 100), 255, 0)
img = cv2.inpaint(src, cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=2), 11, cv2.INPAINT_TELEA)
# badge: wipe "DOUBLE", keep the white pill blank (system fills single/double)
pill = src[2105:2195, 1350:1670]; inner = pill.max(axis=2) > 200
img[2114:2186, 1364:1656] = np.median(pill[inner], axis=0)
# ---- optional couple photo as a see-through layer over the whole card (client 2026-11-11)
#   BGPHOTO=bg_photo_A.jpeg ALPHA=0.33 python build_v2.py <out>
BGPHOTO = os.environ.get("BGPHOTO")
if BGPHOTO:
    A = float(os.environ.get("ALPHA", "0.33"))
    ph = cv2.imread(HERE + "/" + BGPHOTO)
    s = H / ph.shape[0]; pw = int(round(ph.shape[1] * s))
    ph = cv2.resize(ph, (pw, H), interpolation=cv2.INTER_LANCZOS4)   # full card height
    hsv = cv2.cvtColor(ph, cv2.COLOR_BGR2HSV).astype(np.float32)     # tame the bright backdrop / red text / green carpet
    hsv[..., 1] *= float(os.environ.get("SAT", "0.7")); hsv[..., 2] *= float(os.environ.get("VAL", "0.82"))
    ph = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
    x0 = (W - pw) // 2
    layer = img.copy(); layer[:, x0:x0+pw] = ph
    alpha = np.zeros((H, W), np.float32)
    xs = np.arange(pw, dtype=np.float32); F = 260                    # soft left/right edges, no hard seam
    t = np.clip(np.minimum(xs, pw - 1 - xs) / F, 0, 1); ramp = t*t*(3 - 2*t)
    alpha[:, x0:x0+pw] = A * ramp[None, :]
    # the couple: loose hand polygon (photo px, 720x1080), feathered, laid stronger so they show OVER the corner flowers
    COUPLE = {"bg_photo_A.jpeg": [(200,50),(342,42),(358,200),(483,67),(608,75),(625,233),(667,283),(720,1000),(720,1080),
                                  (142,1080),(142,967),(92,633),(83,283),(183,217),(192,100)],
              "bg_photo_B.jpeg": [(133,50),(250,53),(267,183),(333,200),(467,100),(550,92),(608,142),(600,250),(633,433),
                                  (642,1000),(633,1042),(100,1042),(67,667),(67,233),(125,183),(120,83)]}
    P = float(os.environ.get("PEOPLE", "0.6"))
    if BGPHOTO in COUPLE:
        pm = np.zeros((H, pw), np.float32)
        cv2.fillPoly(pm, [np.array([(x*s, y*s) for x, y in COUPLE[BGPHOTO]], np.int32)], 1.0)
        pm = cv2.GaussianBlur(pm, (0, 0), 70)
        alpha[:, x0:x0+pw] = np.maximum(alpha[:, x0:x0+pw], P * pm * ramp[None, :])
    # faces (+hair): nearly opaque so they sit clearly ON TOP of the corner flowers (client: "hidden behind flowers")
    FACES = {"bg_photo_A.jpeg": [(270, 118, 88, 110), (532, 158, 82, 104)],
             "bg_photo_B.jpeg": [(196, 118, 86, 108), (530, 166, 86, 106)]}
    FA = float(os.environ.get("FACE", "0.92"))
    if BGPHOTO in FACES:
        fm = np.zeros((H, pw), np.float32)
        for fx, fy, rx, ry in FACES[BGPHOTO]:
            cv2.ellipse(fm, (int(fx*s), int(fy*s)), (int(rx*s), int(ry*s)), 0, 0, 360, 1.0, -1)
        fm = cv2.GaussianBlur(fm, (0, 0), 55)
        alpha[:, x0:x0+pw] = np.maximum(alpha[:, x0:x0+pw], FA * fm)
    keep = img.copy()
    img = (img * (1 - alpha[..., None]) + layer * alpha[..., None]).astype(np.uint8)
    # badge pill + QR stay crisp/untinted
    for x1, y1, x2, y2 in [(1340, 2095, 1680, 2205), (1350, 2960, 1670, 3270)]:
        reg = src[y1:y2, x1:x2]; mk = reg.min(axis=2) > 215
        ys, xs2 = np.nonzero(mk)
        if len(ys):
            a1, a2, b1, b2 = y1 + ys.min(), y1 + ys.max() + 1, x1 + xs2.min(), x1 + xs2.max() + 1
            img[a1:a2, b1:b2] = keep[a1:a2, b1:b2]
GOLD = (225, 195, 137); WHITE = (252, 252, 252)
def draw_text(c, GOLD=GOLD, WHITE=WHITE, swatch=True):
    global LX, VX, y, AX, STEP
    mont = lambda sz, w=600: c.f("Montserrat.ttf", sz, w)
    script = lambda sz: c.f("GreatVibes-Regular.ttf", sz)

    def tc(x, yc, t, f, fill, align="c"):                             # ink centred vertically on yc
        bb = c.d.textbbox((0, 0), t, font=f); c.text(x, yc - (bb[1] + bb[3])/2, t, f, fill, align=align)

    AX = 1510
    for yc, t in [(734, "Familia ya Bw. & Bi. Pima John"), (818, "wa Kitunda, Dar es Salaam"),
                  (902, "inayo furaha kukualika / kuwaalika")]:
        tc(AX, yc, t, c.fit(t, mont, 64, 1150), GOLD)
    # template gold rule at y~1061 is the guest-name line (writing room above it)
    tc(AX, 1170, "kwenye sherehe ya harusi ya", mont(62), GOLD)
    tc(AX, 1260, "wapendwa wao", mont(62), GOLD)
    tc(AX, 1478, "John & Vedastina", c.fit("John & Vedastina", script, 270, 1300), WHITE)
    tc(AX, 1723, "itakayofanyika siku ya", mont(62), GOLD)
    tc(AX, 1932, "Jumamosi, 28 Novemba 2026", c.fit("Jumamosi, 28 Novemba 2026", lambda z: mont(z, 700), 70, 860), WHITE)
    # label / value rows (Ibada added -> rows slightly tighter than Latifa's)
    lab = mont(60, 700); val = mont(58)
    GAP = 400
    rows = [("Ibada:",  ["Kanisa Anglican la St. Paul's - Ukonga,", "kuanzia saa XX:XX."]),
            ("Ukumbi:", ["Mwigo Empire Hall - Tabata Bima,", "kuanzia saa 12:00 jioni."])]
    BW = GAP + max(c.width(t, val) for _, vs in rows for t in vs)
    LX = AX - BW/2; VX = LX + GAP
    y = 2290; STEP = 74; BLOCK = 104
    for label, vs in rows:
        tc(LX, y, label, lab, WHITE, "l")
        for i, t in enumerate(vs):
            tc(VX, y + i*STEP, t, val, GOLD, "l")
        y += (len(vs) - 1)*STEP + BLOCK
    tc(LX, y, "Rangi:", lab, WHITE, "l")
    tc(VX, y, "Black & Gold", val, GOLD, "l")
    sz, gp = 66, 20
    if swatch: swatches(c, VX + c.width("Black & Gold", val) + 60 + sz + gp/2, y - sz/2, [(10, 10, 12), (212, 175, 55)], size=sz, gap=gp, outline=GOLD)
    y += BLOCK
    tc(LX, y, "Mawasiliano:", lab, WHITE, "l")
    contacts = ["Samuel A. Mshote (M/kiti) - 0754 277 980", "Monica Mshote (Mwekahazina) - 0686 967 238"]
    # long lines -> start under the labels (LX), clear of the bottom-right flowers (x < ~2000)
    cf = c.fit(max(contacts, key=lambda t: c.width(t, val)), mont, 51, 1960 - (LX + 95))
    for i, t in enumerate(contacts):
        tc(LX + 95, y + 84 + i*STEP, t, cf, GOLD, "l")
    print("contact font", cf.size)


if BGPHOTO:   # soft dark glow behind every line of text so gold stays readable over the photo
    g = Card(Image.new("RGB", (W, H), (0, 0, 0)), 1.0); draw_text(g, (255,)*3, (255,)*3, swatch=False)
    gm = np.asarray(g.im.convert("L"), np.float32) / 255
    gm = cv2.GaussianBlur(cv2.dilate(gm, np.ones((9, 9), np.uint8)), (0, 0), 18)
    gm = np.clip(gm * 1.6, 0, 1) * float(os.environ.get("GLOW", "0.6"))
    img = (img * (1 - gm[..., None]) + np.array([12, 10, 10]) * gm[..., None]).astype(np.uint8)
c = Card(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), 1.0)
# v2_final_02 (client 2026-11-11): all white text -> gold like the rest (ALLGOLD=0 restores white names/date/labels)
draw_text(c, WHITE=GOLD if os.environ.get('ALLGOLD', '1') == '1' else WHITE)
# QR kept (placeholder); logo where ekadi was
c.paste_logo(AX - 85, 3330, 300, dark_bg=True, anchor="cm")
save_card(c.im, CLIENT + "/outputs/" + OUT, "John & Vedastina - Harusi", PREV, preview_w=1100)
print("saved", OUT, "rows LX", int(LX), "VX", int(VX), "last y", y + 84 + STEP)
