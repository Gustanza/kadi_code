# Fr. Maximilian Wambura - ANNIVERSARY (Upadrisho) v1 - blueprint = his own birthday poster
# (blueprint_birthday_kolbe_sky.jpeg, 672x896: sky + rays, Happy Birthday, Fr. Maximilian Wambura, St. Maximilian Kolbe x2, cake).
# Birthday wording removed -> Anniversary; cake + "You are loved" banner covered by a brown/gold details plaque.
# Rendered at 3x (2016x2688). run: python3 build_v1.py [out_name] [preview_path]
import sys, os
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE); ROOT = os.path.dirname(CLIENT)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Fr_Maximilian_Wambura_Anniversary_v1_final_01.png"
FONTS = os.path.expanduser("~/.haflaway/fonts/")
LOGO = ROOT + "/HAFLAWAY BRAND/concept_4_green/haflaway_c4g_logo_horizontal_white.png"
K = 3
LNUM = ["lnum"]

# ------------------------------------------------------------------ 1. remove birthday text (inpaint over soft sky)
src = cv2.imread(HERE + "/blueprint_birthday_kolbe_sky.jpeg"); H0, W0 = src.shape[:2]
BOXES = [(178, 80, 494, 143),     # "Happy Birthday"
         (180, 214, 490, 236),    # "Tunamshukuru Mungu kwa Zawadi ya uhai"
         (196, 239, 480, 289)]    # 3-line Kolbe paragraph
mask = np.zeros((H0, W0), np.uint8)
for x1, y1, x2, y2 in BOXES: mask[y1:y2, x1:x2] = 255
clean = cv2.inpaint(src, mask, 9, cv2.INPAINT_TELEA)
soft = cv2.GaussianBlur(clean, (0, 0), 7)
m = cv2.GaussianBlur(mask.astype(np.float32)/255, (0, 0), 3)[..., None]
clean = (soft*m + clean*(1 - m)).astype(np.uint8)

big = cv2.resize(clean, (W0*K, H0*K), interpolation=cv2.INTER_LANCZOS4)
card = Image.fromarray(cv2.cvtColor(big, cv2.COLOR_BGR2RGB)).filter(ImageFilter.UnsharpMask(3, 60, 2)).convert("RGBA")

# ------------------------------------------------------------------ 2. helpers
def var(file, size, wght):
    f = ImageFont.truetype(FONTS + file, int(size*K))
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f
serif = lambda s, w=500: var("EBGaramond[wght].ttf", s, w)
corm = lambda s, w=600: var("CormorantGaramond[wght].ttf", s, w)
script = lambda s: ImageFont.truetype(FONTS + "GreatVibes-Regular.ttf", int(s*K))
GOLD_T, GOLD_B = (236, 200, 120), (150, 104, 36)          # gradient for gold lettering
GOLD = (222, 184, 110); CREAM = (250, 236, 205); INK = (30, 28, 30)

def center_text(img, cx, cy, text, font, fill, shadow=None):
    d = ImageDraw.Draw(img)
    bb = d.textbbox((0, 0), text, font=font, features=LNUM)
    x = cx*K - (bb[0] + bb[2])/2; y = cy*K - (bb[1] + bb[3])/2
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((x, y + 1.5*K), text, font=font, fill=shadow, features=LNUM)
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(1.5*K)))
    d.text((x, y), text, font=font, fill=fill, features=LNUM)
    return x, y, bb

def gold_text(img, cx, cy, text, font):
    """gold vertical gradient lettering with a soft warm shadow (matches the blueprint's gold title)"""
    d = ImageDraw.Draw(img)
    bb = d.textbbox((0, 0), text, font=font)
    x = cx*K - (bb[0] + bb[2])/2; y = cy*K - (bb[1] + bb[3])/2
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).text((x, y), text, font=font, fill=255)
    sh = Image.new("RGBA", img.size, (90, 60, 20, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(2*K)).point(lambda v: v*0.55))
    img.alpha_composite(sh, (0, int(1.5*K)))
    t, b = int(y + bb[1]), int(y + bb[3])
    grad = Image.new("RGBA", img.size)
    gd = ImageDraw.Draw(grad)
    for yy in range(t, b + 1):
        k = (yy - t)/max(1, b - t); k = 0.5 - 0.5*np.cos(k*np.pi)
        col = tuple(int(GOLD_T[i]*(1 - k) + GOLD_B[i]*k) for i in range(3)) + (255,)
        gd.line([(0, yy), (img.width, yy)], fill=col)
    grad.putalpha(m); img.alpha_composite(grad)

def fit(text, maker, size, max_w):
    d = ImageDraw.Draw(card)
    while size > 6 and d.textlength(text, font=maker(size), features=LNUM) > max_w*K: size -= 0.25
    return maker(size)

# ------------------------------------------------------------------ 3. top text
gold_text(card, 336, 110, "Happy Anniversary", fit("Happy Anniversary", script, 64, 360))
center_text(card, 336, 226, "Tunamshukuru Mungu kwa Zawadi ya Upadri", fit("Tunamshukuru Mungu kwa Zawadi ya Upadri", serif, 17, 320), INK)
PAR = ["Mt. Maximilian Kolbe akuombee katika wito wako.",
       "Na katika kumbukizi ya Upadrisho wako",
       "aendelee kuwa mwombezi wako."]
fp = min((fit(t, serif, 12.6, 282) for t in PAR), key=lambda f: f.size)
for i, t in enumerate(PAR): center_text(card, 336, 250 + i*14.5, t, fp, (40, 38, 40))

# ------------------------------------------------------------------ 4. details plaque (covers cake + banner)
PX1, PY1, PX2, PY2 = 16, 698, 656, 886
pl = Image.new("RGBA", card.size, (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
g = Image.new("RGBA", ((PX2 - PX1)*K, (PY2 - PY1)*K))
gd = ImageDraw.Draw(g)
for yy in range(g.height):
    k = yy/g.height
    gd.line([(0, yy), (g.width, yy)], fill=(int(86 - 40*k), int(60 - 30*k), int(38 - 22*k), 255))
gm = Image.new("L", g.size, 0); ImageDraw.Draw(gm).rounded_rectangle([0, 0, g.width - 1, g.height - 1], 14*K, fill=255)
g.putalpha(Image.fromarray(np.minimum(np.array(g.split()[3]), np.array(gm))))
sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle([PX1*K, (PY1 + 3)*K, PX2*K, (PY2 + 3)*K], 14*K, fill=(0, 0, 0, 120))
card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5*K)))
card.alpha_composite(g, (PX1*K, PY1*K))
d = ImageDraw.Draw(card)
d.rounded_rectangle([PX1*K, PY1*K, PX2*K, PY2*K], 14*K, outline=GOLD, width=int(2.2*K))
d.rounded_rectangle([(PX1 + 6)*K, (PY1 + 6)*K, (PX2 - 6)*K, (PY2 - 6)*K], 10*K, outline=(170, 130, 70), width=int(0.9*K))

# motto
center_text(card, 336, 717, "MBIU YANGU", corm(13.5, 700), GOLD)
center_text(card, 336, 737, "“Haikuwa rahisi kulitangaza Neno”", var("EBGaramond-Italic[wght].ttf", 19, 600), CREAM)
# ornament divider
y = 754
d.line([(130*K, y*K), (310*K, y*K)], fill=GOLD, width=int(1.1*K)); d.line([(362*K, y*K), (542*K, y*K)], fill=GOLD, width=int(1.1*K))
d.polygon([(336*K, (y - 5)*K), (343*K, y*K), (336*K, (y + 5)*K), (329*K, y*K)], fill=GOLD)

# two columns
CL, CR = 180, 492
d.line([(336*K, 766*K), (336*K, 846*K)], fill=(170, 130, 70), width=int(1*K))
def col(cx, head, lines):
    center_text(card, cx, 772, head, corm(15, 700), GOLD)
    for i, (t, w) in enumerate(lines):
        f = fit(t, lambda s: serif(s, w), 14.5, 285)
        center_text(card, cx, 793 + i*18, t, f, CREAM)
col(CL, "MISA TAKATIFU", [("Jumapili, 22 Novemba 2026", 700), ("Saa 10:30 jioni", 500), ("St. Peter's, Oysterbay", 500)])
col(CR, "SHEREHE", [("Cardinal Rugambwa Social Hall", 700), ("Kuingia ukumbini", 500), ("saa 1:00 usiku", 500)])

logo = Image.open(LOGO).convert("RGBA")
lw = int(92*K); logo = logo.resize((lw, int(logo.height*lw/logo.width)), Image.LANCZOS)
card.alpha_composite(logo, (int(336*K - lw/2), int(866*K - logo.height/2)))

# ------------------------------------------------------------------ 5. save
os.makedirs(CLIENT + "/outputs", exist_ok=True)
rgb = card.convert("RGB")
rgb.save(CLIENT + "/outputs/" + OUT, dpi=(300, 300))
rgb.save(CLIENT + "/outputs/" + OUT.replace(".png", ".pdf"), "PDF", resolution=300, title="Fr. Maximilian Wambura - Anniversary")
prev = rgb.copy(); prev.thumbnail((1000, 1400)); prev.save(sys.argv[2] if len(sys.argv) > 2 else "/tmp/fm_prev.jpg", quality=90)
print("saved", OUT, rgb.size)
