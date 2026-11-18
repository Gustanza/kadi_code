# Albert & Beatrice - v6 = v5 (the client's own card: white top block, gold flowers, rings, dress-code bar) + the CENTRE
# CONTAINER idea from v3 (frosted glass panel with a faint outer frame over the couple photo, text inside it in dark ink).
# User 2026-11-15: "i want v5 to still feel like it is still v5, but i want the idea of the center container in v3 in v5".
# The photo window (client card 120..632 x 306..880) is rebuilt from the clean photo_A (the client's card had it stretched
# and covered in text); faces stay visible above the panel, bodies blur through it. Old text spilling outside the window
# is inpainted away. Everything outside the window = v5 (client card upscaled 3x).
# run: ~/.haflaway/venv/bin/python build_v6.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *
from PIL import ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Albert_&_Beatrice_v6_final_03.png"
PREV = os.environ.get("PREV", "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/f6869231-aece-4aa7-8bb0-00983d70b42f/scratchpad/ab_v6_prev.jpg")
U = 3
src = cv2.imread(HERE + "/client_card_reference.jpeg"); H, W = src.shape[:2]
b_, g_, r_ = [src[:, :, i].astype(int) for i in range(3)]
WX1, WY1, WX2, WY2 = 120, 306, 632, 880                    # photo window
P = lambda v: round(v*U)

# ---- flowers (stay on top of the new photo / panel)
flower = ((r_ > 180) & (g_ > 125) & (b_ < 120) & (r_ - b_ > 80)).astype(np.uint8)
flower[:, :560] = 0
flower = cv2.morphologyEx(flower, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
cs, _ = cv2.findContours(flower, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
flower = np.zeros_like(flower); cv2.drawContours(flower, [k for k in cs if cv2.contourArea(k) > 80], -1, 1, -1)

# ---- remove old text that spills outside the window (left "katika", right "alasiri / Ukumbi wa / ...waruhusiwi")
txt = np.zeros((H, W), np.uint8)
lum = src.mean(axis=2)
flz = cv2.dilate(flower, np.ones((3, 3), np.uint8)) == 1
sat = src.max(axis=2).astype(int) - src.min(axis=2)
for x1, y1, x2, y2 in [(90, 576, WX1 + 2, 628), (WX2 - 2, 596, 705, 726), (WX2 - 2, 755, 705, 884), (556, 755, WX2, 884)]:
    m = np.zeros((H, W), bool); m[y1:y2, x1:x2] = True
    t = m & ((src.max(axis=2) < 140) | (~flz & ((lum < 222) & (sat < 40) | ((r_ - b_ > 45) & (g_ < 200)))))
    txt[t] = 255
# faint grey "wa" (end of "Ukumbi wa") lies semi-transparent on a gold leaf: take pixels darker than the local leaf colour
bx1, by1, bx2, by2 = 636, 684, 702, 722
sub = src[by1:by2, bx1:bx2]; sl = sub.mean(axis=2)
med = cv2.medianBlur(sub, 15).mean(axis=2)
txt[by1:by2, bx1:bx2][(sl < med - 18)] = 255
img = cv2.inpaint(src, cv2.dilate(txt, np.ones((3, 3), np.uint8), iterations=2), 5, cv2.INPAINT_TELEA)
# left of the window (old "katika" spill): plain card background - blend the clean rows above/below, no inpaint smear
ya, yb = 572, 632
for yy in range(ya + 1, yb):
    t_ = (yy - ya)/(yb - ya)
    img[yy, 86:WX1] = ((1 - t_)*src[ya, 86:WX1].astype(float) + t_*src[yb, 86:WX1].astype(float)).astype(np.uint8)
card = upscale_soft(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), U)
orig = card.copy()

def centre_lines(card, lines, box=None, wipe=()):
    """Lift text lines off the card (un-blended against an inpainted background) and re-place them centred on the card
    axis. lines: (y1, y2, x1, x2, kind 'navy'|'ink', limit) in 1x units; limit = ('L', x) / ('R', x) = keep the line
    clear of decoration on that side (shrinks it just enough), or None."""
    A0 = np.asarray(card).astype(np.float32)
    lumA = A0.mean(axis=2); R_, G_, B_ = A0[:, :, 0], A0[:, :, 1], A0[:, :, 2]
    satA = A0.max(axis=2) - A0.min(axis=2)
    CXC = W/2
    allm = np.zeros(lumA.shape, np.uint8); pieces = []
    for y1, y2, x1, x2, kind, lim in lines:
        ys, xs = slice(P(y1), P(y2)), slice(P(x1), P(x2))
        if kind == "navy": m = (B_[ys, xs] > R_[ys, xs] + 25) & (lumA[ys, xs] < 200)
        else: m = ((lumA[ys, xs] < 205) & (satA[ys, xs] < 45)) | (A0[ys, xs].max(axis=2) < 150)   # 2nd: letters on flowers
        mm = np.zeros(lumA.shape, np.uint8); mm[ys, xs] = m
        mm = cv2.dilate(mm, np.ones((5, 5), np.uint8)); allm |= mm
        pieces.append((y1, y2, x1, x2, kind, lim, mm))
    # the original letters carry a white outline/glow: widen the removal area, but never into gold leaves/flowers
    leafA = ((R_ - B_ > 50) & (satA > 50) & (A0.max(axis=2) > 165)).astype(np.uint8)
    allm = cv2.dilate(allm, np.ones((17, 17), np.uint8)) & (1 - cv2.dilate(leafA, np.ones((3, 3), np.uint8)))
    for x1, y1, x2, y2 in wipe: allm[P(y1):P(y2), P(x1):P(x2)] = 1         # old text + glow on flowers: wipe whole patch
    small = cv2.resize(A0.astype(np.uint8), None, fx=1/U, fy=1/U, interpolation=cv2.INTER_AREA)
    sm = cv2.resize(allm, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
    bgs = cv2.inpaint(small, cv2.dilate(sm, np.ones((3, 3), np.uint8))*255, 7, cv2.INPAINT_TELEA)
    bg = cv2.GaussianBlur(cv2.resize(bgs, (A0.shape[1], A0.shape[0]), interpolation=cv2.INTER_CUBIC), (9, 9), 0).astype(np.float32)
    out = A0.copy(); out[allm == 1] = bg[allm == 1]
    for x1, y1, x2, y2 in wipe:                                             # feather the wiped patch into the petals
        fm = np.zeros(lumA.shape, np.float32); fm[P(y1) + 6:P(y2) - 6, P(x1) + 6:P(x2) - 6] = 1
        fm = cv2.GaussianBlur(fm, (0, 0), 7)[..., None]
        ys, xs = slice(P(y1) - 30, P(y2) + 30), slice(P(x1) - 30, P(x2) + 30)
        keep = (allm[ys, xs] == 1)[..., None] & ~np.zeros_like(fm[ys, xs], bool)
        out[ys, xs] = np.where(keep, bg[ys, xs]*fm[ys, xs] + A0[ys, xs]*(1 - fm[ys, xs]), out[ys, xs])
        # where the old letters were, never fall back to the original pixels
        lt = np.zeros(lumA.shape, np.uint8); lt[ys, xs] = cv2.dilate(((A0[ys, xs].max(axis=2) < 170)).astype(np.uint8), np.ones((9, 9), np.uint8))
        out[lt == 1] = bg[lt == 1]
    if box:   # a plain panel behind the text: repaint it in its own colour (kills the old letters' white glow)
        bm = np.zeros(lumA.shape, bool); bm[P(box[1]):P(box[3]), P(box[0]):P(box[2])] = True
        bm &= ~(cv2.dilate(leafA, np.ones((7, 7), np.uint8)) == 1)
        out[bm] = np.median(A0[bm & (lumA > 238) & (satA < 12)], axis=0)
    for y1, y2, x1, x2, kind, lim, mm in pieces:
        ys, xs = slice(P(y1), P(y2)), slice(P(x1), P(x2))
        cr, bgc, mk = A0[ys, xs], bg[ys, xs], mm[ys, xs]
        col = np.median(cr[(cr.mean(axis=2) < (90 if kind == "navy" else 60)) & (mk == 1)], axis=0)
        bl, cl = bgc.mean(axis=2), cr.mean(axis=2)
        al = np.clip((bl - cl)/np.maximum(bl - col.mean(), 1), 0, 1)*mk
        cols = np.where(al.max(axis=0) > 0.3)[0]; rows = np.where(al.max(axis=1) > 0.3)[0]
        c0, c1, r0, r1 = cols.min(), cols.max() + 1, rows.min(), rows.max() + 1
        al = al[r0:r1, c0:c1]; wpx = c1 - c0
        s = 1.0
        if lim: s = min(1.0, 2*((CXC - (lim[1] + 6)) if lim[0] == "L" else (lim[1] - CXC))*U/wpx)
        al_s = cv2.resize(al, (max(1, round(wpx*s)), max(1, round((r1 - r0)*s))), interpolation=cv2.INTER_AREA)
        ay = P(y1) + r0 + ((r1 - r0) - al_s.shape[0])//2                  # keep each line's vertical centre
        ax = round(P(CXC) - al_s.shape[1]/2)
        reg = out[ay:ay + al_s.shape[0], ax:ax + al_s.shape[1]]
        out[ay:ay + al_s.shape[0], ax:ax + al_s.shape[1]] = reg*(1 - al_s[..., None]) + col*al_s[..., None]
        print("line", y1, "scale", round(s, 3), "x", round(ax/U), round((ax + al_s.shape[1])/U))
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

# ---- final_02: centre the top block (title + 4 family lines) on the card axis; the title + line 1 shrink just enough
# to clear the gold leaves top-left (x<=168).
if os.environ.get("TOPCENTER", "1") == "1":
    card = centre_lines(card, [(112, 166, 158, 722, "navy", ("L", 170)), (167, 198, 176, 722, "ink", ("L", 175)),
                               (198, 226, 112, 700, "ink", ("L", 101)), (226, 255, 176, 640, "ink", None),
                               (255, 284, 222, 594, "ink", None)])

# ---- final_03: centre the bottom block too (user picked "card centre"): Mawasiliano full size; phone line shrinks so it
# reaches no further onto the gold flower than on their card (right end x<=570); the dress-code bar slides to the centre.
if os.environ.get("BOTCENTER", "1") == "1":
    card = centre_lines(card, [(888, 920, 300, 503, "ink", None), (921, 954, 70, 578, "ink", ("R", 570))], box=(68, 881, 506, 954), wipe=[(498, 919, 582, 956)])
    A = np.asarray(card).copy(); r, g, b = [A[:, :, i].astype(int) for i in range(3)]
    reg = (slice(P(962), P(1024)), slice(P(135), P(432)))
    bar = (r[reg] > 215) & (g[reg] > 150) & (g[reg] < 220) & (b[reg] < 100)
    rows = np.where(bar.sum(axis=1) > 0.6*bar.shape[1]*0.8)[0]                  # solid bar rows / columns only
    by1, by2 = P(962) + rows.min(), P(962) + rows.max() + 1
    colsb = np.where(bar[rows.min():rows.max() + 1].mean(axis=0) > 0.25)[0]
    bx1, bx2 = P(135) + colsb.min(), P(135) + colsb.max() + 1
    piece = A[by1:by2, bx1:bx2].copy()
    nx1 = round(P(W/2) - (bx2 - bx1)/2)
    # uncovered strip on the left: blend the clean rows just above / below the old bar, column by column
    ya, yb = by1 - 9, by2 + 9
    t_ = ((np.arange(ya + 1, yb) - ya)/(yb - ya))[:, None, None]
    xa, xb2 = bx1 - 9, nx1 + 9
    A[ya + 1:yb, xa:xb2] = ((1 - t_)*A[ya, xa:xb2].astype(float) + t_*A[yb, xa:xb2].astype(float)).astype(np.uint8)
    A[ya + 1:yb, xa + 6:xb2 - 6] = cv2.GaussianBlur(A[ya + 1:yb, xa:xb2], (31, 1), 0)[:, 6:-6]   # no column streaks
    A[by1:by2, nx1:nx1 + (bx2 - bx1)] = piece
    print("bar", round(bx1/U), round(bx2/U), "->", round(nx1/U), round((nx1 + bx2 - bx1)/U))
    card = Image.fromarray(A)

# ---- new photo window from photo_A (heads near the top, above the panel)
ww, wh = P(WX2 - WX1), P(WY2 - WY1)
ph = crop_to(upscale_soft(load_photo(HERE + "/photo_A.jpeg"), 2.0), ww, wh, cx_frac=0.5,
             top_frac=float(os.environ.get("TOP", "0.115")), zoom=float(os.environ.get("ZOOM", "1.0")))
ph = ImageEnhance.Brightness(ph).enhance(1.05)
win = Image.new("RGB", card.size); win.paste(ph, (P(WX1), P(WY1)))
blur = win.filter(ImageFilter.GaussianBlur(P(5)))

# panel geometry (v3 idea: faint outer frame + frosted inner panel)
OX1, OY1, OX2, OY2 = 134, 446, 618, 872
PX1, PY1, PX2, PY2 = 148, 460, 604, 862
outer = Image.blend(win, Image.new("RGB", card.size, (255, 255, 255)), 0.14)
frost = Image.blend(blur, Image.new("RGB", card.size, (246, 244, 242)), 0.66)
layer = win.copy()
mo = Image.new("L", card.size, 0); ImageDraw.Draw(mo).rectangle([P(OX1), P(OY1), P(OX2), P(OY2)], fill=255)
layer = Image.composite(outer, layer, mo)
mp = Image.new("L", card.size, 0); ImageDraw.Draw(mp).rectangle([P(PX1), P(PY1), P(PX2), P(PY2)], fill=255)
layer = Image.composite(frost, layer, mp)

wm = Image.new("L", card.size, 0); ImageDraw.Draw(wm).rectangle([P(WX1), P(WY1), P(WX2) - 1, P(WY2) - 1], fill=255)
fl = cv2.resize(flower.astype(np.float32), card.size, interpolation=cv2.INTER_LINEAR)
fl = cv2.GaussianBlur(fl, (7, 7), 0)
wa = (np.asarray(wm).astype(np.float32)/255)*(1 - fl)
card = Image.composite(layer, card, Image.fromarray((wa*255).astype(np.uint8)))

# ---- text in the panel (v5's type colours: gold names w/ navy edge, blue date, black body, serif ukumbi)
c = Card(card, U, resize=False)
NAVY = (12, 22, 64); INK = (20, 20, 24); BLUE = (22, 34, 190); GOLD = (244, 178, 24); DGOLD = (150, 96, 8); BROWN = (70, 44, 20)
mont = lambda z, w=700: c.f("Montserrat.ttf", z, w)
CX = (PX1 + PX2)/2; MW = PX2 - PX1 - 30

def stroked(y, t, f, fill, sw=1.4, edge=NAVY):
    w = c.width(t, f); c.d.text((P(CX - w/2), P(y)), t, font=f, fill=fill, stroke_width=P(sw), stroke_fill=edge)

def h(f, t="Ag"):
    bb = c.d.textbbox((0, 0), t, font=f); return (bb[3] - bb[1])/U, bb[1]/U

# rows: (text, font, colour, kind, max width)
fit = lambda t, mk, z, mw=MW: c.fit(t, mk, z, mw)
rows = [
    ("Kwenye Harusi ya Vijana wao", lambda z: mont(z, 500), INK, "t", MW, 20),
    ("Albert Libent", lambda z: c.f("Poppins-Bold.ttf", z), GOLD, "s", MW, 36),
    ("&", lambda z: c.f("Poppins-Bold.ttf", z), GOLD, "s", MW, 26),
    ("Beatrice Adelitus", lambda z: c.f("Poppins-Bold.ttf", z), GOLD, "s", MW, 36),
    ("Itakayofanyika Jumamosi", lambda z: mont(z, 500), INK, "t", MW, 17.5),
    ("21 November, 2026", lambda z: mont(z, 800), BLUE, "t", MW, 29),
    ("katika Kanisa Katoliki Msimbazi, Parokia ya", lambda z: mont(z, 700), INK, "t", MW, 17.5),
    ("Msimbazi Dsm kuanzia saa 9:00 alasiri", lambda z: mont(z, 700), INK, "t", MW, 17.5),
    ("na baadae kufuatiwa na sherehe itakayofanyika", lambda z: mont(z, 700), INK, "t", MW, 17.5),
    ("katika Ukumbi wa", lambda z: mont(z, 700), INK, "t", MW, 17.5),
    ("Grand Paradise (Platinum)", lambda z: c.f("PlayfairDisplay.ttf", z, 700), BROWN, "t", MW, 30),
    ("Yombo Vituka, Mwisho wa Lami", lambda z: mont(z, 800), DGOLD, "t", 390, 18.5),
    ("kuanzia saa 12:00 jioni.", lambda z: mont(z, 700), NAVY, "t", 390, 18.5),
    ("Tafadhali fika na kadi hii", lambda z: mont(z, 600), NAVY, "t", 380, 17),
    ("“Watoto tunawapenda lakini hawaruhusiwi”", lambda z: c.f("PlayfairDisplay-Italic.ttf", z, 600), BROWN, "t", 380, 17.5),
]
# extra gaps before these rows (section breaks), then spread evenly inside the panel
brk = {1: 6, 4: 4, 6: 6, 10: 4, 11: 2, 13: 6}
fonts = [fit(t, mk, z, mw) for t, mk, col, k, mw, z in rows]
hs = [h(f, "&" if t == "&" else "Ag") for f, (t, *_) in zip(fonts, rows)]
tot = sum(x[0] for x in hs) + sum(brk.values())
gap = (PY2 - PY1 - 26 - tot)/(len(rows) - 1)
y = PY1 + 13
for i, ((t, mk, col, k, mw, z), f, (hh, off)) in enumerate(zip(rows, fonts, hs)):
    y += brk.get(i, 0)
    if k == "s": stroked(y - off, t, f, col)
    else: c.text(CX, y - off, t, f, col)
    y += hh + gap

# gold rule at the top of the photo (as on their card)
c.line(190, 318, 655, 318, (214, 172, 64), 1.6)
save_card(c.im, CLIENT + "/outputs/" + OUT, "Albert & Beatrice - Harusi", PREV, preview_w=1000)
print("saved", OUT, "gap", round(gap, 1))
