# Client's own background removal (photo_3U1A1868_cutout_client.png, 576x720 on WHITE, same framing as the original)
# -> alpha mask (white connected to the border = background; enclosed whites like embroidery/cowries kept),
# scaled up and applied to the full-quality original -> photo_3U1A1868_cutout.png (1400x1750 RGBA, used by build_std_v1.py)
import cv2, numpy as np
from PIL import Image, ImageOps
c = np.asarray(Image.open("photo_3U1A1868_cutout_client.png").convert("RGB"))
h, w = c.shape[:2]
white = (c.min(axis=2) >= 236).astype(np.uint8)
ff = white.copy(); m = np.zeros((h + 2, w + 2), np.uint8)
for x in range(w):
    for y in (0, h - 1):
        if ff[y, x] == 1: cv2.floodFill(ff, m, (x, y), 2)
for y in range(h):
    for x in (0, w - 1):
        if ff[y, x] == 1: cv2.floodFill(ff, m, (x, y), 2)
fg = (ff != 2).astype(np.float32)
W, H = 1400, 1750
a = cv2.resize(fg, (W, H), interpolation=cv2.INTER_CUBIC)
a = cv2.erode(np.clip(a, 0, 1), np.ones((3, 3), np.uint8))        # stay inside the edge: no brown backdrop fringe
a = np.clip((cv2.GaussianBlur(a, (0, 0), 1.0) - 0.15)/0.7, 0, 1)
o = ImageOps.exif_transpose(Image.open("photo_3U1A1868.jpeg")).convert("RGB").resize((W, H), Image.LANCZOS)
rgba = np.dstack([np.asarray(o), (a*255).astype(np.uint8)])
Image.fromarray(rgba, "RGBA").save("photo_3U1A1868_cutout.png")
print("saved photo_3U1A1868_cutout.png", W, H)
