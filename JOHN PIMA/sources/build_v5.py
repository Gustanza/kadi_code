# John & Vedastina - WEDDING v5 - black & gold ornate photo frame (ELIAS & JANE/sources/artwork-05.jpg, 2000x2000;
# same blueprint as Deodatus & Victoria v4, Elias v2, Amos v3 - their scripts were not kept, this one is)
# run: ~/.haflaway/venv/bin/python build_v5.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "John_&_Vedastina_v5_final_02.png"
PREV = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/8d5d143e-4e6d-4e7a-9c03-6fcc9b8f790b/scratchpad/john_v5_prev.jpg"

src = cv2.imread(HERE + "/blueprint_black_gold_frame.jpg"); H, W = src.shape[:2]
img = src.copy(); BG = (32, 32, 32)
# ---- wipe template text (flat bg): whole left column between top rule ornament and bottom ornament, ekadi logo
img[240:500, 125:1040] = BG                      # family block + guest name (rule at 501-505 is kept = guest-name line)
img[510:1600, 125:1040] = BG                     # everything from KWENYE.. down to RANGI (box, date lines, pill redrawn)
img[1600:1740, 135:1040] = BG                    # MAWASILIANO + 1st contact row (ornament starts x<80 here)
img[1740:1800, 150:1040] = BG                    # 2nd contact row (stay right of the ornament)
img[1890:1960, 900:1100] = BG                    # ekadi logo

# ---- photo inside the inner gold frame
Rr, Gg, Bb = src[..., 2].astype(int), src[..., 1].astype(int), src[..., 0].astype(int)
gold = ((Rr > 110) & (Rr - Bb > 45)).astype(np.uint8)
x1, y1, x2, y2 = 1040, 200, 1900, 1570
bar = gold[y1:y2, x1:x2].copy()
ff = np.zeros((y2-y1+2, x2-x1+2), np.uint8)
fill = (1 - cv2.dilate(bar, np.ones((3, 3), np.uint8))).astype(np.uint8)
cv2.floodFill(fill, ff, (1460-x1, 900-y1), 2)
reg = (fill == 2).astype(np.uint8)
cnts, _ = cv2.findContours(reg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
win = np.zeros_like(reg); cv2.drawContours(win, [max(cnts, key=cv2.contourArea)], -1, 1, -1)
inner = cv2.erode(win, np.ones((41, 41), np.uint8))                 # deep inside: replace everything (old photo may be gold-ish)
win = cv2.dilate(win, np.ones((5, 5), np.uint8)) & (1 - (bar & (1 - inner)))   # near the edge: up to the gold line, never over it
ys, xs = np.nonzero(win); bx1, bx2, by1, by2 = xs.min(), xs.max()+1, ys.min(), ys.max()+1
print("photo window", bx1+x1, by1+y1, bx2+x1, by2+y1, "area", int(win.sum()))
assert win.sum() < 0.9 * (x2-x1)*(y2-y1), "flood leaked"
pw, ph_ = bx2 - bx1, by2 - by1
ph = crop_to(load_photo(HERE + "/photo_john_vedastina.jpeg"), pw, ph_, cx_frac=float(os.environ.get("CX", "0.55")), top_frac=0.0, zoom=float(os.environ.get("ZOOM", "1.0")))
pha = cv2.cvtColor(np.asarray(ph.convert("RGB")), cv2.COLOR_RGB2BGR)
sub = img[y1+by1:y1+by2, x1+bx1:x1+bx2]; m = win[by1:by2, bx1:bx2].astype(bool)
sub[m] = pha[m]

c = Card(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), 1.0)
GOLD = (209, 172, 80); PILL = (223, 174, 71)
lato = lambda sz: c.f("Lato-Bold.ttf", sz)
play = lambda sz, w=700: c.f("PlayfairDisplay.ttf", sz, w)
CX = 557

def tc(x, yc, t, f, fill=GOLD, align="c", sp=0):                  # caps ink centred on yc
    bb = c.d.textbbox((0, 0), "H", font=f); c.text(x, yc - (bb[1] + bb[3])/2, t, f, fill, align=align, sp=sp)

for yc, t in [(262, "FAMILIA YA"), (312, "BW. & BI. PIMA JOHN"), (362, "WA KITUNDA, DAR ES SALAAM"),
              (412, "INAYO FURAHA KUKUALIKA / KUWAALIKA")]:
    tc(CX, yc, t, c.fit(t, lato, 37, 820))
# blank writing room 430-495 above the template rule (501-505) = guest-name line
tc(CX, 564, "KWENYE HARUSI YA WAPENDWA WAO", lato(37))
# names box (template box was 159-954 x 644-998, 6px) - redrawn shorter for two first names
BX1, BY1, BX2, BY2 = 159, 640, 954, 912
c.d.rectangle([BX1, BY1, BX2, BY2], outline=GOLD, width=6)
fn = play(88)
tc(CX, 712, "JOHN", fn, sp=6); tc(CX, 778, "&", play(70)); tc(CX, 846, "VEDASTINA", c.fit("VEDASTINA", play, 88, 700), sp=6)
tc(CX, 978, "ITAKAYOFANYIKA", lato(37))
c.d.rectangle([271, 1036, 845, 1040], fill=GOLD); c.d.rectangle([271, 1126, 845, 1130], fill=GOLD)
tc(CX, 1083, "JUMAMOSI 28.11.2026", c.fit("JUMAMOSI 28.11.2026", play, 54, 560), sp=2)
c.d.rounded_rectangle([CX-110, 1170, CX+111, 1242], radius=24, fill=PILL)    # blank badge: system fills single/double
# label / value rows (template: labels x 142, values x 367, Lato Bold caps ~37px)
LX, VX, f = 142, 367, lato(35)
rows = [(1300, "IBADA:", "KANISA ANGLICAN LA ST. PAUL'S -"), (1354, "", "UKONGA, SAA XX:XX."),
        (1420, "UKUMBI:", "MWIGO EMPIRE HALL - TABATA BIMA,"), (1474, "", "KUANZIA SAA 12:00 JIONI."),
        (1540, "RANGI:", "BLACK & GOLD.")]
fv = c.fit(max([r[2] for r in rows], key=lambda t: c.width(t, f)), lato, 35, 1015 - VX)
for yc, l, v in rows:
    if l: tc(LX, yc, l, f, align="l")
    tc(VX, yc, v, fv, align="l")
sw = VX + c.width("BLACK & GOLD.", fv) + 34
swatches(c, sw + 50, 1540 - 21, [(12, 12, 12), (212, 175, 55)], size=42, gap=16, outline=GOLD)
tc(LX, 1608, "MAWASILIANO:", f, align="l")
contacts = ["SAMUEL A. MSHOTE (M/KITI) - 0754 277 980", "MONICA MSHOTE (MWEKAHAZINA) - 0686 967 238"]
fc = c.fit(max(contacts, key=lambda t: c.width(t, f)), lato, 35, 1015 - 190)
for i, t in enumerate(contacts): tc(190, 1672 + i*58, t, fc, align="l")
print("value font", fv.size, "contact font", fc.size)
c.paste_logo(1000, 1922, 230, dark_bg=True, anchor="cm")
save_card(c.im, CLIENT + "/outputs/" + OUT, "John & Vedastina - Harusi", PREV, preview_w=1100)
print("saved", OUT)
