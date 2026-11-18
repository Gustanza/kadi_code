# Franco & Agatha - SAVE THE DATE v1 - as close as possible to the blueprint (blueprint_white_gold_oval_save_the_date.jpeg, 736x1031):
# original "Save the Date" script, pill + dark date box and rings icon kept; couple = photo_3U1A1868 cut out of its brown studio
# backdrop (cutout_3U1A1868.py -> photo_3U1A1868_cutout.png) and faded into the white like the blueprint's couple. U=3.
# run: ~/.haflaway/venv/bin/python build_std_v1.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Franco_&_Agatha_SaveTheDate_v1_final_03.png"
PREV = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/8d5d143e-4e6d-4e7a-9c03-6fcc9b8f790b/scratchpad/fa_std_prev.jpg"
U = 3
src = cv2.imread(HERE + "/blueprint_white_gold_oval_save_the_date.jpeg"); H, W = src.shape[:2]

OX = 367                                                                 # oval axis (gold line x 130..605)
# ---- 1. remove the blueprint couple, names and venue line; the rest of the blueprint paper stays original
rm = np.zeros((H, W), np.float32)
for x1, y1, x2, y2 in [(182, 248, 552, 660), (140, 582, 562, 750), (204, 853, 512, 886)]: rm[y1:y2, x1:x2] = 1
m4 = cv2.resize((rm*255).astype(np.uint8), (W//4, H//4), interpolation=cv2.INTER_NEAREST)
m4 = cv2.dilate(m4, np.ones((3, 3), np.uint8))
srcp = src.copy(); srcp[756:854, 312:404] = np.median(src[890:900, 230:260].reshape(-1, 3), axis=0); srcp[880:945, 318:402] = srcp[756, 312]   # (and the rings)                # hide the date box from the fill (no brown smear under it)
s4 = cv2.resize(srcp, (W//4, H//4), interpolation=cv2.INTER_AREA)
fill = cv2.GaussianBlur(cv2.resize(cv2.inpaint(s4, m4, 15, cv2.INPAINT_TELEA), (W, H), interpolation=cv2.INTER_CUBIC), (0, 0), 6)
a = cv2.GaussianBlur(rm, (0, 0), 4)[:, :, None]
img = (src*(1 - a) + fill*a).astype(np.uint8)
# wipe the pill's old text (SATURDAY / AT 2PM) and the box text (April 11th 2025)
g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY); tm = np.zeros((H, W), np.uint8)
for x1, y1, x2, y2 in [(200, 790, 312, 826), (404, 790, 512, 826)]: tm[y1:y2, x1:x2] = (g[y1:y2, x1:x2] < 225)*255
img = cv2.inpaint(img, cv2.dilate(tm, np.ones((3, 3), np.uint8), iterations=2), 5, cv2.INPAINT_TELEA)
BOXC = (10, 50, 59)                                                     # BGR, sampled
cv2.rectangle(img, (322, 768), (393, 843), BOXC, -1)

card = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).resize((W*U, H*U), Image.LANCZOS)
P = lambda v: round(v*U)

# ---- 2. the couple (cut-out), faded into the white at the bottom and softly at the sides
co = Image.open(HERE + "/" + os.environ.get("CUT", "photo_3U1A1868_cutout.png")).convert("RGBA")   # final_01 used CUT=photo_3U1A1868_cutout_auto.png
CW = 392; X0 = OX - CW/2 - 4; Y0 = 246                                   # template units
cw = P(CW); chh = round(co.height*cw/co.width); co = co.resize((cw, chh), Image.LANCZOS)
FADE1, FADE2 = 540, 650                                                  # template y where the fade starts / ends
ys = (np.arange(chh)/U + Y0)[:, None]; xs = (np.arange(cw)/U)[None, :]
f = np.clip((FADE2 - ys)/(FADE2 - FADE1), 0, 1)**1.3 * np.clip(xs/55, 0, 1)**1.5 * np.clip((CW - xs)/40, 0, 1)**1.5
al = np.asarray(co.split()[3]).astype(np.float32)/255*f
co.putalpha(Image.fromarray((al*255).astype(np.uint8)))
card = card.convert("RGBA"); card.alpha_composite(co.crop((0, 0, cw, min(chh, P(FADE2 - Y0)))), (P(X0), P(Y0))); card = card.convert("RGB")

# ---- 3. text in the blueprint's style
c = Card(card, U, resize=False)
NAME = (122, 98, 58); AMP = (64, 55, 18); PILLT = (160, 132, 82); INK = (34, 34, 34); WHITE = (255, 255, 255)
sig = lambda z: c.f("AlexBrush-Regular.ttf", z)
mont = lambda z, w=600: c.f("Montserrat.ttf", z, w)
# names like "Winnie & Robert": first name up-left with a long swash, bold "&", second name down-right
c.text(170, 588, "Franco", sig(86), NAME, align="l")
fx2 = 170 + c.width("Franco", sig(86))
c.text(300, 650, "&", c.f("PlayfairDisplay.ttf", 46, 800), AMP, align="l")
c.text(338, 650, "Agatha", sig(86), NAME, align="l")
# pill
c.text(254, 799, "JUMAPILI", mont(15, 700), PILLT)
t = "SAA 10 ALASIRI"; c.text(460, 799, t, c.fit(t, lambda z: mont(z, 700), 15, 104), PILLT)
c.text(358, 770, "Novemba", mont(15, 600), WHITE)
c.text(358, 789, "29", mont(25, 700), WHITE)
c.text(358, 821, "2026", mont(16, 600), WHITE)
# final_03: reception date (client: save the date = 29)
t = "@Jaks Hall, Mbezi Africana, Dar es Salaam"; c.text(OX, 860, t, c.fit(t, lambda z: mont(z, 700), 13.5, 330), INK)
c.paste_logo(OX, 958, 84, anchor="cm")                                   # official Haflaway logo
save_card(c.im, CLIENT + "/outputs/" + OUT, "Franco & Agatha - Save the Date", PREV, preview_w=1000)
print("saved", OUT)
