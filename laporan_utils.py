"""Pembuat laporan PDF sederhana (reportlab) untuk ketiga lab."""
import textwrap
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)


class Laporan:
    def __init__(self, path, judul, subjudul=""):
        st = getSampleStyleSheet()
        self.s = {
            "judul": ParagraphStyle("j", parent=st["Title"], fontSize=19, spaceAfter=4),
            "sub": ParagraphStyle("sj", parent=st["BodyText"], alignment=1, textColor=colors.grey, spaceAfter=14),
            "h1": ParagraphStyle("h1", parent=st["Heading1"], fontSize=14, spaceBefore=12, spaceAfter=6),
            "h2": ParagraphStyle("h2", parent=st["Heading2"], fontSize=11.5, spaceBefore=9, spaceAfter=4),
            "p": ParagraphStyle("p", parent=st["BodyText"], fontSize=10, leading=14, spaceAfter=5),
            "sel": ParagraphStyle("sel", parent=st["BodyText"], fontSize=8.5, leading=10.5),
            "selb": ParagraphStyle("selb", parent=st["BodyText"], fontSize=8.5, leading=10.5, fontName="Helvetica-Bold"),
            "kode": ParagraphStyle("k", fontName="Courier", fontSize=7.2, leading=8.6,
                                   backColor=colors.whitesmoke, borderPadding=4),
            "cap": ParagraphStyle("cap", parent=st["BodyText"], fontSize=8.5, textColor=colors.grey, spaceAfter=8),
        }
        self.doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                                     topMargin=2 * cm, bottomMargin=2 * cm, title=judul)
        self.c = [Paragraph(escape(judul), self.s["judul"])]
        if subjudul:
            self.c.append(Paragraph(escape(subjudul), self.s["sub"]))

    def h1(self, t): self.c.append(Paragraph(escape(t), self.s["h1"]))
    def h2(self, t): self.c.append(Paragraph(escape(t), self.s["h2"]))
    def p(self, t): self.c.append(Paragraph(escape(t), self.s["p"]))
    def spasi(self, h=6): self.c.append(Spacer(1, h))
    def halaman_baru(self): self.c.append(PageBreak())

    def cap(self, t): self.c.append(Paragraph(escape(t), self.s["cap"]))

    def kode(self, teks, lebar=105):
        baris = []
        for b in teks.expandtabs(4).split("\n"):
            baris += textwrap.wrap(b, lebar, subsequent_indent="    ", drop_whitespace=False) or [""]
        self.c.append(Preformatted("\n".join(baris), self.s["kode"]))

    def teks_chunk(self, teks, maks=700):
        t = teks if len(teks) <= maks else teks[:maks] + " ..."
        self.c.append(Preformatted(t, self.s["kode"], maxLineLength=100, newLineChars="↵"))
        self.c.append(Spacer(1, 4))

    def tabel(self, data, lebar=None, header=True):
        d = [[Paragraph(escape(str(x)), self.s["selb"] if (header and i == 0) else self.s["sel"])
              for x in baris] for i, baris in enumerate(data)]
        tb = Table(d, colWidths=lebar, repeatRows=1 if header else 0, hAlign="LEFT")
        gaya = [("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP")]
        if header:
            gaya.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6e6e6")))
        tb.setStyle(TableStyle(gaya))
        self.c.append(tb)
        self.c.append(Spacer(1, 6))

    def gambar(self, path, lebar_cm=15):
        from PIL import Image as PI
        w, h = PI.open(path).size
        self.c.append(Image(path, width=lebar_cm * cm, height=lebar_cm * cm * h / w))

    def simpan(self):
        def kaki(canvas, doc):
            canvas.saveState()
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(colors.grey)
            canvas.drawCentredString(A4[0] / 2, 1.1 * cm, f"Halaman {doc.page}")
            canvas.restoreState()
        self.doc.build(self.c, onFirstPage=kaki, onLaterPages=kaki)
