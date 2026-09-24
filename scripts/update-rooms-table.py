#!/usr/bin/env python3
"""
Redibuja la tabla de habitaciones (página 2) con los nombres y camas de la web
y reemplaza esa página en cotizacion.pdf.

Uso: .venv/bin/python scripts/update-rooms-table.py
"""
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC_PDF = ROOT / 'cotizacion.full.backup-addr.pdf'
OUT_PDF = ROOT / 'cotizacion.pdf'
TMP_PNG = ROOT / '.rooms-p2-tmp.png'
TMP_JPG = ROOT / '.rooms-p2-tmp.jpg'
DPI = 200
S = DPI / 72

ROOMS = [
    ('Los Farallones', '2 camarotes', 4, 'Externo'),
    ('La Ermita', '2 camarotes', 4, 'Externo'),
    ('La Tertulia', '2 camarotes', 4, 'Interno'),
    ('Bulevar del Río', '1 camarote + 1 cama doble', 4, 'Interno'),
    ('San Antonio', '2 camarotes + 1 cama doble', 6, 'Interno'),
    ('Cristo Rey', '1 camarote', 2, 'Externo'),
    ('Las Tres Cruces', '1 camarote', 2, 'Interno'),
]

C_WHITE = (255, 255, 255)
C_HEAD_BG = (240, 235, 228)
C_BORDER = (226, 219, 209)
C_TEXT = (38, 38, 38)
C_ICON = (120, 110, 95)
C_PILL_BG = (248, 244, 238)
C_PILL_BORDER = (222, 212, 198)

TABLE_X0, TABLE_X1 = 72, 540
TABLE_TOP = 82
HEAD_H = 22
ROW_H = 32
COL_X = {'name': 84, 'beds': 200, 'cap': 362, 'bath': 462}


def px(v):
    return round(v * S)


def font(bold, size_pt):
    name = 'Poppins-Bold.ttf' if bold else 'Poppins-Regular.ttf'
    return ImageFont.truetype(str(ROOT / 'fonts' / name), px(size_pt))


def text_mid(draw, x, cy, text, fnt, fill):
    """Texto centrado verticalmente en cy (pt)."""
    draw.text((px(x), px(cy)), text, font=fnt, fill=fill, anchor='lm')


def bed_icon(draw, x, cy):
    w = px(0.8)
    draw.line([(px(x), px(cy - 3.5)), (px(x), px(cy + 3.5))], fill=C_ICON, width=w)
    draw.line([(px(x), px(cy + 1.5)), (px(x + 10), px(cy + 1.5))], fill=C_ICON, width=w)
    draw.line([(px(x + 10), px(cy - 0.5)), (px(x + 10), px(cy + 3.5))], fill=C_ICON, width=w)
    draw.rounded_rectangle(
        [px(x + 1.5), px(cy - 2.5), px(x + 10), px(cy + 1.5)],
        radius=px(1), outline=C_ICON, width=w,
    )


def people_icon(draw, x, cy):
    w = px(0.7)
    for dx in (0, 3):
        draw.ellipse([px(x + dx), px(cy - 3), px(x + dx + 3), px(cy)], outline=C_ICON, width=w)
        draw.arc([px(x + dx - 1), px(cy + 0.5), px(x + dx + 4), px(cy + 5.5)], 180, 360, fill=C_ICON, width=w)


def draw_table(img):
    d = ImageDraw.Draw(img)
    table_bottom = TABLE_TOP + HEAD_H + ROW_H * len(ROOMS)

    d.rectangle([px(60), px(76), px(552), px(table_bottom + 8)], fill=C_WHITE)

    radius = px(6)
    d.rounded_rectangle(
        [px(TABLE_X0), px(TABLE_TOP), px(TABLE_X1), px(table_bottom)],
        radius=radius, fill=C_WHITE, outline=C_BORDER, width=px(0.75),
    )
    d.rounded_rectangle(
        [px(TABLE_X0), px(TABLE_TOP), px(TABLE_X1), px(TABLE_TOP + HEAD_H)],
        radius=radius, fill=C_HEAD_BG, corners=(True, True, False, False),
    )
    d.rounded_rectangle(
        [px(TABLE_X0), px(TABLE_TOP), px(TABLE_X1), px(table_bottom)],
        radius=radius, outline=C_BORDER, width=px(0.75),
    )

    f_head = font(True, 8.5)
    f_name = font(True, 9)
    f_body = font(False, 9)
    f_pill = font(True, 8)

    head_cy = TABLE_TOP + HEAD_H / 2
    for key, label in (('name', 'Habitación'), ('beds', 'Camas'), ('cap', 'Capacidad'), ('bath', 'Baño')):
        text_mid(d, COL_X[key], head_cy, label, f_head, C_TEXT)

    for i, (name, beds, cap, bath) in enumerate(ROOMS):
        top = TABLE_TOP + HEAD_H + ROW_H * i
        cy = top + ROW_H / 2
        d.line([(px(TABLE_X0), px(top)), (px(TABLE_X1), px(top))], fill=C_BORDER, width=px(0.75))

        text_mid(d, COL_X['name'], cy, name, f_name, C_TEXT)
        bed_icon(d, COL_X['beds'], cy)
        text_mid(d, COL_X['beds'] + 15, cy, beds, f_body, C_TEXT)

        label = f'{cap} personas'
        tw = d.textlength(label, font=f_pill) / S
        pill_w = 7 + 7 + 4 + tw + 7
        d.rounded_rectangle(
            [px(COL_X['cap']), px(cy - 8), px(COL_X['cap'] + pill_w), px(cy + 8)],
            radius=px(3), fill=C_PILL_BG, outline=C_PILL_BORDER, width=px(0.75),
        )
        people_icon(d, COL_X['cap'] + 6, cy)
        text_mid(d, COL_X['cap'] + 18, cy, label, f_pill, C_TEXT)

        text_mid(d, COL_X['bath'], cy, bath, f_body, C_TEXT)


def main():
    subprocess.run(
        ['swift', str(ROOT / 'scripts' / 'render_page.swift'), str(SRC_PDF), '2', str(TMP_PNG), str(S)],
        check=True, cwd=ROOT,
    )
    img = Image.open(TMP_PNG).convert('RGB')
    draw_table(img)
    img.save(TMP_JPG, 'JPEG', quality=92, dpi=(DPI, DPI))
    subprocess.run(
        ['node', str(ROOT / 'scripts' / 'replace-pdf-page.mjs'), str(OUT_PDF), '2', str(TMP_JPG)],
        check=True, cwd=ROOT,
    )
    TMP_PNG.unlink(missing_ok=True)
    TMP_JPG.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
