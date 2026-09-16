#!/usr/bin/env python3
"""Render the 'Roman roads' project description as a single A5 catalogue sheet.

Outputs (300 dpi, 148 x 210 mm -> 1748 x 2480 px):
  output/roman_roads_catalogue_a5.png   raster preview
  output/roman_roads_catalogue_a5.pdf   print-ready PDF (embedded raster)
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = __file__.rsplit("\\", 1)[0] if "\\" in __file__ else "."
OUT_PNG = f"{ROOT}/output/roman_roads_catalogue_a5.png"
OUT_PDF = f"{ROOT}/output/roman_roads_catalogue_a5.pdf"
MAP_PNG = f"{ROOT}/output/01_roman_roads_map.png"

# ---- canvas -------------------------------------------------------------
W, H = 1748, 2480          # A5 @ 300 dpi
M = 150                    # outer margin
CW = W - 2 * M             # content width

# ---- palette ------------------------------------------------------------
PAPER = (250, 246, 238)
INK   = (44, 39, 33)
MUTED = (118, 110, 99)
RED   = (165, 0, 38)
GOLD  = (172, 138, 94)
LINE  = (221, 213, 200)
CARD  = (255, 252, 247)

# ---- fonts --------------------------------------------------------------
F = "C:/Windows/Fonts"
def font(path, size):
    return ImageFont.truetype(f"{F}/{path}", size)

f_kicker   = font("georgia.ttf", 21)
f_title    = font("georgia.ttf", 68)
f_title_it = font("georgiai.ttf", 68)
f_sub      = font("georgia.ttf", 26)
f_sect     = font("georgia.ttf", 23)
f_aim_num  = font("georgiab.ttf", 34)
f_aim_lead = font("georgiab.ttf", 27)
f_aim_body = font("georgia.ttf", 25)
f_stat_num = font("georgiab.ttf", 45)
f_stat_lab = font("georgia.ttf", 20)
f_find     = font("georgia.ttf", 23)
f_cap      = font("georgiai.ttf", 19)
f_foot     = font("georgia.ttf", 17)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

y = 0  # running baseline cursor

def tracked(text, x, yy, fnt, tracking, fill):
    """Draw letter-spaced uppercase text, return its total width."""
    total = 0
    for ch in text:
        d.text((x + total, yy), ch, font=fnt, fill=fill)
        total += d.textlength(ch, font=fnt) + tracking
    return total

def wrap(text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=fnt) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def rule(x0, x1, yy, color=LINE, width=2):
    d.rectangle([x0, yy, x1, yy + width], fill=color)

# ============================================================ header
y = M + 6
d.rectangle([0, 0, W, 10], fill=RED)
d.rectangle([0, 10, W, 14], fill=GOLD)

y += 66
tracked("ROMAN ROADS  \u00b7  PROJECT SHEET", M, y, f_kicker, 2.2, GOLD)
y += 30
rule(M, W - M, y, GOLD, 2)
y += 52

t1 = "Do all the roads lead to "
t2 = "Rome"
tw1 = d.textlength(t1, font=f_title)
x = M
d.text((x, y), t1, font=f_title, fill=INK)
x += tw1
d.text((x, y), t2, font=f_title_it, fill=RED)
x += d.textlength(t2, font=f_title_it)
d.text((x, y), "?", font=f_title, fill=INK)
y += 88

sub = ("A network analysis of the Roman road system and its 1,388 cities \u2014 "
       "measuring the imperial grid, tracing which ancient cities still live on as "
       "today\u2019s metropolises, and recovering who first founded each of them.")
for ln in wrap(sub, f_sub, CW):
    d.text((M, y), ln, font=f_sub, fill=MUTED)
    y += 36
y += 12
rule(M, W - M, y, RED, 3)
y += 36

# ============================================================ aims
def section(label, yy):
    w_ = tracked(label, M, yy, f_sect, 3.0, RED)
    rule(M + w_ + 18, W - M, yy + 9, LINE, 2)
    return yy + 36

y = section("AIM", y)

aims = [
    ("The network.",
     "Rebuild the DARMC Roman road network as a graph \u2014 5,086 junctions and "
     "7,048 segments \u2014 and measure its true hubs, corridors and bottlenecks with "
     "degree and kilometre-weighted betweenness, testing whether all roads really led to Rome."),
    ("The inheritance.",
     "Follow Roman urbanism into the present: match each ancient city to its living "
     "successor and show how the imperial network still shapes the geography of modern "
     "Europe and the Mediterranean \u2014 London, Paris, Milan, Istanbul."),
    ("The founders.",
     "Reveal who first settled each city \u2014 the tribes (Dorian, Ionian, Etruscan, "
     "Phoenician \u2026) and the persons (Romulus and Remus, Philip II, Seleucus I Nicator \u2026) "
     "behind the names on the map."),
]

for i, (lead, body) in enumerate(aims, 1):
    num = str(i)
    nw = d.textlength(num, font=f_aim_num)
    d.text((M, y), num, font=f_aim_num, fill=RED)
    lx = M + nw + 26
    d.text((lx, y + 2), lead, font=f_aim_lead, fill=INK)
    lead_w = d.textlength(lead, font=f_aim_lead)
    body_x = lx + lead_w + 12
    first_w = CW - (body_x - M)
    words = body.split()
    cur, lines = "", []
    for w_ in words:
        maxw = first_w if not lines else CW
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=f_aim_body) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    if lines:
        d.text((body_x, y + 3), lines[0], font=f_aim_body, fill=MUTED)
        yy = y + 3 + 37
        for ln in lines[1:]:
            d.text((lx, yy), ln, font=f_aim_body, fill=MUTED)
            yy += 37
        y = yy
    else:
        y += 37
    y += 18  # gap between aims

y += 6

# ============================================================ stats
y = section("AT A GLANCE", y)
stats = [
    ("5,086 / 7,048", "road junctions / segments"),
    ("1,388", "Roman cities (100 BC\u2013AD 300)"),
    ("80%", "of cities within 5 km of a road"),
    ("46", "living successors of 300,000+"),
    ("887", "cities with population estimates"),
    ("11 / 47", "capitals \u00d72 (imperial / +provincial)"),
]
cols, gap = 2, 20
cell_w = (CW - gap * (cols - 1)) // cols
cell_h = 110
for i, (num, lab) in enumerate(stats):
    cx = M + (i % cols) * (cell_w + gap)
    cy = y + (i // cols) * (cell_h + 14)
    d.rounded_rectangle([cx, cy, cx + cell_w, cy + cell_h], radius=10, fill=CARD, outline=LINE, width=2)
    d.rectangle([cx, cy + 16, cx + 5, cy + cell_h - 16], fill=GOLD)
    d.text((cx + 28, cy + 14), num, font=f_stat_num, fill=RED)
    d.text((cx + 28, cy + 72), lab, font=f_stat_lab, fill=MUTED)
y += 3 * (cell_h + 14)

# ============================================================ map
y += 6
map_img = Image.open(MAP_PNG).convert("RGB")
mw = CW - 340
mh = int(mw * map_img.height / map_img.width)
map_img = map_img.resize((mw, mh), Image.LANCZOS)
mx = (W - mw) // 2
sh = Image.new("RGB", (mw + 24, mh + 24), PAPER)
shd = ImageDraw.Draw(sh)
shd.rounded_rectangle([6, 6, mw + 18, mh + 18], radius=14, fill=(214, 205, 191))
sh = sh.filter(ImageFilter.GaussianBlur(8))
img.paste(sh, (mx - 12, y - 12))
img.paste(map_img, (mx, y))
d.rectangle([mx - 1, y - 1, mx + mw, y + mh], outline=LINE, width=2)
y += mh + 20

cap = ("The road network with cities coloured by Barrington Atlas rank "
       "(dark red = Rome-scale; pale = minor).")
for ln in wrap(cap, f_cap, CW - 120):
    d.text(((W - d.textlength(ln, font=f_cap)) / 2, y), ln, font=f_cap, fill=MUTED)
    y += 30
y += 12

# ============================================================ findings
y = section("FINDINGS", y)
findings = [
    "Rome\u2019s hexagon ranks #1 on both degree and kilometre-weighted betweenness \u2014 "
    "the data confirms the proverb.",
    "Corridor capitals (Byzantium, Sirmium, Ravenna) carry the through-traffic, while "
    "terminal capitals (Rome, York, Carthage) carry almost none \u2014 betweenness measures "
    "position, not importance.",
    "The empire\u2019s hubs are still its heirs: Londinium\u2013London, Lutetia\u2013Paris, "
    "Byzantium\u2013Istanbul, Mediolanum\u2013Milan.",
]
for f in findings:
    d.text((M, y), "Via", font=f_aim_body, fill=RED)
    vw = d.textlength("Via", font=f_aim_body)
    for ln in wrap(f, f_find, CW - vw - 14):
        d.text((M + vw + 14, y + 2), ln, font=f_find, fill=INK)
        y += 32
    y += 6

# ============================================================ footer
y += 10
rule(M, W - M, y, LINE, 2)
y += 14
foot = ("Data: DARMC Roman Road Network 2008 (CC BY-NC 3.0) \u00b7 Hanson 2016 Cities "
        "Database (OxREP) \u00b7 Hanson & Ortman 2017 \u00b7 Reba, Reitsma & Seto 2016. "
        "Method: Urban Network Analysis (City Form Lab, MIT). After Janosov 2023.")
for ln in wrap(foot, f_foot, CW):
    d.text((M, y), ln, font=f_foot, fill=MUTED)
    y += 24
y += 2
d.text((M, y), "romanroads  \u00b7  RomanDataLab", font=f_foot, fill=RED)

print(f"bottom y used: {y} / {H}  (free: {H - y}px)")

img.save(OUT_PNG, dpi=(300, 300))
img.save(OUT_PDF, "PDF", resolution=300.0)
print("wrote", OUT_PNG)
print("wrote", OUT_PDF)
