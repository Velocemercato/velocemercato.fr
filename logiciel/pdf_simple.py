"""Petit générateur PDF sans dépendance (texte simple, A4, police Helvetica).

Suffisant pour des rapports d'atelier lisibles et imprimables. Les caractères
français (é, è, à, ç, €…) passent par l'encodage WinAnsi.
"""
from __future__ import annotations

from pathlib import Path
import textwrap

A4_W, A4_H = 595, 842
MARGIN = 50
LEADING = 14


def _esc(text: str) -> bytes:
    data = text.encode("cp1252", errors="replace")
    return data.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")


def lines_to_pdf(title: str, lines: list[str], path: Path, footer: str = "") -> Path:
    """Écrit un PDF. `lines` : texte brut ; une ligne commençant par '# ' devient un titre."""
    wrapped: list[tuple[str, int, bool]] = []  # (texte, taille, gras)
    wrapped.append((title, 16, True))
    wrapped.append(("", 10, False))
    for line in lines:
        if line.startswith("# "):
            wrapped.append(("", 10, False))
            wrapped.append((line[2:], 12, True))
            continue
        for part in textwrap.wrap(line, 92) or [""]:
            wrapped.append((part, 10, False))

    pages: list[list[tuple[str, int, bool]]] = [[]]
    y = A4_H - MARGIN
    for item in wrapped:
        step = LEADING + (6 if item[1] > 10 else 0)
        if y - step < MARGIN + 20:
            pages.append([])
            y = A4_H - MARGIN
        pages[-1].append(item)
        y -= step

    objects: list[bytes] = []

    def add(obj: bytes) -> int:
        objects.append(obj)
        return len(objects)

    font = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    font_b = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
    pages_id = len(objects) + 1 + 2 * len(pages)  # réservé après pages et contenus
    page_ids = []
    for n, page in enumerate(pages, 1):
        stream = [b"BT"]
        y = A4_H - MARGIN
        for text, size, bold in page:
            step = LEADING + (6 if size > 10 else 0)
            stream.append(b"/%s %d Tf 1 0 0 1 %d %d Tm (%s) Tj" % (b"F2" if bold else b"F1", size, MARGIN, y, _esc(text)))
            y -= step
        foot = f"{footer}   —   page {n}/{len(pages)}" if footer else f"page {n}/{len(pages)}"
        stream.append(b"/F1 8 Tf 1 0 0 1 %d %d Tm (%s) Tj" % (MARGIN, 30, _esc(foot)))
        stream.append(b"ET")
        body = b"\n".join(stream)
        content = add(b"<< /Length %d >>\nstream\n%s\nendstream" % (len(body), body))
        page_ids.append(add(b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %d %d] /Resources << /Font << /F1 %d 0 R /F2 %d 0 R >> >> /Contents %d 0 R >>"
                            % (pages_id, A4_W, A4_H, font, font_b, content)))
    kids = b" ".join(b"%d 0 R" % i for i in page_ids)
    assert add(b"<< /Type /Pages /Kids [%s] /Count %d >>" % (kids, len(page_ids))) == pages_id
    catalog = add(b"<< /Type /Catalog /Pages %d 0 R >>" % pages_id)

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, obj in enumerate(objects, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n%s\nendobj\n" % (i, obj)
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, catalog, xref)
    path = Path(path)
    path.write_bytes(bytes(out))
    return path
