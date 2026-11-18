# Latifah Hellen - SEND-OFF v5 - Envaita two-panel "navy watercolour + torn gold edge" blueprint
# (sources/blueprint_navy_watercolor_twopanel.jpeg, 1775x1245 mockup).  Client wants a LIGHT background:
# right panel recoloured with a decreasing gradient map (navy -> cream/blush, blue-grey wash -> wine),
# gold edge kept; left panel = Latifa on a blush backdrop (photo_latifa_blush_backdrop.jpg, cutout of photo_latifa.jpg).
# Colours from the client's forwarded photo: blush pink, magenta, maroon/wine, black.
# run: ~/.haflaway/venv/bin/python build_v5.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *
from PIL import ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Latifah_Hellen_SendOff_v5_final_02.png"
PREV = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/39ac5a94-2c35-48a2-a078-0faa4526b442/scratchpad/v5_prev.jpg"
K = 2
LX, LY, LX2, LY2 = 92, 77, 858, 1151          # left panel (blueprint px)
RX, RY, RX2, RY2 = 904, 61, 1684, 1155        # right panel

src = cv2.imread(HERE + "/blueprint_navy_watercolor_twopanel.jpeg")
H0, W0 = src.shape[:2]

# ------------------------------------------------------------------ palette
CREAM = (252, 246, 242); WINE = (112, 22, 52); MAROON = (122, 26, 56); GOLD = (178, 130, 54)
GOLD_L = (226, 186, 112); ROSE = (190, 92, 124)
DRESS = [(240, 196, 200), (196, 38, 120), (110, 18, 44), (18, 16, 18)]   # blush, magenta, maroon, black

# ------------------------------------------------------------------ right panel: recolour
rp = src[RY:RY2, RX:RX2].copy(); h, w = rp.shape[:2]
hsv = cv2.cvtColor(rp, cv2.COLOR_BGR2HSV).astype(int)
L = cv2.cvtColor(rp, cv2.COLOR_BGR2GRAY).astype(np.float32)
gold = ((hsv[..., 0] >= 8) & (hsv[..., 0] <= 30) & (hsv[..., 1] > 70) & (hsv[..., 2] > 140)).astype(np.uint8)
n, lab, st, cen = cv2.connectedComponentsWithStats(gold, 8)
edge = np.zeros((h, w), np.uint8)
for i in range(1, n):
    if st[i, cv2.CC_STAT_HEIGHT] > 300 or (cen[i][0] > 530 and st[i, cv2.CC_STAT_AREA] >= 3): edge[lab == i] = 1
# text / icons / logo inside the dark area -> inpaint the luminance field
dark = (L < 80).astype(np.uint8)
darkfill = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, np.ones((35, 35), np.uint8))
txt = ((darkfill > 0) & (dark == 0) & (edge == 0)).astype(np.uint8)
txt[:, :] &= (np.arange(w)[None, :] < 560).astype(np.uint8)          # never touch the wash side
txt[1020:1090, 10:180] = 1                                            # Envaita logo
txt = cv2.dilate(txt, np.ones((5, 5), np.uint8), iterations=2) * (1 - edge)
Lu = np.clip(L, 0, 255).astype(np.uint8)
Lu = cv2.inpaint(Lu, txt, 9, cv2.INPAINT_TELEA)
box = np.zeros((h, w), np.uint8); box[812:1086, 568:778] = 1           # DOUBLE badge + QR
Lu = cv2.inpaint(Lu, box, 15, cv2.INPAINT_TELEA)
# smooth inpainted zones so no ghost of the old text survives
z = cv2.GaussianBlur(cv2.dilate(np.maximum(txt, box), np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 4)
Lf = Lu.astype(np.float32); Lf = cv2.GaussianBlur(Lf, (0, 0), 6)*z + Lf*(1 - z)
# edge pixels: take luminance of the neighbourhood (so the map under the gold is continuous)
Lf = cv2.inpaint(np.clip(Lf, 0, 255).astype(np.uint8), cv2.dilate(edge, np.ones((3, 3), np.uint8)), 5, cv2.INPAINT_TELEA).astype(np.float32)
# gradient map (decreasing): dark navy -> cream/blush paper, ink blotches -> rose, light wash -> wine
xs = [0, 18, 45, 90, 140, 180, 215, 255]
cols = np.array([(255, 250, 247), (253, 246, 242), (247, 230, 228), (234, 190, 198), (192, 104, 134),
                 (146, 42, 80), (112, 22, 52), (84, 14, 38)], np.float32)
lut = np.stack([np.interp(np.arange(256), xs, cols[:, k]) for k in range(3)], 1)
Lc = cv2.GaussianBlur(Lf, (0, 0), 0.8)
rgb = lut[np.clip(Lc, 0, 255).astype(np.uint8)]
# upscale, soft watercolour
rgbK = cv2.resize(rgb, (w*K, h*K), interpolation=cv2.INTER_CUBIC)
rgbK = cv2.GaussianBlur(rgbK, (0, 0), 1.2*K)
# gold edge: smooth antialiased mask + shading from the original gold
em = cv2.GaussianBlur(edge.astype(np.float32), (0, 0), 0.6)
emK = np.clip((cv2.resize(em, (w*K, h*K), interpolation=cv2.INTER_CUBIC) - 0.28)/0.3, 0, 1)
vK = cv2.resize(hsv[..., 2].astype(np.float32), (w*K, h*K), interpolation=cv2.INTER_CUBIC)
t = np.clip((vK - 170)/85, 0, 1)[..., None]
goldK = np.array((168, 118, 48), np.float32)*(1 - t) + np.array((232, 192, 118), np.float32)*t
rgbK = rgbK*(1 - emK[..., None]) + goldK*emK[..., None]
right = Image.fromarray(np.clip(rgbK, 0, 255).astype(np.uint8))

# ------------------------------------------------------------------ right panel: content
c = Card(right, K, resize=False)
serif = lambda sz, wt=500: c.f("PlayfairDisplay.ttf", sz, wt)
ital = lambda sz, wt=700: c.f("PlayfairDisplay-Italic.ttf", sz, wt)
body = lambda sz, wt=500: c.f("EBGaramond.ttf", sz, wt)
script = lambda sz: c.f("GreatVibes-Regular.ttf", sz)

def tc(x, yc, t, f, fill, sp=0):                     # ink centred vertically on yc
    bb = c.d.textbbox((0, 0), t, font=f); c.text(x, yc - (bb[1] + bb[3])/2/K, t, f, fill, sp=sp)

AX = 284
fam = ["FAMILIA YA", "BW. & BI. LING'ANDE", "WA MBWENI, DAR ES SALAAM,", "INAPENDA KUKUKARIBISHA"]
ff = min((c.fit(s, lambda z: serif(z, 600), 23, 440) for s in fam), key=lambda f: f.size)
for i, s in enumerate(fam): tc(AX, 70 + i*29, s, ff, WINE)
c.line(AX - 165, 212, AX + 165, 212, GOLD, 1.6)                       # guest-name line (blank)
for i, s in enumerate(["KWENYE SHEREHE YA KUMUAGA", "BINTI YAO MPENDWA (SEND-OFF)"]):
    tc(AX, 252 + i*29, s, ff, WINE)
fn = c.fit("Latifah Hellen", script, 96, 470)
tc(AX, 362, "Latifah Hellen", fn, MAROON)
tc(AX, 452, "ITAKAYOFANYIKA SIKU YA IJUMAA", c.fit("ITAKAYOFANYIKA SIKU YA IJUMAA", lambda z: serif(z, 700), 24, 440), WINE)
c.line(70, 492, 520, 492, GOLD, 1.6); c.line(70, 580, 520, 580, GOLD, 1.6)
fd = serif(64, 800); dt = "20.11.2026"
wd = c.width(dt, fd); x0 = AX - (wd + 62)/2 + 62
icon_calendar(c, x0 - 62, 512, 46, GOLD, 3.2)
bb = c.d.textbbox((0, 0), dt, font=fd); c.text(x0, 537 - (bb[1] + bb[3])/2/K, dt, fd, GOLD, align="l")

# two columns: Muda (clock) | Ukumbi (pin)
C1, C2 = 144, 400
cx, cy, r = C1, 636, 25                                               # clock icon
c.d.ellipse([c.P(cx - r), c.P(cy - r), c.P(cx + r), c.P(cy + r)], fill=WINE)
c.d.ellipse([c.P(cx - r + 4), c.P(cy - r + 4), c.P(cx + r - 4), c.P(cy + r - 4)], fill=CREAM)
c.line(cx, cy, cx, cy - 14, WINE, 3.2); c.line(cx, cy, cx + 10, cy + 5, WINE, 3.2)
c.d.ellipse([c.P(cx - 3), c.P(cy - 3), c.P(cx + 3), c.P(cy + 3)], fill=WINE)
icon_pin(c, C2, 632, 44, WINE, CREAM)
fl, fv = ital(24, 800), ital(22, 600)
tc(C1, 690, "Muda", fl, GOLD);   tc(C1, 720, "Kuanzia", fv, WINE);  tc(C1, 748, "saa 12:00 jioni", fv, WINE)
tc(C2, 690, "Ukumbi", fl, GOLD)
v1 = "JC Hall – Bahari Beach"
fv2 = min(c.fit(v1, lambda z: ital(z, 600), 22, 236), fv, key=lambda f: f.size)
tc(C2, 720, v1, fv2, WINE); tc(C2, 748, "Dar es Salaam", fv2, WINE)

tc(AX, 800, "Majibu kwa Wasiofika", ital(25, 800), GOLD)
fc = body(26, 600)
tc(AX, 836, "Evans Maseke - " + phone("0762467145"), fc, WINE)
tc(AX, 868, "Irene Mdami - " + phone("0784268720"), fc, WINE)

tc(AX, 918, "Rangi", ital(25, 800), GOLD)
swatches(c, AX, 940, DRESS, size=34, gap=16, shape="round", outline=GOLD)
tc(AX, 1000, "(Blush Pink, Magenta, Maroon & Black)", ital(19, 600), WINE)
c.paste_logo(22, 1056, 150, dark_bg=False)

# blank badge (system fills SINGLE/DOUBLE) + QR placeholder on the wine wash
c.d.rounded_rectangle([c.P(586), c.P(818), c.P(754), c.P(876)], c.P(4), fill=GOLD_L)
qr = src[945 - 0:1141, 1478:1673]                                     # old QR incl. white margin
qg = cv2.cvtColor(qr, cv2.COLOR_BGR2GRAY); qb = np.where(qg < 128, 0, 255).astype(np.uint8)
qimg = Image.fromarray(qb).resize(((1673 - 1478)*K, (1141 - 945)*K), Image.NEAREST).convert("RGB")
right.paste(qimg, ((1478 - RX)*K, (945 - RY)*K))

# ------------------------------------------------------------------ left panel: photo
lw, lh = (LX2 - LX)*K, (LY2 - LY)*K
# v5_final_02: user's photo "HELLEN 3" (lilac gown + gele, light interior) instead of the studio cutout
PHOTO = os.environ.get("PHOTO", "photo_latifa_hellen3.jpeg")
ph = Image.open(HERE + "/" + PHOTO).convert("RGB")
if PHOTO == "photo_latifa_hellen3.jpeg": ch = 1180; cxp = 601; top = 0          # gele to knees, sofa mostly out
else: ch = 2500; cxp = 1620; top = 880
cw = round(ch*lw/lh)
left = ph.crop((cxp - cw//2, top, cxp - cw//2 + cw, top + ch)).resize((lw, lh), Image.LANCZOS)
left = left.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
BLUSH = (248, 228, 228)
left = fade_to(left, BLUSH, lh*0.50, lh*0.78, power=1.15)
# gold sparkles (top-right drift + around the names), deterministic
rng = np.random.default_rng(20)
sp = Image.new("RGBA", (lw, lh), (0, 0, 0, 0)); sd = ImageDraw.Draw(sp)
for _ in range(260):
    if rng.random() < 0.55: x, y = rng.uniform(0.45, 1.0)*lw, rng.beta(1.2, 3.5)*lh*0.55
    else: x, y = rng.uniform(0.05, 0.95)*lw, rng.uniform(0.62, 0.98)*lh
    r = rng.choice([1.0, 1.4, 2.0, 2.8, 3.6], p=[.35, .3, .2, .1, .05])*K*0.8
    if 0.26*lw < x < 0.68*lw and y < 0.62*lh: continue                    # keep sparkles off her face/gele/gown
    a = int(rng.uniform(120, 255)); col = (200, 150, 70, a) if rng.random() < 0.7 else (255, 250, 240, a)
    sd.ellipse([x - r, y - r, x + r, y + r], fill=col)
left.paste(sp, (0, 0), sp)
cl = Card(left, K, resize=False)
sc = lambda sz: cl.f("GreatVibes-Regular.ttf", sz)
def tl(x, yc, t, f, fill, sp_=0):
    bb = cl.d.textbbox((0, 0), t, font=f); cl.text(x, yc - (bb[1] + bb[3])/2/K, t, f, fill, sp=sp_)
PW = LX2 - LX
tl(PW*0.45, 800, "Latifah", sc(124), MAROON)
tl(PW*0.58, 893, "Hellen", sc(124), MAROON)
tl(PW*0.20, 900, "send-off", cl.f("PlayfairDisplay-Italic.ttf", 30, 700), GOLD)
# date strip: NOVEMBA | IJUMAA 20 | 2026
fs = cl.f("PlayfairDisplay.ttf", 17, 600); fbig = cl.f("PlayfairDisplay.ttf", 40, 600)
mx = PW/2
tl(mx - 130, 1030, "NOVEMBA", fs, WINE, 1.5); tl(mx + 122, 1030, "2026", fs, WINE, 1.5)
tl(mx, 1000, "IJUMAA", cl.f("PlayfairDisplay.ttf", 15, 600), WINE, 1.2); tl(mx, 1036, "20", fbig, WINE)
cl.line(mx - 62, 992, mx - 62, 1060, GOLD, 1.3); cl.line(mx + 62, 992, mx + 62, 1060, GOLD, 1.3)

# ------------------------------------------------------------------ compose on the mockup backdrop
base = Image.fromarray(cv2.cvtColor(cv2.resize(src, (W0*K, H0*K), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB))
base.paste(left, (LX*K, LY*K)); base.paste(right, (RX*K, RY*K))
save_card(base, CLIENT + "/outputs/" + OUT, "Latifah Hellen - Send-Off", PREV, 1400)
print("saved", OUT, base.size)
