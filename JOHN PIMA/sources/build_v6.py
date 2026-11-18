# John & Vedastina - BAG PARTY v1 (build_v6.py) - same blueprint + two-panel layout as FRANCO & AGATHA build_v2.py
# (Envaita white-floral gold frame, blueprint_white_floral_gold_frame.jpeg).  Client 2026-11-16 (WhatsApp "Hw - Mpare cooling system"):
# handwritten "Mwaliko wa Bag Party, Familia ya John Samuel Pima wa Kitunda DSM"; dress code white, fascinator white or blue;
# ukumbi nyumbani kwao Kitunda; bag party = sherehe ya kumpongeza kijana wao wa kiume (pre-wedding celebration).
# NOT GIVEN YET: date, day, time -> DATE / DAY / TIME env placeholders.  Contacts reused from the wedding card (v1_final_04).
# run: DATE=21.11.2026 DAY=Jumamosi TIME="saa 10:00 jioni" ~/.haflaway/venv/bin/python build_v6.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *
from PIL import ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
WHICH = os.environ.get("PHOTO", "white")
OUT = sys.argv[1] if len(sys.argv) > 1 else "John_&_Vedastina_BagParty_v1_final_09.png"   # SINGLE=0 -> two-panel (final_02)
DATE = os.environ.get("DATE", "22.11.2026"); DAY = os.environ.get("DAY", "Jumapili")   # client 2026-11-16: "Tarehe ni 22"
TIME = os.environ.get("TIME", "saa 9:30 alasiri")   # client 2026-11-16: "saa 9 .30 alasiri"
SCR = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/39ac5a94-2c35-48a2-a078-0faa4526b442/scratchpad/"
K = 2.5

src = cv2.imread(HERE + "/blueprint_white_floral_gold_frame.jpeg"); H0, W0 = src.shape[:2]
# client 2026-11-16: "Badilisha rangi huo green weka blue" -> blueprint's green leaves turned royal blue (shading kept)
if os.environ.get("LEAVES", "blue") == "blue":
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV).astype(np.float32); hh, ss = hsv[..., 0], hsv[..., 1]
    core = ((hh > 55) & (hh < 100) & (ss > 60)).astype(np.uint8)                        # solid leaf pixels
    region = cv2.dilate(core, np.ones((9, 9), np.uint8), iterations=2).astype(np.float32) # leaf + edge fringe
    region = cv2.GaussianBlur(region, (0, 0), 2)
    lab = cv2.cvtColor(src, cv2.COLOR_BGR2LAB).astype(np.float32)
    A, Bc = lab[..., 1] - 128, lab[..., 2] - 128
    C = np.sqrt(A**2 + Bc**2)
    w = region*np.clip((2 - A)/6, 0, 1)*np.clip((C - 6)/8, 0, 1)                          # greenish with real colour (gold a > 0, paper C < 5)
    ux, uy = 0.12, -0.993                                                                  # royal-blue direction in (a, b)
    Cn = C*(1 + 0.3*np.clip((C - 22)/15, 0, 1))                                          # richer body, edges untouched
    Cn *= np.clip((215 - lab[..., 0])/55, 0.25, 1)                                       # blue reads stronger than green on white paper
    lab[..., 1] = 128 + A*(1 - w) + (Cn*ux)*w
    lab[..., 2] = 128 + Bc*(1 - w) + (Cn*uy)*w
    src = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

# ------------------------------------------------------------------ 1. clean the dummy text (both panels)
TEXT = [(255, 250, 662, 324), (328, 341, 628, 372), (298, 381, 657, 434), (258, 438, 702, 552), (328, 578, 628, 612),
        (278, 626, 728, 742), (318, 748, 642, 892), (333, 896, 617, 972), (362, 976, 562, 1004)]   # Rangi chips + caption kept (fern behind them)
clean = src.copy()
for b in TEXT: clean = clean_by_background(clean, b, thr=20, blur=61)
# smooth the cleaned zones (inpaint streaks on the soft grey-white paper)
zm = np.zeros((H0, W0), np.float32)
for x1, y1, x2, y2 in TEXT: zm[y1:y2, x1:x2] = 1
zm = cv2.GaussianBlur(zm, (0, 0), 3)[..., None]
clean = (cv2.GaussianBlur(clean, (0, 0), 5)*zm + clean*(1 - zm)).astype(np.uint8)

# Envaita logo (plain paper): paint with the local paper estimate
LOGO = (698, 1168, 905, 1272)
lm = np.zeros((H0, W0), np.float32); lm[LOGO[1]:LOGO[3], LOGO[0]:LOGO[2]] = 1; lm = cv2.GaussianBlur(lm, (0, 0), 4)[..., None]
pap = cv2.GaussianBlur(cv2.inpaint(clean, (lm[..., 0] > 0.01).astype(np.uint8)*255, 25, cv2.INPAINT_TELEA), (0, 0), 10)
clean = (pap*lm + clean*(1 - lm)).astype(np.uint8)
# badge: repaint blank in its own brown
BADGE = (689, 780, 806, 817)
BROWN = tuple(int(v) for v in np.median(src[783:790, 692:700].reshape(-1, 3), axis=0)[::-1])

# panel A: also remove badge + QR and rebuild what was behind (paper, frame line, fern tip)
QR = (652, 776, 845, 1017)
pa = clean.copy().astype(np.float32)
y1, y2 = QR[1], QR[3]
fill = clean.astype(np.float32).copy()
top = clean[y1 - 6:y1 - 2].astype(np.float32).mean(axis=0)                 # clean paper row just above the old badge
ref = cv2.GaussianBlur(clean[:, 636:648].astype(np.float32).mean(axis=1), (1, 0), 3).reshape(-1, 3) if False else \
      cv2.GaussianBlur(clean[:, 636:648].astype(np.float32).mean(axis=1)[:, None, :], (1, 31), 0)[:, 0, :]
delta = ref[y1:y2] - ref[y1 - 4]                                             # paper darkens downwards: follow it
fill[y1:y2, 652:796] = top[None, 652:796] + delta[:, None]; fill[y1:y2, 818:845] = top[None, 818:845] + delta[:, None]
line = clean[700:776, 796:818].astype(np.float32).mean(axis=0)                # averaged frame-line profile
fill[y1:y2, 796:818] = line[None] + delta[:, None]
am = np.zeros((H0, W0), np.float32); am[y1:y2, 630:845] = 1
qm = np.zeros((H0, W0), np.uint8); qm[y1:y2, 652:845] = 255
under = cv2.inpaint(clean, qm, 7, cv2.INPAINT_TELEA).astype(np.float32)       # fern grows up into the old QR rows
am = np.minimum(am, np.clip((y2 - np.arange(H0, dtype=np.float32))/26, 0, 1)[:, None])        # paper fades into the fern
am = np.minimum(am, np.clip((np.arange(W0, dtype=np.float32) - 640)/14, 0, 1)[None, :])       # no seam on the left
am = cv2.GaussianBlur(am, (0, 0), 1.5)[..., None]
pa = (fill*am + under*(1 - am)).astype(np.uint8)
pa = clean_by_background(pa, (360, 1003, 566, 1066), thr=26, blur=41)          # panel A: no Rangi chips
cv2.imwrite(SCR + "fa_cleanA.png", pa); cv2.imwrite(SCR + "fa_cleanB.png", clean)
print("brown", BROWN)

# ------------------------------------------------------------------ 2. panel B: the invitation text
clean = clean_by_background(clean, (360, 1003, 566, 1066), thr=26, blur=41)          # old Rangi chips (new colours)
INK = (24, 23, 24); GOLD = (170, 112, 24); GOLD_L = (196, 150, 70)
def up(bgr): return Image.fromarray(cv2.cvtColor(cv2.resize(bgr, (round(W0*K), round(H0*K)), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB))
B = up(clean); c = Card(B, K, resize=False)
serif = lambda sz, wt=500: c.f("PlayfairDisplay.ttf", sz, wt)
ital = lambda sz, wt=600: c.f("PlayfairDisplay-Italic.ttf", sz, wt)
scr = lambda sz: c.f("GreatVibes-Regular.ttf", sz)
def tc(cc, x, yc, t, f, fill, sp=0):                     # ink centred vertically on yc
    bb = cc.d.textbbox((0, 0), t, font=f); cc.text(x, yc - (bb[1] + bb[3])/2/K, t, f, fill, sp=sp)

AX = 462
fam = ["FAMILIA YA", "JOHN SAMUEL PIMA", "WA KITUNDA, DAR ES SALAAM,", "WANAYO FURAHA KUKUALIKA/KUWAALIKA"]
ff = min((c.fit(s, lambda z: serif(z, 500), 21, 420) for s in fam), key=lambda f: f.size)
for i, s in enumerate(fam): tc(c, AX, 256 + i*26, s, ff, INK)
c.line(AX - 150, 382, AX + 150, 382, GOLD, 1.2)                                   # blank guest-name line
for i, s in enumerate(["KWENYE SHEREHE YA BAG PARTY", "YA KUMPONGEZA KIJANA WAO MPENDWA"]): tc(c, AX, 410 + i*26, s, ff, INK)
fn = scr(76)
GROOM = "Adv. John Pima"                                # client 2026-11-16: "anza na Adv John"                                     # bag party = the groom only (kijana wao wa kiume)
par = lambda z: c.f("Parisienne-Regular.ttf", z)                 # client: the Great Vibes "A" did not read as a capital A
fg = c.fit(GROOM, par, 70, 440); bb = c.d.textbbox((0, 0), GROOM, font=fg)
c.text(AX, 496 - (bb[1] + bb[3])/2/K, GROOM, fg, GOLD, stroke=2)                 # slight faux-bold: Parisienne is thin
tc(c, AX, 569, "itakayofanyika " + DAY + " tarehe", ital(23, 600), INK)
c.line(285, 598, 722, 598, GOLD, 1.4); c.line(285, 690, 722, 690, GOLD, 1.4)
fd = serif(60, 700); dt = DATE; wd = c.width(dt, fd); x0 = 503 - (wd + 64)/2 + 64
icon_calendar(c, x0 - 62, 621, 46, GOLD, 3.2)
bb = c.d.textbbox((0, 0), dt, font=fd); c.text(x0, 645 - (bb[1] + bb[3])/2/K, dt, fd, GOLD, align="l")

# Ibada | Ukumbi (two columns above the QR / bottom-left flowers)
C1, C2 = 305, 530
cx_, cy_, r_ = C1, 718, 14                                                      # clock icon
c.d.ellipse([c.P(cx_ - r_), c.P(cy_ - r_), c.P(cx_ + r_), c.P(cy_ + r_)], outline=GOLD, width=c.P(2.6))
c.line(cx_, cy_, cx_, cy_ - 8, GOLD, 2.4); c.line(cx_, cy_, cx_ + 6, cy_ + 3, GOLD, 2.4)
icon_pin(c, C2, 716, 24, GOLD, (236, 236, 236))
fh, fv = ital(21.5, 800), ital(20, 600)
col1 = ["Kuanzia", TIME[0].upper() + TIME[1:]]
col2 = ["Nyumbani kwao,", "Kitunda,", "Dar es Salaam"]
fv = min([fv] + [c.fit(s, lambda z: ital(z, 600), 20, 190) for s in col1 + col2], key=lambda f: f.size)
tc(c, C1, 752, "Muda", fh, INK); tc(c, C2, 752, "Ukumbi", fh, INK)
for i, a in enumerate(col1): tc(c, C1, 776 + i*23, a, fv, INK)
for i, b in enumerate(col2): tc(c, C2, 776 + i*23, b, fv, INK)
# Mawasiliano (between bottom-left flowers and the QR)
MX = 485
tc(c, MX, 876, "MAWASILIANO", serif(20, 700), INK)
fm = min((c.fit(s, lambda z: serif(z, 500), 20, 296) for s in ["MARIA KISHERE - 0754 853 025", "RACHEL MSHOTE - 0754 279 909"]), key=lambda f: f.size)
tc(c, MX, 902, "MARIA KISHERE - " + phone("0754853025"), fm, INK)
tc(c, MX, 927, "RACHEL MSHOTE - " + phone("0754279909"), fm, INK)
tc(c, 490, 968, "RANGI", serif(19, 800), INK)
swatches(c, 490, 984, [(250, 250, 248)], size=30, gap=16, shape="round", outline=GOLD)   # nguo = white only (client: "hio blue itoe")
tc(c, 492, 1034, "Nguo: White", ital(17, 700), INK)
tc(c, 492, 1055, "Fascinator: White au Blue", ital(17, 700), INK)
c.d.rounded_rectangle([c.P(BADGE[0]), c.P(BADGE[1]), c.P(BADGE[2]), c.P(BADGE[3])], c.P(7), fill=BROWN)   # blank badge
c.paste_logo(712, 1214, 165, dark_bg=False)

# ------------------------------------------------------------------ 3. panel A: photo in a gold arch + names + date
A = up(pa); ca = Card(A, K, resize=False)
AX1, AX2, AY1, AY2 = 262, 638, 245, 770
aw, ah = ca.P(AX2 - AX1), ca.P(AY2 - AY1)
ph = Image.open(HERE + "/" + os.environ.get("PHOTO", "photo_john_vedastina.jpeg")).convert("RGB")
cw = float(os.environ.get("CW", "430")); cx = float(os.environ.get("CX", "262")); top = float(os.environ.get("TOP", "12"))      # John alone
chh = cw*ah/aw
ph = ph.crop((round(cx - cw/2), round(top), round(cx + cw/2), round(top + chh))).resize((aw, ah), Image.LANCZOS)
am_ = Image.new("L", (aw, ah), 0); d = ImageDraw.Draw(am_); r = aw/2
d.ellipse([0, 0, aw - 1, 2*r], fill=255); d.rectangle([0, r, aw, ah], fill=255)
A.paste(ph, (ca.P(AX1), ca.P(AY1)), am_.filter(ImageFilter.GaussianBlur(1.2)))
def arch_line(cc, x1, x2, y1, y2, col, w):
    rr = (x2 - x1)/2
    cc.d.arc([cc.P(x1), cc.P(y1), cc.P(x2), cc.P(y1 + 2*rr)], 180, 360, fill=col, width=cc.P(w))
    for x in (x1, x2): cc.line(x, y1 + rr, x, y2, col, w)
    cc.line(x1, y2, x2, y2, col, w)
arch_line(ca, AX1 - 7, AX2 + 7, AY1 - 7, AY2 + 7, GOLD, 1.6)
tc(ca, 470, 846, GROOM, ca.fit(GROOM, scr, 76, 440), GOLD)
tc(ca, 482, 912, "MWALIKO WA BAG PARTY", serif(19, 600), INK, sp=3)
tc(ca, 482, 958, DATE.replace(".", " · "), serif(38, 700), GOLD, sp=1)

# ------------------------------------------------------------------ 4a. single page (client 2026-11-16: "single page like the blueprint")
if os.environ.get("SINGLE", "1") == "1":
    save_card(B, CLIENT + "/outputs/" + OUT, "John Samwel Pima - Bag Party", SCR + "jv_bag_prev.jpg", 900)
    print("saved single", OUT, B.size); sys.exit()
# ------------------------------------------------------------------ 4. side by side on a soft backdrop with shadows
M, G = 60, 50
CW, CH = round((2*M + 2*W0 + G)*K), round((2*M + H0)*K)
canvas = Image.new("RGB", (CW, CH), (236, 234, 230))
sh = Image.new("L", (CW, CH), 0); sd = ImageDraw.Draw(sh)
for x in (M, M + W0 + G): sd.rectangle([round((x + 6)*K), round((M + 10)*K), round((x + W0 + 6)*K), round((M + H0 + 10)*K)], fill=110)
sh = sh.filter(ImageFilter.GaussianBlur(14*K))
canvas = Image.composite(Image.new("RGB", (CW, CH), (150, 146, 140)), canvas, sh)
canvas.paste(A, (round(M*K), round(M*K))); canvas.paste(B, (round((M + W0 + G)*K), round(M*K)))
save_card(canvas, CLIENT + "/outputs/" + OUT, "John Samwel Pima - Bag Party", SCR + "jv_bag_prev.jpg", 1600)
print("saved", OUT, canvas.size)
