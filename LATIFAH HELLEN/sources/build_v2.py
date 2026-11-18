# Latifa Hellen - KITCHEN PARTY v2 - navy & gold flowers (Envaita "Enock & Agness", 2200x2989)
# run: ~/.haflaway/venv/bin/python build_v2.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Latifa_Hellen_KitchenParty_v2_final_01.png"
PREV = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/8d5d143e-4e6d-4e7a-9c03-6fcc9b8f790b/scratchpad/lat_v2_prev.jpg"

src = cv2.imread(HERE + "/blueprint_navy_gold.jpeg"); H, W = src.shape[:2]
pin_icon = src[1645:1745, 1060:1170].copy()                      # keep the template's pin to reuse

# ---- clean template text (light pixels only inside each box; flowers/frame stay)
boxes = [(680,540,1545,700),(730,765,1475,832),(905,875,1315,980),(585,995,1720,1335),(955,1355,1265,1402),
         (1340,1432,1475,1562),(655,1582,955,1685),(1255,1562,1555,1702),(1060,1642,1172,1748),(990,1738,1225,1798),
         (695,1792,1565,1858),(1030,1912,1210,1962),(895,1958,1335,2058),(1000,2090,1200,2138),(790,2138,1410,2238),
         (960,2252,1265,2302),(722,2328,1572,2428),(415,2193,632,2255),(345,2700,705,2850)]
img = src.copy()
bg = cv2.medianBlur(src, 41)
m = np.zeros((H, W), np.uint8)
for x1, y1, x2, y2 in boxes:
    d = src[y1:y2, x1:x2].astype(int).max(axis=2) - bg[y1:y2, x1:x2].astype(int).max(axis=2)
    m[y1:y2, x1:x2] = np.where((d > 28) | (src[y1:y2, x1:x2].max(axis=2) > 95), 255, 0)
m[1962:2052, 900:1332] = 255                                        # old swatch circles (dark ones too)
img = cv2.inpaint(img, cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=2), 11, cv2.INPAINT_TELEA)
img[2318:2382, 692:745] = src[2446:2510, 692:745]                    # quote mark beside QR: plain navy patch
# ---- background colour (client 2026-11-07: "background iwe rangi ya shughuli" = sage, not navy/black)
BG = os.environ.get("BG"); BGS = {"DEEP_SAGE": (50, 77, 62), "SAGE": (116, 139, 111)}
if BG:
    from bg_recolor import recolor_dark_bg
    img = recolor_dark_bg(img, BGS[BG])
    pin_icon = recolor_dark_bg(pin_icon, BGS[BG])
card = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
c = Card(card, 1.0)
GOLD = (202, 185, 136); WHITE = (238, 243, 247); NAVY = (16, 20, 34)
if BG == "SAGE": GOLD = (246, 234, 196)                           # gold text -> champagne for contrast on mid sage
serif = lambda sz, w=500: c.f("PlayfairDisplay.ttf", sz, w)
ital = lambda sz, w=500: c.f("PlayfairDisplay-Italic.ttf", sz, w)
script = lambda sz: c.f("GreatVibes-Regular.ttf", sz)

def tc(x, yc, t, f, fill, sp=0):                                   # text whose INK is centred on (x, yc)
    bb = c.d.textbbox((0, 0), t, font=f); c.text(x, yc - (bb[1] + bb[3])/2, t, f, fill, sp=sp)

AX = 1110; TW = 860                                                # text axis + max text width
fit = lambda t, mk, sz, w=TW: c.fit(t, mk, sz, w)

# family block
for yc, t in [(578, "BI. VALERIE CHILIPWELI LING'ANDE"), (642, "WA MBWENI, DAR ES SALAAM"),
              (706, "ANAYO FURAHA KUKUALIKA / KUWAALIKA")]:
    tc(AX, yc, t, fit(t, serif, 46), WHITE)
c.line(AX - 330, 842, AX + 330, 842, GOLD, 3)                     # guest-name line (writing room above)
tc(AX, 912, "KATIKA KITCHEN PARTY YA", serif(46), WHITE)
tc(AX, 976, "BINTI YAKE MPENDWA", serif(46), WHITE)
# name
tc(AX, 1135, "Latifa Hellen", fit("Latifa Hellen", script, 250, 1000), GOLD)
tc(AX, 1290, "KITCHEN PARTY", serif(44, 600), WHITE, sp=10)
tc(AX, 1380, "ITAKAYOFANYIKA", serif(44), WHITE, sp=2)
# two columns: date | venue   (template divider at x~1110 is kept)
LX, RX = 805, 1405
pin = Image.fromarray(cv2.cvtColor(pin_icon, cv2.COLOR_BGR2RGB)).resize((132, 120), Image.LANCZOS)
c.im.paste(pin, (RX - 66, 1440))
tc(LX, 1616, "Jumapili", ital(46, 700), WHITE)
tc(LX, 1672, "15 Novemba, 2026", ital(46, 700), WHITE)
tc(RX, 1616, "Ukumbi", ital(46, 700), WHITE)
tc(RX, 1672, "Jaks - Africana", ital(46, 700), WHITE)
tc(RX, 1726, "kuanzia saa 10:00 jioni", ital(38), GOLD)
# rangi
tc(AX, 1812, "RANGI", ital(48, 800), WHITE, sp=2)
SAGE = [(50, 77, 62), (116, 139, 111), (142, 166, 140), (191, 208, 189), (219, 229, 218)]
swatches(c, AX, 1852, SAGE, size=78, gap=20, outline=(235, 235, 230))
tc(AX, 1972, "(Shades of Sage Green)", ital(40), GOLD)
# contacts
tc(AX, 2052, "MAWASILIANO", serif(46, 700), WHITE, sp=2)
tc(AX, 2110, "MARIA HAULE - 0784 362 180", serif(44), WHITE)
tc(AX, 2164, "IRENE MDAMI - 0784 268 720", serif(44), WHITE)
# closing paragraph (template verse slot) - clear of the QR (left) and flowers (right)
para = ["Hii ni siku maalum kwa familia yetu, na uwepo",
        "wako utaifanya kuwa ya kukumbukwa zaidi.",
        "Karibu tusherehekee pamoja na Latifa katika",
        "hatua hii mpya ya maisha yake."]
fp = min((fit(t, ital, 40, 740) for t in para), key=lambda f: f.size)
for i, t in enumerate(para): tc(AX, 2252 + i*48, t, fp, WHITE)
tc(AX, 2456, "Karibuni sana,", ital(42, 700), GOLD)
tc(AX, 2508, "Familia ya Bi. Valerie", ital(42, 700), GOLD)
# badge left blank (outline kept), QR kept, logo
c.paste_logo(523, 2775, 330, dark_bg=True, anchor="cm")
save_card(c.im, CLIENT + "/outputs/" + OUT, "Latifa Hellen - Kitchen Party", PREV, preview_w=1100)
print("saved", OUT)
