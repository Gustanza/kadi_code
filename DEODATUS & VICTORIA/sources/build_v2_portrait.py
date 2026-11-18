# Deodatus & Victoria v2 PORTRAIT (print): photo panel on top, gold card below. Built from the latest v2 landscape (selected design).
# run: ~/.haflaway/venv/bin/python build_v2_portrait.py [out_name] [preview] [cmp]
import sys, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
HERE=os.path.dirname(os.path.abspath(__file__)); CL=os.path.dirname(HERE)
sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import save_card
OUT=sys.argv[1] if len(sys.argv)>1 else "Deodatus_&_Victoria_v2_PORTRAIT_final_01.png"
F=os.path.expanduser('~/.haflaway/fonts/')
land=Image.open(CL+'/outputs/Deodatus_&_Victoria_v2_final_03.png').convert('RGB')
card=land.crop((1476,0,land.width,land.height)); W=card.width            # gold card part (2058 x 2717)
BG=(24,22,20); GOLD=(228,190,120); WHITE=(255,255,255)
# ---- photo: full-width crop of the studio photo, heads to hands
ph=Image.open(HERE+'/photo_new_0J7A9238.jpeg').convert('RGB')
y0,y1=430,2450
ph=ph.crop((0,y0,ph.width,y1)); ph=ph.resize((W,round(ph.height*W/ph.width)),Image.LANCZOS)
PH=ph.height
k=W/1456
def font(fn,sz): return ImageFont.truetype(F+fn,sz)
tmp=ImageDraw.Draw(Image.new('RGB',(10,10)))
# names fitted to the same share of the width as on the landscape panel (1290/1456)
def names_fonts(sz): return font('GreatVibes-Regular.ttf',sz), font('GreatVibes-Regular.ttf',round(sz*250/220))
def names_w(sz):
    gv,amp=names_fonts(sz); g=round(14*k)
    return sum(tmp.textbbox((0,0),t,font=f)[2]-tmp.textbbox((0,0),t,font=f)[0] for t,f in [('Deodatus',gv),('&',amp),('Victoria',gv)])+2*g
sz=300
while names_w(sz)>W*1290/1456: sz-=2
gv,amp=names_fonts(sz)
asc=-min(tmp.textbbox((0,0),t,font=f,anchor='ls')[1] for t,f in [('Deodatus',gv),('&',amp),('Victoria',gv)])
desc=max(tmp.textbbox((0,0),t,font=f,anchor='ls')[3] for t,f in [('Deodatus',gv),('&',amp),('Victoria',gv)])
base=PH+30+asc                                     # names fully on black, just under the photo
nb=base+desc
TOP=nb+round(282*k)+round(95*k)
top=Image.new('RGB',(W,TOP),BG)
L=650; tt=np.linspace(0,1,L); fade=np.ones(PH,np.float32); fade[PH-L:]=1-(tt*tt*(3-2*tt))   # smoothstep fade to black
pa=np.asarray(ph).astype(np.float32); t=np.asarray(top).astype(np.float32)
t[:PH]=pa*fade[:,None,None]+np.array(BG,np.float32)*(1-fade[:,None,None])
top=Image.fromarray(t.astype(np.uint8)); d=ImageDraw.Draw(top)
def ink_w(t,f): b=d.textbbox((0,0),t,font=f); return b[2]-b[0],b
parts=[('Deodatus',gv,WHITE),('&',amp,GOLD),('Victoria',gv,WHITE)]
gap=round(14*k); ws=[ink_w(p[0],p[1])[0] for p in parts]; tot=sum(ws)+2*gap
x=(W-tot)/2
for (s_,f,c),w in zip(parts,ws):
    bb=d.textbbox((0,0),s_,font=f,anchor='ls'); d.text((x-bb[0],base),s_,font=f,fill=c,anchor='ls'); x+=w+gap
def centred(s_,f,c,yc,sp=0):
    ws=[d.textlength(ch,font=f) for ch in s_]; tw=sum(ws)+sp*(len(s_)-1); xx=(W-tw)/2
    bb=d.textbbox((0,0),s_,font=f)
    for ch,w in zip(s_,ws): d.text((xx,yc-(bb[1]+bb[3])/2),ch,font=f,fill=c); xx+=w+sp
centred('14.11.2026',font('Poppins-Regular.ttf',round(92*k)),GOLD,nb+round(177*k),sp=round(6*k))
centred('SAVE THE DATE',font('Poppins-SemiBold.ttf',round(38*k)),WHITE,nb+round(282*k),sp=round(17*k))
# ---- stack
out=Image.new('RGB',(W,TOP+card.height),BG); out.paste(top,(0,0)); out.paste(card,(0,TOP))
save_card(out, CL+'/outputs/'+OUT, 'Deodatus & Victoria', sys.argv[2] if len(sys.argv)>2 else None, preview_w=900)
print('saved',OUT,out.size,'top',TOP,'names size',sz)
