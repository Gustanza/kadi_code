# Albert & Beatrice - WEDDING v3 - full-bleed couple photo + frosted panel (blueprint: Haflaway's own "Nestory & Joyce" card,
# sources/blueprint_frosted_photo_nestory_joyce.png, 1240x1748). Rebuilt on the new photo; icons/QR taken from the blueprint.
# run: ~/.haflaway/venv/bin/python build_v3.py [out_name]   (PHOTO=photo_A.jpeg CX=.. for the other photo)
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *
from PIL import ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Albert_&_Beatrice_v3_final_01.png"
PREV = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/8d5d143e-4e6d-4e7a-9c03-6fcc9b8f790b/scratchpad/ab_v3_prev.jpg"
U = 1.5
BP = Image.open(HERE + "/blueprint_frosted_photo_nestory_joyce.png").convert("RGB"); W, H = BP.size
WU, HU = round(W*U), round(H*U)

# ---- background photo (warm-toned a little like the blueprint) + frosted panel
ph = load_photo(HERE + "/" + os.environ.get("PHOTO", "photo_B.jpeg"))
ph = crop_to(upscale_soft(ph, 2.6), WU, HU, cx_frac=float(os.environ.get("CX", "0.47")), top_frac=float(os.environ.get("TOP", "0.23")), zoom=float(os.environ.get("ZOOM", "1.45")))
ph = ImageEnhance.Brightness(ph).enhance(1.08)
P = lambda v: round(v*U)
blur = ph.filter(ImageFilter.GaussianBlur(P(5)))
card = ph.copy()
outer = Image.blend(ph, Image.new("RGB", ph.size, (255, 255, 255)), 0.10)          # faint outer frame (118..1120 x 310..1662)
mo = Image.new("L", ph.size, 0); ImageDraw.Draw(mo).rectangle([P(118), P(310), P(1120), P(1662)], fill=255)
card = Image.composite(outer, card, mo)
frost = Image.blend(blur, Image.new("RGB", ph.size, (246, 244, 242)), 0.56)
mp = Image.new("L", ph.size, 0); ImageDraw.Draw(mp).rectangle([P(150), P(334), P(1088), P(1617)], fill=255)
card = Image.composite(frost, card, mp)

c = Card(card, U, resize=False)
INK = (24, 22, 22); BROWN = (82, 52, 42); CHIP_OL = (30, 30, 30)
mont = lambda sz, w=600: c.f("Montserrat.ttf", sz, w)
CX = 619; MW = 860

def icon(box, at, col=INK, thr=95):
    """re-draw a blueprint icon (its dark pixels) in col at template position at (top-left)"""
    cr = BP.crop(box); gm = np.asarray(cr.convert("L")) < thr
    m = Image.fromarray((gm*255).astype(np.uint8)).resize((P(cr.width), P(cr.height)), Image.LANCZOS)
    c.im.paste(Image.new("RGB", m.size, col), (P(at[0]), P(at[1])), m)

# family block
fam = ["FAMILIA YA BW. & BI. LIBENT RAPHAEL ISHABAILU", "WA UKONGA MAJUMBA SITA, DAR ES SALAAM,", "WANAYO FURAHA KUKUALIKA / KUWAALIKA"]
for i, t in enumerate(fam): c.text(CX, 386 + i*40, t, c.fit(t, lambda z: mont(z, 600), 27, MW), INK)
c.line(358, 557, 888, 557, INK, 3)                                                  # guest-name line (room above)
t = "KWENYE HARUSI YA VIJANA WAO WAPENDWA"; c.text(CX, 574, t, c.fit(t, lambda z: mont(z, 600), 27, MW), INK)
# names (script) with a soft grey "&" like the blueprint's monogram
scr = lambda z: c.f("GreatVibes-Regular.ttf", z)
c.text(CX, 700, "&", scr(84), (120, 112, 112))
for t, y in [("Albert Libent", 604), ("Beatrice Adelitus", 768)]:
    c.text(CX, y, t, c.fit(t, scr, 108, 740), BROWN)
t = "ITAKAYOFANYIKA, JUMAMOSI"; c.text(CX, 916, t, mont(28, 600), INK)
c.line(340, 966, 908, 966, INK, 3); c.line(340, 1063, 908, 1063, INK, 3)
fd = mont(46, 700); dt = "21 NOVEMBA 2026"; dw = c.width(dt, fd) + 88
icon((349, 984, 420, 1052), (CX - dw/2, 984))
c.text(CX - dw/2 + 88, 990, dt, fd, INK, align="l")
# ibada / ukumbi rows
row = lambda z: mont(z, 600)
icon((276, 1076, 324, 1128), (262, 1086)); t = "IBADA:  KANISA KATOLIKI, MSIMBAZI"; c.text(318, 1092, t, c.fit(t, row, 28, 700), INK, align="l")
icon((350, 1128, 395, 1170), (318, 1134)); t = "MUDA:  KUANZIA SAA 9:00 ALASIRI"; c.text(372, 1137, t, c.fit(t, row, 28, 640), INK, align="l")
icon((273, 1193, 316, 1233), (262, 1196)); t = "UKUMBI:  GRAND PARADISE (PLATINUM)"; c.text(318, 1197, t, c.fit(t, row, 28, 700), INK, align="l")
t = "YOMBO VITUKA, MWISHO WA LAMI"; c.text(372, 1238, t, c.fit(t, row, 26, 640), INK, align="l")
icon((350, 1240, 395, 1282), (318, 1279)); t = "MUDA:  KUANZIA SAA 12:00 JIONI"; c.text(372, 1282, t, c.fit(t, row, 28, 640), INK, align="l")
# dress code chips (blueprint style: rounded boxes with names)
icon((260, 1322, 322, 1386), (262, 1340)); c.text(326, 1346, "RANGI:", mont(28, 600), INK, align="l")
chips = [("KAHAWIA", (153, 100, 52), (255, 255, 255)), ("BLUE", (40, 155, 240), (255, 255, 255)), ("NYEUPE", (248, 248, 246), INK)]
x = 470
for nm, col, tcol in chips:
    f = mont(21, 600); w = c.width(nm, f) + 44
    c.d.rounded_rectangle([P(x), P(1336), P(x + w), P(1388)], P(10), fill=col, outline=CHIP_OL, width=P(2.5))
    c.text(x + w/2, 1349, nm, f, tcol); x += w + 22
c.text(CX, 1418, "MAWASILIANO:", mont(26, 700), INK)
t = "0715 194 900  /  0694 026 550  /  0788 016 290"; c.text(CX, 1454, t, c.fit(t, lambda z: mont(z, 600), 27, MW), INK)
t = "Watoto tunawapenda, lakini hawaruhusiwi."; c.text(CX, 1500, t, c.f("PlayfairDisplay-Italic.ttf", 26, 500), BROWN)
c.paste_logo(310, 1582, 170, anchor="cm")                                           # official Haflaway logo
# blank SINGLE/DOUBLE badge (blueprint colours) + QR placeholder from the blueprint
c.d.rounded_rectangle([P(672), P(1580), P(922), P(1664)], P(20), fill=(232, 222, 190), outline=(60, 44, 36), width=P(5))
q = BP.crop((960, 1456, 1200, 1697)).resize((P(240), P(241)), Image.NEAREST); c.im.paste(q, (P(960), P(1456)))
save_card(c.im, CLIENT + "/outputs/" + OUT, "Albert & Beatrice - Harusi", PREV, preview_w=1000)
print("saved", OUT)
