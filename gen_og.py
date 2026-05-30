from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1200, 630
PURPLE=(124,58,237); PINK=(236,72,153); AMBER=(245,158,11)
DARK=(31,41,55); GRAY=(107,114,128)

def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
def grad3(t):
    return lerp(PURPLE,PINK,t/0.5) if t<0.5 else lerp(PINK,AMBER,(t-0.5)/0.5)

img = Image.new("RGB",(W,H),(255,255,255))
px = img.load()
# soft vertical background lavender -> white
top=(243,232,255); bot=(255,255,255)
for y in range(H):
    c=lerp(top,bot,min(1,y/360))
    for x in range(W): px[x,y]=c
d=ImageDraw.Draw(img)
# top gradient accent bar
for x in range(W):
    d.line([(x,0),(x,12)], fill=grad3(x/(W-1)))

def font(path,size): return ImageFont.truetype(path,size)
AB="/System/Library/Fonts/Supplemental/Arial Bold.ttf"
ABL="/System/Library/Fonts/Supplemental/Arial Black.ttf"
AR="/System/Library/Fonts/Supplemental/Arial.ttf"

# logo, rounded
logo=Image.open("assets/logo.jpg").convert("RGB").resize((150,150))
mask=Image.new("L",(150,150),0)
ImageDraw.Draw(mask).rounded_rectangle([0,0,150,150],radius=34,fill=255)
img.paste(logo,(80,72),mask)

# wordmark + sub
d.text((258,80), "LUCID RESEARCH", font=font(ABL,40), fill=PURPLE)
d.text((260,138), "Conference deadline tracker", font=font(AR,26), fill=GRAY)

# headline
d.text((80,290), "Every CS conference deadline,", font=font(AB,58), fill=DARK)
d.text((80,360), "in one place.", font=font(AB,58), fill=PURPLE)

# stats
d.text((80,478), "185+ venues    ·    9 areas    ·    refreshed daily    ·    free",
       font=font(AB,30), fill=GRAY)

img.save("og-image.png")
print("wrote og-image.png", img.size)
