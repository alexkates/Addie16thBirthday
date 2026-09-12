from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing, Group, Rect
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
URL = "https://alexkates.github.io/Addie16thBirthday/"
PAGE = (5 * inch, 7 * inch)

INK = HexColor("#150726")
PINK = HexColor("#ff3d9a")
CREAM = HexColor("#fff4e6")
PURPLE = HexColor("#6b3fa0")


def qr_drawing(size):
    drawing = Drawing(size, size)
    drawing.add(Rect(0, 0, size, size, fillColor=CREAM, strokeColor=None))
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


def draw_insert(path):
    c = canvas.Canvas(str(path), pagesize=PAGE)
    width, height = PAGE
    c.setTitle("Addie's 16th birthday card insert")
    c.setFillColor(CREAM)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    centered(c, "ADDIE", 398, "Helvetica-Bold", 42, PINK, 2)
    centered(c, "The real present wouldn't", 359, "Helvetica", 11.5, PURPLE)
    centered(c, "fit inside this card.", 342, "Helvetica", 11.5, PURPLE)

    qr_size = 150
    qr_x = (width - qr_size) / 2
    qr_y = 159
    renderPDF.draw(qr_drawing(qr_size), c, qr_x, qr_y)

    centered(c, "SCAN FOR YOUR GIFT", 132, "Courier-Bold", 9, PINK, 1.4)
    centered(c, "Love, Aunt Sam + Uncle Alex", 79, "Helvetica-Oblique", 10.5, PURPLE)

    c.showPage()
    c.save()


def main():
    draw_insert(ROOT / "card-insert-cream.pdf")
    save_qr_png(ROOT / "qr.png")


if __name__ == "__main__":
    main()
