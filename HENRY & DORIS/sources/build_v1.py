# Henry & Doris - WEDDING v1 - Envaita "Brown-&-Burnt-Orange-Invitation" blueprint
# (blueprint_brown_roses_pampas.jpeg, 1526x2120, dummy "Denis & Mishel" wedding, same artwork as JOSHUA MSETI v1).
# Rendered at 2x (3052x4240). Self-contained: needs pillow, opencv-python-headless, numpy + fonts in ~/.haflaway/fonts
# run: python3 build_v1.py [out_name]
import sys, os
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE); ROOT = os.path.dirname(CLIENT)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Henry_&_Doris_v1_final_02.png"
FONTS = os.path.expanduser("~/.haflaway/fonts/")
LOGO = ROOT + "/HAFLAWAY BRAND/concept_4_green/haflaway_c4g_logo_horizontal_white.png"
K = 2                                                    # output scale vs blueprint px

# ------------------------------------------------------------------ 1. clean dummy text (flat brown background)
src = cv2.imread(HERE + "/blueprint_brown_roses_pampas.jpeg"); H0, W0 = src.shape[:2]
BG = np.array([22, 29, 68], np.uint8)                   # BGR of the flat card background
# text boxes (x1, y1, x2, y2) in blueprint px; x2 kept left of the flowers
TEXT = [(120, 226, 470, 274), (120, 280, 650, 328), (120, 333, 540, 382),     # family block (3 lines)
        (120, 460, 765, 512),                                                 # guest name + underline
        (120, 578, 765, 680), (120, 735, 770, 950),                           # "to the wedding..." + names
        (120, 1005, 770, 1112), (120, 1148, 770, 1302),                       # date, service
        (120, 1370, 865, 1530), (120, 1588, 760, 1742),                       # reception, rsvp
        (120, 1770, 560, 1932), (120, 1978, 440, 2090),                       # colours + chips, Envaita logo
        (1180, 1590, 1375, 1640)]                                             # "DOUBLE" inside the badge
clean = src.copy()
for x1, y1, x2, y2 in TEXT: clean[y1:y2, x1:x2] = BG
# soften the patch edges against the JPEG-noisy background
m = np.zeros((H0, W0), np.float32)
for x1, y1, x2, y2 in TEXT: m[y1:y2, x1:x2] = 1
m = cv2.GaussianBlur(m, (0, 0), 2)[..., None]
clean = (clean*m + src*(1 - m)).astype(np.uint8)
clean[1590:1640, 1180:1375] = BG                       # badge interior fully flat (outline left intact)

big = cv2.resize(clean, (W0*K, H0*K), interpolation=cv2.INTER_LANCZOS4)
card = Image.fromarray(cv2.cvtColor(big, cv2.COLOR_BGR2RGB)).convert("RGBA")
d = ImageDraw.Draw(card)

# ------------------------------------------------------------------ 2. fonts / helpers
CREAM = (226, 207, 193)
def var(file, size, wght):
    f = ImageFont.truetype(FONTS + file, int(size*K))
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f
light = lambda s: var("CormorantGaramond[wght].ttf", s, 500)
bold = lambda s: var("EBGaramond[wght].ttf", s, 700)
pop = lambda s: ImageFont.truetype(FONTS + "Poppins-SemiBold.ttf", int(s*K))
script = lambda s: ImageFont.truetype(FONTS + "PinyonScript-Regular.ttf", int(s*K))
LNUM = ["lnum"]                                         # lining figures (Cormorant defaults to old-style)
X = 136                                                 # left text edge (blueprint px)

def line(y_top, cap_h, text, font, fill=CREAM, x=X, sp=0):
    """place text so its cap top sits at y_top (blueprint px) like the blueprint lines"""
    bb = d.textbbox((0, 0), "H", font=font)
    yy = y_top*K - bb[1]
    if sp:
        cx = x*K
        for ch in text:
            d.text((cx, yy), ch, font=font, fill=fill, features=LNUM); cx += d.textlength(ch, font=font, features=LNUM) + sp*K
    else:
        d.text((x*K, yy), text, font=font, fill=fill, features=LNUM)
    return d.textbbox((x*K, yy), text, font=font, features=LNUM)

def fit(text, maker, size, max_w):
    while size > 10 and d.textlength(text, font=maker(size), features=LNUM) > max_w*K: size -= 0.5
    return maker(size)

# ------------------------------------------------------------------ 3. content
L = 46                                                  # light line size (cap ~31 px like blueprint)
line(234, 31, "FAMILIA YA", light(L))
line(288, 31, "GABRIEL MSELLE", light(L))
line(342, 31, "INAYO FURAHA KUKUALIKA", light(L))

d.line([(X*K, 506*K), (640*K, 506*K)], fill=CREAM, width=int(2*K))           # blank guest-name line (system fills)

line(586, 31, "KWENYE SHEREHE YA HARUSI", light(L))
line(640, 31, "YA WATOTO WAO WAPENDWA", light(L))

line(742, 48, "HENRY", bold(68))
d.text(((X + 14)*K, 792*K), "na", font=script(66), fill=CREAM)
line(895, 48, "DORIS", bold(68))

line(1015, 31, "ITAKAYOFANYIKA", light(L))
line(1066, 38, "JUMAMOSI, 21 NOVEMBA 2026", bold(50))

line(1156, 31, "MISA TAKATIFU", light(L))
line(1209, 32, "ST. JOSEPH CATHEDRAL, POSTA", fit("ST. JOSEPH CATHEDRAL, POSTA", bold, 44, 760))
line(1265, 31, "SAA 8:00 MCHANA", light(L))

line(1377, 31, "SHEREHE", light(L))
line(1431, 36, "WHITE SANDS HOTEL,", bold(48))
line(1485, 31, "TERRACE GARDEN, SAA 12:00 JIONI", light(L))         # time added 2026-11-18 (v1_final_02)

line(1596, 31, "MAWASILIANO", bold(44))
CON = ["0714 545 460 - OLIVA GABRIEL MSELLE", "0654 083 886 - JUNIOR LIBERATH MASSAWE"]
fc = min((fit(t, light, L, 900) for t in CON), key=lambda f: f.size)
line(1650, 31, CON[0], fc); line(1704, 31, CON[1], fc)

line(1777, 31, "RANGI", bold(44))
BROWNS = [(59, 33, 24), (111, 71, 42), (160, 106, 64), (205, 163, 120)]       # shades of brown
for i, col in enumerate(BROWNS):
    x0 = X + i*98
    d.rectangle([x0*K, 1847*K, (x0 + 84)*K, 1924*K], fill=col, outline=(240, 230, 220), width=int(2*K))
line(1872, 31, "(SHADES OF BROWN)", light(40), x=X + 4*98 + 14)

logo = Image.open(LOGO).convert("RGBA")
lw = 300*K; logo = logo.resize((lw, int(logo.height*lw/logo.width)), Image.LANCZOS)
card.alpha_composite(logo, (X*K, int(2032*K - logo.height/2)))

# ------------------------------------------------------------------ 4. save png + pdf
os.makedirs(CLIENT + "/outputs", exist_ok=True)
rgb = card.convert("RGB")
rgb.save(CLIENT + "/outputs/" + OUT, dpi=(300, 300))
rgb.save(CLIENT + "/outputs/" + OUT.replace(".png", ".pdf"), "PDF", resolution=300, title="Henry & Doris - Harusi")
prev = rgb.copy(); prev.thumbnail((1100, 1600)); prev.save(sys.argv[2] if len(sys.argv) > 2 else "/tmp/hd_prev.jpg", quality=90)
print("saved", OUT, rgb.size)
