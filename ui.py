"""Screen artwork for beats 5 and 6.

Both are flat graphics that later get mapped onto 3D: the file manager onto
the laptop screen, the lock screen onto the phone. Drawing them here rather
than in Blender keeps them crisp and editable, and costs no GPU time while
Cycles is busy.

The reference's laptop UI leans on a big image thumbnail. Ours leans on the
numbers instead, because the size drop IS the product - it is what the whole
piece has been building toward since "Files / Too / Big?".
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

F = "/Users/ariga/Library/Fonts/Satoshi-%s.otf"
MARK = "/private/tmp/claude-501/-Users-ariga-Documents/019cd3fd-0ae7-43c6-90b7-f122889b1e47/scratchpad/logo_mark.png"
OUT = "/Users/ariga/Documents/skwizy/renders/ui"

BLUE = (43, 92, 255)
GREEN = (44, 206, 126)


def font(weight, size):
    return ImageFont.truetype(F % weight, size)


def mark(size, tint=None):
    m = Image.open(MARK).convert("RGBA")
    m = m.resize((size, int(size * m.height / m.width)), Image.LANCZOS)
    if tint:
        solid = Image.new("RGBA", m.size, tint + (255,))
        solid.putalpha(m.split()[3])
        return solid
    return m


# ---------------------------------------------------------------- palette
BG       = (9, 9, 11)
PANEL    = (17, 17, 20)
PANEL_IN = (22, 22, 26)
LINE     = (33, 33, 38)
TXT      = (244, 245, 248)
DIM      = (138, 140, 152)
FAINT    = (104, 106, 118)
VIOLET   = (124, 92, 255)
TEAL     = (20, 184, 166)
AMBER    = (249, 141, 48)
RED      = (239, 80, 80)


# ---------------------------------------------------------------- glyphs
# Drawn, not stood in for. Plain squares read as unfinished and tell the
# viewer nothing - a sidebar's icons have to say what their rows mean.
def _ln(d, pts, c, w=2):
    d.line(pts, fill=c, width=w, joint="curve")


def g_dash(d, x, y, s, c):
    d.ellipse([x + s * .06, y + s * .06, x + s * .94, y + s * .94],
              outline=c, width=2)
    d.pieslice([x + s * .06, y + s * .06, x + s * .94, y + s * .94],
               -90, 20, fill=c)


def g_folder(d, x, y, s, c):
    _ln(d, [(x, y + s * .22), (x + s * .38, y + s * .22),
            (x + s * .48, y + s * .36), (x + s, y + s * .36)], c)
    d.rounded_rectangle([x, y + s * .22, x + s, y + s * .92], s * .12,
                        outline=c, width=2)


def g_image(d, x, y, s, c):
    d.rounded_rectangle([x, y + s * .18, x + s, y + s * .9], s * .12,
                        outline=c, width=2)
    d.ellipse([x + s * .18, y + s * .34, x + s * .34, y + s * .5],
              outline=c, width=2)
    _ln(d, [(x + s * .1, y + s * .82), (x + s * .42, y + s * .54),
            (x + s * .66, y + s * .74), (x + s * .8, y + s * .62),
            (x + s, y + s * .8)], c)


def g_video(d, x, y, s, c):
    d.rounded_rectangle([x, y + s * .22, x + s * .7, y + s * .88], s * .12,
                        outline=c, width=2)
    _ln(d, [(x + s * .78, y + s * .38), (x + s, y + s * .26),
            (x + s, y + s * .84), (x + s * .78, y + s * .72)], c)


def g_archive(d, x, y, s, c):
    d.rounded_rectangle([x, y + s * .2, x + s, y + s * .44], s * .08,
                        outline=c, width=2)
    d.rounded_rectangle([x + s * .08, y + s * .44, x + s * .92, y + s * .9],
                        s * .08, outline=c, width=2)
    _ln(d, [(x + s * .4, y + s * .62), (x + s * .6, y + s * .62)], c)


def g_share(d, x, y, s, c):
    r = s * .13
    for cx, cy in ((x + s * .82, y + s * .24), (x + s * .82, y + s * .84),
                   (x + s * .14, y + s * .54)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=2)
    _ln(d, [(x + s * .26, y + s * .46), (x + s * .7, y + s * .3)], c)
    _ln(d, [(x + s * .26, y + s * .62), (x + s * .7, y + s * .78)], c)


def g_compress(d, x, y, s, c):
    """Arrows driven inward onto a centre line - the app's own idea, and the
    logo's. The tips must stop short of the bar or it reads as an asterisk."""
    _ln(d, [(x + s * .5, y + s * .2), (x + s * .5, y + s * .88)], c, 2)
    for sign, edge in ((1, x), (-1, x + s)):
        tip = edge + sign * s * .36
        _ln(d, [(edge + sign * s * .02, y + s * .54), (tip, y + s * .54)], c)
        _ln(d, [(tip - sign * s * .15, y + s * .41), (tip, y + s * .54),
                (tip - sign * s * .15, y + s * .67)], c)


def g_queue(d, x, y, s, c):
    for i, w in enumerate((1.0, .74, .48)):
        _ln(d, [(x + s * .06, y + s * (.28 + i * .24)),
                (x + s * .06 + s * .88 * w, y + s * (.28 + i * .24))], c)


def g_sliders(d, x, y, s, c):
    for fy, kx in ((.28, .66), (.54, .36), (.8, .72)):
        _ln(d, [(x + s * .06, y + s * fy), (x + s * .94, y + s * fy)], c)
        d.ellipse([x + s * kx - s * .1, y + s * fy - s * .1,
                   x + s * kx + s * .1, y + s * fy + s * .1],
                  fill=PANEL, outline=c, width=2)


def g_bolt(d, x, y, s, c):
    d.polygon([(x + s * .58, y + s * .08), (x + s * .2, y + s * .56),
               (x + s * .46, y + s * .56), (x + s * .4, y + s * .94),
               (x + s * .8, y + s * .44), (x + s * .52, y + s * .44)],
              outline=c, width=2)


def g_chart(d, x, y, s, c):
    _ln(d, [(x + s * .08, y + s * .88), (x + s * .08, y + s * .1)], c)
    _ln(d, [(x + s * .08, y + s * .88), (x + s * .94, y + s * .88)], c)
    _ln(d, [(x + s * .22, y + s * .7), (x + s * .44, y + s * .44),
            (x + s * .62, y + s * .58), (x + s * .88, y + s * .24)], c)


def g_clock(d, x, y, s, c):
    d.ellipse([x + s * .06, y + s * .14, x + s * .94, y + s * .94],
              outline=c, width=2)
    _ln(d, [(x + s * .5, y + s * .34), (x + s * .5, y + s * .56),
            (x + s * .68, y + s * .66)], c)


def g_search(d, x, y, s, c):
    d.ellipse([x + s * .08, y + s * .16, x + s * .72, y + s * .8],
              outline=c, width=2)
    _ln(d, [(x + s * .68, y + s * .76), (x + s * .94, y + s * .96)], c)


def g_plus(d, x, y, s, c, w=2):
    _ln(d, [(x + s * .5, y + s * .14), (x + s * .5, y + s * .86)], c, w)
    _ln(d, [(x + s * .14, y + s * .5), (x + s * .86, y + s * .5)], c, w)


def g_db(d, x, y, s, c):
    d.ellipse([x + s * .08, y + s * .1, x + s * .92, y + s * .34],
              outline=c, width=2)
    _ln(d, [(x + s * .08, y + s * .22), (x + s * .08, y + s * .74)], c)
    _ln(d, [(x + s * .92, y + s * .22), (x + s * .92, y + s * .74)], c)
    d.arc([x + s * .08, y + s * .62, x + s * .92, y + s * .86], 0, 180,
          fill=c, width=2)


def card(d, box, r=18, fill=PANEL, line=LINE):
    d.rounded_rectangle(box, r, fill=fill, outline=line, width=2)


# ---------------------------------------------------------------- laptop
def screen(path=OUT + "/screen.png"):
    """A dashboard, not a file list.

    The reference this is built against earns its polish from a few things:
    everything sits in a bordered card, the sidebar is grouped under quiet
    uppercase section labels, numbers come with a coloured delta against last
    month, and there is real chart colour rather than one accent. The content
    is Skwizy's own - what a compression tool would actually report.
    """
    W, H = 1920, 1280
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im, "RGBA")

    SIDE = 420
    d.rectangle([0, 0, SIDE, H], fill=(13, 13, 15))
    d.line([SIDE, 0, SIDE, H], fill=LINE, width=2)

    # ---- sidebar
    im.paste(mark(30), (36, 40), mark(30))
    d.text((80, 42), "Skwizy", font=font("Bold", 27), fill=TXT)
    d.rounded_rectangle([SIDE - 72, 40, SIDE - 36, 70], 8, outline=LINE, width=2)
    _ln(d, [(SIDE - 58, 42), (SIDE - 58, 68)], LINE)

    card(d, [34, 100, SIDE - 34, 156], 13, (22, 22, 26), (38, 38, 44))
    g_search(d, 54, 116, 22, FAINT)
    d.text((90, 128), "Search", font=font("Regular", 21), fill=FAINT, anchor="lm")
    d.rounded_rectangle([SIDE - 76, 112, SIDE - 46, 144], 8, fill=(38, 38, 44))
    d.text((SIDE - 61, 128), "K", font=font("Medium", 17), fill=DIM, anchor="mm")

    y = 182
    d.rounded_rectangle([30, y, SIDE - 30, y + 52], 12, fill=(18, 34, 86))
    g_dash(d, 52, y + 14, 24, BLUE)
    d.text((94, y + 26), "Dashboard", font=font("Bold", 22), fill=BLUE,
           anchor="lm")
    y += 76

    groups = [
        ("FILES", [("All files", g_folder), ("Images", g_image),
                   ("Video", g_video), ("Archives", g_archive)]),
        ("COMPRESS", [("Queue", g_queue), ("Presets", g_sliders),
                      ("Batch jobs", g_compress)]),
        ("TOOLS", [("Automations", g_bolt), ("Analytics", g_chart),
                   ("Shared", g_share)]),
    ]
    for title, items in groups:
        d.text((40, y), title, font=font("Bold", 15), fill=(96, 98, 110))
        y += 34
        for label, gl in items:
            gl(d, 44, y + 4, 23, (156, 158, 172))
            d.text((94, y + 16), label, font=font("Medium", 22),
                   fill=(186, 188, 202), anchor="lm")
            y += 50
        y += 22

    cy = H - 212
    card(d, [30, cy, SIDE - 30, cy + 170], 16, (22, 22, 26), (36, 36, 42))
    g_db(d, 54, cy + 26, 22, GREEN)
    d.text((88, cy + 37), "Saved this month", font=font("Medium", 19),
           fill=DIM, anchor="lm")
    d.text((54, cy + 62), "14.2 GB", font=font("Bold", 40), fill=TXT)
    bx0, bx1, by = 54, SIDE - 54, cy + 124
    d.rounded_rectangle([bx0, by, bx1, by + 10], 5, fill=(44, 44, 54))
    d.rounded_rectangle([bx0, by, bx0 + (bx1 - bx0) * .68, by + 10], 5,
                        fill=GREEN)
    d.text((bx0, by + 22), "68% of your plan reclaimed",
           font=font("Regular", 16), fill=FAINT)

    # ---- top bar
    d.text((SIDE + 54, 48), "Dashboard", font=font("Bold", 26), fill=TXT)
    d.line([SIDE, 110, W, 110], fill=LINE, width=2)

    X = SIDE + 54
    RIGHT = W - 54

    d.text((X, 160), "Welcome back, Aristote!", font=font("Bold", 46), fill=TXT)
    pre = "Today you compressed "
    d.text((X, 232), pre, font=font("Medium", 24), fill=DIM)
    px = X + d.textlength(pre, font=font("Medium", 24))
    for txt, col in ((" 7 files", BLUE), (", saved ", DIM), ("6.9 GB", GREEN)):
        d.text((px, 232), txt, font=font("Bold", 24) if col != DIM
               else font("Medium", 24), fill=col)
        px += d.textlength(txt, font=font("Bold", 24) if col != DIM
                           else font("Medium", 24))

    # ---- KPI row
    kpis = [
        ("Storage Saved", "14.2 GB", "+18.4%", "vs last month", GREEN, BLUE, g_db),
        ("Files Compressed", "1,284", "+12% (137)", "vs last month", GREEN,
         VIOLET, g_compress),
        ("Avg. Reduction", "92.3%", "+3.1%", "vs last month", GREEN, TEAL,
         g_chart),
    ]
    kx, kw, kh, ky = X, (RIGHT - X - 2 * 26) // 3, 200, 292
    for title, value, delta, note, dcol, icol, gl in kpis:
        card(d, [kx, ky, kx + kw, ky + kh])
        d.rounded_rectangle([kx + 26, ky + 26, kx + 64, ky + 64], 10, fill=icol)
        gl(d, kx + 35, ky + 35, 20, (255, 255, 255))
        d.text((kx + 78, ky + 45), title, font=font("Medium", 22), fill=TXT,
               anchor="lm")
        # the inner card has to clear the delta line - at kh 196 the
        # "vs last month" row sat on its bottom border
        card(d, [kx + 20, ky + 86, kx + kw - 20, ky + kh - 18], 13, PANEL_IN,
             (30, 30, 36))
        d.text((kx + 44, ky + 98), value, font=font("Bold", 46), fill=TXT)
        d.text((kx + 44, ky + 152), delta, font=font("Bold", 20), fill=dcol)
        d.text((kx + 44 + d.textlength(delta, font=font("Bold", 20)) + 14,
                ky + 154), note, font=font("Regular", 18), fill=FAINT)
        kx += kw + 26

    # ---- charts
    gy, gh = 520, 440
    dw = 700
    card(d, [X, gy, X + dw, gy + gh])
    g_compress(d, X + 28, gy + 26, 24, DIM)
    d.text((X + 66, gy + 38), "Savings by file type", font=font("Bold", 24),
           fill=TXT, anchor="lm")

    segs = [("Video", 3.2, BLUE), ("Images", 2.1, VIOLET),
            ("Documents", 1.4, TEAL), ("Archives", 0.8, GREEN)]
    total = sum(v for _, v, _ in segs)
    cxy = (X + 46, gy + 92, X + 46 + 236, gy + 92 + 236)
    ang = -90
    for _, v, col in segs:
        sweep = 360 * v / total
        d.arc(cxy, ang + 2, ang + sweep - 2, fill=col, width=26)
        ang += sweep
    ccx, ccy = (cxy[0] + cxy[2]) / 2, (cxy[1] + cxy[3]) / 2
    d.text((ccx, ccy - 16), "7.5 GB", font=font("Bold", 42), fill=TXT,
           anchor="mm")
    d.text((ccx, ccy + 26), "total saved", font=font("Regular", 19), fill=FAINT,
           anchor="mm")

    ly = gy + 104
    for label, v, col in segs:
        d.rounded_rectangle([X + 332, ly, X + 338, ly + 28], 3, fill=col)
        d.text((X + 358, ly + 14), label, font=font("Medium", 23), fill=TXT,
               anchor="lm")
        d.text((X + dw - 32, ly + 14), f"{v:.1f} GB", font=font("Bold", 23),
               fill=DIM, anchor="rm")
        ly += 56

    card(d, [X + 332, gy + gh - 86, X + dw - 28, gy + gh - 26], 13, PANEL_IN,
         (30, 30, 36))
    d.text(((X + 332 + X + dw - 28) / 2, gy + gh - 56), "More details",
           font=font("Medium", 22), fill=TXT, anchor="mm")

    # ---- flow panel
    fx = X + dw + 26
    card(d, [fx, gy, RIGHT, gy + gh])
    g_chart(d, fx + 28, gy + 26, 24, DIM)
    d.text((fx + 66, gy + 38), "Data reduced", font=font("Bold", 24), fill=TXT,
           anchor="lm")
    d.text((fx + 28, gy + 84), "6.9 TB", font=font("Bold", 52), fill=TXT)
    d.text((fx + 28, gy + 150), "Total reduced (last 6 months)",
           font=font("Regular", 20), fill=FAINT)

    card(d, [fx + 24, gy + 196, RIGHT - 24, gy + gh - 28], 14, PANEL_IN,
         (30, 30, 36))
    d.text((fx + 50, gy + 222), "Best performing month", font=font("Bold", 23),
           fill=TXT)
    for i, line in enumerate(("March reduced the most data in the",
                              "last 6 months, at 1.6 TB")):
        d.text((fx + 50, gy + 262 + i * 30), line, font=font("Regular", 20),
               fill=DIM)
    bw, bx = 10, fx + 50
    import math
    for i in range(34):
        hgt = 56 * (0.42 + 0.58 * abs(math.sin(i * 0.46)))
        on = i < 24
        d.rounded_rectangle([bx, gy + gh - 70 - hgt, bx + bw, gy + gh - 70], 3,
                            fill=BLUE if on else (48, 48, 56))
        bx += bw + 6

    # ---- table
    # The panel runs off the bottom of the viewport rather than closing with a
    # border, which is what the reference does: a dashboard's last table is
    # always mid-scroll, and a tidy bottom edge would read as an empty page.
    ty = 962
    card(d, [X, ty, RIGHT, H + 60])
    g_folder(d, X + 28, ty + 26, 24, DIM)
    d.text((X + 66, ty + 38), "Recent files", font=font("Bold", 24), fill=TXT,
           anchor="lm")
    card(d, [RIGHT - 230, ty + 20, RIGHT - 24, ty + 62], 11, PANEL_IN,
         (34, 34, 40))
    g_search(d, RIGHT - 210, ty + 32, 18, FAINT)
    d.text((RIGHT - 180, ty + 41), "Search files", font=font("Regular", 18),
           fill=FAINT, anchor="lm")

    cols = (X + 92, X + 980, X + 1130, X + 1270)
    hdr = ty + 92
    for label, cx, an in (("Name", cols[0], "la"), ("Before", cols[1], "ra"),
                          ("After", cols[2], "ra"), ("Saved", cols[3], "ma")):
        d.text((cx, hdr), label, font=font("Medium", 18), fill=FAINT, anchor=an)
    d.line([X + 28, hdr + 34, RIGHT - 28, hdr + 34], fill=LINE, width=2)

    TYPES = {"zip": BLUE, "mov": (120, 200, 255), "psd": VIOLET,
             "pdf": (255, 112, 96), "mp4": TEAL}
    rows = [("Project_Final.zip", "2.4 GB", "180 MB", "92%"),
            ("Sizzle_master.mov", "1.8 GB", "142 MB", "92%"),
            ("Cover_art.psd", "412 MB", "31 MB", "92%")]
    ry = hdr + 44
    for name, before, after, saved in rows:
        ext = name.rsplit(".", 1)[-1]
        col = TYPES.get(ext, DIM)
        d.rounded_rectangle([X + 28, ry + 10, X + 52, ry + 34], 6,
                            outline=(62, 62, 72), width=2)
        d.rounded_rectangle([cols[0] - 20, ry + 4, cols[0] + 24, ry + 48], 11,
                            fill=(col[0] // 5, col[1] // 5, col[2] // 5))
        d.text((cols[0] + 2, ry + 26), ext.upper(), font=font("Bold", 14),
               fill=col, anchor="mm")
        d.text((cols[0] + 44, ry + 26), name, font=font("Medium", 23), fill=TXT,
               anchor="lm")
        d.text((cols[1], ry + 26), before, font=font("Medium", 22), fill=FAINT,
               anchor="rm")
        d.text((cols[2], ry + 26), after, font=font("Bold", 22), fill=TXT,
               anchor="rm")
        bw2 = d.textlength(saved, font=font("Bold", 19)) + 30
        d.rounded_rectangle([cols[3] - bw2 / 2, ry + 7, cols[3] + bw2 / 2,
                             ry + 45], 19, fill=(16, 54, 38))
        d.text((cols[3], ry + 26), saved, font=font("Bold", 19), fill=GREEN,
               anchor="mm")
        ry += 62

    im.save(path)
    return path


# ---------------------------------------------------------------- phone
def phone(path=OUT + "/phone.png"):
    W, H = 1179, 2556
    im = Image.new("RGB", (W, H), (10, 14, 44))
    d = ImageDraw.Draw(im, "RGBA")

    # wallpaper: soft blobs, blurred, in the piece's own palette
    for box, col in (((-300, 900, 820, 2100), (38, 86, 230)),
                     ((420, 1500, 1500, 2700), (26, 170, 150)),
                     ((120, 260, 1100, 1250), (22, 40, 120))):
        d.ellipse(box, fill=col)
    im = im.filter(ImageFilter.GaussianBlur(190))
    d = ImageDraw.Draw(im, "RGBA")

    d.text((96, 150), "9:41", font=font("Bold", 50), fill=(255, 255, 255))
    for i, w in enumerate((8, 14, 20, 26)):
        d.rounded_rectangle([900 + i * 22, 196 - w, 912 + i * 22, 196], 3,
                            fill=(255, 255, 255, 230))
    d.rounded_rectangle([1010, 170, 1086, 196], 7,
                        outline=(255, 255, 255, 200), width=3)
    d.rounded_rectangle([1015, 175, 1070, 191], 4, fill=(255, 255, 255, 230))

    # notification: real glass, not a flat panel - blur what is behind it
    nx, ny, nw, nh = 64, 470, W - 128, 300
    card = im.crop((nx, ny, nx + nw, ny + nh)).filter(
        ImageFilter.GaussianBlur(26))
    veil = Image.new("RGBA", (nw, nh), (255, 255, 255, 46))
    card = Image.alpha_composite(card.convert("RGBA"), veil)
    rounded = Image.new("L", (nw, nh), 0)
    ImageDraw.Draw(rounded).rounded_rectangle([0, 0, nw, nh], 58, fill=255)
    im.paste(card, (nx, ny), rounded)
    d.rounded_rectangle([nx, ny, nx + nw, ny + nh], 58,
                        outline=(255, 255, 255, 58), width=2)

    ix, iy, isz = nx + 44, ny + 48, 124
    d.rounded_rectangle([ix, iy, ix + isz, iy + isz], 30,
                        fill=(255, 255, 255))
    m = mark(84, BLUE)
    im.paste(m, (ix + 20, iy + 22), m)

    d.text((ix + isz + 36, iy + 6), "Skwizy", font=font("Bold", 42),
           fill=(255, 255, 255))
    d.text((nx + nw - 44, iy + 12), "now", font=font("Medium", 32),
           fill=(226, 230, 245), anchor="ra")
    for i, line in enumerate(("Your files are compressed and",
                              "ready to share")):
        d.text((ix + isz + 36, iy + 68 + i * 46), line,
               font=font("Regular", 36), fill=(244, 246, 255))

    im.save(path)
    return path


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    print("SCREEN", screen())
    print("PHONE", phone())
