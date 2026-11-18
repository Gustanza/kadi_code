# Latifa Hellen - KITCHEN PARTY v3 - black & cream/gold 3D flowers (ekadi Ekadi_109, 3020x3652; same blueprint as Hafidh & Lamlaty)
# run: ~/.haflaway/venv/bin/python build_v3.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Latifa_Hellen_KitchenParty_v3_final_01.png"
PREV = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/8d5d143e-4e6d-4e7a-9c03-6fcc9b8f790b/scratchpad/lat_v3_prev.jpg"

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
wt = np.median(pill[inner], axis=0)
img[2114:2186, 1364:1656] = wt
# ---- background colour (client 2026-11-07: "background iwe rangi ya shughuli" = sage, not navy/black)
BG = os.environ.get("BG"); BGS = {"DEEP_SAGE": (50, 77, 62), "SAGE": (116, 139, 111)}
if BG:
    from dark_recolor import recolor          # smooth Lab tone-map recolour (agent-reviewed winner, 2026-11-07)
    img = recolor(img, BGS[BG])
card = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
c = Card(card, 1.0)
GOLD = (225, 195, 137); WHITE = (252, 252, 252)
if BG == "SAGE": GOLD = (246, 234, 196)                           # gold text -> champagne for contrast on mid sage
mont = lambda sz, w=600: c.f("Montserrat.ttf", sz, w)
script = lambda sz: c.f("GreatVibes-Regular.ttf", sz)

def tc(x, yc, t, f, fill, align="c"):                             # ink centred vertically on yc
    bb = c.d.textbbox((0, 0), t, font=f); c.text(x, yc - (bb[1] + bb[3])/2, t, f, fill, align=align)

AX = 1510
for yc, t in [(734, "Bi. Valerie Chilipweli Ling'ande"), (818, "wa Mbweni, Dar es Salaam"),
              (902, "anayo furaha kukualika / kuwaalika")]:
    tc(AX, yc, t, c.fit(t, mont, 64, 1150), GOLD)
# template gold rule at y~1061 is the guest-name line (writing room above it)
tc(AX, 1170, "katika Kitchen Party ya binti", mont(62), GOLD)
tc(AX, 1260, "yake mpendwa", mont(62), GOLD)
tc(AX, 1478, "Latifa Hellen", c.fit("Latifa Hellen", script, 270, 1300), WHITE)
tc(AX, 1723, "itakayofanyika siku ya", mont(62), GOLD)
tc(AX, 1932, "Jumapili, 15 Novemba 2026", c.fit("Jumapili, 15 Novemba 2026", lambda z: mont(z, 700), 70, 860), WHITE)
# label / value rows
lab = mont(62, 700); val = mont(60)
GAP = 367                                                          # label column -> value column (template)
vals = ["Jaks - Africana,", "kuanzia saa 10:00 jioni.", "Shades of Sage Green", "Maria Haule - 0784 362 180", "Irene Mdami - 0784 268 720"]
BW = GAP + max(c.width(t, val) for t in vals)                      # whole label/value block width
LX = AX - BW/2; VX = LX + GAP                                      # block centred on the card axis
tc(LX, 2312, "Ukumbi:", lab, WHITE, "l")
tc(VX, 2312, "Jaks - Africana,", val, GOLD, "l")
tc(VX, 2398, "kuanzia saa 10:00 jioni.", val, GOLD, "l")
tc(LX, 2505, "Rangi:", lab, WHITE, "l")
tc(VX, 2505, "Shades of Sage Green", val, GOLD, "l")
SAGE = [(50, 77, 62), (116, 139, 111), (142, 166, 140), (191, 208, 189), (219, 229, 218)]
sz, gp = 72, 22
swatches(c, VX + (5*sz + 4*gp)/2, 2560, SAGE, size=sz, gap=gp, outline=GOLD)
tc(LX, 2706, "Mawasiliano:", lab, WHITE, "l")
tc(VX, 2792, "Maria Haule - 0784 362 180", val, GOLD, "l")
tc(VX, 2876, "Irene Mdami - 0784 268 720", val, GOLD, "l")
# QR kept (placeholder); logo where ekadi was
c.paste_logo(AX - 85, 3330, 300, dark_bg=True, anchor="cm")
save_card(c.im, CLIENT + "/outputs/" + OUT, "Latifa Hellen - Kitchen Party", PREV, preview_w=1100)
print("saved", OUT)
