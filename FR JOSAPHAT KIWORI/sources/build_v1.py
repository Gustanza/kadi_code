# Fr. Josaphat Kiwori - KADI YA MWALIKO (harambee; was KADI YA MCHANGO until final_02), Jubilei ya miaka 25 ya Upadrisho - v1
# Blueprint: blueprint_priestly_anniversary.jpeg (purple, white panel, priest cut-out right; 736x920) - rendered 3x
# Photo: photo_fr_josaphat.jpeg (full length, outdoor) -> GrabCut cut-out placed where the template priest stood
# run: ~/.haflaway/venv/bin/python build_v1.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Fr_Josaphat_Kiwori_Mchango_v1_final_01.png"
PREV = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/8d5d143e-4e6d-4e7a-9c03-6fcc9b8f790b/scratchpad/fr_v1_prev.jpg"
U = 3

src = cv2.imread(HERE + "/blueprint_priestly_anniversary.jpeg"); H, W = src.shape[:2]
img = src.copy()

# ---- 1. top: parish logo + parish name + "Cordially invites you" + "To The Celebration Of The"
bg = cv2.medianBlur(src, 61)
diff = np.abs(src.astype(int) - bg.astype(int)).max(axis=2)
m = np.zeros((H, W), np.uint8)
x1, y1, x2, y2 = 200, 22, 548, 222
m[y1:y2, x1:x2] = (diff[y1:y2, x1:x2] > 22) * 255
cv2.circle(m, (282, 83), 54, 255, -1)                                   # parish logo disc
m = cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=2)
img = cv2.inpaint(img, m, 15, cv2.INPAINT_TELEA)
sm = cv2.GaussianBlur(img, (0, 0), 6)                                    # smooth the inpainted patch
a = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 4)[..., None]
img = (img * (1 - a) + sm * a).astype(np.uint8)

# ---- 2. the template priest: replace him with a smooth purple backdrop (inpainting smeared his grey jacket)
poly = np.array([(492, 236), (640, 236), (648, 390), (736, 418), (736, 920), (380, 920), (340, 700),
                 (342, 560), (362, 458), (420, 412), (494, 392)], np.int32)
pm = np.zeros((H, W), np.uint8); cv2.fillPoly(pm, [poly], 255); pm = cv2.dilate(pm, np.ones((9, 9), np.uint8))
pm[:, :433] = 0                                                         # panel part is repainted white below
ring = (cv2.dilate(pm, np.ones((31, 31), np.uint8)) > 0) & (pm == 0); ring[:, :440] = False
ctop = np.median(src[ring], axis=0).astype(np.float32)                 # backdrop tone right around him
ys = np.arange(H, dtype=np.float32)[:, None, None]
grad = ctop * (1 - 0.35 * np.clip((ys - 236) / (H - 236), 0, 1))   # darker towards the bottom
grad = np.repeat(grad, W, axis=1)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
glow = np.exp(-(((xx - 570) / 210) ** 2 + ((yy - 330) / 230) ** 2))   # soft light behind his head
fill = grad * (1 + 0.12 * glow[..., None])
low = cv2.GaussianBlur(src, (0, 0), 35).astype(np.float32) * 0.85     # keep the backdrop's large light/dark variation
fill = 0.55 * fill + 0.45 * low
rng = np.random.default_rng(7); fill = np.clip(fill + rng.normal(0, 2.5, fill.shape), 0, 255)
a = cv2.GaussianBlur(pm.astype(np.float32) / 255, (0, 0), 12)[..., None]; a[:, :433] = (pm[:, :433, None] > 0)
img = (img * (1 - a) + fill * a).astype(np.uint8)

# ---- 3. white panel (x 52-432, top 280): wipe all template text, keep chalice art, ribbon, gold rule + ornament, swooshes
WHITE = np.array([255, 255, 255], np.uint8)
reg = img[288:398, 178:345]; b_, g_, r_ = [reg[..., i].astype(int) for i in range(3)]
reg[~((g_ > r_ + 10) & (g_ > b_))] = WHITE                              # "10th" (keep green palm leaves)
img[398:840, 55:433] = WHITE                                            # priestly .. RSVP + template priest's sleeve
reg = img[840:920, 380:433]; b_, g_, r_ = [reg[..., i].astype(int) for i in range(3)]
reg[~((r_ > g_ + 60) | (reg.min(axis=2) > 225) | ((r_ > 150) & (g_ > 110) & (b_ < 120)))] = WHITE  # sleeve left over at the bottom

img[849:920, 365:433] = WHITE                                          # speckles of the template sleeve by the corner
c = Card(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), U)

# ---- 4. Fr. Josaphat
# final_05 (2026-11-13): client's own cut-out (Untitled design.pdf -> photo_fr_josaphat_cutout.png, person on white, both hands
# natural) replaces the GrabCut cut-out below (kept for reference: CUTOUT=0)
if os.environ.get("CUTOUT", "1") == "1":
    co = cv2.imread(HERE + "/photo_fr_josaphat_cutout.png"); CH, CW = co.shape[:2]
    nw = (co.min(axis=2) < 232).astype(np.uint8)                          # not white
    bgm = 1 - nw; ffm = np.zeros((CH + 2, CW + 2), np.uint8)
    for sx, sy in [(0, 0), (CW - 1, 0), (0, CH - 1), (CW - 1, CH - 1)]:
        if bgm[sy, sx]: cv2.floodFill(bgm, ffm, (sx, sy), 2)
    fgc = (bgm != 2).astype(np.uint8)
    holes = (co.min(axis=2) >= 236).astype(np.uint8) & fgc                 # enclosed white = background seen between arm and body
    n5, l5, st5, _ = cv2.connectedComponentsWithStats(holes, 8)
    for i in range(1, n5):
        x_, y_, w_, h_, ar = st5[i]
        if (ar > 400 or (ar > 15 and y_ > 850)) and not (1150 < x_ < 1350 and 900 < y_ < 1150): fgc[l5 == i] = 0   # badge (white cross) stays
    n4, l4, st4, _ = cv2.connectedComponentsWithStats(fgc, 8); fgc = (l4 == 1 + np.argmax(st4[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    fgc = cv2.erode(fgc, np.ones((9, 9), np.uint8))                       # drop the white anti-alias fringe
    ys, xs = np.nonzero(fgc)
    top = ys.min(); band = fgc[top + int(0.18 * (ys.max() - top)): top + int(0.45 * (ys.max() - top))]   # shoulders..hands
    bx = np.nonzero(band.any(axis=0))[0]; armL, armR = bx.min(), bx.max()
    S2 = 342 / (armR - armL)                                              # same width on the card as before
    LEFT, TOP = 386, 254
    k2 = S2 * U
    big = cv2.resize(co, (round(CW * k2), round(CH * k2)), interpolation=cv2.INTER_AREA if k2 < 1 else cv2.INTER_LANCZOS4)
    al = cv2.GaussianBlur(cv2.resize(fgc.astype(np.float32), (big.shape[1], big.shape[0]), interpolation=cv2.INTER_AREA), (0, 0), 1.0)
    arr = cv2.cvtColor(big, cv2.COLOR_BGR2RGB).astype(np.float32); tint = np.array([120, 70, 150], np.float32)
    arr = arr * 0.9 + tint * 0.1 * (arr.mean(axis=2, keepdims=True) / 255)    # same light purple grade as before
    bigi = Image.fromarray(np.clip(arr * 1.04, 0, 255).astype(np.uint8))
    px, py = round((LEFT - armL * S2) * U), round((TOP - top * S2) * U)
    c.im.paste(bigi, (px, py), Image.fromarray((np.clip(al, 0, 1) * 255).astype(np.uint8)))
    print("cutout scale", round(S2, 4), "arms", armL, armR, "top", top)
else:
    # ---- 4. Fr. Josaphat cut-out
    ph = cv2.imread(HERE + "/photo_fr_josaphat.jpeg"); PH, PW = ph.shape[:2]
    mask = np.full((PH, PW), cv2.GC_BGD, np.uint8); mask[130:700, 215:520] = cv2.GC_PR_BGD
    hsv = cv2.cvtColor(ph, cv2.COLOR_BGR2HSV)
    r = np.zeros((PH, PW), bool); r[150:700, 225:510] = True
    mask[r & (hsv[..., 2] < 90)] = cv2.GC_PR_FGD
    cv2.ellipse(mask, (372, 205), (36, 55), 0, 0, 360, cv2.GC_FGD, -1)
    cv2.rectangle(mask, (300, 270), (450, 630), cv2.GC_FGD, -1)
    cv2.rectangle(mask, (245, 420), (285, 540), cv2.GC_FGD, -1); cv2.rectangle(mask, (465, 420), (495, 540), cv2.GC_FGD, -1)
    cv2.grabCut(ph, mask, None, np.zeros((1, 65)), np.zeros((1, 65)), 8, cv2.GC_INIT_WITH_MASK)
    fg = np.isin(mask, [1, 3]).astype(np.uint8)
    green = (hsv[..., 0] > 25) & (hsv[..., 0] < 95) & (hsv[..., 1] > 35)    # plant leaves caught at the sleeves / hand
    fg[green] = 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg, 8); fg = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)); fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    inv = 1 - fg; ff = np.zeros((PH + 2, PW + 2), np.uint8); cv2.floodFill(inv, ff, (0, 0), 2); fg[inv == 1] = 1
    xs = np.where(fg[620])[0]; fg[620:, :xs.min()] = 0; fg[620:, xs.max() + 1:] = 0   # skirting band by the hem
    edge = fg - cv2.erode(fg, np.ones((15, 15), np.uint8))                 # wall / window frame caught on the shoulders
    wall = (hsv[..., 2] > 120) & (hsv[..., 1] < 90); wall[320:375, 395:445] = False   # (not the Passionist badge)
    fg[(edge > 0) & wall & (np.arange(PH)[:, None] > 230)] = 0             # below the face only
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg, 8); fg = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    for gx1, gx2 in [(262, 308), (448, 492)]:                               # wall seen between arms and body
        g = fg[420:575, gx1:gx2]; h = hsv[420:575, gx1:gx2]
        g[(h[..., 2] > 105) & (h[..., 1] < 120) & (h[..., 0] >= 8) & (h[..., 0] <= 35)] = 0
        g[(h[..., 0] > 25) & (h[..., 0] < 95) & (h[..., 1] > 18)] = 0
        g[:120][(h[:120, :, 2] > 95) | ((h[:120, :, 0] > 22) & (h[:120, :, 0] < 100))] = 0   # final_02: yellow-green wall sliver (cassock hue ~125)
    lf = (hsv[550:610, 452:510, 0] > 22) & (hsv[550:610, 452:510, 0] < 95)   # leaf between fingers -> rebuilt from the skin around it
    lm = np.zeros((PH, PW), np.uint8); lm[550:610, 452:510][lf] = 255
    ph = cv2.inpaint(ph, cv2.dilate(lm, np.ones((3, 3), np.uint8)), 5, cv2.INPAINT_TELEA)
    hb = hsv[550:610, 452:510]; skin = (hb[..., 0] <= 22) & (hb[..., 1] > 45) & (hb[..., 2] > 55)   # his left hand (leaf in front)
    fg[550:610, 452:510] |= skin.astype(np.uint8)
    fg[540:615, 445:515] = cv2.morphologyEx(cv2.morphologyEx(fg[540:615, 445:515], cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)),
                                           cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    hb2 = cv2.cvtColor(ph[548:615, 445:515], cv2.COLOR_BGR2HSV)          # final_02: hand = drawn outline + dark cassock only (no gravel)
    hand = np.zeros((PH, PW), np.uint8)
    cv2.fillPoly(hand, [np.array([(457, 562), (493, 560), (492, 566), (483, 574), (478, 586), (469, 587), (467, 576), (458, 570)], np.int32)], 1)
    cas = (fg[548:615, 445:515] > 0) & (hb2[..., 2] < 75) & (hb2[..., 0] > 100)
    new = (cas | (hand[548:615, 445:515] > 0)).astype(np.uint8); new[:12] |= fg[548:560, 445:515]   # sleeve cuff above the hand stays
    fg[548:615, 445:515] = new
    gap = np.zeros((PH, PW), bool); gap[440:540, 280:300] = True            # final_02: arm-body gap -> cassock (wall sliver gone)
    gap &= (hsv[..., 0] > 15) & (hsv[..., 0] < 100)
    nb = ph[440:540, 270:310].reshape(-1, 3); nv = hsv[440:540, 270:310, 2].reshape(-1)
    ph[gap] = np.median(nb[(nv < 50) & (nv > 15)], axis=0); fg[gap] = 1   # dark cassock in the fold
    CAS = np.median(nb[(nv < 50) & (nv > 15)], axis=0)
    hh = cv2.cvtColor(ph, cv2.COLOR_BGR2HSV); grav = (hand > 0) & (hh[..., 1] < 70) & (hh[..., 2] > 55)   # gravel between thumb and fingers
    ph = cv2.inpaint(ph, grav.astype(np.uint8) * 255, 4, cv2.INPAINT_TELEA)     # rebuild from the skin around it
    hbx = ph[555:595, 450:500]; ph[555:595, 450:500] = np.where((hand[555:595, 450:500] > 0)[..., None], cv2.GaussianBlur(hbx, (0, 0), 0.9), hbx)
    # final_04 (user: "issue with fingers"): his left hand is mostly hidden in the photo (thumb tip only) -> mirror his clear right hand
    RY1, RY2, RX1, RX2 = 572, 614, 248, 302                                 # right hand below the cuff (photo px)
    rp = ph[RY1:RY2, RX1:RX2].copy(); rh = cv2.cvtColor(rp, cv2.COLOR_BGR2HSV)
    rm = (((rh[..., 0] <= 20) | (rh[..., 0] >= 165)) & (rh[..., 1] > 35) & (rh[..., 2] > 70)).astype(np.uint8)
    rm = cv2.morphologyEx(cv2.morphologyEx(rm, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n3, l3, st3, _ = cv2.connectedComponentsWithStats(rm, 8); rm = (l3 == 1 + np.argmax(st3[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    rm = cv2.morphologyEx(rm, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    rm[((rh[..., 0] > 22) & (rh[..., 0] < 100) & (rh[..., 1] > 25)) | (rh[..., 2] < 60)] = 0   # no leaf, no cuff shadow
    rm = cv2.morphologyEx(rm, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n3, l3, st3, _ = cv2.connectedComponentsWithStats(rm, 8); rm = (l3 == 1 + np.argmax(st3[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    rp, rm = rp[:, ::-1], rm[:, ::-1]                                        # mirror: thumb toward the body
    TY, TX0 = 556, 452                                                       # under his left cuff
    R = (slice(556, 620), slice(445, 515))
    body_side = np.zeros((PH, PW), bool); body_side[R] = True
    casr = (fg > 0) & (hsv[..., 2] < 75) & (hsv[..., 0] > 100) & body_side   # keep the cassock body + cuff
    ph[body_side & ~casr] = CAS; fg[body_side & ~casr] = 0                   # old stub hand gone
    hh_, ww_ = rm.shape; tgt = (slice(TY, TY + hh_), slice(TX0, TX0 + ww_))
    ph[tgt][rm > 0] = rp[rm > 0]; fg[tgt] |= rm
    inv = 1 - fg; ff = np.zeros((PH + 2, PW + 2), np.uint8); cv2.floodFill(inv, ff, (0, 0), 2); fg[inv == 1] = 1   # no see-through holes
    fg = cv2.erode(fg, np.ones((3, 3), np.uint8))
    fg = (cv2.GaussianBlur(fg.astype(np.float32), (0, 0), 1.6) > 0.5).astype(np.uint8)   # final_02: smooth the jpeg-pixel steps off the outline
    S_, LEFT, TOP = 1.25, 386, 254                                          # scale (template px), left edge of arms, top of head
    ox, oy = LEFT - 230 * S_, TOP - 145 * S_
    k = S_ * U
    big = upscale_soft(Image.fromarray(cv2.cvtColor(ph, cv2.COLOR_BGR2RGB)), k)
    al = cv2.GaussianBlur(cv2.resize(fg.astype(np.float32), (big.width, big.height), interpolation=cv2.INTER_LINEAR), (0, 0), 0.8 * k)
    al = np.clip((al - 0.3) / 0.4, 0, 1)                                    # final_02: no stair-steps on the sleeves
    # light purple grade so he sits in the card's light (template priest is lit purple)
    arr = np.asarray(big).astype(np.float32); tint = np.array([120, 70, 150], np.float32)
    arr = arr * 0.9 + tint * 0.1 * (arr.mean(axis=2, keepdims=True) / 255)
    big = Image.fromarray(np.clip(arr * 1.04, 0, 255).astype(np.uint8))
    c.im.paste(big, (round(ox * U), round(oy * U)), Image.fromarray((al * 255).astype(np.uint8)))

# ---- 5. text
MAROON = (133, 0, 64); DARK = (34, 28, 40); CREAM = (255, 250, 242)
mont = lambda sz, w=500: c.f("Montserrat.ttf", sz, w)
play = lambda sz, w=700: c.f("PlayfairDisplay.ttf", sz, w)
playi = lambda sz, w=500: c.f("PlayfairDisplay-Italic.ttf", sz, w)
script = lambda sz: c.f("GreatVibes-Regular.ttf", sz)

def tc(x, yc, t, f, fill, align="c", sp=0, ref=None):                   # ink centred on yc (template px)
    bb = c.d.textbbox((0, 0), ref or t, font=f); c.text(x, yc - (bb[1] + bb[3]) / 2 / U, t, f, fill, align=align, sp=sp)

TX = 368                                                                 # top block axis (card centre)
# final_03 (client 2026-11-12): label as KADI YA MWALIKO wa harambee, keep the ways to contribute
tc(TX, 62, "KADI YA MWALIKO", c.fit("KADI YA MWALIKO", lambda z: mont(z, 700), 30, 330), CREAM, sp=4, ref="H")
tc(TX, 100, "“Kuacha alama ya utumishi na upendo”", c.fit("“Kuacha alama ya utumishi na upendo”", playi, 21, 340), CREAM)
tc(TX, 160, "Unaalikwa Harambee", c.fit("Unaalikwa Harambee", script, 62, 340), CREAM, ref="Ua")
tc(TX, 205, "ya Jubilei ya Miaka", mont(18, 600), CREAM, sp=2.5, ref="H")
# panel
PX = 212                                                                 # panel text axis (left of the priest)
tc(262, 345, "25", play(118, 800), MAROON, ref="25")
tc(262, 420, "ya Upadrisho", c.fit("ya Upadrisho", play, 40, 236), MAROON, ref="yU")
tc(262, 458, "(Jubilei ya Shaba)", playi(21, 600), MAROON, ref="(J")
MW = 300                                                                 # usable width (panel edge left, his sleeve right)
tc(PX, 498, "Rev. Fr. Josaphat Kiwori", c.fit("Rev. Fr. Josaphat Kiwori", lambda z: play(z, 600), 30, MW), DARK, ref="R")
# guest line
tc(66, 532, "Mpendwa:", mont(16, 600), DARK, align="l", ref="M")
c.line(66 + c.width("Mpendwa:", mont(16, 600)) + 6, 539, 352, 539, DARK, 1.2)
body = ["Unaalikwa kwenye harambee ya ujenzi", "wa Seminari (Nyumba ya Malezi ya Mwanzo)."]
fb = c.fit(body[1], mont, 15, MW)
for i, t in enumerate(body): tc(PX, 561 + i * 19, t, fb, DARK, ref="Hy")
# event details: label + bold value columns
rows = [("Tarehe:", ["Jumapili, 15/11/2026"]), ("Muda:", ["saa 12:00 jioni - 5:00 usiku"]),
        ("Mahali:", ["Mikocheni B, Mwai Kibaki Road,", "Gate No. 413", "(Kibao: Passionist Fathers)"])]
fl = mont(14.5, 500); LBX = 68; VLX = LBX + max(c.width(l, fl) for l, _ in rows) + 8
fv = c.fit(max([v for _, vs in rows for v in vs], key=lambda t: c.width(t, mont(14.5, 700))), lambda z: mont(z, 700), 14.5, 352 - VLX)
y = 606
for l, vs in rows:
    tc(LBX, y, l, fl, DARK, align="l", ref="Hy")
    for v in vs: tc(VLX, y, v, fv, DARK, align="l", ref="Hy"); y += 19
    y += 3
tc(PX, y + 6, "Vinywaji na chakula vitakuwepo.", c.fit("Vinywaji na chakula vitakuwepo.", lambda z: playi(z, 700), 17, MW), MAROON, ref="Vy")
YP = y + 28                                                              # ways to contribute
tc(PX, YP, "Michango:", mont(14, 700), DARK, ref="M")
lg = Image.open(HERE + "/logo_crdb.png").convert("RGBA"); lg = lg.crop(lg.getbbox())
LW = 88; lgr = lg.resize((c.P(LW), round(lg.height * c.P(LW) / lg.width)), Image.LANCZOS)
c.im.paste(lgr, (c.P(72), c.P(YP + 33) - lgr.height // 2), lgr)
tc(172, YP + 23, "PASSIONIST FATHERS", c.fit("PASSIONIST FATHERS", lambda z: mont(z, 700), 15, 178), DARK, align="l", ref="H")
tc(172, YP + 45, "10508412245", c.fit("10508412245", lambda z: mont(z, 800), 21, 178), MAROON, align="l", ref="1")
tc(PX, YP + 72, "Mawasiliano:", mont(14, 600), DARK, ref="M")
tc(PX, YP + 88, "0766 777 611 / 0783 903 800", c.fit("0766 777 611 / 0783 903 800", lambda z: mont(z, 700), 17, MW - 20), DARK, ref="0")
print("panel last line y", YP + 88)
c.paste_logo(250, 903, 88, dark_bg=False, anchor="cm")
save_card(c.im, CLIENT + "/outputs/" + OUT, "Fr. Josaphat Kiwori - Kadi ya Mwaliko (Harambee)", PREV, preview_w=1100)
print("saved", OUT, c.im.size)
