from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing, Group, Rect
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
URL = "https://alexkates.github.io/Addie16thBirthday/"
PAGE = (5 * inch, 7 * inch)

INK = HexColor("#150726")
PINK = HexColor("#ff3d9a")
LIME = HexColor("#ccff33")
CREAM = HexColor("#fff4e6")
TAPE = HexColor("#ffe45c")
PURPLE = HexColor("#6b3fa0")


def qr_drawing(size):
    drawing = Drawing(size, size)
    drawing.add(Rect(0, 0, size, size, fillColor=white, strokeColor=None))
    widget = QrCodeWidget(URL)
    x0, y0, x1, y1 = widget.getBounds()
    scale = (size * 0.86) / max(x1 - x0, y1 - y0)
    group = Group(widget)
    group.transform = [scale, 0, 0, scale, size * 0.07, size * 0.07]
    drawing.add(group)
    return drawing


def save_qr_png(path, size=1225):
    widget = QrCodeWidget(URL)
    widget.qr.make()
    matrix = widget.qr.modules
    quiet = 4
    modules = len(matrix) + quiet * 2
    pixel = size // modules
    used = pixel * modules
    offset = (size - used) // 2
    image = Image.new("1", (size, size), 1)
    draw = ImageDraw.Draw(image)
    for row, values in enumerate(matrix):
        for column, filled in enumerate(values):
            if filled:
                x = offset + (column + quiet) * pixel
                y = offset + (row + quiet) * pixel
                draw.rectangle((x, y, x + pixel - 1, y + pixel - 1), fill=0)
    image.save(path)


def centered(c, text, y, font, size, color, tracking=0):
    c.setFillColor(color)
    c.setFont(font, size)
    if tracking:
        t = c.beginText()
        text_width = stringWidth(text, font, size) + tracking * (len(text) - 1)
        t.setTextOrigin((PAGE[0] - text_width) / 2, y)
        t.setCharSpace(tracking)
        t.textLine(text)
        c.drawText(t)
    else:
        c.drawCentredString(PAGE[0] / 2, y, text)


def flower(c, x, y, radius, color):
    c.setFillColor(color)
    for dx, dy in ((0, radius), (radius, 0), (0, -radius), (-radius, 0)):
        c.circle(x + dx, y + dy, radius * 0.62, fill=1, stroke=0)
    c.setFillColor(CREAM)
    c.circle(x, y, radius * 0.42, fill=1, stroke=0)


def striped_frame(c, x, y, width, height):
    c.saveState()
    path = c.beginPath()
    path.rect(x, y, width, height)
    c.clipPath(path, stroke=0)
    colors = (PINK, LIME, CREAM)
    c.setLineWidth(7)
    index = 0
    for offset in range(-int(height), int(width + height), 10):
        c.setStrokeColor(colors[index % len(colors)])
        c.line(x + offset, y, x + offset + height, y + height)
        index += 1
    c.restoreState()
    c.setStrokeColor(INK)
    c.setLineWidth(2)
    c.roundRect(x, y, width, height, 8, fill=0, stroke=1)


def draw_insert(path, dark):
    bg = INK if dark else CREAM
    fg = CREAM if dark else INK
    muted = HexColor("#d8c8ed") if dark else PURPLE
    c = canvas.Canvas(str(path), pagesize=PAGE)
    width, height = PAGE
    c.setFillColor(bg)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    c.setStrokeColor(LIME if dark else PURPLE)
    c.setLineWidth(1.5)
    c.roundRect(18, 18, width - 36, height - 36, 12, fill=0, stroke=1)

    centered(c, "SPECIAL DELIVERY  /  BIRTHDAY NO. 16", height - 49, "Courier-Bold", 8.5, LIME if dark else PURPLE, 1.15)
    centered(c, "ADDIE", height - 118, "Helvetica-Bold", 46, fg, 3)
    centered(c, "this one would not fit", height - 146, "Helvetica-Oblique", 11.5, muted)
    centered(c, "in an envelope.", height - 161, "Helvetica-Oblique", 11.5, muted)

    flower(c, 42, height - 92, 5, PINK)
    flower(c, width - 43, height - 155, 4, LIME)
    flower(c, width - 54, 55, 4, PINK)

    stamp_x, stamp_y = width - 83, height - 85
    c.saveState()
    c.translate(stamp_x, stamp_y)
    c.rotate(7)
    c.setFillColor(PINK)
    c.setStrokeColor(INK)
    c.setLineWidth(2)
    c.circle(0, 0, 26, fill=1, stroke=1)
    c.setFillColor(CREAM)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(0, -5, "16")
    c.setFont("Courier-Bold", 5)
    c.drawCentredString(0, -15, "VIP")
    c.restoreState()

    panel_x, panel_y = 34, 116
    panel_w, panel_h = width - 68, 214
    striped_frame(c, panel_x, panel_y, panel_w, panel_h)
    c.setFillColor(CREAM if dark else INK)
    c.roundRect(panel_x + 7, panel_y + 7, panel_w - 14, panel_h - 14, 5, fill=1, stroke=0)

    qr_size = 128
    qr_x = panel_x + 18
    qr_y = panel_y + 42
    renderPDF.draw(qr_drawing(qr_size), c, qr_x, qr_y)

    copy_color = INK if dark else CREAM
    copy_x = qr_x + qr_size + 13
    c.setFillColor(PINK if dark else LIME)
    c.setFont("Courier-Bold", 10)
    c.drawString(copy_x, panel_y + 164, "SCAN THIS")
    c.setFillColor(copy_color)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(copy_x, panel_y + 139, "YOUR")
    c.drawString(copy_x, panel_y + 124, "PRESENT")
    c.drawString(copy_x, panel_y + 109, "IS WAITING.")
    c.setFont("Helvetica", 9)
    c.drawString(copy_x, panel_y + 80, "phone up.")
    c.drawString(copy_x, panel_y + 66, "sound up.")
    c.drawString(copy_x, panel_y + 52, "no spoilers.")

    c.setFillColor(copy_color)
    c.setFont("Courier", 5.5)
    c.drawCentredString(width / 2, panel_y + 20, "alexkates.github.io/")
    c.drawCentredString(width / 2, panel_y + 12, "Addie16thBirthday")

    centered(c, "LOVE, AUNT SAM + UNCLE ALEX", 79, "Courier-Bold", 12, PINK, 1)
    centered(c, "tap the envelope when you get there.", 57, "Helvetica-Oblique", 10, muted)

    c.showPage()
    c.save()


def main():
    draw_insert(ROOT / "card-insert-cream.pdf", dark=False)
    save_qr_png(ROOT / "qr.png")


if __name__ == "__main__":
    main()
