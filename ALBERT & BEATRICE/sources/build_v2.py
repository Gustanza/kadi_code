# Albert & Beatrice - WEDDING v2 - cream & maroon, photo in rounded frame (blueprint: Haflaway's own "Peter Daud" card,
# sources/blueprint_cream_maroon_peter_daud.png, 1024x1536). Rendered at U=2.
# run: ~/.haflaway/venv/bin/python build_v2.py [out_name]   (PHOTO=photo_B.jpeg CX=.. for the other photo)
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Albert_&_Beatrice_v2_final_01.png"
PREV = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/8d5d143e-4e6d-4e7a-9c03-6fcc9b8f790b/scratchpad/ab_v2_prev.jpg"
U = 2

src = cv2.imread(HERE + "/blueprint_cream_maroon_peter_daud.png"); H, W = src.shape[:2]
img = src.copy()

# ---- 1. remove template text (right column + contacts); rules, icons, ornament, QR, pill stay
bg = cv2.medianBlur(src, 41); diff = np.abs(src.astype(int) - bg.astype(int)).max(axis=2)
m = np.zeros((H, W), np.uint8)
for x1, y1, x2, y2 in [(520, 60, 975, 180), (505, 268, 980, 505), (618, 545, 945, 662), (618, 702, 870, 766),
                       (618, 822, 945, 912), (618, 965, 860, 1160), (530, 1236, 790, 1322), (492, 1285, 600, 1325)]:
    m[y1:y2, x1:x2] = (diff[y1:y2, x1:x2] > 18)*255
img = cv2.inpaint(img, cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=2), 9, cv2.INPAINT_TELEA)
m2 = np.zeros((H, W), np.uint8)                                             # second pass: faint halos left by pass 1
bg2 = cv2.medianBlur(img, 41); d2 = np.abs(img.astype(int) - bg2.astype(int)).max(axis=2)
for x1, y1, x2, y2 in [(520, 60, 975, 180), (505, 268, 980, 505), (618, 545, 945, 662), (618, 702, 870, 766),
                       (618, 822, 945, 912), (618, 965, 860, 1160), (530, 1236, 790, 1322), (492, 1285, 600, 1325)]:
    m2[y1:y2, x1:x2] = (d2[y1:y2, x1:x2] > 10)*255
img = cv2.inpaint(img, cv2.dilate(m2, np.ones((3, 3), np.uint8), iterations=2), 7, cv2.INPAINT_TELEA)
img[1336:1374, 606:762] = src[1336:1374, 606:762]                          # keep the gold pill = blank SINGLE/DOUBLE badge

# ---- 2. photo inside the rounded frame (flowers on top stay)
frame = np.zeros((H, W), np.uint8)
X1, Y1, X2, Y2, R = 44, 137, 473, 1029, 86
cv2.rectangle(frame, (X1 + R, Y1), (X2 - R, Y2), 255, -1); cv2.rectangle(frame, (X1, Y1 + R), (X2, Y2 - R), 255, -1)
for cx, cy in [(X1 + R, Y1 + R), (X2 - R, Y1 + R), (X1 + R, Y2 - R), (X2 - R, Y2 - R)]: cv2.circle(frame, (cx, cy), R, 255, -1)
hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
flow = ((hsv[:, :, 1] > 70) & (hsv[:, :, 2] > 60)).astype(np.uint8)        # roses, leaves, gold sprigs
flow[:, 300:] = 0; flow[272:740, :] = 0                                     # only the two flower clusters on the left
flow = cv2.morphologyEx(flow, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
cs, _ = cv2.findContours(flow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
flow = np.zeros_like(flow); cv2.drawContours(flow, [k for k in cs if cv2.contourArea(k) > 150], -1, 1, -1)   # fill blossom holes
keep = cv2.GaussianBlur((flow*255).astype(np.uint8), (5, 5), 0)
alpha = (frame.astype(np.float32)/255)*(1 - keep.astype(np.float32)/255)

card = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).resize((W*U, H*U), Image.LANCZOS)
PH = load_photo(HERE + "/" + os.environ.get("PHOTO", "photo_A.jpeg"))
pw, ph_ = (X2 - X1)*U, (Y2 - Y1)*U
ph = crop_to(upscale_soft(PH, 2.2), pw, ph_, cx_frac=float(os.environ.get("CX", "0.47")), top_frac=0.0, zoom=1.0)
layer = card.copy(); layer.paste(ph, (X1*U, Y1*U))
am = Image.fromarray((alpha*255).astype(np.uint8)).resize((W*U, H*U), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
card = Image.composite(layer, card, am)

# ---- 3. text
c = Card(card, U, resize=False)
MAR = (92, 14, 22); GOLD = (178, 128, 40); INK = (70, 40, 34)
cin = lambda sz, w=500: c.f("Cinzel.ttf", sz, w)
mont = lambda sz, w=500: c.f("Montserrat.ttf", sz, w)
CX = 740; MW = 450
fam = ["FAMILIA YA", "BW. & BI. LIBENT RAPHAEL ISHABAILU", "WA UKONGA MAJUMBA SITA, DAR ES SALAAM,", "WANAYO FURAHA KUKUALIKA / KUWAALIKA"]
for i, t in enumerate(fam):
    f = c.fit(t, lambda z: cin(z, 600), 17, MW - 10)
    while c.width(t, f, 3) > MW and f.size > 10: f = cin(f.size/U - 0.5, 600)
    c.text(CX, 66 + i*30, t, f, MAR, sp=3)
# maroon rule at 245 (template) = guest-name line, room above it
t = "KWENYE HARUSI YA VIJANA WAO"; c.text(CX, 256, t, mont(13, 600), GOLD, sp=4)
for t, y in [("ALBERT LIBENT", 284), ("BEATRICE ADELITUS", 430)]:
    c.text(CX, y, t, c.fit(t, lambda z: cin(z, 700), 60, MW), MAR)
for x1, x2 in [(560, 690), (778, 908)]: c.line(x1, 398, x2, 398, GOLD, 2)   # rules beside "&" (template ones survived? redrawn same place)
c.text(CX, 370, "&", c.f("PlayfairDisplay-Italic.ttf", 44, 500), GOLD)

TX = 626
lab = mont(15, 600); big = mont(19, 700); sm = mont(15, 400)
def tl(y, t, f, col, maxw=330):
    while c.width(t, f) > maxw and f.size > 8: f = mont(f.size/U - 0.5, 600 if f is lab else 400)
    c.text(TX, y, t, f, col, align="l")
tl(548, "UKUMBI", lab, GOLD); c.text(TX, 579, "GRAND PARADISE (PLATINUM)", c.fit("GRAND PARADISE (PLATINUM)", lambda z: mont(z, 700), 19, 320), MAR, align="l")
c.text(TX, 611, "YOMBO VITUKA, MWISHO WA LAMI", c.fit("YOMBO VITUKA, MWISHO WA LAMI", lambda z: mont(z, 400), 15, 320), INK, align="l")
c.text(TX, 636, "MUDA: KUANZIA SAA 12:00 JIONI", c.fit("MUDA: KUANZIA SAA 12:00 JIONI", lambda z: mont(z, 400), 15, 320), INK, align="l")
c.text(TX, 706, "TAREHE YA HARUSI", lab, GOLD, align="l")
c.text(TX, 737, "JUMAMOSI, 21/11/2026", big, MAR, align="l")
c.text(TX, 825, "MUDA WA KUFUNGA NDOA", lab, GOLD, align="l")
c.text(TX, 857, "SAA 9:00 ALASIRI", big, MAR, align="l")
t = "KANISA KATOLIKI, PAROKIA YA MSIMBAZI"; c.text(TX, 889, t, c.fit(t, lambda z: mont(z, 400), 15, 320), INK, align="l")
c.text(TX, 969, "RANGI ZA HARUSI", lab, GOLD, align="l")
for i, (col, nm) in enumerate([((153, 100, 52), "KAHAWIA"), ((40, 155, 240), "BLUE"), ((246, 246, 242), "NYEUPE")]):
    y = 1008 + i*38
    c.d.ellipse([c.P(629), c.P(y), c.P(661), c.P(y + 32)], fill=col, outline=(214, 196, 160), width=c.P(1.5))
    c.text(679, y + 6, nm, mont(16, 500), INK, align="l", sp=1)
t = "Watoto tunawapenda, lakini hawaruhusiwi."; c.text(TX, 1128, t, c.fit(t, lambda z: c.f("PlayfairDisplay-Italic.ttf", z, 500), 17, 320), MAR, align="l")

c.text(663, 1236, "MAWASILIANO", mont(15, 700), GOLD, sp=2)
for i, t in enumerate(["0715 194 900", "0694 026 550", "0788 016 290"]):
    c.text(663, 1259 + i*24, t, mont(18, 700), MAR, sp=1)
c.paste_logo(663, 1412, 150, anchor="cm")                                   # official Haflaway logo
save_card(c.im, CLIENT + "/outputs/" + OUT, "Albert & Beatrice - Harusi", PREV, preview_w=1100)
print("saved", OUT)
