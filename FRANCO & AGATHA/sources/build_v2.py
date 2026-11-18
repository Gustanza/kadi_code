# Franco & Agatha - INVITATION v2 - Envaita white-floral gold-frame blueprint (blueprint_white_floral_gold_frame.jpeg,
# 955x1280, dummy "Dotto & Lilian").  Client (2026-11-16): "Picha ya kadi ya harusi naomba nitolee sample 2
# (hii nguo nyeupe na ile ya nguo za ki Naija)" -> two drafts on the SAME blueprint:
#   PHOTO=white -> photo_IMG_2876_white.jpeg (white outfits)          -> Franco_&_Agatha_v2_final_01.png
#   PHOTO=naija -> photo_3U1A1868.jpeg (black + gold gele, studio)      -> Franco_&_Agatha_v3_final_01.png
# The blueprint has no photo slot and its text fills the frame -> two panels side by side:
#   panel A = blueprint art + photo in a gold arch + names + date, panel B = the full invitation text.
# run: PHOTO=white|naija ~/.haflaway/venv/bin/python build_v2.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *
from PIL import ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
WHICH = os.environ.get("PHOTO", "white")
OUT = sys.argv[1] if len(sys.argv) > 1 else ("Franco_&_Agatha_v2_final_01.png" if WHICH == "white" else "Franco_&_Agatha_v3_final_01.png")
SCR = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/39ac5a94-2c35-48a2-a078-0faa4526b442/scratchpad/"
K = 2.5

src = cv2.imread(HERE + "/blueprint_white_floral_gold_frame.jpeg"); H0, W0 = src.shape[:2]
# client 2026-11-16: no green and no gold on the card -> art recoloured into their palette (PALETTE=orig to undo):
#   gold (ferns, frame line, berries, flower centres) -> pink (Fondant), green leaves -> light blue (Airy Blue). Lightness kept.
PAL = os.environ.get("PALETTE", "pinkblue")
if PAL == "pinkblue":
    lab = cv2.cvtColor(src, cv2.COLOR_BGR2LAB).astype(np.float32)
    L, A, Bc = lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128
    C = np.sqrt(A**2 + Bc**2)
    wg = np.clip((C - 6)/10, 0, 1)*np.clip((Bc - 3)/8, 0, 1)*np.clip((A + 8)/6, 0, 1)        # gold / yellow / brown
    seed = (((A < -5) & (C > 7)) | ((L < 70) & (A < -2))).astype(np.uint8)                   # leaf pixels (lit + shadowed)
    seed = cv2.morphologyEx(seed, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))                  # drop JPEG specks on white petals
    seed = cv2.morphologyEx(seed, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))                 # fill veins / holes
    n_, lab_, st_, _ = cv2.connectedComponentsWithStats(seed, 8)
    keep = np.zeros_like(seed)
    for k in range(1, n_):
        if st_[k, cv2.CC_STAT_AREA] >= 40: keep[lab_ == k] = 1                               # whole leaves only
    darkpx = ((L < 80) & (A < 3) & (Bc < 10)).astype(np.uint8)                                # neutral-black leaf shadows
    for _ in range(12):                                                                       # geodesic growth from the leaves
        keep = np.maximum(keep, cv2.dilate(keep, np.ones((3, 3), np.uint8)) & darkpx)
    keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    wl = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 1.0)
    wg = cv2.GaussianBlur(wg, (0, 0), 0.6); wg = np.minimum(wg, 1 - wl)
    pink, blue = (0.995, 0.02), (-0.06, -0.998)                                              # (a, b) directions
    Cg = np.minimum(C*0.72, 32); Cb = np.clip(20 + 0.5*C, 0, 34)                                                          # soft airy blue, keeps some texture
    A2 = A*(1 - wg - wl) + Cg*pink[0]*wg + Cb*blue[0]*wl
    B2 = Bc*(1 - wg - wl) + Cg*pink[1]*wg + Cb*blue[1]*wl
    L2 = L + ((255 - L)*0.32 + np.clip(110 - L, 0, None)*0.40)*wl                     # lift dark leaf shadows                                                                # leaves lighter (airy blue)
    lab = np.stack([L2, A2 + 128, B2 + 128], -1)
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
clean = clean_by_background(clean, (360, 1003, 566, 1066), thr=26, blur=41)          # old blueprint Rangi chips + caption
INK = (24, 23, 24); GOLD = (170, 112, 24); GOLD_L = (196, 150, 70)
if PAL == "pinkblue": GOLD = (176, 84, 116); BROWN = (226, 160, 182)                     # deep rose text/lines, pink badge
def up(bgr): return Image.fromarray(cv2.cvtColor(cv2.resize(bgr, (round(W0*K), round(H0*K)), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB))
B = up(clean); c = Card(B, K, resize=False)
serif = lambda sz, wt=500: c.f("PlayfairDisplay.ttf", sz, wt)
ital = lambda sz, wt=600: c.f("PlayfairDisplay-Italic.ttf", sz, wt)
scr = lambda sz: c.f("GreatVibes-Regular.ttf", sz)
def tc(cc, x, yc, t, f, fill, sp=0):                     # ink centred vertically on yc
    bb = cc.d.textbbox((0, 0), t, font=f); cc.text(x, yc - (bb[1] + bb[3])/2/K, t, f, fill, sp=sp)

AX = 462
fam = ["FAMILIA YA", "MZEE CHARLES ATILYO YETULA", "WA KAWE, DAR ES SALAAM,", "INAYO FURAHA KUKUALIKA/KUWAALIKA"]
ff = min((c.fit(s, lambda z: serif(z, 500), 21, 420) for s in fam), key=lambda f: f.size)
for i, s in enumerate(fam): tc(c, AX, 256 + i*26, s, ff, INK)
c.line(AX - 150, 382, AX + 150, 382, GOLD, 1.2)                                   # blank guest-name line
for i, s in enumerate(["KWENYE SHEREHE YA", "HARUSI YA VIJANA WAO WAPENDWA"]): tc(c, AX, 410 + i*26, s, ff, INK)
fn = scr(76)
tc(c, 336, 498, "Franco", fn, GOLD); tc(c, 462, 506, "&", scr(54), GOLD); tc(c, 590, 498, "Agatha", fn, GOLD)
tc(c, AX, 569, "itakayofanyika Jumapili tarehe", ital(23, 600), INK)
c.line(285, 598, 722, 598, GOLD, 1.4); c.line(285, 690, 722, 690, GOLD, 1.4)
fd = serif(60, 700); dt = "29.11.2026"; wd = c.width(dt, fd); x0 = 503 - (wd + 64)/2 + 64      # client 2026-11-16: "Tarehe ya event iwe 29"
icon_calendar(c, x0 - 62, 621, 46, GOLD, 3.2)
bb = c.d.textbbox((0, 0), dt, font=fd); c.text(x0, 645 - (bb[1] + bb[3])/2/K, dt, fd, GOLD, align="l")

# Ibada | Ukumbi (two columns above the QR / bottom-left flowers)
C1, C2 = 305, 530
icon_cross(c, C1, 720, 26, GOLD); icon_pin(c, C2, 716, 24, GOLD, (236, 236, 236))
fh, fv = ital(21.5, 800), ital(20, 600)
col1 = ["Kanisa la Mt.", "Maximilian Kolbe,", "Mwenge", "Jumamosi 28.11.2026", "Saa 9:00 Alasiri"]
col2 = ["Jaks Hall,", "Mbezi Africana", "Saa 10:00 Alasiri"]
fv = min([fv] + [c.fit(s, lambda z: ital(z, 600), 20, 190) for s in col1 + col2], key=lambda f: f.size)
tc(c, C1, 752, "Ibada ya Ndoa", fh, INK); tc(c, C2, 752, "Ukumbi", fh, INK)
for i, a in enumerate(col1): tc(c, C1, 775 + i*22, a, fv, INK)
for i, b in enumerate(col2): tc(c, C2, 775 + i*22, b, fv, INK)
# Mawasiliano (between bottom-left flowers and the QR)
MX = 485
tc(c, MX, 897, "MAWASILIANO", serif(20, 700), INK)
fm = min((c.fit(s, lambda z: serif(z, 500), 20, 312) for s in ["ENOCK MAYAO - 0713 398 540", "JIMMY ATILYO - 0653 099 772"]), key=lambda f: f.size)
tc(c, MX, 922, "ENOCK MAYAO - " + phone("0713398540"), fm, INK)
tc(c, MX, 946, "JIMMY ATILYO - " + phone("0653099772"), fm, INK)
tc(c, 462, 993, "RANGI", serif(19, 800), INK)
# client 2026-11-16 dress code: PINK BLUE BLACK; Pantone Fondant + Airy Blue (dress_code_*.jpeg)
swatches(c, 462, 1008, [(231, 186, 204), (169, 198, 237), (17, 17, 17)], size=30, gap=16, shape="round", outline=GOLD)
tc(c, 462, 1058, "(Pink, Light Blue & Black)", ital(17, 700), INK)
c.d.rounded_rectangle([c.P(BADGE[0]), c.P(BADGE[1]), c.P(BADGE[2]), c.P(BADGE[3])], c.P(7), fill=BROWN)   # blank badge
c.paste_logo(712, 1214, 165, dark_bg=False)

# ------------------------------------------------------------------ 3. panel A: photo in a gold arch + names + date
A = up(pa); ca = Card(A, K, resize=False)
AX1, AX2, AY1, AY2 = 262, 638, 245, 770
aw, ah = ca.P(AX2 - AX1), ca.P(AY2 - AY1)
if WHICH == "white":
    ph = Image.open(HERE + "/photo_IMG_2876_white.jpeg").convert("RGB")
    cw = float(os.environ.get("CW", "1330")); cx = float(os.environ.get("CX", "1010")); top = float(os.environ.get("TOP", "300"))
else:
    ph = Image.open(HERE + "/photo_3U1A1868.jpeg").convert("RGB")
    cw = float(os.environ.get("CW", "3300")); cx = float(os.environ.get("CX", "2277")); top = float(os.environ.get("TOP", "60"))
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
fn2 = scr(76); t1, t2, t3 = "Franco ", "&", " Agatha"
w1, w2, w3 = ca.width(t1, fn2), ca.width(t2, scr(52)), ca.width(t3, fn2); x0 = 470 - (w1 + w2 + w3)/2
for t, f, xx, yy in [(t1, fn2, x0, 846), (t2, scr(52), x0 + w1, 854), (t3, fn2, x0 + w1 + w2, 846)]:
    bb = ca.d.textbbox((0, 0), t, font=f); ca.text(xx, yy - (bb[1] + bb[3])/2/K, t, f, GOLD, align="l")
tc(ca, 482, 912, "MWALIKO WA HARUSI", serif(19, 600), INK, sp=3)
tc(ca, 482, 958, "29 · 11 · 2026", serif(38, 700), GOLD, sp=1)

# ------------------------------------------------------------------ 4. side by side on a soft backdrop with shadows
M, G = 60, 50
CW, CH = round((2*M + 2*W0 + G)*K), round((2*M + H0)*K)
canvas = Image.new("RGB", (CW, CH), (236, 234, 230))
sh = Image.new("L", (CW, CH), 0); sd = ImageDraw.Draw(sh)
for x in (M, M + W0 + G): sd.rectangle([round((x + 6)*K), round((M + 10)*K), round((x + W0 + 6)*K), round((M + H0 + 10)*K)], fill=110)
sh = sh.filter(ImageFilter.GaussianBlur(14*K))
canvas = Image.composite(Image.new("RGB", (CW, CH), (150, 146, 140)), canvas, sh)
canvas.paste(A, (round(M*K), round(M*K))); canvas.paste(B, (round((M + W0 + G)*K), round(M*K)))
save_card(canvas, CLIENT + "/outputs/" + OUT, "Franco & Agatha - Mwaliko wa Harusi", SCR + "fa_prev_" + WHICH + ".jpg", 1600)
print("saved", OUT, canvas.size)
