# Baraka & Sophia - WEDDING RECEPTION v1 - Envaita two-panel blueprint (blueprint_twopanel_photo_blush_pampas.jpeg,
# 1834x1286 mock-up, dummy "Sam-Clinton & Faith"): left = photo panel, right = text panel with blush pampas.
# Client palette Emerald Green & Gold -> pampas recoloured to champagne gold, text emerald + gold, photo fades to deep emerald.
# No church (ndoa ilishafungwa). run: ~/.haflaway/venv/bin/python -I build_v1.py [out_name]   (PHOTO=photo_A_cheek.jpeg to swap)
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *
from PIL import ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Baraka_&_Sophia_v1_final_01.png"
SCR = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/39ac5a94-2c35-48a2-a078-0faa4526b442/scratchpad/"
K = 2

src = cv2.imread(HERE + "/blueprint_twopanel_photo_blush_pampas.jpeg"); H0, W0 = src.shape[:2]
g = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY).astype(int)
yy, xx = np.mgrid[0:H0, 0:W0]

# ------------------------------------------------------------------ 1. right panel: remove the dummy text
TEXT = [(1150, 158, 1585, 290), (1180, 300, 1570, 345), (1150, 352, 1585, 418), (1078, 428, 1655, 512),
        (1200, 528, 1570, 592), (1128, 592, 1625, 922), (1030, 1165, 1700, 1205)]
SOLID = [(1252, 922, 1494, 968), (1458, 1036, 1596, 1092)]          # colour chips, DOUBLE badge (redrawn blank)
TXT_COLS = np.array([[116, 113, 143], [37, 72, 143], [145, 158, 198], [190, 190, 190], [120, 100, 120]], np.float32)  # BGR
clean = src.copy()
for x1, y1, x2, y2 in SOLID:
    m = np.zeros((H0, W0), np.uint8); m[y1:y2, x1:x2] = 255
    clean = cv2.inpaint(clean, m, 15, cv2.INPAINT_TELEA)
tm = np.zeros((H0, W0), np.uint8)
for x1, y1, x2, y2 in TEXT:
    sub = src[y1:y2, x1:x2].astype(np.float32)
    dmin = np.min([np.linalg.norm(sub - c, axis=2) for c in TXT_COLS], axis=0)
    tm[y1:y2, x1:x2] = ((dmin < 46) | (g[y1:y2, x1:x2] < 175)).astype(np.uint8)*255
FLORAL = (xx < 1200) & (yy > 290) & (yy < 760)                       # left pampas cluster: tight colour-only mask there
fl_m = np.zeros((H0, W0), np.uint8)
srcf = src.astype(np.float32)
dmin_all = np.min([np.linalg.norm(srcf - c, axis=2) for c in TXT_COLS[:3]], axis=0)
for x1, y1, x2, y2 in TEXT:
    box = np.zeros((H0, W0), bool); box[y1:y2, x1:x2] = True
    fl_m[box & FLORAL & (dmin_all < 30)] = 255
tm[FLORAL] = 0
tm = cv2.dilate(tm, np.ones((3, 3), np.uint8), iterations=2)
clean = cv2.inpaint(clean, tm, 5, cv2.INPAINT_TELEA)
clean = cv2.inpaint(clean, cv2.dilate(fl_m, np.ones((3, 3), np.uint8), iterations=1), 3, cv2.INPAINT_TELEA)
# paper zones (no pampas): median-background pass removes the anti-aliased remnants
for b in [(1150, 158, 1585, 290), (1180, 300, 1570, 345), (1185, 352, 1585, 418), (1185, 528, 1570, 592),
          (1185, 592, 1625, 922), (1100, 1165, 1600, 1205)]:
    clean = clean_by_background(clean, b, thr=10, blur=41)
# leftover blobs of "la" on the frond tips and a dot after "Sam-C": compare against a local median estimate
for b_ in [(1150, 616, 1205, 664), (1185, 462, 1218, 492)]:
    clean = clean_by_background(clean, b_, thr=12, blur=25)
zm = np.zeros((H0, W0), np.float32)
for x1, y1, x2, y2 in [(1195, 158, 1585, 290), (1195, 300, 1570, 345), (1195, 352, 1585, 418), (1195, 428, 1655, 512),
                       (1195, 528, 1570, 592), (1195, 592, 1625, 922), (1100, 1165, 1600, 1205)]: zm[y1:y2, x1:x2] = 1
zm = cv2.GaussianBlur(zm, (0, 0), 5)[..., None]
clean = (cv2.GaussianBlur(clean, (0, 0), 4)*zm + clean*(1 - zm)).astype(np.uint8)   # soften ghosts on the plain paper
cv2.imwrite(SCR + "bs_clean.jpg", clean)

# ------------------------------------------------------------------ 2. pampas: blush -> champagne gold (right panel only)
lab = cv2.cvtColor(clean, cv2.COLOR_BGR2LAB).astype(np.float32)
L, A, B = lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128
C = np.sqrt(A**2 + B**2)
w = np.clip((C - 4)/6, 0, 1)*(xx >= 962)
GD = (0.17, 0.985)                                                   # champagne-gold direction in (a, b)
Cn = C*1.3
lab[..., 1] = 128 + A*(1 - w) + Cn*GD[0]*w
lab[..., 2] = 128 + B*(1 - w) + Cn*GD[1]*w
clean = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

# ------------------------------------------------------------------ 3. upscale; left panel rebuilt (photo, emerald fade, gold frame)
card = Image.fromarray(cv2.cvtColor(cv2.resize(clean, (W0*K, H0*K), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB))
c = Card(card, K, resize=False); P = c.P
PX1, PY1, PX2, PY2 = 128, 83, 882, 1229                              # photo panel (blueprint px, exclusive end)
pw, ph = P(PX2 - PX1), P(PY2 - PY1)
photo = Image.open(HERE + "/" + os.environ.get("PHOTO", "photo_B_embrace.jpeg")).convert("RGB")
sc = max(pw/photo.width, ph/photo.height)*float(os.environ.get("ZOOM", "1.0"))
photo = photo.resize((round(photo.width*sc), round(photo.height*sc)), Image.LANCZOS)
ox = round((photo.width - pw)*float(os.environ.get("CX", "0.5"))); oy = round((photo.height - ph)*float(os.environ.get("CY", "0.0")))
panel = photo.crop((ox, oy, ox + pw, oy + ph)).convert("RGBA")
DARK = (9, 34, 27)                                                   # deep emerald
yv = np.linspace(0, 1, ph)[:, None]
a_top = np.clip((0.20 - yv)/0.20, 0, 1)**1.3*0.88
a_bot = np.clip((yv - 0.56)/0.26, 0, 1)**1.2
alpha = np.clip(np.maximum(a_top, a_bot), 0, 1)*np.ones((1, pw))
ov = Image.new("RGBA", (pw, ph), DARK + (0,)); ov.putalpha(Image.fromarray((alpha*255).astype(np.uint8)))
panel = Image.alpha_composite(panel, ov).convert("RGB")
card.paste(panel, (P(PX1), P(PY1)))
GOLD = (198, 160, 92); GOLD_D = (176, 138, 62); CREAM = (250, 246, 236)
c.d.rectangle([P(151), P(103), P(855), P(1194)], outline=GOLD, width=max(1, P(0.9)))
mont = lambda z, w=400: c.f("Montserrat.ttf", z, w)
corm = lambda z, w=500: c.f("CormorantGaramond.ttf", z, w)
scr = lambda z: c.f("GreatVibes-Regular.ttf", z)
popp = lambda z: c.f("Poppins-Regular.ttf", z); popb = lambda z: c.f("Poppins-SemiBold.ttf", z)
def tc(x, yc, t, f, fill, sp=0, align="c"):
    bb = c.d.textbbox((0, 0), "Ag" if t.strip("&") else t, font=f)       # same reference for every line -> even rhythm
    c.text(x, yc - (bb[1] + bb[3])/2/K, t, f, fill, sp=sp, align=align)
LX = 503
for i, t in enumerate(["TUNAKUKARIBISHA", "KWENYE SHEREHE YA", "HARUSI YA"]): tc(LX, 156 + i*24, t, mont(17, 400), CREAM, sp=7)
fN = corm(78, 500)
tc(186, 905, "BARAKA", fN, CREAM, align="l")
wS = c.width("SOPHIA", fN); tc(790 - wS, 968, "SOPHIA", fN, CREAM, align="l")
tc(790 - wS - 48, 966, "&", scr(58), GOLD, align="r")
c.line(205, 1013, 803, 1013, GOLD, 1.2)
tc(LX, 1042, "21.11.2026", mont(27, 500), CREAM, sp=9)
tc(LX, 1077, "TENGA TAREHE", mont(15, 500), GOLD, sp=6)
c.paste_logo(LX - 215/2, 1140, 215, dark_bg=True)

# ------------------------------------------------------------------ 4. right panel text (emerald + gold)
EM = (14, 84, 62); EM_D = (20, 64, 50)
AX = 1372
fam = ["Familia ya", "Bw. Twaha Fungafunga na", "Bi. Redempta Henjewele", "Wanayo furaha kukualika/kuwaalika"]
fb = min((c.fit(t, popp, 26, 470) for t in fam), key=lambda f: f.size)
for i, t in enumerate(fam): tc(AX, 180 + i*32, t, fb, EM_D)
c.line(AX - 150, 334, AX + 150, 334, GOLD_D, 1.3)                                  # blank guest-name line
for i, t in enumerate(["Kwenye sherehe ya harusi ya", "vijana wao wapendwa"]): tc(AX, 376 + i*32, t, fb, EM_D)
tc(AX, 478, "Baraka & Sophia", c.fit("Baraka & Sophia", scr, 84, 400), GOLD_D)
tc(AX, 550, "itakayofanyika", fb, EM_D)
tc(AX, 582, "Jumamosi, Tarehe 21/11/2026", popb(26), EM)
tc(AX, 632, "Sherehe", popb(26), EM)
for i, t in enumerate(["Landmark Hotel - Ubungo", "Dar es Salaam", "Kuanzia Saa 12:00 Jioni"]): tc(AX, 664 + i*32, t, fb, EM_D)
tc(AX, 780, "Mawasiliano", popb(26), EM)
CON = [phone("0723913704") + " - REDEMPTA HENJEWELE", phone("0656124423") + " - PETRO MWAMBELEKO"]
fc = min((c.fit(t, popp, 25, 460) for t in CON), key=lambda f: f.size)
for i, t in enumerate(CON): tc(AX, 812 + i*31, t, fc, EM_D)
tc(AX, 888, "Rangi:", popb(26), EM)
for i, col in enumerate([(4, 99, 73), (199, 160, 64)]):
    x0 = AX - 44 + i*52; c.d.rectangle([P(x0), P(906), P(x0 + 36), P(942)], fill=col)
tc(AX, 963, "(Emerald Green & Gold)", c.f("Poppins-Regular.ttf", 19), EM_D)
c.d.rounded_rectangle([P(1458), P(1038), P(1594), P(1090)], P(6), fill=EM)        # blank badge (system fills it)
save_card(card, CLIENT + "/outputs/" + OUT, "Baraka & Sophia - Mwaliko wa Harusi", SCR + "bs_prev.jpg", 1600)
print("saved", OUT, card.size)
