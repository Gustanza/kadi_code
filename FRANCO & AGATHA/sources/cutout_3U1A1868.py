import cv2, numpy as np, sys
S=sys.argv[1]
a=cv2.imread(S+"/fa_1868_1400.jpg"); H,W=a.shape[:2]
P=lambda pts: np.array(pts,np.int32)
mask=np.full((H,W),cv2.GC_PR_BGD,np.uint8)
person=[P([(370,60),(720,40),(735,420),(660,540),(800,520),(880,560),(1120,250),(1130,560),(1110,600),(1180,640),(1400,740),(1400,900),(1360,900),(1360,1750),(200,1750),(40,1180),(0,1150),(0,830),(60,560),(330,500),(420,300)])]
cv2.fillPoly(mask, person, cv2.GC_PR_FGD)
fg=[P([(420,110),(690,80),(700,420),(620,500),(480,500),(440,300)]),           # his head+hat
    P([(120,600),(780,560),(860,720),(860,1300),(720,1750),(300,1750),(120,1150),(60,900)]),   # his body
    P([(760,330),(920,270),(1080,320),(1090,520),(1000,620),(860,620),(780,520)]),  # her head
    P([(900,720),(1150,720),(1330,800),(1330,850),(1240,900),(1280,1750),(880,1750),(860,1000)])]  # her body
for p in fg: cv2.fillPoly(mask,[p],cv2.GC_FGD)
bg=[P([(0,0),(340,0),(340,90),(250,300),(120,480),(0,520)]),
    P([(760,0),(1400,0),(1400,230),(1140,240),(1000,210),(860,220),(760,200)]),
    P([(1160,420),(1400,420),(1400,690),(1200,620)]),
    P([(1385,930),(1400,930),(1400,1750),(1385,1750)]),
    P([(0,1220),(25,1220),(120,1750),(0,1750)]),
    P([(628,0),(760,0),(760,152),(702,152)]),
    P([(0,0),(1400,0),(1400,4),(0,4)]),
    P([(0,540),(40,560),(8,790),(0,800)]),
    P([(110,1240),(175,1230),(205,1420),(160,1430)])]
for p in bg: cv2.fillPoly(mask,[p],cv2.GC_BGD)
sm=cv2.resize(a,(W//2,H//2),interpolation=cv2.INTER_AREA); m2=cv2.resize(mask,(W//2,H//2),interpolation=cv2.INTER_NEAREST)
b=np.zeros((1,65)); f=np.zeros((1,65))
cv2.grabCut(sm,m2,None,b,f,10,cv2.GC_INIT_WITH_MASK)
fgm=np.isin(m2,[1,3]).astype(np.uint8)
n,l,st,_=cv2.connectedComponentsWithStats(fgm,8); fgm=(l==1+np.argmax(st[1:,4])).astype(np.uint8)
fgm=cv2.morphologyEx(fgm,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
# fill small holes
inv=1-fgm; n,l,st,_=cv2.connectedComponentsWithStats(inv,4)
for i in range(1,n):
    if st[i,4]<400 and st[i,0]>0 and st[i,1]>0 and st[i,0]+st[i,2]<W//2 and st[i,1]+st[i,3]<H//2: fgm[l==i]=1
al=cv2.resize(fgm.astype(np.float32),(W,H),interpolation=cv2.INTER_LINEAR)
hsvF=cv2.cvtColor(a,cv2.COLOR_BGR2HSV).astype(int)
orange=(hsvF[...,1]>150)&(hsvF[...,0]<25)&(hsvF[...,2]>40)
zone=np.zeros((H,W),bool); zone[0:170,590:770]=True                 # beside the black hat only (no skin there)
al[cv2.dilate((orange&zone).astype(np.uint8),np.ones((5,5),np.uint8))>0]=0
al=cv2.GaussianBlur(al,(0,0),1.6); al=np.clip((al-0.2)/0.6,0,1)
np.save(S+"/fa_alpha.npy",al)
v=(a*al[...,None]+255*(1-al[...,None])).astype(np.uint8)
dbg=a.copy(); 
for p in fg: cv2.polylines(dbg,[p],True,(0,255,0),3)
for p in bg: cv2.polylines(dbg,[p],True,(255,0,0),3)
cv2.imwrite(S+"/fa_cut.jpg",cv2.resize(np.hstack([v,dbg]),(1400,875)))
