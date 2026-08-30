"""Build the judge-submission README PDF from the repository README.

The renderer supports the small Markdown subset used by README.md so the
project keeps one human-maintainable source of submission truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "README.md"
OUTPUT = ROOT / "output" / "pdf" / "SilentSignal_Judge_Submission_README.pdf"

PAGE_WIDTH, PAGE_HEIGHT = A4
NAVY = HexColor("#101B35")
NAVY_2 = HexColor("#182A55")
PURPLE = HexColor("#6756D9")
PURPLE_SOFT = HexColor("#F0EEFF")
AQUA = HexColor("#5CE5C5")
INK = HexColor("#25324A")
MUTED = HexColor("#66738A")
LINE = HexColor("#DDE2EC")
PALE = HexColor("#F6F8FC")
WHITE = colors.white


def register_fonts() -> None:
    """Register a Unicode-capable Windows font family for the submission."""

    pdfmetrics.registerFont(TTFont("Segoe", r"C:\Windows\Fonts\segoeui.ttf"))
    pdfmetrics.registerFont(TTFont("Segoe-Semibold", r"C:\Windows\Fonts\seguisb.ttf"))
    pdfmetrics.registerFont(TTFont("Segoe-Bold", r"C:\Windows\Fonts\segoeuib.ttf"))
    pdfmetrics.registerFont(TTFont("Consolas", r"C:\Windows\Fonts\consola.ttf"))
    pdfmetrics.registerFontFamily(
        "Segoe",
        normal="Segoe",
        bold="Segoe-Bold",
        italic="Segoe",
        boldItalic="Segoe-Bold",
    )


class SectionRule(Flowable):
    """Short accent rule placed below major section headings."""

    def __init__(self, width: float = 21 * mm) -> None:
        super().__init__()
        self.width = width
        self.height = 3 * mm

    def draw(self) -> None:
        self.canv.setFillColor(AQUA)
        self.canv.roundRect(0, 1.1 * mm, self.width, 1.2 * mm, 0.6 * mm, fill=1, stroke=0)


class JudgeDocument(BaseDocTemplate):
    """Document template with bookmarks and a generated table of contents."""

    def __init__(self, filename: str, **kwargs) -> None:
        super().__init__(filename, **kwargs)
        self._bookmark_index = 0

    def beforeDocument(self) -> None:
        self._bookmark_index = 0

    def afterFlowable(self, flowable: Flowable) -> None:
        if not isinstance(flowable, Paragraph):
            return
        level = getattr(flowable, "toc_level", None)
        if level is None:
            return
        self._bookmark_index += 1
        key = f"section-{self._bookmark_index}"
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(flowable.getPlainText(), key, level=level, closed=False)
        self.notify("TOCEntry", (level, flowable.getPlainText(), self.page, key))


def draw_cover(canvas, doc) -> None:
    """Draw the high-impact cover background."""

    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    canvas.setFillColor(NAVY_2)
    canvas.circle(PAGE_WIDTH + 8 * mm, PAGE_HEIGHT - 13 * mm, 66 * mm, fill=1, stroke=0)
    canvas.setFillColor(PURPLE)
    canvas.circle(PAGE_WIDTH - 12 * mm, 10 * mm, 52 * mm, fill=1, stroke=0)
    canvas.setFillColor(AQUA)
    canvas.circle(24 * mm, PAGE_HEIGHT - 25 * mm, 3.5 * mm, fill=1, stroke=0)
    canvas.setStrokeColor(HexColor("#33446B"))
    canvas.setLineWidth(0.7)
    canvas.line(19 * mm, 18 * mm, PAGE_WIDTH - 19 * mm, 18 * mm)
    canvas.restoreState()


def draw_content_page(canvas, doc) -> None:
    """Draw consistent running furniture on content pages."""

    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.55)
    canvas.line(18 * mm, PAGE_HEIGHT - 16 * mm, PAGE_WIDTH - 18 * mm, PAGE_HEIGHT - 16 * mm)
    canvas.setFont("Segoe-Semibold", 7.4)
    canvas.setFillColor(PURPLE)
    canvas.drawString(18 * mm, PAGE_HEIGHT - 12.5 * mm, "SILENTSIGNAL")
    canvas.setFont("Segoe", 7.4)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(PAGE_WIDTH - 18 * mm, PAGE_HEIGHT - 12.5 * mm, "JUDGE SUBMISSION README")
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 14 * mm, PAGE_WIDTH - 18 * mm, 14 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Segoe", 7.2)
    canvas.drawString(18 * mm, 9.5 * mm, "BusinessIntelligence.ai - Evidence-first banking risk operations")
    canvas.drawRightString(PAGE_WIDTH - 18 * mm, 9.5 * mm, f"Page {doc.page}")
    canvas.restoreState()


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "cover_kicker": ParagraphStyle(
            "CoverKicker", parent=base["Normal"], fontName="Segoe-Semibold", fontSize=9,
            leading=12, textColor=AQUA, spaceAfter=7,
        ),
        "cover_title": ParagraphStyle(
            "CoverTitle", parent=base["Title"], fontName="Segoe-Bold", fontSize=35,
            leading=38, textColor=WHITE, spaceAfter=8,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle", parent=base["Normal"], fontName="Segoe", fontSize=14.5,
            leading=20, textColor=HexColor("#D7DFF0"), spaceAfter=23,
        ),
        "cover_body": ParagraphStyle(
            "CoverBody", parent=base["Normal"], fontName="Segoe", fontSize=9.4,
            leading=14.2, textColor=HexColor("#C5CEE3"), spaceAfter=8,
        ),
        "cover_badge": ParagraphStyle(
            "CoverBadge", parent=base["Normal"], fontName="Segoe-Semibold", fontSize=8.2,
            leading=11, textColor=WHITE, alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontName="Segoe-Bold", fontSize=18,
            leading=22, textColor=NAVY, spaceBefore=8, spaceAfter=4, keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="Segoe-Bold", fontSize=14,
            leading=18, textColor=NAVY, spaceBefore=12, spaceAfter=6, keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName="Segoe", fontSize=8.9,
            leading=13.6, textColor=INK, spaceAfter=6, alignment=TA_LEFT,
        ),
        "small": ParagraphStyle(
            "Small", parent=base["BodyText"], fontName="Segoe", fontSize=7.5,
            leading=10.6, textColor=MUTED,
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=base["BodyText"], fontName="Segoe", fontSize=8.65,
            leading=12.9, textColor=INK, leftIndent=4, firstLineIndent=0, spaceAfter=2.2,
        ),
        "quote": ParagraphStyle(
            "Quote", parent=base["BodyText"], fontName="Segoe-Semibold", fontSize=9.3,
            leading=14, textColor=NAVY, leftIndent=10, rightIndent=8, spaceBefore=5,
            spaceAfter=9, borderColor=PURPLE, borderWidth=1.8, borderPadding=8,
            backColor=PURPLE_SOFT,
        ),
        "code": ParagraphStyle(
            "Code", parent=base["Code"], fontName="Consolas", fontSize=7.1,
            leading=10.1, textColor=NAVY, backColor=PALE,
            borderPadding=8, leftIndent=0, rightIndent=0, spaceBefore=4, spaceAfter=8,
        ),
        "toc_title": ParagraphStyle(
            "TocTitle", parent=base["Heading1"], fontName="Segoe-Bold", fontSize=19,
            leading=23, textColor=NAVY, spaceAfter=5,
        ),
        "toc1": ParagraphStyle(
            "TOC1", parent=base["Normal"], fontName="Segoe-Semibold", fontSize=9,
            leading=13, leftIndent=0, firstLineIndent=0, textColor=INK, spaceBefore=3,
        ),
        "toc2": ParagraphStyle(
            "TOC2", parent=base["Normal"], fontName="Segoe", fontSize=8.1,
            leading=11, leftIndent=10, firstLineIndent=0, textColor=MUTED, spaceBefore=1,
        ),
    }


def inline_markup(text: str) -> str:
    """Convert the small inline Markdown subset to ReportLab markup."""

    text = escape(text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<link href="\2" color="#6756D9"><u>\1</u></link>', text)
    text = re.sub(r"`([^`]+)`", r'<font name="Consolas" color="#4B3FB2">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    return text


def make_table(rows: list[list[str]], available_width: float, styles: dict[str, ParagraphStyle]) -> Table:
    """Create a readable table with widths based on content density."""

    columns = max(len(row) for row in rows)
    normalized = [row + [""] * (columns - len(row)) for row in rows]
    weights = []
    for index in range(columns):
        longest = max(len(row[index]) for row in normalized)
        weights.append(min(max(longest, 16), 42))
    total_weight = sum(weights)
    widths = [available_width * weight / total_weight for weight in weights]
    cell_style = ParagraphStyle(
        "TableCell", parent=styles["small"], fontSize=6.9, leading=9.1, textColor=INK,
    )
    head_style = ParagraphStyle(
        "TableHead", parent=cell_style, fontName="Segoe-Semibold", textColor=WHITE,
    )
    data = []
    for row_index, row in enumerate(normalized):
        style = head_style if row_index == 0 else cell_style
        data.append([Paragraph(inline_markup(cell), style) for cell in row])
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY_2),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.35, LINE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
            ]
        )
    )
    return table


@dataclass
class ParsedBlock:
    kind: str
    content: object


def parse_markdown(source: str) -> list[ParsedBlock]:
    """Parse the README subset into block objects."""

    lines = source.splitlines()
    blocks: list[ParsedBlock] = []
    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        if not line:
            index += 1
            continue
        if line.startswith("```"):
            language = line[3:].strip()
            index += 1
            code_lines = []
            while index < len(lines) and not lines[index].startswith("```"):
                code_lines.append(lines[index].rstrip())
                index += 1
            index += 1
            blocks.append(ParsedBlock("code", (language, "\n".join(code_lines))))
            continue
        if line.startswith("|"):
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            parsed = [[cell.strip() for cell in row.strip("|").split("|")] for row in table_lines]
            if len(parsed) >= 2 and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in parsed[1]):
                parsed.pop(1)
            blocks.append(ParsedBlock("table", parsed))
            continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            blocks.append(ParsedBlock(f"h{len(heading.group(1))}", heading.group(2)))
            index += 1
            continue
        if line.startswith("> "):
            quote_lines = []
            while index < len(lines) and lines[index].startswith("> "):
                quote_lines.append(lines[index][2:].strip())
                index += 1
            blocks.append(ParsedBlock("quote", " ".join(quote_lines)))
            continue
        if re.match(r"^-\s+", line):
            items = []
            while index < len(lines) and re.match(r"^-\s+", lines[index].strip()):
                items.append(re.sub(r"^-\s+", "", lines[index].strip()))
                index += 1
            blocks.append(ParsedBlock("bullets", items))
            continue
        if re.match(r"^\d+\.\s+", line):
            items = []
            while index < len(lines) and re.match(r"^\d+\.\s+", lines[index].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[index].strip()))
                index += 1
            blocks.append(ParsedBlock("numbers", items))
            continue
        paragraph_lines = [line]
        index += 1
        while index < len(lines):
            candidate = lines[index].rstrip()
            if not candidate or candidate.startswith(("#", "```", "|", "> ")):
                break
            if re.match(r"^-\s+|^\d+\.\s+", candidate.strip()):
                break
            paragraph_lines.append(candidate.strip())
            index += 1
        blocks.append(ParsedBlock("paragraph", " ".join(paragraph_lines)))
    return blocks


def build_story(styles: dict[str, ParagraphStyle]) -> list[Flowable]:
    """Build the cover, TOC, and parsed README content."""

    story: list[Flowable] = [
        Spacer(1, 31 * mm),
        Paragraph("ACCENTURE BUSINESSINTELLIGENCE.AI INNOVATION CHALLENGE", styles["cover_kicker"]),
        Paragraph("SilentSignal", styles["cover_title"]),
        Paragraph("Evidence-first KPI intelligence to governed human action", styles["cover_subtitle"]),
        Paragraph(
            "A judge-ready technical and business README for a synthetic banking risk operations prototype. "
            "The system connects five governed KPIs, transparent relationship evidence, honest uncertainty, "
            "role-based security, and auditable actions in one Streamlit workspace.",
            styles["cover_body"],
        ),
        Spacer(1, 9 * mm),
        Table(
            [[
                Paragraph("3 governed sources", styles["cover_badge"]),
                Paragraph("5 connected KPIs", styles["cover_badge"]),
                Paragraph("5 acceptance scenarios", styles["cover_badge"]),
            ]],
            colWidths=[50 * mm, 50 * mm, 50 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), HexColor("#24365E")),
                    ("BOX", (0, 0), (-1, -1), 0.7, HexColor("#52658F")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.7, HexColor("#52658F")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ]
            ),
        ),
        Spacer(1, 55 * mm),
        Paragraph("Version 1.0.0  |  Synthetic data only  |  Deterministic analytics  |  Optional LLM narrative", styles["cover_body"]),
        Paragraph("Repository: github.com/tushantrao141-arch/Buisness_Intelligence.ai", styles["cover_body"]),
        NextPageTemplate("Content"),
        PageBreak(),
        Paragraph("Document map", styles["toc_title"]),
        SectionRule(),
        Spacer(1, 3 * mm),
    ]
    toc = TableOfContents()
    toc.levelStyles = [styles["toc1"], styles["toc2"]]
    story.extend([toc, PageBreak()])

    blocks = parse_markdown(SOURCE.read_text(encoding="utf-8-sig"))
    available_width = PAGE_WIDTH - 36 * mm
    for block in blocks:
        if block.kind == "h1":
            continue
        if block.kind == "h2":
            paragraph = Paragraph(inline_markup(str(block.content)), styles["h1"])
            paragraph.toc_level = 0
            story.extend([paragraph, SectionRule(), Spacer(1, 1.5 * mm)])
        elif block.kind == "h3":
            paragraph = Paragraph(inline_markup(str(block.content)), styles["h2"])
            paragraph.toc_level = 1
            story.extend([paragraph, Spacer(1, 1.2 * mm)])
        elif block.kind == "paragraph":
            story.append(Paragraph(inline_markup(str(block.content)), styles["body"]))
        elif block.kind == "quote":
            story.append(Paragraph(inline_markup(str(block.content)), styles["quote"]))
        elif block.kind == "code":
            _, code_text = block.content
            story.append(Preformatted(code_text, styles["code"], maxLineLength=95))
        elif block.kind == "table":
            story.extend([make_table(block.content, available_width, styles), Spacer(1, 3 * mm)])
        elif block.kind in {"bullets", "numbers"}:
            items = [
                ListItem(Paragraph(inline_markup(item), styles["bullet"]), leftIndent=7)
                for item in block.content
            ]
            list_options = {
                "bulletType": "1" if block.kind == "numbers" else "bullet",
                "leftIndent": 14,
                "bulletFontName": "Segoe-Semibold",
                "bulletFontSize": 7.5,
                "bulletColor": PURPLE,
                "spaceAfter": 6,
            }
            if block.kind == "numbers":
                list_options["start"] = "1"
            story.append(ListFlowable(items, **list_options))
    return story


def build_pdf() -> Path:
    """Generate the final submission PDF and return its path."""

    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    content_frame = Frame(
        18 * mm,
        17 * mm,
        PAGE_WIDTH - 36 * mm,
        PAGE_HEIGHT - 36 * mm,
        leftPadding=0,
        rightPadding=0,
        topPadding=3 * mm,
        bottomPadding=2 * mm,
        id="content-frame",
    )
    cover_frame = Frame(
        20 * mm,
        20 * mm,
        PAGE_WIDTH - 40 * mm,
        PAGE_HEIGHT - 40 * mm,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
        id="cover-frame",
    )
    document = JudgeDocument(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=19 * mm,
        bottomMargin=18 * mm,
        title="SilentSignal Judge Submission README",
        author="SilentSignal Team",
        subject="BusinessIntelligence.ai banking risk operations prototype",
    )
    document.addPageTemplates(
        [
            PageTemplate(id="Cover", frames=[cover_frame], onPage=draw_cover),
            PageTemplate(id="Content", frames=[content_frame], onPage=draw_content_page),
        ]
    )
    document.multiBuild(build_story(make_styles()))
    return OUTPUT


if __name__ == "__main__":
    print(build_pdf())
