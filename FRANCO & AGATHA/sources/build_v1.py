# Franco & Agatha - WEDDING v1 - white & gold oval "Save the Date" blueprint (sources/blueprint_white_gold_oval_save_the_date.jpeg,
# 736x1031, foreign template: all its text/photo wiped) turned into a full invitation. Rendered at U=3.
# run: ~/.haflaway/venv/bin/python build_v1.py [out_name]     (PHOTO=photo_3U1A1858.jpeg ZOOM/CX/TOP to try another photo)
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Franco_&_Agatha_v1_final_01.png"
PREV = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/8d5d143e-4e6d-4e7a-9c03-6fcc9b8f790b/scratchpad/fa_v1_prev.jpg"
U = 3
src = cv2.imread(HERE + "/blueprint_white_gold_oval_save_the_date.jpeg"); H, W = src.shape[:2]

# ---- 1. empty the oval panel (gold oval line x 130..605, y 42..986)
OX, HW, TOPC, BOTC = 367, 237, 42 + 237, 986 - 237
ov = np.zeros((H, W), np.uint8)
cv2.ellipse(ov, (OX, TOPC), (HW, HW), 0, 180, 360, 255, -1); cv2.ellipse(ov, (OX, BOTC), (HW, HW), 0, 0, 180, 255, -1)
cv2.rectangle(ov, (OX - HW, TOPC), (OX + HW, BOTC), 255, -1)
inner = cv2.erode(ov, np.ones((25, 25), np.uint8))                     # everything 12 px inside the line
s4 = cv2.resize(src, (W//4, H//4), interpolation=cv2.INTER_AREA); m4 = cv2.resize(inner, (W//4, H//4), interpolation=cv2.INTER_NEAREST)
fill = cv2.resize(cv2.inpaint(s4, m4, 9, cv2.INPAINT_TELEA), (W, H), interpolation=cv2.INTER_CUBIC)
fill = cv2.GaussianBlur(fill, (0, 0), 8)
a = cv2.GaussianBlur(inner.astype(np.float32)/255, (0, 0), 3)[:, :, None]
img = (src*(1 - a) + fill*a).astype(np.uint8)
card = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).resize((W*U, H*U), Image.LANCZOS)
P = lambda v: round(v*U)

# ---- 2. photo in an arch window with a thin gold line
AX1, AX2, AY1, AY2 = 222, 512, 296, 560
ph = load_photo(HERE + "/" + os.environ.get("PHOTO", "photo_3U1A1868.jpeg"))
ph = crop_to(ph, P(AX2 - AX1), P(AY2 - AY1), cx_frac=float(os.environ.get("CX", "0.5")),
             top_frac=float(os.environ.get("TOP", "0.0")), zoom=float(os.environ.get("ZOOM", "1.42")))
am = Image.new("L", ph.size, 0); d = ImageDraw.Draw(am); r = P((AX2 - AX1)/2)
d.ellipse([0, 0, ph.width - 1, 2*r], fill=255); d.rectangle([0, r, ph.width, ph.height], fill=255)
card.paste(ph, (P(AX1), P(AY1)), am.filter(ImageFilter.GaussianBlur(1.5)))
c = Card(card, U, resize=False)
GOLD = (176, 138, 72); GOLD_D = (150, 112, 50); GREEN = (46, 78, 58); INK = (52, 46, 42); BOX = (62, 46, 22)
def arch_line(x1, x2, y1, y2, col, w):
    rr = (x2 - x1)/2
    c.d.arc([P(x1), P(y1), P(x2), P(y1 + 2*rr)], 180, 360, fill=col, width=P(w))
    for x in (x1, x2): c.line(x, y1 + rr, x, y2, col, w)
    c.line(x1, y2, x2, y2, col, w)
arch_line(AX1 - 5, AX2 + 5, AY1 - 5, AY2 + 5, GOLD, 1.6)

mont = lambda z, w=600: c.f("Montserrat.ttf", z, w)
pit = lambda z, w=500: c.f("PlayfairDisplay-Italic.ttf", z, w)
scr = lambda z: c.f("GreatVibes-Regular.ttf", z)
CX = OX
def tc(y, t, f, col, sp=0):                                              # centre the INK of t on the oval axis
    c.text(CX, y, t, f, col, sp=sp)

# ---- 3. text
tc(96, "Mwaliko wa Harusi", c.fit("Mwaliko wa Harusi", scr, 60, 320), GREEN)
for i, t in enumerate(["Familia ya Mzee Charles Atilyo Yetula", "wa Kawe, Dar es Salaam, inayo furaha", "kukualika / kuwaalika"]):
    tc(178 + i*21, t, c.fit(t, lambda z: mont(z, 600 if i == 0 else 500), 16, 390), INK)
c.line(252, 262, 482, 262, GOLD, 1.2)                                    # guest-name line
t = "kwenye sherehe ya harusi ya vijana wao"; tc(268, t, c.fit(t, pit, 16, 380), INK)
tc(566, "Franco & Agatha", c.fit("Franco & Agatha", scr, 66, 400), GOLD_D)
# date pill (blueprint style: outline pill + dark centre box)
PY1, PY2 = 664, 712
c.d.rounded_rectangle([P(176), P(PY1), P(558), P(PY2)], P(24), outline=GOLD, width=P(1.6))
c.d.rounded_rectangle([P(323), P(PY1 - 10), P(411), P(PY2 + 10)], P(5), fill=BOX)
tc_ = lambda x, y, t, f, col, sp=0: c.text(x, y, t, f, col, sp=sp)
tc_(250, 680, "JUMAMOSI", mont(14, 700), GOLD_D, sp=1)
t = "SAA 9:00 ALASIRI"; tc_(485, 681, t, c.fit(t, lambda z: mont(z, 700), 14, 132), GOLD_D)
tc_(367, 656, "NOVEMBA", mont(11.5, 600), (255, 255, 255), sp=0.5)
tc_(367, 667, "28", mont(27, 700), (255, 255, 255))
tc_(367, 702, "2026", mont(11.5, 600), (255, 255, 255), sp=1)
tc(740, "IBADA YA NDOA", mont(13.5, 700), GOLD_D, sp=2)
t = "Kanisa la Mt. Maximilian Kolbe, Mwenge"; tc(758, t, c.fit(t, lambda z: mont(z, 500), 17, 405), INK)
tc(792, "UKUMBI  \u2022  JUMAPILI 29.11.2026", mont(13.5, 700), GOLD_D, sp=1.5)
t = "Jaks Hall, Mbezi Africana  -  saa 10:00 alasiri"; tc(810, t, c.fit(t, lambda z: mont(z, 500), 17, 405), INK)
tc(844, "MAWASILIANO", mont(13.5, 700), GOLD_D, sp=2)
for i, t in enumerate(["0713 398 540  -  Enock Mayao", "0653 099 773  -  Jimmy Atilyo"]):
    tc(862 + i*21, t, mont(16, 500), INK)
c.paste_logo(CX, 928, 128, anchor="cm")                                  # official Haflaway logo
save_card(c.im, CLIENT + "/outputs/" + OUT, "Franco & Agatha - Harusi", PREV, preview_w=1000)
print("saved", OUT)
