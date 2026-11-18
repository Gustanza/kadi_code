# Albert & Beatrice - WEDDING v4 - red & gold roses, photo in gold arch (blueprint: Haflaway's own "Piter Alex" engagement card,
# sources/blueprint_red_engagement_piter_alex.png, 1024x1536; engagement wording turned into a wedding invitation). U=2.
# run: ~/.haflaway/venv/bin/python build_v4.py [out_name]   (PHOTO=photo_B.jpeg CX=.. for the other photo)
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Albert_&_Beatrice_v4_final_01.png"
PREV = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/8d5d143e-4e6d-4e7a-9c03-6fcc9b8f790b/scratchpad/ab_v4_prev.jpg"
U = 2
src = cv2.imread(HERE + "/blueprint_red_engagement_piter_alex.png"); H, W = src.shape[:2]
b_, g_, r_ = [src[:, :, i].astype(int) for i in range(3)]

# ---- 1. frame interior + flowers on top (traced from the gold line)
gold = ((r_ > 170) & (g_ > 120) & (b_ < 150) & (r_ - b_ > 70)).astype(np.uint8)
fl = gold.copy(); fl[:, :530] = 0; fl[:300, :552] = 0; fl[:, 1005:] = 0; fl[1040:, :] = 0; fl[:60, :] = 0
fl[:335, 850:] = 0; fl[785:, 700:] = 0; fl[840:, :625] = 0; fl[140:1000, 600:940] = 0
pts = cv2.findNonZero(fl).reshape(-1, 2)
extra = np.array([[990, 200], [970, 140], [930, 100], [960, 960], [920, 1010], [880, 1030]] +
                 [[690 + 88*np.cos(t), 948 + 88*np.sin(t)] for t in np.linspace(np.pi/2, np.pi, 12)])   # round bottom-left corner (blueprint curve)
hull = cv2.convexHull(np.vstack([pts, extra]).astype(np.int32))
fr = np.zeros((H, W), np.uint8); cv2.fillPoly(fr, [hull], 255)
inner = cv2.erode(fr, np.ones((17, 17), np.uint8)); inner[848:1008, :609] = 0                 # date box sits on top of the frame
gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY).astype(np.float32)
mu = cv2.blur(gray, (5, 5)); sd = np.sqrt(np.maximum(cv2.blur(gray*gray, (5, 5)) - mu*mu, 0))
clus = np.zeros((H, W), np.uint8); clus[:345, 830:] = 1; clus[930:, 690:] = 1; clus[870:, 850:] = 1; clus[780:, 930:] = 1
red = (r_ > 100) & (g_ < 70) & (b_ < 80)
cand = ((sd > 13) | (gold == 1) | ((src.min(axis=2) > 200) & (sd > 4))) & (clus == 1)
cand[780:, 690:840] &= ~red[780:, 690:840]; cand[250:345, 830:] &= ~red[250:345, 830:]
f = cv2.morphologyEx(cand.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
f = cv2.morphologyEx(f, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
cs, _ = cv2.findContours(f, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
f = np.zeros_like(f); cv2.drawContours(f, [k for k in cs if cv2.contourArea(k) > 300], -1, 1, -1)
beige = (r_ > 165) & (g_ > 135) & (b_ > 100) & (r_ - b_ < 95) & (src.min(axis=2) < 215) & (sd < 12)
f[beige] = 0; f = cv2.morphologyEx(f, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))      # old photo's ground between the leaves

# ---- 2. clean template text (light text on red; dark text on the cream date box)
img = src.copy()
bgm = cv2.medianBlur(src, 41); diff = np.abs(src.astype(int) - bgm.astype(int)).max(axis=2)
m = np.zeros((H, W), np.uint8)
for x1, y1, x2, y2 in [(30, 130, 548, 262), (70, 285, 510, 365), (60, 395, 525, 540), (120, 605, 480, 690), (40, 690, 535, 825),
                       (130, 1045, 505, 1085), (170, 1085, 440, 1210), (130, 1230, 815, 1268), (360, 1305, 670, 1345), (410, 1415, 620, 1455)]:
    m[y1:y2, x1:x2] = (diff[y1:y2, x1:x2] > 28)*255
legs = np.zeros((H, W), bool); legs[985:1062, 650:870] = True
legs &= ~(cv2.dilate(fr, np.ones((3, 3), np.uint8)) > 0) & (f == 0)
img = cv2.inpaint(img, cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=2), 11, cv2.INPAINT_TELEA)
lg = cv2.dilate(legs.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0                  # old legs that stepped out of the frame -> plain card red
redbg = np.median(src[1040:1090, 600:680].reshape(-1, 3), axis=0)
fill = np.clip(redbg + np.random.default_rng(1).normal(0, 2.5, img.shape), 0, 255).astype(np.uint8)
fill = cv2.GaussianBlur(fill, (5, 5), 0)
la = cv2.GaussianBlur(lg.astype(np.float32), (9, 9), 0)[:, :, None]
img = (img*(1 - la) + fill*la).astype(np.uint8)
gl = np.median(src[300:700, 540:575][gold[300:700, 540:575] == 1], axis=0)           # frame gold
hp = hull.reshape(-1, 2); seg = [i for i in range(len(hp)) if hp[i][1] > 985 and 630 < hp[i][0] < 900]
cnt = cv2.findContours(fr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0][0].reshape(-1, 2)
bot = cnt[(cnt[:, 1] > 960) & (cnt[:, 0] > 592) & (cnt[:, 0] < 885)]
bot = bot[np.argsort(bot[:, 0])]
bot = bot[~((bot[:, 0] < 612) & (bot[:, 1] < 1008))]                                  # not over the date box
cv2.polylines(img, [(bot - [0, 4]).reshape(-1, 1, 2).astype(np.int32)], False, tuple(int(v) for v in gl), 7, cv2.LINE_AA)   # frame bottom (was hidden by the old legs)
# date box: wipe its text (tight boxes; dividers, tab and paper art kept)
gm = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
dm = np.zeros((H, W), np.uint8)
for x1, y1, x2, y2 in [(165, 856, 478, 892), (55, 918, 222, 962), (268, 898, 398, 992), (432, 918, 598, 982)]:
    dm[y1:y2, x1:x2] = (gm[y1:y2, x1:x2] < 232)*255
img = cv2.inpaint(img, cv2.dilate(dm, np.ones((3, 3), np.uint8), iterations=3), 7, cv2.INPAINT_TELEA)
pb = cv2.GaussianBlur(cv2.medianBlur(img, 31), (0, 0), 6)                              # embossed ghost letters in the paper -> smooth paper
for x1, y1, x2, y2 in [(122, 862, 520, 892), (42, 900, 238, 990), (252, 900, 412, 990), (428, 900, 588, 990)]:
    img[y1:y2, x1:x2] = pb[y1:y2, x1:x2]

# ---- 3. photo into the arch
alpha = (inner.astype(np.float32)/255)*(1 - cv2.GaussianBlur((f*255).astype(np.uint8), (5, 5), 0).astype(np.float32)/255)
card = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).resize((W*U, H*U), Image.LANCZOS)
x, y, w, h = cv2.boundingRect(hull)
ph = crop_to(upscale_soft(load_photo(HERE + "/" + os.environ.get("PHOTO", "photo_A.jpeg")), 2.4), w*U, h*U,
             cx_frac=float(os.environ.get("CX", "0.45")), top_frac=0.0, zoom=1.0)
layer = card.copy(); layer.paste(ph, (x*U, y*U))
am = Image.fromarray((alpha*255).astype(np.uint8)).resize((W*U, H*U), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
card = Image.composite(layer, card, am)

# ---- 4. text
c = Card(card, U, resize=False)
GOLD = (246, 198, 104); CREAM = (252, 238, 214); WINE = (110, 10, 18)
play = lambda z, w=700: c.f("PlayfairDisplay.ttf", z, w)
eb = lambda z, w=600: c.f("EBGaramond.ttf", z, w)
scr = lambda z: c.f("GreatVibes-Regular.ttf", z)
LC = 290
c.text(LC, 134, "MWALIKO WA", c.fit("MWALIKO WA", play, 62, 470), GOLD)
c.text(LC, 200, "HARUSI", play(62), GOLD)
for i, t in enumerate(["FAMILIA YA BW. & BI. LIBENT RAPHAEL", "ISHABAILU WA UKONGA MAJUMBA SITA, DSM,", "WANAYO FURAHA KUKUALIKA / KUWAALIKA"]):
    fz = c.fit(t, eb, 21, 450)
    c.text(LC, 288 + i*30, t, fz, CREAM, sp=1)
c.line(95, 410, 485, 410, (236, 196, 120), 2)                                      # guest-name line
t = "KWENYE HARUSI YA VIJANA WAO"; c.text(LC, 420, t, eb(19, 700), CREAM, sp=3)
c.text(LC, 448, "Albert Libent", c.fit("Albert Libent", scr, 104, 450), GOLD)
c.text(LC, 600, "&", play(40, 500), CREAM)
c.text(LC, 680, "Beatrice Adelitus", c.fit("Beatrice Adelitus", scr, 104, 470), CREAM)
# date box
c.text(318, 855, "ITAKAYOFANYIKA", eb(28, 700), WINE, sp=3)
c.text(138, 917, "JUMAMOSI", c.fit("JUMAMOSI", lambda z: eb(z, 700), 31, 160), WINE)
f21 = c.f("Cinzel.ttf", 120, 700); bb = f21.getbbox("21"); c.text(333, 906 - bb[1]/U, "21", f21, WINE)
c.text(515, 916, "NOVEMBA", eb(28, 700), WINE, sp=1); c.text(515, 946, "2026", eb(28, 700), WINE, sp=1)
# ibada / ukumbi
c.text(LC, 1032, "IBADA YA NDOA", eb(21, 700), GOLD, sp=3)
t = "KANISA KATOLIKI, PAROKIA YA MSIMBAZI"; c.text(LC, 1060, t, c.fit(t, lambda z: eb(z, 600), 22, 480), CREAM)
c.text(LC, 1088, "SAA 9:00 ALASIRI", eb(21, 600), CREAM, sp=1)
c.text(LC, 1124, "UKUMBI", eb(21, 700), GOLD, sp=3)
c.text(LC, 1148, "Grand Paradise (Platinum)", c.fit("Grand Paradise (Platinum)", scr, 56, 470), GOLD)
c.text(LC, 1210, "YOMBO VITUKA, MWISHO WA LAMI", eb(21, 600), CREAM, sp=1)
c.text(LC, 1237, "KUANZIA SAA 12:00 JIONI", eb(21, 600), CREAM, sp=1)
t = "MAWASILIANO: 0715 194 900 / 0694 026 550 / 0788 016 290"; c.text(440, 1278, t, c.fit(t, lambda z: eb(z, 700), 23, 600), CREAM)
fr_ = eb(22, 700); cap = "(Kahawia, Blue & Nyeupe)"; fcap = c.f("PlayfairDisplay-Italic.ttf", 19, 500)
rw = c.width("RANGI:", fr_, 2) + 14 + 3*32 + 2*12 + 14 + c.width(cap, fcap); x0 = 430 - rw/2
c.text(x0, 1318, "RANGI:", fr_, GOLD, sp=2, align="l"); x0 += c.width("RANGI:", fr_, 2) + 14
for col in [(153, 100, 52), (40, 155, 240), (246, 246, 242)]:
    c.d.ellipse([c.P(x0), c.P(1316), c.P(x0 + 32), c.P(1348)], fill=col, outline=GOLD, width=c.P(2)); x0 += 44
c.text(x0 + 2, 1320, cap, fcap, CREAM, align="l")
t = "Watoto tunawapenda, lakini hawaruhusiwi."; c.text(500, 1362, t, c.f("PlayfairDisplay-Italic.ttf", 19, 500), CREAM)
c.paste_logo(515, 1442, 170, dark_bg=True, anchor="cm")                             # official Haflaway logo (white)
save_card(c.im, CLIENT + "/outputs/" + OUT, "Albert & Beatrice - Harusi", PREV, preview_w=1000)
print("saved", OUT)
