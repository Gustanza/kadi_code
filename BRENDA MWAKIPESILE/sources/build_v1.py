# Brenda Mwakipesile - SEND-OFF - white & gold floral arch + photo panel (same blueprint as Elias v3 / Tony & Sarafina)
# run: ~/.haflaway/venv/bin/python build_v1.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Brenda_Mwakipesile_SendOff_v1_final_01.png"
PREV = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/8d5d143e-4e6d-4e7a-9c03-6fcc9b8f790b/scratchpad/brenda_prev.jpg"

# ---- clean the blueprint (template text, swatches, seal leftovers, old badge)
img = cv2.imread(HERE + "/blueprint_white_gold_arch.jpeg"); H, W = img.shape[:2]
bgest = cv2.medianBlur(img, 61); diff = np.abs(img.astype(int) - bgest.astype(int)).max(axis=2)
boxes = [(2290,715,2695,875),(2175,925,2835,990),(2245,1005,2725,1110),(2085,1130,2865,1345),(2275,1365,2705,1430),
         (2195,1455,2775,1635),(2045,1645,2935,1850),(2235,1875,2755,2065),(2215,2085,2815,2235),(2255,2240,2745,2270),
         (2600,2355,2860,2470)]
m = np.zeros((H, W), np.uint8)
for x1, y1, x2, y2 in boxes: m[y1:y2, x1:x2] = np.where(diff[y1:y2, x1:x2] > 22, 255, 0)
m[1926-8:2010+8, 2236-8:2754+8] = 255
img = cv2.inpaint(img, cv2.dilate(m, np.ones((7, 7), np.uint8), iterations=2), 15, cv2.INPAINT_TELEA)
r = img[840:930, 2260:2420]; mm = (np.abs(r.astype(int) - cv2.medianBlur(r, 31).astype(int)).max(axis=2) > 8).astype(np.uint8)*255
img[840:930, 2260:2420] = cv2.inpaint(r, cv2.dilate(mm, np.ones((5, 5), np.uint8), iterations=2), 9, cv2.INPAINT_TELEA)
bm = np.zeros((H, W), np.uint8); bm[2182:2270, 2000:2240] = 255
img = cv2.inpaint(img, bm, 15, cv2.INPAINT_TELEA)
for x1, y1, x2, y2 in [(2200, 1336, 2840, 1366)]:     # stray template marks
    r = img[y1:y2, x1:x2]; mm = (np.abs(r.astype(int) - cv2.medianBlur(r, 21).astype(int)).max(axis=2) > 10).astype(np.uint8)*255
    img[y1:y2, x1:x2] = cv2.inpaint(r, cv2.dilate(mm, np.ones((5, 5), np.uint8), iterations=2), 7, cv2.INPAINT_TELEA)
card = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
c = Card(card, 1.0)
INK = (42, 36, 32); GOLD = (176, 122, 48); GOLD_LT = (228, 190, 120); WHITE = (255, 255, 255); PAPER = (236, 236, 230)
play = lambda sz, w=400: c.f("PlayfairDisplay-Italic.ttf", sz, w)
playR = lambda sz, w=500: c.f("PlayfairDisplay.ttf", sz, w)
script = lambda sz: c.f("GreatVibes-Regular.ttf", sz)

# ---- photo panel (left)
PW = 1456
ph = crop_to(load_photo(HERE + "/photo_G79F6858.jpeg"), PW, H, cx_frac=0.546, top_frac=0.02, zoom=1.0)
ph = fade_to(ph, (24, 22, 20), 1560, 1990)
c.im.paste(ph, (0, 0))
c.d = ImageDraw.Draw(c.im)
LC = PW/2
f_nm = c.fit("Brenda Mwakipesile", script, 210, PW - 200)
c.text(LC, 1990, "Brenda Mwakipesile", f_nm, WHITE)
c.text(LC, 2270, "14.11.2026", c.f("Poppins-Regular.ttf", 92), GOLD_LT, sp=10)
c.text(LC, 2410, "SEND-OFF PARTY", c.f("Poppins-SemiBold.ttf", 40), WHITE, sp=14)

# ---- invitation panel (inside the arch)
RC, AW = 2520, 650
fl = lambda t, mk, sz: c.fit(t, mk, sz, AW)                                    # never wider than the arch
c.text(RC, 652, "Familia ya", play(52), INK)
c.text(RC, 716, "Godian Mwakipesile", fl("Godian Mwakipesile", lambda z: play(z, 700), 60), INK)
c.text(RC, 786, "inayo furaha kukualika / kuwaalika", fl("inayo furaha kukualika / kuwaalika", play, 46), INK)
c.line(RC-310, 945, RC+310, 945, INK, 3)                                    # guest-name line
c.text(RC, 968, "kwenye sherehe ya kumuaga na", fl("kwenye sherehe ya kumuaga na", play, 46), INK)
c.text(RC, 1022, "kumtakia kheri binti yao mpendwa", fl("kumtakia kheri binti yao mpendwa", play, 46), INK)
c.text(RC - 8, 1135, "Brenda Mwakipesile", c.fit("Brenda Mwakipesile", script, 170, AW), GOLD)
c.text(RC, 1284, "itakayofanyika Jumamosi", play(52), INK)
c.line(RC-300, 1372, RC+300, 1372, GOLD, 3); c.line(RC-300, 1497, RC+300, 1497, GOLD, 3)
fdate = playR(86); dt = "14.11.2026"
ix = RC - (c.width(dt, fdate) + 110)/2
icon_calendar(c, ix, 1393, 80, GOLD, width=7)
c.text(ix + 110, 1377, dt, fdate, GOLD, align="l")
icon_pin(c, RC, 1560, 52, GOLD, PAPER)
c.text(RC, 1612, "Ukumbi", play(56, 800), INK)
c.text(RC, 1676, "Tengeru - Matunda Garden", fl("Tengeru - Matunda Garden", play, 54), INK)
c.text(RC, 1738, "Saa 9:00 mchana", play(50), GOLD)                         # muda wa ukumbini (15:00)
c.text(RC, 1810, "Rangi", play(52, 800), INK)
swatches(c, RC, 1876, [(255, 255, 255), (18, 18, 18), (0, 106, 78)], size=70, gap=32, outline=(196, 170, 130))
c.text(RC, 1956, "(White, Black & Emerald Green)", play(36), INK)
c.text(RC, 2008, "Mawasiliano", play(52, 800), INK)
fc = c.f("Poppins-Regular.ttf", 44)
c.text(RC, 2072, "0678 517 545", fc, INK); c.text(RC, 2122, "0788 408 839", fc, INK)
c.d.rounded_rectangle([2008, 2190, 2232, 2262], 14, fill=GOLD)                # blank badge: system fills single/double
c.paste_logo(2748, 2412, 225, anchor="cm")                                    # official Haflaway logo
save_card(c.im, CLIENT + "/outputs/" + OUT, "Brenda Mwakipesile - Send-Off", PREV, preview_w=1300)
print("saved", OUT)
