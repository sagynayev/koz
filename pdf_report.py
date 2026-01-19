import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


OUTPUT_PATH = "output/meeting_report.pdf"
FONT_PATH = "fonts/DejaVuSans.ttf"
pdfmetrics.registerFont(
    TTFont("DejaVu", FONT_PATH)
)


def generate_pdf():
    with open("output/summary.json", encoding="utf-8") as f:
        summary = json.load(f)

    with open("output/tasks.json", encoding="utf-8") as f:
        tasks = json.load(f)

    os.makedirs("output", exist_ok=True)

    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = "DejaVu"
    elements = []

    # title s
    elements.append(Paragraph("<b>Протокол встречи</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    # summary
    elements.append(Paragraph("<b>Краткое резюме</b>", styles["Heading2"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(summary["summary"], styles["BodyText"]))
    elements.append(Spacer(1, 12))

    # solution
    if summary.get("decisions"):
        elements.append(Paragraph("<b>Принятые решения</b>", styles["Heading2"]))
        elements.append(Spacer(1, 6))
        decisions_list = ListFlowable(
            [ListItem(Paragraph(d, styles["BodyText"])) for d in summary["decisions"]],
            bulletType="bullet"
        )
        elements.append(decisions_list)
        elements.append(Spacer(1, 12))

    # tasks
    elements.append(Paragraph("<b>Задачи</b>", styles["Heading2"]))
    elements.append(Spacer(1, 6))

    if tasks:
        task_items = []
        for t in tasks:
            text = f"{t['task']} — приоритет: {t['priority']}"
            if t.get("owner"):
                text += f", ответственный: {t['owner']}"
            task_items.append(ListItem(Paragraph(text, styles["BodyText"])))

        elements.append(ListFlowable(task_items, bulletType="1"))
    else:
        elements.append(Paragraph("Задачи не зафиксированы.", styles["BodyText"]))

    doc.build(elements)

    return OUTPUT_PATH
