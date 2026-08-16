"""Regenerate og-image.png, the 1200x630 card shown when the site is shared.

Mirrors the site's Win95 look: teal desktop, silver bevelled window, navy
titlebar, Times headline, and the black deadline ticker. Run it after changing
the site's wording:

    .venv/bin/python gen_og.py
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630

TEAL = (0, 128, 128)
SILVER = (192, 192, 192)
NAVY = (0, 0, 128)
BLUE = (16, 132, 208)
INK = (0, 0, 0)
WHITE = (255, 255, 255)
LITE = (223, 223, 223)
GREY = (128, 128, 128)
ALARM = (204, 0, 0)
AMBER = (255, 210, 74)
GREEN = (51, 255, 102)
DARKGREEN = (10, 42, 18)

F = "/System/Library/Fonts/Supplemental/"
def font(name, size):
    return ImageFont.truetype(F + name, size)

TIMES_B = "Times New Roman Bold.ttf"
TIMES_I = "Times New Roman Italic.ttf"
COURIER_B = "Courier New Bold.ttf"
TAHOMA = "Tahoma.ttf"
TAHOMA_B = "Tahoma Bold.ttf"


def bevel_out(d, box, fill=SILVER):
    """The raised Win95 panel: light top-left, dark bottom-right."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=fill)
    d.line([(x0, y0), (x1, y0)], fill=WHITE)
    d.line([(x0, y0), (x0, y1)], fill=WHITE)
    d.line([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=LITE)
    d.line([(x0 + 1, y0 + 1), (x0 + 1, y1 - 1)], fill=LITE)
    d.line([(x0, y1), (x1, y1)], fill=INK)
    d.line([(x1, y0), (x1, y1)], fill=INK)
    d.line([(x0 + 1, y1 - 1), (x1 - 1, y1 - 1)], fill=GREY)
    d.line([(x1 - 1, y0 + 1), (x1 - 1, y1 - 1)], fill=GREY)


img = Image.new("RGB", (W, H), TEAL)
d = ImageDraw.Draw(img)

# ---- window ----
bevel_out(d, (40, 40, W - 40, H - 40))

# ---- titlebar: navy fading to blue ----
tb = (52, 52, W - 52, 92)
for x in range(tb[0], tb[2] + 1):
    t = (x - tb[0]) / (tb[2] - tb[0])
    d.line([(x, tb[1]), (x, tb[3])], fill=tuple(int(NAVY[i] + (BLUE[i] - NAVY[i]) * t) for i in range(3)))
d.text((66, 60), "Lucid Research  -  CS conference deadline tracker", font=font(TAHOMA_B, 20), fill=WHITE)
for i, glyph in enumerate(("_", "❑", "X")):
    bx = W - 172 + i * 38
    bevel_out(d, (bx, 58, bx + 30, 86))
    d.text((bx + 9, 62), glyph, font=font(TAHOMA_B, 16), fill=INK)

# ---- logo ----
logo = Image.open("assets/logo.jpg").convert("RGB").resize((132, 132))
d.rectangle((72, 122, 210, 260), fill=WHITE, outline=GREY)
img.paste(logo, (75, 125))

# ---- wordmark ----
d.text((232, 118), "Lucid ", font=font(TIMES_B, 76), fill=NAVY)
w = d.textlength("Lucid ", font=font(TIMES_B, 76))
d.text((232 + w, 118), "Research", font=font(TIMES_B, 76), fill=ALARM)
d.text((236, 208), "Every CS conference deadline, in one place.", font=font(TIMES_I, 34), fill=(32, 32, 32))

# ---- odometer: the venue count ----
digits = "0184"
ox, oy = 900, 300
d.rectangle((ox - 8, oy - 8, ox + 4 + len(digits) * 44, oy + 62), fill=INK)
for i, ch in enumerate(digits):
    d.rectangle((ox + i * 44, oy, ox + i * 44 + 36, oy + 54), fill=DARKGREEN)
    d.text((ox + i * 44 + 8, oy + 6), ch, font=font(COURIER_B, 44), fill=GREEN)
d.text((ox - 8, oy + 74), "VENUES TRACKED", font=font(TAHOMA, 18), fill=(32, 32, 32))

# ---- ticker ----
d.rectangle((72, 300, 856, 350), fill=INK)
d.text((86, 314), "> USENIX SEC [2 days left]   > VLDB [9d]   > SIGCOMM [21d]",
       font=font(COURIER_B, 22), fill=AMBER)

# ---- stat strip ----
stats = [("185+", "VENUES"), ("9", "AREAS"), ("DAILY", "REFRESH"), ("FREE", "& OPEN")]
sx = 72
for value, label in stats:
    bevel_out(d, (sx, 396, sx + 176, 486))
    d.text((sx + 18, 412), value, font=font(COURIER_B, 34), fill=NAVY)
    d.text((sx + 18, 456), label, font=font(TAHOMA, 17), fill=(48, 48, 48))
    sx += 190

# ---- footer line ----
d.line([(72, 520), (W - 72, 520)], fill=GREY)
d.line([(72, 521), (W - 72, 521)], fill=WHITE)
d.text((72, 536), "krimler.github.io/paper-tracker", font=font(TAHOMA_B, 24), fill=NAVY)
d.text((72, 566), "Deadlines, countdowns, calendar and RSS feeds. Rebuilt daily.",
       font=font(TAHOMA, 20), fill=(48, 48, 48))

img.save("og-image.png")
print("wrote og-image.png", img.size)
