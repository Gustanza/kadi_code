# Latifa Hellen - KITCHEN PARTY v4 - "Sage Green Luxurious" blueprint (1076x1462, already carries Latifa's text on sage #748B6F-ish)
# Lower block (Rangi -> closing) is wiped and redrawn: correct sage swatches, NEW "Theme: Nigerian Attire" line
# under the colours (client 2026-11-07), typo "utafanya" -> "utaifanya".  Rendered at 2x.
# run: ~/.haflaway/venv/bin/python build_v4.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Latifa_Hellen_KitchenParty_v4_final_01.png"
PREV = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/8d5d143e-4e6d-4e7a-9c03-6fcc9b8f790b/scratchpad/lat_v4_prev.jpg"
K = 2

src = cv2.imread(HERE + "/blueprint_sage_luxurious.png")
src = cv2.resize(src, None, fx=K, fy=K, interpolation=cv2.INTER_LANCZOS4); H, W = src.shape[:2]
bg = cv2.medianBlur(src, 61)
m = np.zeros((H, W), np.uint8)
for x1, y1, x2, y2 in [(345, 855, 745, 1062), (345, 1076, 742, 1174), (418, 1172, 672, 1240), (598, 792, 778, 822)]:          # blueprint px (x1)
    x1, y1, x2, y2 = [v*K for v in (x1, y1, x2, y2)]
    d = src[y1:y2, x1:x2].astype(int).max(axis=2) - bg[y1:y2, x1:x2].astype(int).max(axis=2)
    m[y1:y2, x1:x2] = np.where(d > 12, 255, 0)
m[888*K:942*K, 420*K:668*K] = 255                                 # old swatches incl. their soft shadows
img = cv2.inpaint(src, cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=2), 13, cv2.INPAINT_TELEA)
# smooth the inpainted zone (inpaint leaves streaky ghosts on this soft gradient paper)
mz = m.copy(); mz[780*K:835*K, 590*K:790*K] = 0                   # venue line: inpaint only (no blur near Ukumbi/kuanzia)
zone = cv2.dilate(mz, np.ones((25, 25), np.uint8))
zone = cv2.GaussianBlur(zone.astype(np.float32)/255, (0, 0), 8)[..., None]
img = (cv2.GaussianBlur(img, (0, 0), 18).astype(np.float32)*zone + img.astype(np.float32)*(1 - zone)).astype(np.uint8)
card = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
c = Card(card, K, resize=False)                                                 # draw in blueprint units
GOLD = (240, 206, 98); WHITE = (236, 243, 228)
serif = lambda sz, w=500: c.f("PlayfairDisplay.ttf", sz, w)
ital = lambda sz, w=500: c.f("PlayfairDisplay-Italic.ttf", sz, w)

def tc(x, yc, t, f, fill):                                          # ink centred on yc (blueprint units)
    bb = c.d.textbbox((0, 0), t, font=f); c.text(x, yc - (bb[1] + bb[3])/2/K, t, f, fill)

AX = 544
# sizes matched to the upper half of the card (caps lines there are 16 px cap height = Playfair ~22.5)
tc(AX, 874, "RANGI", ital(22, 800), WHITE)
SAGE = [(50, 77, 62), (116, 139, 111), (142, 166, 140), (191, 208, 189), (219, 229, 218)]
swatches(c, AX, 890, SAGE, size=36, gap=10, outline=(240, 240, 232))
tc(AX, 944, "(Shades of Sage Green)", ital(18, 700), GOLD)
f_l, f_v = ital(22, 700), ital(22, 800)
lab, val = "Theme: ", "Nigerian Attire"
wl, wv = c.width(lab, f_l), c.width(val, f_v); x0 = AX - (wl + wv)/2
bb = c.d.textbbox((0, 0), lab + val, font=f_v); yt = 974 - (bb[1] + bb[3])/2/K
c.text(x0, yt, lab, f_l, WHITE, align="l"); c.text(x0 + wl, yt, val, f_v, GOLD, align="l")
tc(AX, 1008, "MAWASILIANO", serif(22.5, 700), WHITE)
tc(AX, 1036, "MARIA HAULE - 0784 362 180", serif(22.5), WHITE)
tc(AX, 1064, "IRENE MDAMI - 0784 268 720", serif(22.5), WHITE)
para = ["Hii ni siku maalum kwa familia yetu,",
        "na uwepo wako utaifanya kuwa ya",
        "kukumbukwa zaidi. Karibu tusherehekee",
        "pamoja na Latifa katika hatua hii",
        "mpya ya maisha yake."]
fp = min((c.fit(t, ital, 20, 370) for t in para), key=lambda f: f.size)
for i, t in enumerate(para): tc(AX, 1098 + i*25, t, fp, WHITE)
# venue: client "usisahau Jaks Hall" (2026-11-08) - same style as the blueprint line (Playfair Italic 800, ~21.5)
tc(687.5, 806.5, "Jaks Hall \u2013 Africana", ital(21.5, 800), WHITE)
# "Karibuni sana, Familia ya Bi. Valerie" removed (2026-11-07, user request)
save_card(c.im, CLIENT + "/outputs/" + OUT, "Latifa Hellen - Kitchen Party", PREV, preview_w=1100)
print("saved", OUT)
