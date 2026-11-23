#!/usr/bin/env python3
"""news-image-20261123 v1 renderer: draws one 1024x1024 PNG summing up
Monday 23 November 2026 world news. Standard library + PIL only.
Deterministic: no random, no clock, no network. Run: python3 make_image.py
"""
import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.environ.get("OUT", "entry.png")

NAVY = (15, 42, 74)
BLUE = (27, 79, 114)
RED = (192, 57, 43)
GREEN = (30, 132, 73)
GREY = (85, 85, 85)
LIGHTGREY = (242, 244, 246)
SKY = (174, 214, 241)
SEA = (133, 193, 233)
DARKSEA = (46, 134, 193)
SAND = (250, 243, 224)
ORANGE = (230, 126, 34)
YELLOW = (247, 220, 111)

CREAM = (250, 243, 224)
GOLD = (212, 172, 13)
TEAL = (23, 120, 113)
PURPLE = (108, 92, 180)
DARKGREY = (60, 60, 60)

FDIR = "/usr/share/fonts/truetype/liberation/"
FB = os.path.join(FDIR, "LiberationSans-Bold.ttf")
FR = os.path.join(FDIR, "LiberationSans-Regular.ttf")
SDIR = "/usr/share/fonts/truetype/dejavu/"
SERIFB = os.path.join(SDIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(SDIR, "DejaVuSerif.ttf")
SERIFI = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


f_mast = F(FB, 17)
f_mast_r = F(FR, 12)
f_date = F(FB, 13)
f_date_r = F(FR, 11)
f_lead_t = F(FB, 15)
f_lead_b = F(FR, 11)
f_attr = F(FR, 10)
f_med_t = F(FB, 13)
f_med_b = F(FR, 11)
f_also = F(FR, 10)
f_badge = F(FB, 9)
f_num = F(FB, 20)
f_num_l = F(FR, 10)
f_label = F(FB, 10)
f_dc = F(FB, 11)
f_dc_r = F(FR, 11)
f_foot = F(FR, 10)
f_foot_b = F(FB, 10)
f_bot = F(FB, 11)
f_bot_r = F(FR, 10)
f_map_n = F(FB, 9)
f_chip = F(FB, 12)
# v2 reference structure: giant serif date title, red italic sub-headline,
# big red number strip, region strip, UTC timeline, mini panels with chips.
f_bigdate = F(SERIFB, 60)
f_subhead = F(SERIFI, 15)
f_bignum = F(SERIFB, 26)
f_bignum_l = F(FR, 9)
f_region = F(FB, 10)
f_timeline = F(FR, 10)
f_timeline_b = F(FB, 10)
f_lead_meta = F(FB, 10)
f_lead_t2 = F(SERIFB, 16)
f_med_loc = F(FB, 9)
f_med_chip = F(FB, 9)
f_med_t2 = F(FB, 12)
f_med_b2 = F(FR, 10)
f_section = F(FB, 13)
f_section_r = F(FR, 10)
f_also_tag = F(FB, 10)
f_dc2 = F(FB, 11)


def tw(d, text, font):
    return d.textlength(text, font=font)


def wrap(d, text, font, max_w):
    """Greedy word wrap, returns list of lines that fit max_w."""
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if tw(d, trial, font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_one_line(d, text, font, max_w, suffix="..."):
    """Truncate to one line that fits, with ellipsis if needed."""
    if tw(d, text, font) <= max_w:
        return text
    while text and tw(d, text + suffix, font) > max_w:
        text = text[:-1].rstrip()
    return text + suffix if text else ""


def rrect(d, box, radius, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


# ---------------------------------------------------------------- stories
# LEAD: (title, body, attribution)
LEAD = [
    ("Nvidia Brings Back Huang as CEO; Shares Jump 33%",
     "Board reinstates founder Jensen Huang as chief executive, 11 days after "
     "his exit. The S and P 500 rose 4.82% and the Nasdaq about 6.5% as AI "
     "stocks rebounded from last week's sell-off.",
     "Reuters, CNBC, BBC"),
    ("Iran Vows to Fight US Blockade of Hormuz; Claims US Drone Downed",
     "Tehran says it will use every means against the US naval blockade, "
     "calling it aggression. Its army claims it shot down a US LUCAS drone "
     "east of the strait; the IRGC claims 78 US drones downed in all.",
     "Daily Summary, Press TV, Anadolu"),
    ("Zelenskyy Confirms Ukraine Sank Russian Corvette in Benghazi",
     "Seven sea drones sank the corvette Merkury at Libya's Benghazi port on "
     "Sunday, Kyiv says; cargo ship Angara was also hit. The UN mission in "
     "Libya called for an independent inquiry.",
     "Reuters, BBC, Guardian"),
]

# MEDIUM: (title, body, attribution, icon key)
MEDIUM = [
    ("Russian Strikes Kill at Least 15 in Kyiv Region",
     "A 7-year-old was pulled alive from rubble in Dymer after 14 hours; a "
     "79-year-old after 22. Zelenskyy pressed the US to release paid-for "
     "Patriot missiles.",
     "BBC", "flame"),
    ("NATO Vows to Defend Every Inch of Allied Land",
     "Mark Rutte said the alliance will defend itself against threats in "
     "space as the annual meeting closed in Berlin.",
     "Tagesschau", "shield"),
    ("EU Proposes 22nd Sanctions Package on Russia",
     "The plan would bar Russian athletes from competing for their country "
     "at EU events and target ex-combatants' visas.",
     "Guardian", "stars"),
    ("Tata Steel's $1.67bn APL Apollo Deal Sinks Its Shares 8%",
     "The steelmaker will buy a 26.6% promoter stake in APL Apollo Tubes; "
     "the Sensex fell 1,484 points.",
     "Hindu BusinessLine", "factory"),
    ("India Pledges $1.6bn to Rebuild Flood-Hit Nepal",
     "PM Balen Shah made his first foreign visit to Delhi; Modi also "
     "announced an IIT campus and rail and hydropower deals.",
     "Euronews", "mountain"),
    ("Iran Flogs Singer Parastoo Ahmadi 74 Times",
     "Ahmadi and four band members were flogged in Qom over a 2024 "
     "livestream concert performed without a hijab.",
     "Daily Summary", "mic"),
    ("Oxfam: War Has Contaminated 99% of Gaza",
     "Heavy metals, explosives residue and asbestos threaten air, soil and "
     "water for generations, the report warns.",
     "BBC, Guardian", "warn"),
    ("Belgium Airports Grounded for a Day by Air Traffic Strike",
     "Controllers walked out from 07:00 to 21:00, hitting 50,000+ travellers "
     "at Brussels and Charleroi.",
     "France 24, BBC", "plane"),
    ("CrowdStrike to Buy Zscaler in $44bn All-Stock Deal",
     "The cybersecurity pair said the deal answers AI-powered attacks and "
     "builds a bigger cloud security firm.",
     "CNBC", "dollar"),
    ("Kenya and DR Congo Restore Full Diplomatic Ties",
     "Presidents Ruto and Tshisekedi agreed the reset at a summit in Oyo "
     "after tensions over eastern Congo.",
     "BBC, Africanews", "flags"),
]

# LEAD meta: (location line, REPORTED/CLAIM chip) per lead, same order.
LEAD_META = [
    ("AMERICAS · MARKETS", "REPORTED"),
    ("MIDDLE EAST · GULF", "CLAIM"),
    ("AFRICA · WAR", "REPORTED"),
]

# MEDIUM chips + location lines, same order as MEDIUM.
MED_CHIP = [
    "15 KILLED", "NATO MEETS", "SANCTIONS", "$1.67BN DEAL", "€1.4BN AID",
    "74 LASHES", "99% POLLUTED", "FLIGHTS GROUNDED", "$44BN DEAL",
    "TIES RESTORED",
]
MED_LOC = [
    "KYIV REGION, UKRAINE · WAR",
    "BERLIN, GERMANY · SECURITY",
    "BRUSSELS, EU · POLITICS",
    "MUMBAI, INDIA · MARKETS",
    "NEW DELHI, INDIA · AID",
    "QOM, IRAN · RIGHTS",
    "GAZA · CONFLICT",
    "BRUSSELS, BELGIUM · TRAVEL",
    "WASHINGTON, US · TECH",
    "OYO, CONGO · POLITICS",
]

# Region strip: (name, story count, colour), widths set in build().
REGIONS = [
    ("EUROPE", 9, BLUE),
    ("MIDDLE EAST", 4, RED),
    ("ASIA-PACIFIC", 7, ORANGE),
    ("AMERICAS", 7, TEAL),
    ("AFRICA", 6, GREEN),
    ("OCEANIA", 1, PURPLE),
    ("WORLD", 1, GREY),
]

# "THE DAY IN UTC" timeline: (UTC time, short event).
TIMELINE = [
    ("03:15", "Belgium airports shut"),
    ("06:10", "Kyiv strikes kill 15"),
    ("07:00", "Merkury sunk"),
    ("10:08", "Iran vows blockade fight"),
    ("14:32", "Amtrak derails"),
    ("18:04", "Ahmadi flogged"),
]

# COMPACT: (number, region tag, text) - one line each, source at the end.
# Kept short to fit a ~280px column at 10px.
ALSO = [
    (14, "Middle East", "Hodeida strike kills 4 - CNBC"),
    (15, "Africa", "UN Libya seeks Benghazi inquiry - DS"),
    (16, "Africa", "Drones hit Khartoum, UN site - RFI"),
    (17, "Asia", "Tajikistan quits ICC - Asharq"),
    (18, "Asia", "Kim stresses sovereignty - DS"),
    (19, "Americas", "Democrats plan 12 debates - UPI"),
    (20, "Americas", "US admits citizen deported - Guardian"),
    (21, "World", "US to host 2031 Women's Cup - BBC"),
    (22, "Europe", "Magyar plans Transcarpathia visit - DS"),
    (23, "Europe", "Russia tried to kill rapper twice - DS"),
    (24, "Americas", "US Army to blast Iowa explosives - BBC"),
    (25, "Africa", "Nigeria boat toll rises to 29 - BBC"),
    (26, "Asia", "Banten search on; 29 missing - Reuters"),
    (27, "Oceania", "Sydney trial: deaths execution - DS"),
    (28, "Americas", "Bolsonaro in intensive care - MercoPress"),
    (29, "Americas", "Amtrak derails; 5 hurt - DS"),
    (30, "Asia", "Nepal gets first climate payout - RFI"),
    (31, "Asia", "Shuri Castle reopens after 7 yrs - JT"),
    (32, "Europe", "Princess of Wales on cancer - France 24"),
    (33, "Africa", "WHO urges peace amid Ebola - DS"),
    (34, "Europe", "~450 schools get bomb threats - Al Jazeera"),
    (35, "Europe", "Gas up 8.6%; Brent $86.78 - OilPrice"),
]

NUMBERS = [
    ("NVIDIA +33%", "Huang returns as CEO"),
    ("S&P +4.82%", "Wall St rebounds"),
    ("7 SEA DRONES", "sank corvette Merkury"),
    ("74 LASHES", "Iran flogs singer Ahmadi"),
    ("50,000+", "travellers hit, Belgium airports"),
    ("$44 BILLION", "CrowdStrike buys Zscaler"),
]

# Map pins: (story number, lon, lat, badge dx, badge dy)
PINS = [
    (29, -91.5, 30.2, 0, -14),
    (3, 20.1, 32.1, 24, 8),
    (2, 56.5, 26.6, 16, 10),
    (4, 30.5, 50.5, 14, -12),
    (5, 13.4, 52.5, -2, -16),
    (11, 4.35, 50.85, -16, -6),
    (8, 77.2, 28.6, 12, -12),
    (9, 50.9, 34.6, 8, -20),
    (10, 34.5, 31.5, -18, 4),
    (14, 42.9, 14.8, 10, 12),
    (16, 32.5, 15.6, -14, 10),
    (25, 6.0, 4.9, -12, 12),
    (26, 106.0, -6.3, 12, 10),
    (27, 151.2, -33.9, 0, -14),
    (31, 127.7, 26.2, 12, -12),
]

# Simplified continent polygons in (lon, lat)
N_AMERICA = [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60),
             (-135, 57), (-130, 54), (-125, 49), (-124, 42), (-120, 34),
             (-114, 29), (-108, 25), (-105, 22), (-97, 16), (-94, 17),
             (-90, 14), (-86, 12), (-83, 9), (-79, 9), (-81, 13),
             (-84, 16), (-87, 21), (-90, 21), (-91, 19), (-95, 19),
             (-97, 26), (-93, 30), (-89, 30), (-84, 30), (-81, 26),
             (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-68, 45),
             (-65, 44), (-60, 47), (-55, 47), (-53, 50), (-56, 52),
             (-60, 55), (-65, 60), (-68, 58), (-78, 62), (-85, 66),
             (-92, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70),
             (-155, 71), (-165, 68)]
GREENLAND = [(-55, 60), (-45, 60), (-40, 64), (-32, 68), (-22, 70),
             (-20, 74), (-25, 78), (-35, 80), (-50, 80), (-58, 76),
             (-60, 72), (-55, 64)]
S_AMERICA = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
             (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44),
             (-74, -50), (-70, -54), (-66, -55), (-68, -50), (-65, -45),
             (-62, -41), (-58, -35), (-52, -32), (-48, -28), (-41, -23),
             (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
             (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11),
             (-72, 12), (-77, 8)]
AFRICA = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15),
          (-15, 11), (-12, 8), (-8, 5), (-4, 5), (0, 6), (6, 4),
          (9, 4), (9, 0), (12, -4), (13, -10), (12, -17), (14, -22),
          (16, -28), (18, -33), (20, -35), (26, -34), (28, -32),
          (32, -29), (35, -24), (36, -18), (40, -15), (40, -10),
          (42, -4), (46, -1), (51, 2), (51, 11), (48, 11), (44, 11),
          (40, 15), (38, 18), (37, 22), (34, 27), (32, 31), (30, 31),
          (25, 32), (19, 33), (15, 32), (11, 34), (10, 37), (5, 37),
          (0, 36)]
EUROPE = [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48),
          (-1, 49), (2, 51), (4, 53), (8, 57), (10, 59), (5, 60),
          (5, 62), (10, 64), (12, 66), (18, 69), (25, 71), (30, 70),
          (32, 68), (35, 66), (40, 64), (42, 60), (40, 57), (38, 54),
          (35, 52), (30, 50), (28, 47), (30, 45), (28, 44), (23, 40),
          (26, 38), (23, 36), (20, 39), (18, 40), (16, 42), (12, 44),
          (8, 44), (3, 43), (0, 40), (-2, 37), (-6, 36), (-9, 37)]
ASIA = [(30, 70), (45, 68), (60, 69), (75, 72), (90, 75), (105, 77),
        (120, 74), (135, 72), (150, 70), (160, 66), (162, 60), (158, 55),
        (156, 51), (150, 59), (142, 55), (140, 44), (137, 37), (132, 34),
        (127, 35), (126, 39), (122, 40), (120, 34), (118, 28), (112, 22),
        (108, 14), (105, 9), (101, 7), (98, 12), (94, 17), (91, 22),
        (88, 21), (85, 19), (80, 13), (77, 8), (74, 14), (70, 21),
        (66, 25), (61, 25), (57, 26), (54, 26), (51, 28), (48, 30),
        (44, 29), (40, 24), (36, 17), (39, 13), (43, 12), (47, 14),
        (52, 16), (56, 18), (59, 22), (57, 26), (53, 27), (51, 29),
        (48, 30), (45, 31), (42, 33), (39, 36), (36, 36), (33, 36),
        (30, 36), (30, 41), (28, 44), (30, 46), (32, 48), (34, 52),
        (36, 56), (38, 60), (36, 64), (33, 68)]
AUSTRALIA = [(113, -22), (114, -30), (115, -34), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -22),
             (146, -19), (142, -15), (142, -11), (140, -17), (136, -15),
             (135, -12), (132, -11), (130, -13), (126, -14), (122, -17),
             (118, -20)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
      (1, 51), (-2, 50)]
JAPAN = [(130, 31), (132, 33), (134, 34), (137, 35), (139, 37),
         (141, 39), (141, 41), (143, 42), (145, 44), (141, 45),
         (139, 42), (137, 39), (135, 36), (133, 34), (131, 32)]


# ---------------------------------------------------------------- icons
def icon(d, key, x, y, s=48):
    """Draw a big, bold, high-contrast icon for a medium story.

    The box is 48x48 and every shape fills most of it: thick filled
    silhouettes with no fine detail, so each icon reads at a glance.
    """
    import math

    def star_pts(sx, sy, r_out, r_in):
        pts = []
        for k in range(10):
            r = r_out if k % 2 == 0 else r_in
            a = -math.pi / 2 + k * math.pi / 5
            pts.append((sx + r * math.cos(a), sy + r * math.sin(a)))
        return pts

    rrect(d, [x, y, x + s, y + s], 8, fill=LIGHTGREY)
    cx, cy = x + s // 2, y + s // 2
    if key == "flame":
        # dark rubble blocks at the base
        d.rectangle([x + 3, y + 39, x + 21, y + 45], fill=GREY)
        d.rectangle([x + 24, y + 41, x + 45, y + 45], fill=GREY)
        # big outer flame
        d.polygon([(cx, y + 3), (cx + 15, y + 15), (cx + 17, y + 28),
                   (cx + 10, y + 39), (cx - 10, y + 39),
                   (cx - 17, y + 28), (cx - 15, y + 15)], fill=ORANGE)
        # inner flame
        d.polygon([(cx, y + 16), (cx + 8, y + 26), (cx + 5, y + 37),
                   (cx - 5, y + 37), (cx - 8, y + 26)], fill=YELLOW)
        # bright core
        d.polygon([(cx, y + 26), (cx + 4, y + 32), (cx, y + 37),
                   (cx - 4, y + 32)], fill=(255, 255, 255))
    elif key == "shield":
        d.polygon([(cx, y + 2), (cx + 19, y + 8), (cx + 19, y + 26),
                   (cx, y + 46), (cx - 19, y + 26), (cx - 19, y + 8)],
                  fill=NAVY)
        d.polygon(star_pts(cx, cy + 1, 12, 5), fill=(255, 255, 255))
    elif key == "stars":
        d.ellipse([x + 2, y + 2, x + 46, y + 46], fill=NAVY)
        gold = (255, 204, 0)
        for k in range(12):
            a = -math.pi / 2 + k * math.pi / 6
            px = cx + 15 * math.cos(a)
            py = cy + 15 * math.sin(a)
            d.polygon(star_pts(px, py, 3.5, 1.4), fill=gold)
    elif key == "factory":
        slate = (52, 73, 94)
        # smoke puffs above the chimneys
        d.ellipse([x + 7, y + 2, x + 15, y + 10], fill=(160, 160, 160))
        d.ellipse([x + 17, y + 1, x + 27, y + 9], fill=(160, 160, 160))
        # chimneys
        d.rectangle([x + 8, y + 10, x + 14, y + 26], fill=slate)
        d.rectangle([x + 18, y + 6, x + 24, y + 26], fill=slate)
        # main hall with a sawtooth roof
        d.polygon([(x + 4, y + 26), (x + 12, y + 19), (x + 20, y + 26),
                   (x + 28, y + 19), (x + 36, y + 26), (x + 44, y + 26),
                   (x + 44, y + 45), (x + 4, y + 45)], fill=slate)
        # glowing windows
        for wx in (x + 8, x + 20, x + 32):
            d.rectangle([wx, y + 30, wx + 7, y + 38], fill=ORANGE)
    elif key == "mountain":
        d.polygon([(x + 2, y + 45), (x + 19, y + 11), (x + 37, y + 45)],
                  fill=BLUE)
        d.polygon([(x + 24, y + 45), (x + 38, y + 17), (x + 46, y + 45)],
                  fill=NAVY)
        d.polygon([(x + 15, y + 18), (x + 19, y + 11), (x + 23, y + 18),
                   (x + 19, y + 22)], fill=(255, 255, 255))
        d.polygon([(x + 34, y + 24), (x + 38, y + 17), (x + 42, y + 24),
                   (x + 38, y + 28)], fill=(255, 255, 255))
    elif key == "mic":
        d.ellipse([cx - 13, y + 4, cx + 13, y + 25], fill=NAVY)
        d.line([cx - 10, y + 11, cx + 10, y + 11], fill=(255, 255, 255),
               width=2)
        d.line([cx - 11, y + 17, cx + 11, y + 17], fill=(255, 255, 255),
               width=2)
        d.line([cx, y + 25, cx, y + 36], fill=NAVY, width=5)
        d.line([cx - 11, y + 38, cx + 11, y + 38], fill=NAVY, width=5)
    elif key == "warn":
        d.polygon([(cx, y + 3), (cx + 22, y + 43), (cx - 22, y + 43)],
                  fill=YELLOW, outline=ORANGE, width=3)
        d.rectangle([cx - 3, y + 15, cx + 3, y + 31], fill=NAVY)
        d.ellipse([cx - 2, y + 35, cx + 2, y + 39], fill=NAVY)
    elif key == "plane":
        # tail fin
        d.polygon([(x + 5, y + 25), (x + 9, y + 9), (x + 16, y + 9),
                   (x + 16, y + 25)], fill=NAVY)
        # main wing pointing down
        d.polygon([(x + 19, y + 29), (x + 25, y + 43), (x + 32, y + 43),
                   (x + 32, y + 29)], fill=NAVY)
        # fuselage
        d.polygon([(x + 3, y + 27), (x + 9, y + 21), (x + 39, y + 17),
                   (x + 45, y + 21), (x + 45, y + 26), (x + 39, y + 31),
                   (x + 9, y + 33), (x + 3, y + 30)], fill=NAVY)
        # windows
        for wx in (x + 28, x + 33, x + 38):
            d.ellipse([wx, y + 22, wx + 3, y + 25], fill=(255, 255, 255))
    elif key == "dollar":
        d.ellipse([x + 3, y + 3, x + 45, y + 45], fill=GREEN)
        t = "$"
        d.text((cx - tw(d, t, f_num) / 2, cy - 11), t, font=f_num,
               fill=(255, 255, 255))
    elif key == "flags":
        d.line([x + 13, y + 5, x + 13, y + 45], fill=GREY, width=3)
        d.line([x + 33, y + 5, x + 33, y + 45], fill=GREY, width=3)
        d.ellipse([x + 10, y + 2, x + 16, y + 8], fill=(255, 204, 0))
        d.ellipse([x + 30, y + 2, x + 36, y + 8], fill=(255, 204, 0))
        d.rectangle([x + 13, y + 6, x + 30, y + 21], fill=GREEN)
        d.rectangle([x + 33, y + 6, x + 45, y + 21], fill=RED)
        d.rectangle([x + 13, y + 12, x + 30, y + 15], fill=(255, 255, 255))
        d.rectangle([x + 33, y + 12, x + 45, y + 15], fill=(255, 255, 255))


# ------------------------------------------------------- lead illustrations
def lead1_art(d, x, y, w, h):
    """Rising stock chart + chip."""
    rrect(d, [x, y, x + w, y + h], 6, fill=(234, 242, 248))
    # grid
    for gy in range(1, 4):
        yy = y + h * gy // 4
        d.line([x + 8, yy, x + w - 8, yy], fill=(213, 220, 229), width=1)
    # bars rising
    bw = 26
    heights = [22, 34, 48, 64]
    for i, bh in enumerate(heights):
        bx = x + 22 + i * 44
        d.rectangle([bx, y + h - 14 - bh, bx + bw, y + h - 14],
                    fill=BLUE if i < 3 else GREEN)
    # rising line with arrow
    pts = [(x + 20, y + h - 30), (x + 90, y + h - 52), (x + 160, y + h - 44),
           (x + 230, y + h - 70), (x + 292, y + h - 88)]
    d.line(pts, fill=GREEN, width=4, joint="curve")
    d.polygon([(x + 292, y + h - 88), (x + 280, y + h - 84),
               (x + 288, y + h - 76)], fill=GREEN)
    # chip
    cx0, cy0 = x + w - 108, y + 12
    d.rectangle([cx0, cy0, cx0 + 84, cy0 + 40], fill=NAVY)
    for px in range(5):
        d.line([cx0 + 10 + px * 16, cy0 - 5, cx0 + 10 + px * 16, cy0],
               fill=(212, 172, 13), width=3)
        d.line([cx0 + 10 + px * 16, cy0 + 40, cx0 + 10 + px * 16,
                cy0 + 45], fill=(212, 172, 13), width=3)
    d.text((cx0 + 22, cy0 + 12), "NVDA", font=f_chip, fill=(255, 255, 255))
    d.text((x + 14, y + 8), "+33%", font=F(FB, 22), fill=GREEN)


def lead2_art(d, x, y, w, h):
    """Tanker in a strait + drone above."""
    rrect(d, [x, y, x + w, y + h], 6, fill=SKY)
    # land masses narrowing the strait
    d.polygon([(x, y), (x + 70, y), (x + 46, y + h), (x, y + h)],
              fill=SAND)
    d.polygon([(x + w, y), (x + w - 64, y), (x + w - 40, y + h),
               (x + w, y + h)], fill=SAND)
    # sea
    d.rectangle([x, y + h - 44, x + w, y + h], fill=DARKSEA)
    d.line([x, y + h - 44, x + w, y + h - 44], fill=(255, 255, 255), width=2)
    # tanker: long hull, 3 cylinder tanks, superstructure, funnel
    hx0, hy = x + 88, y + h - 38
    d.polygon([(hx0, hy), (hx0 + 150, hy), (hx0 + 138, hy + 22),
               (hx0 + 10, hy + 22)], fill=(44, 62, 80))
    d.line([hx0 + 4, hy + 5, hx0 + 146, hy + 5], fill=RED, width=3)
    for i in range(3):
        tx = hx0 + 18 + i * 40
        d.ellipse([tx, hy - 22, tx + 30, hy - 2], fill=(255, 255, 255),
                  outline=GREY)
        d.rectangle([tx, hy - 12, tx + 30, hy - 2], fill=(255, 255, 255))
    d.rectangle([hx0 + 118, hy - 30, hx0 + 142, hy - 2],
                fill=(255, 255, 255))
    d.rectangle([hx0 + 128, hy - 40, hx0 + 138, hy - 30], fill=RED)
    # small flame on deck
    d.polygon([(hx0 + 60, hy - 4), (hx0 + 66, hy - 14), (hx0 + 72, hy - 4)],
              fill=ORANGE)
    # drone above
    dx, dy = x + w - 78, y + 22
    d.ellipse([dx - 5, dy - 3, dx + 5, dy + 3], fill=(44, 62, 80))
    for sx in (-12, 12):
        d.line([dx + sx - 7, dy - 4, dx + sx + 7, dy - 4], fill=GREY,
               width=2)
        d.line([dx + sx, dy - 4, dx, dy], fill=GREY, width=1)
    d.text((x + 12, y + 8), "STRAIT OF HORMUZ", font=f_label,
           fill=NAVY)


def lead3_art(d, x, y, w, h):
    """Warship + sea drone + blast at stern."""
    rrect(d, [x, y, x + w, y + h], 6, fill=SKY)
    d.rectangle([x, y + h - 40, x + w, y + h], fill=DARKSEA)
    d.line([x, y + h - 40, x + w, y + h - 40], fill=(255, 255, 255), width=2)
    # warship hull with pointed bow
    hx0, hy = x + 30, y + h - 34
    d.polygon([(hx0, hy), (hx0 + 190, hy), (hx0 + 176, hy + 20),
               (hx0 + 14, hy + 20), (hx0 + 2, hy + 8)], fill=(93, 109, 126))
    d.line([hx0 + 6, hy + 5, hx0 + 188, hy + 5], fill=(255, 255, 255),
           width=2)
    for i in range(6):
        px = hx0 + 24 + i * 24
        d.ellipse([px, hy + 9, px + 6, hy + 15], fill=(255, 255, 255))
    # bridge tower + mast + funnel
    d.rectangle([hx0 + 96, hy - 26, hx0 + 132, hy], fill=(236, 240, 241))
    d.rectangle([hx0 + 102, hy - 20, hx0 + 126, hy - 12], fill=NAVY)
    d.line([hx0 + 114, hy - 44, hx0 + 114, hy - 26], fill=GREY, width=3)
    d.line([hx0 + 104, hy - 40, hx0 + 124, hy - 40], fill=GREY, width=2)
    d.rectangle([hx0 + 140, hy - 22, hx0 + 152, hy], fill=RED)
    # gun dome + barrel forward
    d.pieslice([hx0 + 44, hy - 14, hx0 + 68, hy + 2], 180, 360, fill=NAVY)
    d.line([hx0 + 56, hy - 8, hx0 + 22, hy - 18], fill=NAVY, width=4)
    # blast + smoke at stern
    bx, by = hx0 + 196, hy - 6
    d.polygon([(bx, by - 16), (bx + 8, by - 4), (bx + 16, by - 12),
               (bx + 12, by + 2), (bx + 20, by + 6), (bx + 6, by + 8),
               (bx, by + 16), (bx - 6, by + 6), (bx - 16, by + 8),
               (bx - 10, by - 2), (bx - 16, by - 10)], fill=ORANGE)
    d.ellipse([bx - 14, by - 30, bx + 2, by - 14], fill=(200, 200, 200))
    d.ellipse([bx - 4, by - 38, bx + 12, by - 22], fill=(220, 220, 220))
    # sea drone bottom right
    sx, sy = x + w - 66, y + h - 26
    d.polygon([(sx, sy), (sx + 34, sy), (sx + 28, sy + 10), (sx + 6, sy + 10)],
              fill=(44, 62, 80))
    d.line([sx + 17, sy, sx + 17, sy - 8], fill=GREY, width=2)
    d.line([sx - 14, sy + 12, sx - 2, sy + 12], fill=(255, 255, 255),
           width=2)
    d.line([sx - 8, sy + 16, sx + 4, sy + 16], fill=(255, 255, 255), width=2)
    d.text((x + 12, y + 8), "BENGHAZI, LIBYA", font=f_label, fill=NAVY)


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    black = (0, 0, 0)

    # 1. masthead navy strip
    d.rectangle([0, 0, W, 28], fill=NAVY)
    d.text((12, 7), "THE WORLD IN ONE DAY", font=f_mast,
           fill=(255, 255, 255))
    rt = "35 STORIES · 7 REGIONS · EVERY ONE DATED MONDAY 23 NOVEMBER 2026"
    d.text((W - 12 - tw(d, rt, f_mast_r), 8), rt, font=f_mast_r,
           fill=(255, 255, 255))
    d.rectangle([0, 28, W, 31], fill=RED)

    # 2. giant serif date title, one full line
    title = "Monday 23 November 2026"
    d.text((12, 36), title, font=f_bigdate, fill=black)

    # 3. red italic sub-headline summing up the 3 leads, centred
    sub = ("Nvidia shares jump 33% as Huang returns  ·  Iran vows to fight "
           "Hormuz blockade  ·  Merkury sunk off Benghazi")
    d.text(((W - tw(d, sub, f_subhead)) / 2, 102), sub, font=f_subhead,
           fill=RED)
    d.line([12, 122, W - 12, 122], fill=black, width=1)

    # 4. number strip: 6 big red numbers with small labels.
    # One uniform size: the largest that fits the widest number in its
    # column, so neighbouring numbers never touch.
    ns_y = 126
    strip_w = (W - 24) // 6
    num_size = 26
    while num_size > 14:
        f_try = F(SERIFB, num_size)
        if max(tw(d, num, f_try) for num, _ in NUMBERS) <= strip_w - 8:
            break
        num_size -= 1
    f_bignum_fit = F(SERIFB, num_size)
    for i, (num, label) in enumerate(NUMBERS):
        cx = 12 + i * strip_w + strip_w // 2
        d.text((cx - tw(d, num, f_bignum_fit) / 2, ns_y), num,
               font=f_bignum_fit, fill=RED)
        d.text((cx - tw(d, label, f_bignum_l) / 2, ns_y + 30), label,
               font=f_bignum_l, fill=GREY)
        if i:
            d.line([12 + i * strip_w, ns_y + 2, 12 + i * strip_w,
                    ns_y + 40], fill=(190, 175, 150), width=1)
    d.line([12, ns_y + 46, W - 12, ns_y + 46], fill=black, width=1)

    # 5. region strip: coloured segments with story counts
    reg_y = 176
    reg_w = [220, 110, 180, 180, 170, 70, 70]
    rx = 12
    for (name, count, colour), wseg in zip(REGIONS, reg_w):
        d.rectangle([rx, reg_y, rx + wseg, reg_y + 18], fill=colour)
        lab = "%s %d" % (name, count)
        d.text((rx + (wseg - tw(d, lab, f_region)) / 2, reg_y + 4), lab,
               font=f_region, fill=(255, 255, 255))
        rx += wseg

    # 6. "THE DAY IN UTC" timeline strip
    tl_y = 198
    d.rectangle([0, tl_y, W, tl_y + 20], fill=NAVY)
    tx = 12
    d.text((tx, tl_y + 5), "THE DAY IN UTC", font=f_timeline_b,
           fill=GOLD)
    tx += tw(d, "THE DAY IN UTC", f_timeline_b) + 14
    for t, ev in TIMELINE:
        d.text((tx, tl_y + 5), t, font=f_timeline_b, fill=(255, 255, 255))
        tx += tw(d, t, f_timeline_b) + 4
        d.text((tx, tl_y + 5), ev, font=f_timeline, fill=(255, 255, 255))
        tx += tw(d, ev, f_timeline) + 10

    # 7. three big LEAD panels with drawn scenes on top
    col_w = 322
    gap = 11
    lead_y = 222
    art_h = 92
    for i, (title, body, attr) in enumerate(LEAD):
        x = 12 + i * (col_w + gap)
        if i == 0:
            lead1_art(d, x, lead_y, col_w, art_h)
        elif i == 1:
            lead2_art(d, x, lead_y, col_w, art_h)
        else:
            lead3_art(d, x, lead_y, col_w, art_h)
        # meta line: "1 · AMERICAS · MARKETS" + REPORTED/CLAIM chip
        loc, chip = LEAD_META[i]
        my = lead_y + art_h + 6
        d.text((x, my), "%d · %s" % (i + 1, loc), font=f_lead_meta,
               fill=NAVY)
        chip_w = tw(d, chip, f_med_chip) + 10
        chip_x = x + col_w - chip_w
        chip_col = GREEN if chip == "REPORTED" else RED
        d.rectangle([chip_x, my - 1, chip_x + chip_w, my + 11],
                    outline=chip_col, width=1)
        d.text((chip_x + 5, my + 1), chip, font=f_med_chip, fill=chip_col)
        # serif bold title, 2 lines
        ty = my + 16
        for ln in wrap(d, title, f_lead_t2, col_w)[:2]:
            d.text((x, ty), ln, font=f_lead_t2, fill=black)
            ty += 20
        # body, up to 4 lines
        by = ty + 2
        for ln in wrap(d, body, f_lead_b, col_w)[:4]:
            d.text((x, by), ln, font=f_lead_b, fill=black)
            by += 13
        d.text((x, lead_y + 212), attr, font=f_attr, fill=GREY)
        if i < 2:
            d.line([x + col_w + 5, lead_y, x + col_w + 5, lead_y + 224],
                   fill=(190, 175, 150), width=1)

    # 8. "THE DAY IN TEN": 10 medium items, 2 rows x 5 columns.
    # Each cell: a drawn mini panel with a red chip on top, location line,
    # bold title, 2-line body, source.
    d.text((12, 450), "THE DAY IN TEN", font=f_section, fill=NAVY)
    sec_r = "THE STORIES THAT MOVED THE WORLD TODAY"
    d.text((W - 12 - tw(d, sec_r, f_section_r), 452), sec_r,
           font=f_section_r, fill=GREY)
    med_y0 = 466
    cell_w = 193
    cell_gap = 8
    cell_h = 126
    for idx, (title, body, attr, key) in enumerate(MEDIUM):
        r, c = divmod(idx, 5)
        x = 12 + c * (cell_w + cell_gap)
        y = med_y0 + r * (cell_h + 8)
        # mini panel with the drawn icon centred inside
        d.rectangle([x, y, x + cell_w, y + 48], fill=(238, 236, 228))
        icon(d, key, x + (cell_w - 48) // 2, y)
        # red chip label overlaid at the panel's top-left corner
        chip = MED_CHIP[idx]
        chip_w = tw(d, chip, f_med_chip) + 10
        d.rectangle([x, y, x + chip_w, y + 13], fill=RED)
        d.text((x + 5, y + 2), chip, font=f_med_chip,
               fill=(255, 255, 255))
        # location line
        d.text((x, y + 51), MED_LOC[idx], font=f_med_loc, fill=NAVY)
        # title, 2 lines
        ty = y + 62
        for ln in wrap(d, title, f_med_t2, cell_w)[:2]:
            d.text((x, ty), ln, font=f_med_t2, fill=black)
            ty += 14
        # body, 2 lines
        by = ty + 1
        for ln in wrap(d, body, f_med_b2, cell_w)[:2]:
            d.text((x, by), ln, font=f_med_b2, fill=black)
            by += 12
        d.text((x, by + 1), attr, font=f_attr, fill=GREY)

    # 9. map (left) + ALSO list (right)
    d.text((12, 730), "WHERE IT HAPPENED", font=f_label, fill=NAVY)
    d.text((404, 730), "ALSO ON MONDAY 23 NOVEMBER - 22 MORE STORIES",
           font=f_label, fill=NAVY)
    band_y = 746

    # ALSO list: 2 columns x 11 rows, each "14 Middle East: text - source"
    also_x0 = 404
    also_col_w = 300
    for j, (num, region, text) in enumerate(ALSO):
        c, r = divmod(j, 11)
        x = also_x0 + c * also_col_w
        y = band_y + r * 13
        d.ellipse([x, y, x + 13, y + 13], fill=NAVY)
        n = str(num)
        d.text((x + 6.5 - tw(d, n, f_badge) / 2, y + 1), n, font=f_badge,
               fill=(255, 255, 255))
        tag = region + ": "
        tx = x + 18
        d.text((tx, y), tag, font=f_also_tag, fill=NAVY)
        rest = fit_one_line(d, text, f_also,
                            also_col_w - 18 - tw(d, tag, f_also_tag) - 4)
        d.text((tx + tw(d, tag, f_also_tag), y), rest, font=f_also,
               fill=black)

    # map
    mx0, my0, mw, mh = 12, band_y, 380, 144
    d.rectangle([mx0, my0, mx0 + mw, my0 + mh], outline=(190, 175, 150),
                width=1)
    d.rectangle([mx0 + 1, my0 + 1, mx0 + mw - 1, my0 + mh - 1],
                fill=(235, 245, 251))

    def proj(lon, lat):
        return (mx0 + (lon + 180) / 360 * mw,
                my0 + (85 - lat) / 145 * mh)

    land = (198, 214, 196)
    for poly in (N_AMERICA, GREENLAND, S_AMERICA, AFRICA, EUROPE, ASIA,
                 AUSTRALIA, UK, JAPAN):
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=land)
    # pins with leader lines, fanned so badges never touch
    anchors = {}
    for num, lon, lat, dx, dy in PINS:
        ax, ay = proj(lon, lat)
        anchors[num] = (ax, ay)
        d.ellipse([ax - 3, ay - 3, ax + 3, ay + 3], fill=RED)
    for num, lon, lat, dx, dy in PINS:
        ax, ay = anchors[num]
        bx, by = ax + dx, ay + dy
        d.line([ax, ay, bx, by], fill=GREY, width=1)
        d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=NAVY,
                  outline=(255, 255, 255), width=1)
        n = str(num)
        d.text((bx - tw(d, n, f_map_n) / 2, by - 5), n, font=f_map_n,
               fill=(255, 255, 255))

    # 11. DATE CHECK, red-bordered, naming what was left out on purpose
    d.rectangle([12, 896, W - 12, 938], outline=RED, width=2)
    d.text((22, 901), "DATE CHECK:", font=f_dc2, fill=RED)
    dc1 = ("All 35 stories on this page happened or were first reported "
           "on Monday, 23 November 2026.")
    d.text((22 + tw(d, "DATE CHECK: ", f_dc2) + 4, 901), dc1, font=f_dc_r,
           fill=black)
    dc2 = ("Left out on purpose - they happened on Sunday 22 November: "
           "COP31 ends without a deal · Democrats take 258 House seats · "
           "Liverpool beat Man Utd 4-0.")
    d.text((22, 917), dc2, font=f_dc_r, fill=GREY)

    # 12. tag legend, sources, certainty, bottom navy strip
    d.text((12, 942),
           "HOW TO READ THE TAGS - REPORTED = carried by the day's wires "
           "· CLAIM = one side's account, labelled as such",
           font=f_foot_b, fill=GREY)
    src = ("Sources: Reuters, AP, BBC, CNN, France 24, Daily Summary, "
           "One Turn, Guardian, Al Jazeera, CNBC, Press TV, Anadolu, "
           "Japan Times, RFI, Hindu BusinessLine, MercoPress.")
    d.text((12, 956), src, font=f_foot, fill=GREY)
    d.text((12, 970),
           "CERTAINTY: All 35 stories checked against the day's wires; "
           "claims are labelled CLAIM, never stated as fact. Scenes are "
           "drawn illustrations, not photographs.",
           font=f_foot_b, fill=GREY)
    d.rectangle([0, 996, W, H], fill=NAVY)
    d.text((12, 1005), "THE WORLD IN ONE DAY", font=f_bot,
           fill=(255, 255, 255))
    rt2 = "MONDAY 23 NOVEMBER 2026  ·  ONE PAGE"
    d.text((W - 12 - tw(d, rt2, f_bot_r), 1006), rt2, font=f_bot_r,
           fill=(255, 255, 255))

    return img


if __name__ == "__main__":
    img = build()
    img.save(OUT, optimize=True)
    print(OUT, img.size, os.path.getsize(OUT), "bytes")
    print("sha256", hashlib.sha256(open(OUT, "rb").read()).hexdigest())
