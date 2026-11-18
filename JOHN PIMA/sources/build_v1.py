# John & Vedastina - WEDDING v1 - beach photo + white sprigs blueprint (ekadi template, 1395x1966). Rendered at 1.5x.
# Family, contacts and church time are BOILERPLATE until the client sends them (see details.txt).
# run: ~/.haflaway/venv/bin/python build_v1.py [out_name] [preview]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *
from pymatting import estimate_alpha_cf, estimate_foreground_ml

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "John_&_Vedastina_v1_final_01.png"
PREV = sys.argv[2] if len(sys.argv) > 2 else None
K = 1.5; FLAT = 236

# ---- 1. cut the couple out of the photo (hand silhouette -> trimap -> closed-form matting)
ph = cv2.imread(HERE + "/photo_john_vedastina.jpeg")[:770]
POLY = [(262,42),(290,43),(308,62),(322,100),(340,145),(338,165),(328,188),(320,205),(335,207),(355,200),(372,212),(388,240),
        (402,275),(416,310),(440,290),(470,265),(500,251),(516,240),(516,214),(500,180),(494,162),(492,125),(510,92),(548,76),(585,88),
        (606,128),(604,175),(598,205),(580,212),(590,232),(620,240),(636,262),(645,300),(650,370),(650,440),(653,530),(662,630),
        (675,769),(165,769),(158,680),(130,640),(125,612),(106,590),(90,480),(84,375),(90,320),(105,255),(125,227),(170,206),
        (206,184),(215,170),(212,150),(203,110),(205,75),(228,52)]
SC = 2                                                                     # matte at 2x so edges stay clean after scaling
ph2 = cv2.resize(ph, None, fx=SC, fy=SC, interpolation=cv2.INTER_CUBIC)
mask = np.zeros(ph2.shape[:2], np.uint8); cv2.fillPoly(mask, [np.array(POLY, np.int32)*SC], 255)
B = 13*SC; ell = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (B, B))
tri = np.full(mask.shape, 0.5, np.float64); tri[cv2.erode(mask, ell) > 0] = 1; tri[cv2.dilate(mask, ell) == 0] = 0
for scribble in [[(95,195),(204,160),(204,176),(168,197),(124,219),(100,245)], [(478,240),(508,205),(511,232),(496,243),(475,254)]]:
    sb = np.zeros(mask.shape, np.uint8); cv2.fillPoly(sb, [np.array(scribble, np.int32)*SC], 1); tri[sb > 0] = 0   # sure backdrop
rgb = cv2.cvtColor(ph2, cv2.COLOR_BGR2RGB).astype(np.float64)/255
alpha = estimate_alpha_cf(rgb, tri)
fg = estimate_foreground_ml(rgb, alpha)                                    # removes the red/white backdrop spill from the edges
alpha = np.clip((alpha - 0.08)/0.84, 0, 1)

# ---- 2. blueprint: remove the model and all template text, keep scene + sprigs
src = cv2.imread(HERE + "/blueprint_photo_white_sprigs.jpg"); H, W = src.shape[:2]
hole = np.zeros((H, W), np.uint8)
MODEL = [(640,160),(700,148),(780,152),(835,195),(900,280),(900,335),(850,390),(822,400),(850,470),(900,480),(945,600),(955,780),
         (1035,780),(1035,1015),(365,1015),(365,780),(500,780),(505,660),(535,560),(575,495),(625,440),(625,375),(540,300),(540,262),(600,230)]
cv2.fillPoly(hole, [np.array(MODEL, np.int32)], 1)                          # only the model + text: the real hill/sky around her stays
# smooth (harmonic) fill from all four sides, at low res: the scene behind the model is soft anyway
D = 6
small = cv2.resize(src, (W//D, H//D), interpolation=cv2.INTER_AREA).astype(np.float32)
hs = cv2.resize(hole, (W//D, H//D), interpolation=cv2.INTER_NEAREST) > 0
hs = cv2.dilate(hs.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
u = small.copy(); u[hs] = small[~hs].mean(axis=0)
for _ in range(6000):
    v = cv2.blur(u, (3, 3)); u[hs] = v[hs]
fill = cv2.GaussianBlur(cv2.resize(u, (W, H), interpolation=cv2.INTER_CUBIC), (0, 0), 6)
z = cv2.GaussianBlur(cv2.dilate(hole, np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 5)[..., None]
img = np.clip(src.astype(np.float32)*(1 - z) + fill*z, 0, 255).astype(np.uint8)
img[1014:1030, 280:1115] = src[1014:1030, 280:1115]                        # guest line stays crisp
for x1, y1, x2, y2 in [(365,1040,1030,1140),(360,1170,1040,1262),(480,1298,915,1348),(405,1398,610,1456),(405,1468,610,1520),
                       (625,1412,788,1512),(803,1398,1000,1456),(803,1468,1000,1520),(335,1585,1125,1782),(248,1786,1150,1830),
                       (535,1830,1150,1880),(635,1905,762,1952)]:
    img[y1:y2, x1:x2] = FLAT
img[1722:1754, 1192:1338] = 0                                              # badge: blank pill (system fills single/double)

# ---- 3. couple onto the scene (heads between the sprigs, fades away above the text like the template's model)
S = 1.4; X0, Y0 = 235 - 84*S, 225 - 42*S
card = cv2.resize(img, None, fx=K, fy=K, interpolation=cv2.INTER_LANCZOS4).astype(np.float32); CH, CW = card.shape[:2]
f = K*S/SC
fgs = cv2.resize(fg.astype(np.float32), None, fx=f, fy=f, interpolation=cv2.INTER_LANCZOS4)[..., ::-1]*255
als = np.clip(cv2.resize(alpha.astype(np.float32), None, fx=f, fy=f, interpolation=cv2.INTER_CUBIC), 0, 1)
ox, oy = int(round(X0*K)), int(round(Y0*K)); h = min(fgs.shape[0], CH - oy); w = min(fgs.shape[1], CW - ox)
yy = (np.arange(h, dtype=np.float32) + oy)/K
t = np.clip((yy - 650)/(805 - 650), 0, 1); fade = 1 - t*t*(3 - 2*t)        # blueprint units
a = (als[:h, :w]*fade[:, None])[..., None]
card[oy:oy+h, ox:ox+w] = fgs[:h, :w]*a + card[oy:oy+h, ox:ox+w]*(1 - a)
card = Image.fromarray(cv2.cvtColor(np.clip(card, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB))

# ---- 4. text (blueprint units)
c = Card(card, K, resize=False)
INK = (22, 20, 18); GOLD = (201, 162, 74); BLACK = (17, 17, 17)
eb = lambda sz, w=600: c.f("EBGaramond.ttf", sz, w)
def tc(x, yc, t, f, fill=INK, align="c"):
    if align == "r": x -= c.width(t, f); align = "l"
    bb = c.d.textbbox((0, 0), "Hx", font=f); c.text(x, yc - (bb[1] + bb[3])/2/K, t, f, fill, align=align)   # shared baseline per size
AX = 697
for yc, t in [(810, "Familia ya Bw. & Bi. Pima John"), (860, "wa Kitunda, Dar es Salaam"), (910, "wanayo furaha kukualika / kuwaalika")]:
    tc(AX, yc, t, eb(40))
tc(AX, 1065, "kwenye harusi ya", eb(40)); tc(AX, 1115, "wapendwa wao", eb(40))
tc(AX, 1215, "JOHN & VEDASTINA", c.fit("JOHN & VEDASTINA", lambda z: c.f("Cinzel.ttf", z, 600), 78, 860))
tc(AX, 1322, "itakayofanyika siku ya", eb(40))
d = eb(37)
tc(505, 1426, "Jumamosi", d); tc(505, 1494, "Saa 12:00 jioni", c.fit("Saa 12:00 jioni", eb, 37, 196))
tc(899, 1426, "Novemba", d); tc(899, 1494, "2026", d)
tc(706, 1462, "28", eb(92, 700))
LX, VX = 492, 543; lab = eb(36, 800); val = eb(36)
tc(LX, 1578, "Ibada:", lab, align="r"); tc(VX, 1578, "Kanisa Anglican la St. Paul's - Ukonga,", c.fit("Kanisa Anglican la St. Paul's - Ukonga,", eb, 36, 600), align="l")
tc(VX, 1624, "saa XX:XX.", val, align="l")
tc(LX, 1682, "Ukumbi:", lab, align="r"); tc(VX, 1682, "Mwigo Empire Hall - Tabata Bima.", val, align="l")
tc(LX, 1745, "Rangi:", lab, align="r")
swatches(c, VX + 147/2, 1720, [BLACK, GOLD], size=50, gap=47, outline=(190, 185, 178))
tc(VX + 147 + 32, 1745, "Black & Gold", val, align="l")
tc(LX, 1808, "Mawasiliano:", lab, align="r")
contacts = ["Samuel A. Mshote (M/kiti) - 0754 277 980", "Monica Mshote (Mwekahazina) - 0686 967 238"]
fc = min((c.fit(t, eb, 36, 628) for t in contacts), key=lambda f: f.size)     # same size on both lines, clear of the QR
tc(VX, 1808, contacts[0], fc, align="l"); tc(VX, 1856, contacts[1], fc, align="l"); print("contact font", fc.size)
c.paste_logo(AX, 1930, 170, dark_bg=False, anchor="cm")
save_card(c.im, CLIENT + "/outputs/" + OUT, "John & Vedastina", PREV, preview_w=1000)
print("saved", OUT, c.im.size)
