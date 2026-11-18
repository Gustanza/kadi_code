# Albert & Beatrice v7 - client's current card (client_card_2026-11-16.jpeg, 853x1280 WhatsApp copy, from ~/Downloads)
# with the script capital "A" of "Albert" (Great Vibes loop that reads as a small "a") replaced by a clear capital A
# (Parisienne, same brown, same height/baseline, slightly emboldened to match the Great Vibes stroke).
# Work is done at S x the WhatsApp size. run: ~/.haflaway/venv/bin/python -I build_v7.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *
from PIL import ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Albert_&_Beatrice_v7_final_03.png"
SCR = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/39ac5a94-2c35-48a2-a078-0faa4526b442/scratchpad/"
S = 3
FONTS = os.path.expanduser("~/.haflaway/fonts/")

src = cv2.imread(HERE + "/client_card_2026-11-16.jpeg"); H0, W0 = src.shape[:2]
g = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

# 1. erase the old A (its ink only; the "l" starts at x~126, its loop top at y~391)
yy, xx = np.mgrid[0:H0, 0:W0]
zone = (xx >= 56) & (yy >= 374) & (yy <= 456) & ((((xx <= 121) & ~((yy > 415) & (xx > 116)))) | ((yy <= 390) & (xx <= 137)) | ((yy <= 406) & (xx <= 133)) | ((yy <= 401) & (xx <= 135)))
ink = cv2.dilate(((g < 200) & zone).astype(np.uint8)*255, np.ones((3, 3), np.uint8), iterations=2)
clean = cv2.inpaint(src, ink, 7, cv2.INPAINT_TELEA)

# 2. "lbert Libent" moved right by SHIFT px so the wider new A keeps the line centred (letters re-laid from their own ink)
SHIFT = int(os.environ.get("SHIFT", "10"))
R = (116, 372, 434, 467)                                  # x1, y1, x2, y2 (stays above the gold divider)
reg = np.zeros((H0, W0), bool); reg[R[1]:R[3], R[0]:R[2]] = True; reg[R[3]:472, 305:330] = True   # tail of the L loop
tailstrip = np.zeros_like(reg); tailstrip[R[3]:472, 305:330] = True
rest = (g < 205) & reg & ~zone
rest[R[3]:472, 305:330] &= (g[R[3]:472, 305:330] < 140) & (src[R[3]:472, 305:330, 2].astype(int) - src[R[3]:472, 305:330, 0] < 95)   # brown loop only, not the tan divider
n_, lab_, st_, _ = cv2.connectedComponentsWithStats(rest.astype(np.uint8), 8)
for k in range(1, n_):
    if st_[k, cv2.CC_STAT_AREA] < 25 and st_[k, cv2.CC_STAT_LEFT] < 140: rest[lab_ == k] = False   # crumbs of the old A
clean = cv2.inpaint(clean, cv2.dilate((((g < 205) & reg & ~zone & ~tailstrip) & ~rest).astype(np.uint8)*255, np.ones((3, 3), np.uint8), iterations=2), 5, cv2.INPAINT_TELEA)
alpha = np.clip((236.0 - g)/(236.0 - 70.0), 0, 1)*cv2.dilate(rest.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
clean = cv2.inpaint(clean, cv2.dilate(rest.astype(np.uint8)*255, np.ones((3, 3), np.uint8), iterations=2), 7, cv2.INPAINT_TELEA)
INK = (100, 69, 32)
al = np.zeros_like(alpha); al[:, SHIFT:] = alpha[:, :-SHIFT]
INK_BGR = np.array(INK[::-1], np.float32)
clean = (clean.astype(np.float32)*(1 - al[..., None]) + INK_BGR*al[..., None]).astype(np.uint8)
# restore the gold divider where the old L-loop end touched it (inpaint had smoothed it to paper)
dz = (slice(469, 478), slice(296, 340))
sd = src[dz].astype(int); div = (sd[..., 2] - sd[..., 0] > 30) & (cv2.cvtColor(src[dz], cv2.COLOR_BGR2GRAY) > 140) & (al[dz] < 0.2)
clean[dz][div] = src[dz][div]

# 2b. same for "Adelitus": erase its A, "Beatrice" re-laid 8px left and "delitus" 8px right to make room
def relay(img, mask, dx):
    """move the ink in mask by dx px (re-laid in INK from its own darkness), paper inpainted behind"""
    a_ = np.clip((236.0 - g)/(236.0 - 70.0), 0, 1)*cv2.dilate(mask.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    img = cv2.inpaint(img, cv2.dilate(mask.astype(np.uint8)*255, np.ones((3, 3), np.uint8), iterations=2), 7, cv2.INPAINT_TELEA)
    sh = np.zeros_like(a_)
    if dx > 0: sh[:, dx:] = a_[:, :-dx]
    else: sh[:, :dx] = a_[:, -dx:]
    return (img.astype(np.float32)*(1 - sh[..., None]) + INK_BGR*sh[..., None]).astype(np.uint8)
DSH = int(os.environ.get("DSH", "8"))
zoneB = (xx >= 254) & (yy >= 566) & (yy <= 632) & (((xx <= 305) & ~((yy > 608) & (xx > 300))) | ((yy <= 596) & (xx <= 320)))
inkB = cv2.dilate(((g < 200) & zoneB).astype(np.uint8)*255, np.ones((3, 3), np.uint8), iterations=2)
clean = cv2.inpaint(clean, inkB, 7, cv2.INPAINT_TELEA)
band = (yy >= 560) & (yy <= 640) & (g < 205) & ~zoneB
clean = relay(clean, band & (xx >= 40) & (xx < 254), -(DSH + 3))                   # Beatrice
rest2 = band & (xx > 300) & (xx <= 446)
n_, lab_, st_, _ = cv2.connectedComponentsWithStats(rest2.astype(np.uint8), 8)
for k in range(1, n_):
    if st_[k, cv2.CC_STAT_AREA] < 25 and st_[k, cv2.CC_STAT_LEFT] < 322: rest2[lab_ == k] = False
clean = relay(clean, rest2, DSH)                                              # delitus

# 2c. client 2026-11-17: Rangi "Nyeupe" -> "Off White": erase the caption (re-typed after upscale), chip 1 -> off-white
cap = ((g < 190) & (yy >= 1097) & (yy <= 1124) & (xx >= 358) & (xx <= 556)).astype(np.uint8)*255
clean = cv2.inpaint(clean, cv2.dilate(cap, np.ones((3, 3), np.uint8), iterations=2), 7, cv2.INPAINT_TELEA)
chip = (np.hypot(xx - 266, yy - 1108) <= 10.5)
OFFW = np.array([226, 238, 246], np.float32)                     # BGR of off-white (246,238,226)
cw = np.clip((10.5 - np.hypot(xx - 266, yy - 1108))/1.5, 0, 1)[..., None]
clean = (clean.astype(np.float32)*(1 - cw) + OFFW*cw).astype(np.uint8)

# 3. upscale and set the new A (Parisienne, 82% width, old A height/baseline, right edge just before the shifted "l")
big = Image.fromarray(cv2.cvtColor(cv2.resize(clean, (W0*S, H0*S), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB))
TOP, BASE, RIGHT, SX = 381, 451, 129 + SHIFT, float(os.environ.get("SX", "0.82"))
for sz in range(40, 260):
    f = ImageFont.truetype(FONTS + "Parisienne-Regular.ttf", sz*S); bb = f.getbbox("A")
    if bb[3] - bb[1] >= (BASE - TOP)*S: break
lay = Image.new("L", (bb[2] + 40*S, bb[3] + 40*S), 0)
ImageDraw.Draw(lay).text((20*S, 20*S), "A", font=f, fill=255, stroke_width=round(0.9*S), stroke_fill=255)
lay = lay.crop(lay.getbbox()); lay = lay.resize((round(lay.width*SX), lay.height), Image.LANCZOS)
lay = lay.filter(ImageFilter.GaussianBlur(0.45*S))      # match the soft edges of the WhatsApp-compressed lettering
x0 = RIGHT*S - lay.width; y0 = BASE*S - lay.height
big.paste(Image.new("RGB", lay.size, INK), (x0, y0), lay)
print("name line x", x0/S, "-", 427 + SHIFT)
# Adelitus A: old A ink box y 571..627, right edge just before the shifted "d"
TOP, BASE, RIGHT = 571, 627, 316 + DSH; SXB = 0.76
for sz in range(40, 260):
    f = ImageFont.truetype(FONTS + "Parisienne-Regular.ttf", sz*S); bb = f.getbbox("A")
    if bb[3] - bb[1] >= (BASE - TOP)*S: break
lay = Image.new("L", (bb[2] + 40*S, bb[3] + 40*S), 0)
ImageDraw.Draw(lay).text((20*S, 20*S), "A", font=f, fill=255, stroke_width=round(0.8*S), stroke_fill=255)
lay = lay.crop(lay.getbbox()); lay = lay.resize((round(lay.width*SXB), lay.height), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.45*S))
x0 = RIGHT*S - lay.width; big.paste(Image.new("RGB", lay.size, INK), (x0, BASE*S - lay.height), lay)
print("Adelitus A x", x0/S, "-", RIGHT)
# Rangi caption re-typed (Playfair Italic, same ink, same left edge / x-height as the old one)
CAP = "(Kahawia, Blue & Off White)"; CAP_INK = (88, 66, 46)
for sz in range(10, 40):
    fc = ImageFont.truetype(FONTS + "PlayfairDisplay-Italic.ttf", sz*S); fc.set_variation_by_axes([600])
    bb = fc.getbbox("(K"); 
    if bb[3] - bb[1] >= (1118 - 1103)*S: break
dc = ImageDraw.Draw(big); bb = dc.textbbox((0, 0), CAP, font=fc)
dc.text((362*S - bb[0], 1119*S - bb[3] + (bb[3] - dc.textbbox((0, 0), "(K", font=fc)[3])), CAP, font=fc, fill=CAP_INK)
print("caption ends x", (362*S + bb[2] - bb[0])/S)

save_card(big, CLIENT + "/outputs/" + OUT, "Albert & Beatrice - Mwaliko wa Harusi", SCR + "ab_prev.jpg", 900)
big.crop((20*S, 360*S, 460*S, 650*S)).resize((660, 435)).save(SCR + "ab_name.png")
print("saved", OUT, big.size)
