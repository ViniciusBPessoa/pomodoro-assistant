"""
Gera assets/icon.png (256px) e assets/icon.ico (multi-size) para o Pomodoro Assistant.
Execução: uv run python tools/make_icon.py
"""

import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QBrush, QColor, QImage, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QApplication

ASSETS = Path(__file__).resolve().parent.parent / "assets"
SIZE   = 256
BG     = "#1C1C1E"
GREEN  = "#4CAF50"


def _render(size: int) -> QImage:
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)

    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    m  = size * 0.115          # margem (~30px em 256)
    cx = size / 2.0
    cy = size / 2.0

    # --- Fundo arredondado ---
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor(BG)))
    p.drawRoundedRect(QRectF(0, 0, size, size), size * 0.18, size * 0.18)

    # --- Vértices da ampulheta ---
    tl = QPointF(m,          m)
    tr = QPointF(size - m,   m)
    bl = QPointF(m,          size - m)
    br = QPointF(size - m,   size - m)
    ct = QPointF(cx,         cy)

    # --- Fill semi-transparente (dois triângulos) ---
    fill = QColor(GREEN)
    fill.setAlpha(50)
    p.setBrush(QBrush(fill))
    p.setPen(Qt.PenStyle.NoPen)

    top_path = QPainterPath()
    top_path.moveTo(tl); top_path.lineTo(tr); top_path.lineTo(ct); top_path.closeSubpath()
    p.drawPath(top_path)

    bot_path = QPainterPath()
    bot_path.moveTo(bl); bot_path.lineTo(br); bot_path.lineTo(ct); bot_path.closeSubpath()
    p.drawPath(bot_path)

    # --- Contorno ---
    pen = QPen(QColor(GREEN))
    pen.setWidthF(size * 0.030)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # TL→TR (barra topo) → CT → BR→BL (barra base) → CT → fecha (TL)
    outline = QPainterPath()
    outline.moveTo(tl)
    outline.lineTo(tr)
    outline.lineTo(ct)
    outline.lineTo(br)
    outline.lineTo(bl)
    outline.lineTo(ct)
    outline.closeSubpath()
    p.drawPath(outline)

    # Pequena bola no centro (waist) para reforçar o ∞
    dot_r = size * 0.038
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor(GREEN)))
    p.drawEllipse(QPointF(cx, cy), dot_r, dot_r)

    p.end()
    return img


def main() -> None:
    app = QApplication(sys.argv)  # necessário para QPainter

    ASSETS.mkdir(exist_ok=True)
    png_path = ASSETS / "icon.png"
    ico_path = ASSETS / "icon.ico"

    # Salva PNG 256×256
    img = _render(SIZE)
    img.save(str(png_path), "PNG")
    print(f"PNG gerado: {png_path}")

    # Converte para ICO multi-size via Pillow
    from PIL import Image as PILImage
    pil_256 = PILImage.open(png_path).convert("RGBA")
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    pil_256.save(ico_path, format="ICO", sizes=ico_sizes)
    print(f"ICO gerado:  {ico_path}")

    app.quit()


if __name__ == "__main__":
    main()
