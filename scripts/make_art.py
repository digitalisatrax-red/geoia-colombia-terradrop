import json, os
import os; OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','assets','img')
def lg(i,c1,c2,x1=0,y1=0,x2=1,y2=1):
    return f'<linearGradient id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>'
def rg(i,c1,c2,cx=.35,cy=.3,r=.8):
    return f'<radialGradient id="{i}" cx="{cx}" cy="{cy}" r="{r}"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></radialGradient>'
SH='<filter id="blur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9"/></filter><filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2"/></filter>'
def svg(body,defs='',vb='0 0 480 480'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" fill="none"><defs>{SH}{defs}</defs>{body}</svg>'
def shadow(cx,cy,rx,ry,op=.22):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#1b1030" opacity="{op}" filter="url(#blur)"/>'
def gloss(x,y,w,h,r,op=.55):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="#fff" opacity="{op}" filter="url(#soft)"/>'

# ---------- ROBOT ----------
d=lg('pk','#FFB3D1','#FF5C97')+lg('bl','#6FB2FF','#2459D8')+lg('yl','#FFE27A','#FF9F1C')+lg('rd','#FF8A7A','#E5322D')+lg('nv','#26335F','#0E1430')+lg('wh','#FFFFFF','#DCE3F5')
b=shadow(240,438,150,24)
# legs
b+='<rect x="190" y="372" width="30" height="52" rx="14" fill="url(#yl)"/><rect x="260" y="372" width="30" height="52" rx="14" fill="url(#yl)"/>'
b+='<ellipse cx="205" cy="426" rx="26" ry="12" fill="url(#rd)"/><ellipse cx="275" cy="426" rx="26" ry="12" fill="url(#rd)"/>'
# arms
b+='<path d="M132 300 Q88 312 82 352" stroke="url(#yl)" stroke-width="22" stroke-linecap="round"/><circle cx="82" cy="356" r="19" fill="url(#rd)"/>'
b+='<path d="M348 300 Q398 282 408 238" stroke="url(#yl)" stroke-width="22" stroke-linecap="round"/><circle cx="410" cy="232" r="19" fill="url(#rd)"/>'
# body
b+='<rect x="140" y="268" width="200" height="120" rx="44" fill="url(#bl)"/>'+gloss(158,278,90,22,11)
b+='<rect x="188" y="302" width="104" height="56" rx="18" fill="url(#nv)"/><circle cx="214" cy="330" r="9" fill="#FFD23F"/><circle cx="240" cy="330" r="9" fill="#FF5C97"/><circle cx="266" cy="330" r="9" fill="#5FE3A1"/>'
# neck+head
b+='<rect x="218" y="250" width="44" height="30" rx="10" fill="url(#wh)"/>'
b+='<rect x="108" y="108" width="264" height="158" rx="62" fill="url(#pk)"/>'+gloss(132,120,120,26,13,.6)
b+='<rect x="84" y="160" width="30" height="58" rx="15" fill="url(#yl)"/><rect x="366" y="160" width="30" height="58" rx="15" fill="url(#yl)"/>'
b+='<rect x="140" y="140" width="200" height="104" rx="40" fill="url(#nv)"/>'
b+='<circle cx="198" cy="190" r="22" fill="#FFE27A"/><circle cx="282" cy="190" r="22" fill="#FFE27A"/><circle cx="204" cy="184" r="8" fill="#fff"/><circle cx="288" cy="184" r="8" fill="#fff"/>'
b+='<path d="M212 222 Q240 240 268 222" stroke="#5FE3A1" stroke-width="7" stroke-linecap="round"/>'
# antenna
b+='<rect x="236" y="62" width="9" height="54" rx="4" fill="#1b1030" opacity=".85"/><circle cx="240" cy="56" r="20" fill="url(#rd)"/>'+gloss(230,44,12,9,5,.7)
open(f'{OUT}/robot.svg','w').write(svg(b,d))

# ---------- MACHINE (descargas) ----------
d=lg('or','#FFB066','#FF5A1F')+lg('bl','#7CC4FF','#2D6BE0')+lg('yl','#FFE27A','#FFA81C')+lg('rd','#FF8A7A','#E5322D')+lg('gl','#E9F4FF','#B8D6F5')+lg('gr','#7CF0C0','#18B07A')+lg('pk','#FFB3D1','#FF5C97')+lg('nv','#26335F','#0E1430')
b=shadow(240,440,180,22)
b+='<path d="M96 86 L180 86 L160 140 L116 140Z" fill="url(#yl)"/>'+gloss(104,90,40,12,6,.6)  # funnel
b+='<rect x="90" y="140" width="290" height="236" rx="46" fill="url(#or)"/>'+gloss(112,152,150,24,12,.55)
b+='<rect x="118" y="172" width="170" height="156" rx="30" fill="url(#gl)" stroke="#fff" stroke-width="4" opacity=".95"/>'
balls=[(150,300,'#FF5C97'),(182,308,'#FFD23F'),(214,302,'#3B82F6'),(246,308,'#2DD4A0'),(166,272,'#3B82F6'),(198,276,'#FF5C97'),(230,274,'#FFD23F'),(262,282,'#FF7A3D'),(182,244,'#2DD4A0'),(214,246,'#FF5C97')]
for x,y,c in balls: b+=f'<circle cx="{x}" cy="{y}" r="15" fill="{c}"/><circle cx="{x-5}" cy="{y-6}" r="5" fill="#fff" opacity=".7"/>'
# lever
b+='<rect x="318" y="190" width="14" height="86" rx="7" fill="#1b1030" opacity=".8"/><circle cx="325" cy="186" r="22" fill="url(#rd)"/>'+gloss(316,172,14,10,5,.7)
b+='<rect x="304" y="270" width="42" height="26" rx="13" fill="url(#nv)"/>'
# chute and basket
b+='<path d="M380 300 Q432 300 432 350 L432 372" stroke="url(#bl)" stroke-width="30" stroke-linecap="round"/>'
b+='<rect x="396" y="372" width="82" height="58" rx="14" fill="url(#bl)"/>'+gloss(404,378,40,10,5,.55)
for x,y,c in [(420,372,'#FFD23F'),(446,368,'#FF5C97'),(462,372,'#2DD4A0')]: b+=f'<circle cx="{x}" cy="{y}" r="13" fill="{c}"/><circle cx="{x-4}" cy="{y-5}" r="4" fill="#fff" opacity=".7"/>'
b+='<rect x="150" y="344" width="110" height="16" rx="8" fill="url(#nv)"/><circle cx="166" cy="352" r="4" fill="#5FE3A1"/>'
b+='<rect x="120" y="376" width="40" height="38" rx="12" fill="url(#nv)"/><rect x="310" y="376" width="40" height="38" rx="12" fill="url(#nv)"/>'
# falling balls into funnel
for x,y,c in [(120,40,'#FF5C97'),(150,18,'#3B82F6'),(168,62,'#FFD23F')]: b+=f'<circle cx="{x}" cy="{y}" r="13" fill="{c}"/><circle cx="{x-4}" cy="{y-5}" r="4" fill="#fff" opacity=".7"/>'
open(f'{OUT}/machine.svg','w').write(svg(b,d))

# ---------- LAYERS ----------
def plate(cx,cy,w,h,t,top,side1,side2,extra=''):
    p=f'<path d="M{cx} {cy-h/2} L{cx+w/2} {cy} L{cx} {cy+h/2} L{cx-w/2} {cy}Z" fill="{top}"/>'
    l=f'<path d="M{cx-w/2} {cy} L{cx} {cy+h/2} L{cx} {cy+h/2+t} L{cx-w/2} {cy+t}Z" fill="{side1}"/>'
    r=f'<path d="M{cx+w/2} {cy} L{cx} {cy+h/2} L{cx} {cy+h/2+t} L{cx+w/2} {cy+t}Z" fill="{side2}"/>'
    return l+r+p+extra
d=lg('t1','#6FB2FF','#3B82F6')+lg('t2','#7CF0C0','#2DD4A0')+lg('t3','#FFE27A','#FFC93C')+lg('t4','#FF9A8A','#FF5A5A')+lg('rd','#FF8A7A','#E5322D')
b=shadow(240,430,170,24)
cols=[('#FF6B5E','#D94A3E','#B8372E'),('#FFD23F','#E6B21F','#C2940F'),('#3DDCA0','#20B880','#139066'),('#4F8DF7','#2F69D6','#2455AE')]
ys=[372,300,228,156]
for (top,s1,s2),y in zip(cols,ys): b+=plate(240,y,330,150,16,top,s1,s2)
# details on plates
b+='<path d="M170 156 L230 126 L300 160 L250 186Z" fill="#fff" opacity=".35"/>'
b+='<circle cx="262" cy="228" r="12" fill="#fff" opacity=".6"/><circle cx="208" cy="246" r="8" fill="#fff" opacity=".5"/><path d="M180 300 Q240 268 306 304" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity=".6"/>'
b+='<path d="M170 372 L230 352 L250 380 L196 392Z" fill="#fff" opacity=".35"/>'
# pin on top
b+='<ellipse cx="240" cy="148" rx="14" ry="6" fill="#1b1030" opacity=".3"/><path d="M240 142 C216 110 218 70 240 70 C262 70 264 110 240 142Z" fill="url(#rd)" transform="translate(0,-8)"/><circle cx="240" cy="92" r="9" fill="#fff"/>'
b+='<path d="M72 130 L72 400 M408 130 L408 400" stroke="#1b1030" stroke-width="2" stroke-dasharray="3 8" opacity=".25"/>'
open(f'{OUT}/layers.svg','w').write(svg(b,d))

# ---------- PUZZLE CUBE ----------
def cube(cx,cy,s,c1,c2,c3):
    h=s*0.5
    top=f'<path d="M{cx} {cy-s} L{cx+s*.87} {cy-s/2} L{cx} {cy} L{cx-s*.87} {cy-s/2}Z" fill="{c1}"/>'
    left=f'<path d="M{cx-s*.87} {cy-s/2} L{cx} {cy} L{cx} {cy+s} L{cx-s*.87} {cy+s/2}Z" fill="{c2}"/>'
    right=f'<path d="M{cx+s*.87} {cy-s/2} L{cx} {cy} L{cx} {cy+s} L{cx+s*.87} {cy+s/2}Z" fill="{c3}"/>'
    return left+right+top
d=''
b=shadow(240,436,150,20)
b+=cube(240,330,120,'#A78BFA','#7C5CE0','#5B3FC2')
b+=cube(240,214,70,'#FF9CC2','#E8609A','#C94682')
b+=cube(360,130,52,'#FFE27A','#F5B21B','#D4950F')
b+=cube(120,150,40,'#7CC4FF','#3F8DE3','#2E6FBD')
b+='<path d="M200 292 l30 -17 l30 17 l-30 17Z" fill="#fff" opacity=".4"/><circle cx="176" cy="372" r="9" fill="#fff" opacity=".5"/><circle cx="296" cy="378" r="9" fill="#fff" opacity=".5"/>'
b+='<path d="M240 100 L240 60" stroke="#1b1030" stroke-width="3" stroke-dasharray="3 7" opacity=".3"/><circle cx="240" cy="52" r="10" fill="#2DD4A0"/>'
open(f'{OUT}/cube.svg','w').write(svg(b,d))

# ---------- MAGNIFIER ----------
d=lg('yl','#FFE27A','#FF9F1C')+rg('gl','#FFFFFF','#9BD0FF',.3,.25,.9)+lg('rd','#FF8A7A','#E5322D')+lg('nv','#26335F','#0E1430')+lg('gr','#7CF0C0','#18B07A')
b=shadow(250,440,150,20)
b+='<rect x="292" y="300" width="64" height="150" rx="32" fill="url(#nv)" transform="rotate(-42 324 375)"/>'
b+='<circle cx="212" cy="214" r="136" fill="url(#yl)"/><circle cx="212" cy="214" r="108" fill="url(#gl)" opacity=".92"/>'
b+='<path d="M120 252 q40 -60 92 -34 t92 -10" stroke="#18B07A" stroke-width="22" stroke-linecap="round" opacity=".8"/><path d="M130 286 q60 -20 104 8 t60 -12" stroke="#2D6BE0" stroke-width="16" stroke-linecap="round" opacity=".75"/>'
b+='<path d="M212 242 C180 200 184 148 212 148 C240 148 244 200 212 242Z" fill="url(#rd)"/><circle cx="212" cy="178" r="12" fill="#fff"/>'
b+=gloss(130,130,60,16,8,.9).replace('<rect','<rect transform="rotate(-38 160 138)"')
b+='<circle cx="388" cy="100" r="30" fill="url(#gr)"/><circle cx="380" cy="90" r="9" fill="#fff" opacity=".7"/><circle cx="64" cy="392" r="18" fill="url(#rd)"/><circle cx="58" cy="386" r="6" fill="#fff" opacity=".7"/>'
open(f'{OUT}/magnifier.svg','w').write(svg(b,d))

# ---------- GLOBE (geovisores) ----------
d=rg('sp','#9AD6FF','#1F5FD0',.32,.28,.85)+lg('gr','#7CF0C0','#18B07A')+lg('yl','#FFE27A','#FF9F1C')+lg('rd','#FF8A7A','#E5322D')+'<clipPath id="cp"><circle cx="240" cy="240" r="150"/></clipPath>'
b=shadow(240,430,130,18)
b+='<circle cx="240" cy="240" r="150" fill="url(#sp)"/>'
b+='<g clip-path="url(#cp)"><path d="M150 150 q40 -40 90 -10 q30 20 10 50 q-30 30 -20 70 q-30 40 -70 10 q-40 -50 -10 -120Z" fill="url(#gr)"/><path d="M270 250 q50 -30 80 10 q10 50 -30 70 q-40 10 -50 -30 q-10 -30 0 -50Z" fill="url(#gr)"/><path d="M290 130 q40 -10 60 20 q-30 20 -60 -20Z" fill="url(#gr)"/></g>'
b+=gloss(150,128,80,22,11,.7).replace('<rect','<rect transform="rotate(-30 190 140)"')
b+='<ellipse cx="240" cy="250" rx="196" ry="56" stroke="url(#yl)" stroke-width="13" transform="rotate(-22 240 250)" fill="none"/>'
b+='<g transform="rotate(-22 240 250)"><rect x="398" y="228" width="36" height="44" rx="10" fill="url(#rd)"/><rect x="364" y="240" width="36" height="20" rx="6" fill="#26335F"/><rect x="432" y="240" width="36" height="20" rx="6" fill="#26335F"/></g>'
b+='<path d="M240 90 C222 66 224 40 240 40 C256 40 258 66 240 90Z" fill="url(#rd)"/><circle cx="240" cy="58" r="7" fill="#fff"/>'
open(f'{OUT}/globe.svg','w').write(svg(b,d))

# ---------- HERO COLOMBIA extruded ----------
M=json.load(open('/home/claude/repo/data/mapa_colombia.json'))
pal=['#FFC93C','#4F8DF7','#FF6B5E','#3DDCA0','#FF9CC2','#A78BFA','#7CC4FF','#FF9F1C']
W,H=M['w'],M['h']
body=''
deps=[(k,v) for k,v in M['dep'].items() if v['p']]
shape=''.join(f'<path d="{v["p"]}"/>' for k,v in deps)
layers=''.join(f'<use href="#shp" transform="translate({i*1.6},{i*3.4})" fill="{"#16235a" if i>10 else "#1b2b6b" if i>5 else "#243a85"}"/>' for i in range(14,0,-1))
fill=''
for i,(k,v) in enumerate(deps):
    c=pal[(int(k)*3+i)%len(pal)]
    fill+=f'<path d="{v["p"]}" fill="{c}" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/>'
vb=f'-60 -40 {W+220} {H+240}'
hero=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" fill="none"><defs><filter id="blur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="22"/></filter></defs>'
hero+=f'<defs><g id="shp">{shape}</g></defs>'
hero+=f'<ellipse cx="{W*0.55}" cy="{H+110}" rx="{W*0.5}" ry="48" fill="#1b1030" opacity=".22" filter="url(#blur)"/>'
hero+=f'<g>{layers}</g><g>{fill}</g>'
hero+='</svg>'
open(f'{OUT}/colombia-3d.svg','w').write(hero)
print('ok')
