# v2_final_02 -> v2_final_03: second Mawasiliano number 0742 010 203 under 0769 028 699 (client 2026-11-09)
import sys, os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/haflaway-cards/scripts"))
from cardkit import save_card
from PIL import Image, ImageDraw, ImageFont
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/outputs/'
im=Image.open(D+'Deodatus_&_Victoria_v2_final_02.png').convert('RGB'); d=ImageDraw.Draw(im)
f=ImageFont.truetype(os.path.expanduser('~/.haflaway/fonts/Poppins-Regular.ttf'),38.5); SP=2.5; INK=(42,36,32)
t='0742 010 203'; ws=[d.textlength(c,font=f) for c in t]; tw=sum(ws)+SP*(len(t)-1)
b=d.textbbox((0,0),t,font=f); x=(2378+2662)/2-tw/2-b[0]*0; y=2114+56-b[1]       # same style, one line below
for c,w in zip(t,ws): d.text((x,y),c,font=f,fill=INK); x+=w+SP
save_card(im, D+'Deodatus_&_Victoria_v2_final_03.png', 'Deodatus & Victoria', sys.argv[1] if len(sys.argv)>1 else None, preview_w=1000)
