#!/usr/bin/env python3
"""
Reemplaza la línea de dirección de la firma (página 3) y actualiza cotizacion.pdf.

Uso: .venv/bin/python scripts/update-address.py
"""
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC_PDF = ROOT / 'cotizacion.full.backup-addr.pdf'
OUT_PDF = ROOT / 'cotizacion.pdf'
TMP_PNG = ROOT / '.address-p3-tmp.png'
TMP_JPG = ROOT / '.address-p3-tmp.jpg'
DPI = 200
S = DPI / 72

ADDRESS = 'Calle 9D #42-33 Segundo Piso, Barrio Los Cambulos - Cali'
TEXT_X = 38
BASELINE_Y = 662.7
COVER = (36, 651.5, 300, 666)


def px(v):
    return round(v * S)


def main():
    subprocess.run(
        ['swift', str(ROOT / 'scripts' / 'render_page.swift'), str(SRC_PDF), '3', str(TMP_PNG), str(S)],
        check=True, cwd=ROOT,
    )
    img = Image.open(TMP_PNG).convert('RGB')
    d = ImageDraw.Draw(img)
    d.rectangle([px(v) for v in COVER], fill=(255, 255, 255))
    fnt = ImageFont.truetype(str(ROOT / 'fonts' / 'Poppins-Regular.ttf'), px(10))
    d.text((px(TEXT_X), px(BASELINE_Y)), ADDRESS, font=fnt, fill=(0, 0, 0), anchor='ls')
    img.save(TMP_JPG, 'JPEG', quality=92, dpi=(DPI, DPI))
    subprocess.run(
        ['node', str(ROOT / 'scripts' / 'replace-pdf-page.mjs'), str(OUT_PDF), '3', str(TMP_JPG)],
        check=True, cwd=ROOT,
    )
    TMP_PNG.unlink(missing_ok=True)
    TMP_JPG.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
