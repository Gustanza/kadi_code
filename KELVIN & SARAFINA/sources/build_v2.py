# Kelvin & Sarafina - WEDDING v2 - navy watercolour card with torn gold edge + photo card (blueprint_A.jpeg, Envaita
# "Dr. Sadiki & Vivian" mock-up, 1775x1245, two cards on grey) - rendered 2.5x
# missing info shown as xxxx; no couple photo yet -> placeholder (drop photo_kelvin_sarafina.jpeg in sources/ and re-run)
# run: ~/.haflaway/venv/bin/python build_v2.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Kelvin_&_Sarafina_v2_final_01.png"
PREV = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/8d5d143e-4e6d-4e7a-9c03-6fcc9b8f790b/scratchpad/ks_v2_prev.jpg"
U = 2.5

src = cv2.imread(HERE + "/blueprint_A.jpeg"); H, W = src.shape[:2]
img = src.copy()

# ---- right card: wipe all template text inside the navy part (left of the torn gold edge)
X0, Y0, Y1 = 906, 64, 1150
zone = np.zeros((H, W), np.uint8)
R_, G_, B_ = [src[..., i].astype(int) for i in (2, 1, 0)]
lightblue = cv2.GaussianBlur(((src.mean(axis=2) > 150) & (B_ >= R_ - 8)).astype(np.float32), (0, 0), 8) > 0.6
for y in range(Y0, Y1):                                              # thin white text blurs away; the pale wash does not
    xs = np.where(lightblue[y, 1200:1700])[0]
    ex = 1200 + (xs.min() if len(xs) else 480)
    zone[y, X0:ex - 30] = 1                                          # stay clear of the gold torn edge
bgm = cv2.medianBlur(src, 41)
diff = np.abs(src.astype(int) - bgm.astype(int)).max(axis=2)
m = ((diff > 24) & (zone > 0)).astype(np.uint8) * 255
for x1, y1, x2, y2 in [(1022, 666, 1098, 738), (1300, 664, 1378, 735)]:   # keep church + pin icons
    m[y1:y2, x1:x2] = 0
m = cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=2) & (zone * 255)
m[1012:1056, 1098:1312] = 255                                        # template colour chips: wipe solid
bd = src[870:950, 1470:1680]; red = (bd[..., 2].astype(int) - bd[..., 1].astype(int)) > 50
ys, xs = np.where(red); bx1, by1, bx2, by2 = 1470 + xs.min(), 870 + ys.min(), 1470 + xs.max(), 870 + ys.max()
m[by1 - 8:by2 + 8, bx1 - 8:bx2 + 8] = 0                             # badge is not text
img = cv2.inpaint(img, m, 9, cv2.INPAINT_TELEA)
# DOUBLE badge -> blank maroon (system fills single/double)
img[by1:by2 + 1, bx1:bx2 + 1] = np.median(bd[red], axis=0)

# ---- left card: placeholder (or the couple's photo)
LX1, LY1, LX2, LY2 = 92, 76, 858, 1151
PHOTO = HERE + "/photo_kelvin_sarafina.jpeg"
c = Card(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), U)
pw, ph_ = c.P(LX2) - c.P(LX1), c.P(LY2) - c.P(LY1)
if os.path.exists(PHOTO):
    ph = crop_to(load_photo(PHOTO), pw, ph_, cx_frac=0.5, top_frac=0.0)
    ph = fade_to(ph, (10, 10, 12), int(ph_ * 0.5), int(ph_ * 0.8), max_a=0.95)
else:
    yy = np.linspace(0, 1, ph_)[:, None, None]
    ph = Image.fromarray(np.repeat((np.array([70, 70, 74]) * (1 - yy) + np.array([10, 10, 12]) * yy).astype(np.uint8), pw, axis=1))
c.im.paste(ph, (c.P(LX1), c.P(LY1)))
d = ImageDraw.Draw(c.im); c.d = d
rng = np.random.default_rng(3)                                     # gold dust like the template
for _ in range(260):
    x = rng.uniform(LX1 + 10, LX2 - 10); y = rng.uniform(LY1 + 10, LY2 - 10)
    if rng.random() < 0.6 and LY1 + 200 < y < LY1 + 700 and LX1 + 200 < x < LX2 - 200: continue
    r = rng.choice([0.8, 1.1, 1.6, 2.2], p=[0.45, 0.3, 0.17, 0.08])
    a = rng.uniform(0.35, 1)
    col = tuple(int(v * a) for v in (236, 186, 120))
    d.ellipse([c.P(x - r), c.P(y - r), c.P(x + r), c.P(y + r)], fill=col)
GOLD = (236, 182, 116); WHITE = (250, 248, 244)
script = lambda sz: c.f("GreatVibes-Regular.ttf", sz)
serif = lambda sz, w=500: c.f("PlayfairDisplay.ttf", sz, w)
seri = lambda sz, w=700: c.f("PlayfairDisplay-Italic.ttf", sz, w)
mont = lambda sz, w=500: c.f("Montserrat.ttf", sz, w)
LCX = (LX1 + LX2) / 2

def tc(x, yc, t, f, fill, align="c", sp=0, ref=None):            # ink centred on yc (blueprint px)
    bb = c.d.textbbox((0, 0), ref or t, font=f); c.text(x, yc - (bb[1] + bb[3]) / 2 / U, t, f, fill, align=align, sp=sp)

if not os.path.exists(PHOTO):
    tc(LCX, 470, "PICHA YA WANANDOA", mont(30, 600), (150, 146, 140), sp=5, ref="H")
    tc(LCX, 515, "(xxxx)", mont(26), (150, 146, 140))
tc(LCX - 40, 880, "Kelvin", script(124), GOLD, ref="K")
tc(LCX - 150, 958, "and", script(52), GOLD, ref="a")
tc(LCX + 50, 968, "Saraphina", script(124), GOLD, ref="S")
# date row: NOVEMBA | IJUMAA 13 | 2026
tc(LCX - 95, 1110, "NOVEMBA", serif(17), WHITE, align="c", ref="N")
tc(LCX, 1092, "IJUMAA", serif(16), WHITE, ref="I")
tc(LCX, 1120, "13", serif(36), WHITE, ref="1")
tc(LCX + 85, 1110, "2026", serif(17), WHITE, ref="2")
for x in (LCX - 44, LCX + 44): c.line(x, 1078, x, 1138, WHITE, 1.2)

# ---- right card text (axis = centre of the navy part)
CX = 1150
f1 = c.fit("INAYO FURAHA KUKUALIKA / KUWAALIKA", serif, 21, 470)
for yc, t in [(135, "FAMILIA YA"), (162, "BW. & BI. ANICETH MGIMBILA"), (189, "INAYO FURAHA KUKUALIKA / KUWAALIKA")]:
    tc(CX, yc, t, f1, WHITE, ref="H")
c.line(CX - 190, 284, CX + 190, 284, WHITE, 1.4)                     # guest-name line (writing room above)
tc(CX, 320, "KWENYE SHEREHE YA HARUSI YA", f1, WHITE, ref="H")
tc(CX, 347, "WAPENDWA WAO", f1, WHITE, ref="H")
tc(CX - 5, 433, "Kelvin & Saraphina", c.fit("Kelvin & Saraphina", script, 92, 430), GOLD, ref="K")
tc(CX, 522, "ITAKAYOFANYIKA IJUMAA", c.f("PlayfairDisplay.ttf", 21, 700), WHITE, ref="H")
c.line(975, 562, 1425, 562, (150, 116, 76), 1.6); c.line(975, 645, 1425, 645, (150, 116, 76), 1.6)
fd = serif(56, 800); dt = "13.11.2026"
ix = CX - (c.width(dt, fd) + 70) / 2
icon_calendar(c, ix, 584, 46, GOLD, width=3.5)
tc(ix + 70, 604, dt, fd, GOLD, align="l", ref="1")
for x, lines in [(1060, ["Ibada ya Ndoa", "Madibira Mission", "saa 4:00 asubuhi"]), (1338, ["Ukumbi", "Madibira Mission", "saa 1:00 jioni - 6:00 usiku"])]:
    tc(x, 752, lines[0], seri(21, 800), WHITE, ref="Ib")
    for j, t in enumerate(lines[1:]):
        tc(x, 778 + j * 26, t, c.fit(t, seri, 20, 240), WHITE, ref="Mx")
tc(CX, 851, "Mawasiliano", seri(21, 800), GOLD, ref="Mw")
for i, t in enumerate(["0675 656 176", "0680 104 878"]):
    tc(CX, 890 + i * 31, t, mont(21, 400), WHITE, ref="x0")
tc(CX, 988, "Rangi", seri(21, 800), WHITE, ref="R")
RANGI = [(183, 72, 28), (212, 175, 55), (122, 16, 32), (14, 14, 14)]   # rusty orange, gold, maroon, black (client 2026-11-12)
for i, col in enumerate(RANGI):
    x = CX - (4 * 52 + 3 * 18) / 2 + i * 70
    c.d.rounded_rectangle([c.P(x), c.P(1003), c.P(x + 52), c.P(1033)], radius=c.P(4), fill=col, outline=WHITE, width=c.P(1))
t = "(Rusty Orange, Gold, Maroon & Black)"; tc(CX, 1058, t, c.fit(t, lambda z: seri(z, 500), 19, 420), WHITE, ref="(x")
c.paste_logo(1000, 1104, 150, dark_bg=True, anchor="cm")
save_card(c.im, CLIENT + "/outputs/" + OUT, "Kelvin & Sarafina - Harusi", PREV, preview_w=1400)
print("saved", OUT, c.im.size)
