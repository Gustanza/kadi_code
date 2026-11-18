# Deodatus & Victoria v2_final_01 -> v2_final_02: Ibada time saa 6:00 -> saa 7:00 mchana (build script lost; patch delivered PNG)
import sys, os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import *
from PIL import ImageFont, ImageDraw
D=os.path.expanduser('~/AndroidStudioProjects/kadi_code/DEODATUS & VICTORIA/outputs/')
src=cv2.imread(D+'Deodatus_&_Victoria_v2_final_01.png'); H,W=src.shape[:2]
F=os.path.expanduser('~/.haflaway/fonts/PlayfairDisplay-Italic.ttf')
f=ImageFont.truetype(F,36.75); f.set_variation_by_axes([500])
INK=(48,42,38)
# verify: re-render old text and compare with the card
old='saa 6:00 mchana'; bb=f.getbbox(old); ox,oy=2381-bb[0],1639-bb[1]
test=Image.new('L',(W,H),0); ImageDraw.Draw(test).text((ox,oy),old,font=f,fill=255)
t=np.asarray(test)[1630:1680,2370:2670]>128; r=src[1630:1680,2370:2670].sum(2)<400
print('overlap IoU', (t&r).sum()/(t|r).sum())
# erase old line
x1,y1,x2,y2=2370,1634,2670,1674
bg=cv2.medianBlur(src,31)
d=bg[y1:y2,x1:x2].astype(int).max(2)-src[y1:y2,x1:x2].astype(int).max(2)
m=np.zeros((H,W),np.uint8); m[y1:y2,x1:x2]=np.where(d>10,255,0)
img=cv2.inpaint(src,cv2.dilate(m,np.ones((3,3),np.uint8),iterations=2),9,cv2.INPAINT_TELEA)
z=np.zeros((H,W),np.float32); z[y1:y2,x1:x2]=1; z=cv2.GaussianBlur(z,(0,0),4)[...,None]
img=(cv2.GaussianBlur(img,(0,0),6).astype(np.float32)*z+img.astype(np.float32)*(1-z)).astype(np.uint8)
im=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
new='saa 7:00 mchana'; nb=f.getbbox(new); cx=(2381+2655)/2
ImageDraw.Draw(im).text((cx-(nb[0]+nb[2])/2, oy), new, font=f, fill=INK)
save_card(im, D+'Deodatus_&_Victoria_v2_final_02.png', 'Deodatus & Victoria', sys.argv[1], preview_w=1000)
im.crop((2150,1540,2900,1720)).resize((1125,270)).save(sys.argv[2])
a=np.asarray(im).astype(int); b=cv2.cvtColor(src,cv2.COLOR_BGR2RGB).astype(int)
ys,xs=np.where(np.abs(a-b).max(2)>0); print('changed bbox',xs.min(),ys.min(),xs.max(),ys.max())
