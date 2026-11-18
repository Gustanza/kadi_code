# John & Vedastina - WEDDING v4 - white & gold floral arch + photo panel (as Deodatus & Victoria v2; script base: Brenda build_v1.py)
# run: ~/.haflaway/venv/bin/python build_v1.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "John_&_Vedastina_v4_final_01.png"
PREV = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/8d5d143e-4e6d-4e7a-9c03-6fcc9b8f790b/scratchpad/john_v3_prev.jpg"

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
ph = crop_to(load_photo(HERE + "/photo_john_vedastina.jpeg"), PW, H, cx_frac=0.5, top_frac=0.0, zoom=1.0)
ph = fade_to(ph, (24, 22, 20), 1560, 1990)
c.im.paste(ph, (0, 0))
c.d = ImageDraw.Draw(c.im)
LC = PW/2
f_nm = c.fit("John & Vedastina", script, 210, PW - 220)
c.text(LC, 1990, "John & Vedastina", f_nm, WHITE)
c.text(LC, 2270, "28.11.2026", c.f("Poppins-Regular.ttf", 92), GOLD_LT, sp=10)
c.text(LC, 2410, "SAVE THE DATE", c.f("Poppins-SemiBold.ttf", 40), WHITE, sp=14)

# ---- invitation panel (inside the arch)
RC, AW = 2520, 650
fl = lambda t, mk, sz: c.fit(t, mk, sz, AW)                                    # never wider than the arch
c.text(RC, 640, "Familia ya", play(48), INK)
c.text(RC, 700, "Bw. & Bi. Pima John", fl("Bw. & Bi. Pima John", lambda z: play(z, 700), 58), INK)
c.text(RC, 768, "wa Kitunda, Dar es Salaam", fl("wa Kitunda, Dar es Salaam", play, 44), INK)
c.text(RC, 822, "inayo furaha kukualika / kuwaalika", fl("inayo furaha kukualika / kuwaalika", play, 44), INK)
c.line(RC-310, 945, RC+310, 945, INK, 3)                                    # guest-name line
c.text(RC, 968, "kwenye sherehe ya harusi ya", fl("kwenye sherehe ya harusi ya", play, 46), INK)
c.text(RC, 1022, "wapendwa wao", play(46), INK)
c.text(RC - 8, 1112, "John & Vedastina", c.fit("John & Vedastina", script, 150, AW), GOLD)
c.text(RC, 1256, "itakayofanyika Jumamosi", play(48), INK)
c.line(RC-280, 1330, RC+280, 1330, GOLD, 3); c.line(RC-280, 1438, RC+280, 1438, GOLD, 3)
fdate = playR(76); dt = "28.11.2026"
ix = RC - (c.width(dt, fdate) + 100)/2
icon_calendar(c, ix, 1348, 70, GOLD, width=6)
c.text(ix + 100, 1334, dt, fdate, GOLD, align="l")
c.text(RC, 1462, "Ibada ya Ndoa", play(46, 800), INK)
c.text(RC, 1516, "Kanisa Anglican la St. Paul's - Ukonga", fl("Kanisa Anglican la St. Paul's - Ukonga", play, 40), INK)
c.text(RC, 1564, "saa XX:XX", play(40), GOLD)
icon_pin(c, RC, 1652, 42, GOLD, PAPER)
c.text(RC, 1702, "Ukumbi", play(46, 800), INK)
c.text(RC, 1756, "Mwigo Empire Hall - Tabata Bima", fl("Mwigo Empire Hall - Tabata Bima", play, 44), INK)
c.text(RC, 1806, "saa 12:00 jioni", play(40), GOLD)
c.text(RC, 1862, "Rangi", play(46, 800), INK)
swatches(c, RC, 1920, [(18, 18, 18), (212, 175, 55)], size=60, gap=28, outline=(196, 170, 130))
c.text(RC, 1986, "(Black & Gold)", play(36), INK)
c.text(RC, 2034, "Mawasiliano", play(46, 800), INK)
contacts = ["Samuel A. Mshote (M/kiti) - 0754 277 980", "Monica Mshote (Mwekahazina) - 0686 967 238"]
fc = c.fit(max(contacts, key=lambda t: c.width(t, play(36))), play, 36, AW + 20)
for i, t in enumerate(contacts): c.text(RC, 2090 + i*44, t, fc, INK)
print("contact font", fc.size)
c.d.rounded_rectangle([2008, 2190, 2232, 2262], 14, fill=GOLD)                # blank badge: system fills single/double
c.paste_logo(2748, 2412, 225, anchor="cm")                                    # official Haflaway logo
save_card(c.im, CLIENT + "/outputs/" + OUT, "John & Vedastina - Harusi", PREV, preview_w=1300)
print("saved", OUT)
