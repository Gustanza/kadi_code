# Albert & Beatrice - v5 = the client's OWN card (client_card_reference.jpeg, 743x1080, WhatsApp 2026-11-13 5.34 PM), fixed.
# Client comment: "Hayo maandishi ya chini ya ukumbi tafuta colour inayosomeka" -> the lines under "Grand Paradise (Platnum)"
# (Yombo Vituka..., kuanzia saa 12:000 jioni, Tafadhali fika..., Watoto...) were gold-brown on the white shirts.
# Fix: remove them, dark navy band over the bottom of the photo, re-set the lines in white / gold. Rest of their card untouched
# (only upscaled 3x). "12:000" -> "12:00".   run: ~/.haflaway/venv/bin/python build_v5.py [out_name]
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *

HERE = os.path.dirname(os.path.abspath(__file__)); CLIENT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Albert_&_Beatrice_v5_final_01.png"
PREV = "/private/tmp/claude-501/-Users-gustanzasam-AndroidStudioProjects-kadi-code/8d5d143e-4e6d-4e7a-9c03-6fcc9b8f790b/scratchpad/ab_v5_prev.jpg"
U = 3
src = cv2.imread(HERE + "/client_card_reference.jpeg"); H, W = src.shape[:2]
b_, g_, r_ = [src[:, :, i].astype(int) for i in range(3)]

# ---- 1. remove the old lines (their gold-brown text + dark outline) inside the photo
X1, X2, Y1, Y2 = 121, 630, 764, 879                       # photo area under the ukumbi line
flower = ((r_ > 180) & (g_ > 125) & (b_ < 120) & (r_ - b_ > 80)).astype(np.uint8)
flower[:, :572] = 0
flower = cv2.morphologyEx(flower, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
cs, _ = cv2.findContours(flower, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
flower = np.zeros_like(flower); cv2.drawContours(flower, [k for k in cs if cv2.contourArea(k) > 80], -1, 1, -1)
txt = np.zeros((H, W), np.uint8)
for x1, y1, x2, y2 in [(212, 766, 604, 816), (128, 826, 664, 881)]:
    sub = src[y1:y2, x1:x2].astype(int)
    txt[y1:y2, x1:x2] = (((sub[:, :, 2] - sub[:, :, 0] > 45) & (sub[:, :, 1] < 200)) | (sub.max(axis=2) < 70))*255
txt[flower == 1] = 0
on_fl = np.zeros((H, W), bool); on_fl[766:881, 560:664] = True                  # end of the old Watoto line runs over the flowers:
dk = (src.max(axis=2) < 140) & on_fl & (cv2.dilate(flower, np.ones((9, 9), np.uint8)) == 1)
txt[dk] = 255                                                                   # remove only its dark letters there
img = cv2.inpaint(src, cv2.dilate(txt, np.ones((3, 3), np.uint8), iterations=2), 5, cv2.INPAINT_TELEA)

card = upscale_soft(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), U)

# ---- 2. navy band (fades in from the photo, flowers stay on top)
NAVY = (12, 22, 64)
ys = (np.arange(H*U)/U)[:, None]
a = np.clip((ys - Y1)/26, 0, 1)*0.86*np.ones((1, W*U))
a[:, :X1*U] = 0; a[:, X2*U:] = 0; a[Y2*U:, :] = 0
fl = cv2.resize(flower.astype(np.float32), (W*U, H*U), interpolation=cv2.INTER_LINEAR)
fl = cv2.GaussianBlur(fl, (7, 7), 0)
a = a*(1 - fl)
am = Image.fromarray((a*255).astype(np.uint8))
card = Image.composite(Image.new("RGB", card.size, NAVY), card, am)

# ---- 3. the lines again, readable
c = Card(card, U, resize=False)
GOLD = (255, 206, 84); WHITE = (255, 255, 255)
mont = lambda z, w=700: c.f("Montserrat.ttf", z, w)
CX = 368
c.text(CX, 769, "Yombo Vituka, Mwisho wa Lami", mont(20, 700), GOLD)
c.text(CX, 793, "kuanzia saa 12:00 jioni.", mont(20, 700), WHITE)
c.text(CX, 823, "Tafadhali fika na kadi hii", mont(18, 600), WHITE)
t = "\u201cWatoto tunawapenda lakini hawaruhusiwi\u201d"; c.text(CX, 847, t, c.fit(t, lambda z: mont(z, 600), 18, 380), GOLD)
save_card(c.im, CLIENT + "/outputs/" + OUT, "Albert & Beatrice - Harusi", PREV, preview_w=900)
print("saved", OUT)
