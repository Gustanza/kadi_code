# Marymanka Aurelian - SEND-OFF v1 - Envaita cream & rose-gold arch blueprint with wax seal
# (blueprint_cream_rosegold_seal_arch.jpeg, 2076x2717, dummy "Joseph & Noela" wedding).  Rendered at 1x (full-res blueprint).
# run: ~/.haflaway/venv/bin/python build_v1.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Marymanka_Aurelian_SendOff_v1_final_01.png"
SCR = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/39ac5a94-2c35-48a2-a078-0faa4526b442/scratchpad/"
K = 1

src = cv2.imread(HERE + "/blueprint_cream_rosegold_seal_arch.jpeg"); H0, W0 = src.shape[:2]

# ------------------------------------------------------------------ 1. clean the dummy text / icons / chips / logo
TEXT = [(615, 714, 1448, 908),      # family block
        (721, 952, 1367, 1008),     # guest name (Mr & Mrs Praygod Mangi)
        (782, 1031, 1285, 1129),    # to the wedding ceremony...
        (650, 1128, 1420, 1314),    # names + surnames
        (938, 1349, 1136, 1392),    # to be held on
        (741, 1387, 952, 1675),     # calendar + date
        (1112, 1398, 1444, 1654),   # church icon + service
        (768, 1659, 1306, 1845),    # pin + reception + hall
        (857, 1868, 1272, 2008),    # dress code + chips
        (768, 2031, 1376, 2171)]    # rsvp + contacts
# solid shapes first (bigger than the median window): church disc, colour chips, Envaita logo -> local paper colour
SOLID = [(1222, 1398, 1350, 1500), (850, 1918, 1280, 2008), (1344, 2500, 1582, 2582), (1358, 2490, 1434, 2504)]
clean = src.copy().astype(np.float32)
for x1, y1, x2, y2 in SOLID:
    ring = np.concatenate([clean[y2 + 4:y2 + 14, x1:x2].reshape(-1, 3),                     # below + sides (above may hold the arch line)
                           clean[y1:y2, x1 - 14:x1 - 4].reshape(-1, 3), clean[y1:y2, x2 + 4:x2 + 14].reshape(-1, 3)])
    col = np.median(ring, axis=0)
    m = np.zeros((H0, W0), np.float32); m[y1:y2, x1:x2] = 1; m = cv2.GaussianBlur(m, (0, 0), 1.5)[..., None]
    clean = col*m + clean*(1 - m)
clean = clean.astype(np.uint8)
for b in TEXT: clean = clean_by_background(clean, b, thr=18, blur=61)
zm = np.zeros((H0, W0), np.float32)
for x1, y1, x2, y2 in TEXT: zm[y1:y2, x1:x2] = 1
zm = cv2.GaussianBlur(zm, (0, 0), 4)[..., None]
clean = (cv2.GaussianBlur(clean, (0, 0), 6)*zm + clean*(1 - zm)).astype(np.uint8)
cv2.imwrite(SCR + "ma_clean.jpg", clean)

# ------------------------------------------------------------------ 2. content (blueprint px, 1x)
card = Image.fromarray(cv2.cvtColor(clean, cv2.COLOR_BGR2RGB)); c = Card(card, K, resize=False)
INK = (38, 35, 33); GOLD = (176, 110, 20); BADGE = (136, 128, 126)
BUTTER, BROWN = (247, 228, 150), (111, 71, 42)                      # Rangi: Butter Yellow & Brown
ital = lambda sz, wt=500: c.f("PlayfairDisplay-Italic.ttf", sz, wt)
serif = lambda sz, wt=500: c.f("PlayfairDisplay.ttf", sz, wt)
scr = lambda sz: c.f("GreatVibes-Regular.ttf", sz)
def tc(x, yc, t, f, fill, sp=0):
    bb = c.d.textbbox((0, 0), t, font=f); c.text(x, yc - (bb[1] + bb[3])/2, t, f, fill, sp=sp)
AX = 1036
fam = ["Familia ya", "Mr & Mrs Aurelian", "wa Kimara Bonyokwa, Dar es Salaam,", "wanayo furaha kukualika/kuwaalika"]
ff = min((c.fit(s, lambda z: ital(z), 42, 760) for s in fam), key=lambda f: f.size)
for i, s in enumerate(fam): tc(AX, 734 + i*51, s, ff, INK)
c.line(AX - 250, 1004, AX + 250, 1004, GOLD, 2.2)                                   # blank guest-name line
for i, s in enumerate(["kwenye hafla ya kumuaga", "binti yao mpendwa"]): tc(AX, 1058 + i*50, s, ff, INK)
tc(AX, 1216, "Marymanka", c.fit("Marymanka", scr, 150, 700), GOLD)
tc(AX, 1302, "AURELIAN", serif(34, 700), INK, sp=7)
tc(AX, 1370, "itakayofanyika", ital(38), INK)
# left column: calendar + date
L, R = 845, 1272
icon_calendar(c, L - 58, 1402, 116, GOLD, 7)
tc(L, 1560, "Jumatano", ital(38), INK); tc(L, 1606, "18 Novemba", ital(42, 800), INK); tc(L, 1650, "2026", ital(36), INK)
# right column: time (gold disc + white clock, like the blueprint's church disc)
cx, cy, r = R, 1452, 54
c.d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD)
c.d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], outline=(255, 255, 255), width=6)
c.line(cx, cy, cx, cy - 20, (255, 255, 255), 6); c.line(cx, cy, cx + 15, cy + 8, (255, 255, 255), 6)
tc(R, 1560, "Muda", ital(40, 800), INK); tc(R, 1606, "Kuanzia", ital(38), INK); tc(R, 1650, "saa 12:00 jioni", ital(38), INK)
# venue
icon_pin(c, AX, 1680, 54, GOLD, (236, 236, 230))
tc(AX, 1758, "Ukumbi", ital(40, 800), INK)
tc(AX, 1806, "Modamba Hall – Goba Center", ital(40), INK)
# rangi
tc(AX, 1864, "Rangi", ital(40, 800), INK)
for i, col in enumerate([BUTTER, BROWN]):
    x0 = AX - 105 + i*115; c.d.rectangle([x0, 1890, x0 + 95, 1942], fill=col, outline=(200, 170, 120), width=2)
tc(AX, 1972, "(Butter Yellow & Brown)", ital(32), INK)
# mawasiliano
tc(AX, 2024, "Mawasiliano", ital(40, 800), INK)
CON = [("SISTU P. MALLYA", phone("0754669897")), ("THEOPHAN PANTALEY", "07825830"), ("EMMANUEL AURELIAN", phone("+255655659097"))]
fc = min((c.fit(f"{n} - {p}", lambda z: serif(z, 500), 31, 640) for n, p in CON), key=lambda f: f.size)
for i, (n, p) in enumerate(CON): tc(AX, 2066 + i*40, f"{n} - {p}", fc, INK)
# blank badge (system fills SINGLE/DOUBLE), QR placeholder stays, Haflaway logo in place of Envaita
c.d.rounded_rectangle([548, 2198, 774, 2266], 12, fill=BADGE)
c.paste_logo(1352, 2537, 225, dark_bg=False)
save_card(card, CLIENT + "/outputs/" + OUT, "Marymanka Aurelian - Send-Off", SCR + "ma_prev.jpg", 1100)
print("saved", OUT, card.size)
