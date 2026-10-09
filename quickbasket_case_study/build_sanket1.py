# -*- coding: utf-8 -*-
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "sanket1.pptx")

NAVY = RGBColor(0x0B, 0x24, 0x47)
HEADER_BG = RGBColor(0x0B, 0x24, 0x47)
HEADER_TEXT = RGBColor(0xFF, 0xFF, 0xFF)
ROW_ALT = RGBColor(0xF0, 0xF3, 0xF8)
ROW_MAIN = RGBColor(0xFF, 0xFF, 0xFF)
TEXT = RGBColor(0x22, 0x22, 0x2A)
GRAY = RGBColor(0x5B, 0x64, 0x72)
GREEN = RGBColor(0x1B, 0x7F, 0x5B)
BORDER = RGBColor(0xD7, 0xDC, 0xE8)

FONT = "Calibri"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]


def add_rect(slide, x, y, w, h, color, line=False):
    from pptx.enum.shapes import MSO_SHAPE
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.shadow.inherit = False
    if line:
        shp.line.color.rgb = BORDER
        shp.line.width = Pt(0.75)
    else:
        shp.line.fill.background()
    return shp


def add_text(slide, x, y, w, h, text, size=14, color=TEXT, bold=False,
             italic=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
             line_spacing=1.0, font=FONT):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.name = font
        r.font.color.rgb = color
    return box


def header(slide, page_no, title, kicker="QUICKBASKET — CFO PERSPECTIVE"):
    add_rect(slide, 0, 0, SW, Inches(0.55), HEADER_BG)
    add_text(slide, Inches(0.4), 0, Inches(8), Inches(0.55), kicker,
              size=12, color=RGBColor(0xC9, 0xD4, 0xE6), bold=True,
              anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, SW - Inches(1.2), 0, Inches(0.8), Inches(0.55), str(page_no),
              size=12, color=RGBColor(0xC9, 0xD4, 0xE6), bold=True,
              align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(0.4), Inches(0.7), Inches(12.5), Inches(0.55),
              title, size=24, color=NAVY, bold=True)


def add_table(slide, x, y, w, h, headers, rows, col_widths=None,
              header_size=13, body_size=12.5, header_color=HEADER_BG,
              align_cols=None):
    n_rows = len(rows) + 1
    n_cols = len(headers)
    gtable = slide.shapes.add_table(n_rows, n_cols, x, y, w, h).table

    if col_widths:
        total = sum(col_widths)
        for i, cw in enumerate(col_widths):
            gtable.columns[i].width = int(w * cw / total)

    for j, htext in enumerate(headers):
        cell = gtable.cell(0, j)
        cell.text = ""
        cell.fill.solid()
        cell.fill.fore_color.rgb = header_color
        cell.margin_left = Inches(0.08)
        cell.margin_right = Inches(0.08)
        cell.margin_top = Inches(0.04)
        cell.margin_bottom = Inches(0.04)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.alignment = align_cols[j] if align_cols else PP_ALIGN.LEFT
        r = p.add_run()
        r.text = htext
        r.font.size = Pt(header_size)
        r.font.bold = True
        r.font.name = FONT
        r.font.color.rgb = HEADER_TEXT

    for i, row in enumerate(rows):
        bg = ROW_MAIN if i % 2 == 0 else ROW_ALT
        for j, val in enumerate(row):
            cell = gtable.cell(i + 1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.08)
            cell.margin_top = Inches(0.04)
            cell.margin_bottom = Inches(0.04)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = align_cols[j] if align_cols else PP_ALIGN.LEFT
            r = p.add_run()
            r.text = str(val)
            r.font.size = Pt(body_size)
            r.font.name = FONT
            r.font.bold = (j == 0)
            r.font.color.rgb = TEXT
    return gtable


def add_note(slide, x, y, w, h, text, size=12, color=GRAY):
    add_text(slide, x, y, w, h, text, size=size, color=color, italic=True,
              line_spacing=1.15)


# ============================================================ SLIDE 1: TITLE
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, SW, SH, RGBColor(0xFF, 0xFF, 0xFF))
add_rect(s, 0, 0, SW, Inches(3.0), HEADER_BG)
add_text(s, Inches(0.6), Inches(1.0), SW - Inches(1.2), Inches(0.9),
          "Saving QuickBasket", size=42, color=RGBColor(0xFF, 0xFF, 0xFF),
          bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, Inches(0.6), Inches(1.85), SW - Inches(1.2), Inches(0.5),
          "A CFO's Strategy for Survival and Profitability",
          size=17, color=RGBColor(0xC9, 0xD4, 0xE6), align=PP_ALIGN.CENTER,
          anchor=MSO_ANCHOR.MIDDLE)

info_rows = [
    ["Role", "Chief Financial Officer (CFO)"],
    ["Prepared By", "Sanket"],
    ["Case", "Saving QuickBasket — Leadership Case Study"],
]
add_table(s, Inches(2.5), Inches(3.6), Inches(8.3), Inches(1.8),
          ["Field", "Details"], info_rows, col_widths=[3, 7],
          header_size=13, body_size=13)

# ============================================ SLIDE 2: CFO-RELEVANT CHALLENGES
s = prs.slides.add_slide(BLANK)
header(s, 2, "1. Challenges Most Relevant to the CFO")

chal_rows = [
    ["Rising Customer Acquisition Cost (+70% in a year)",
     "Every new user now costs far more to acquire, but is not spending more — CAC is "
     "outrunning the revenue each user brings in."],
    ["Losing money on almost every order",
     "Even with 8 lakh+ users across 12 cities, negative unit economics mean growth is "
     "currently making losses bigger, not smaller."],
]
add_table(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(2.2),
          ["Challenge", "Why It Is a Finance Problem"], chal_rows,
          col_widths=[4, 8.5])

add_note(s, Inches(0.4), Inches(4.0), Inches(12.5), Inches(1.5),
         "These two issues sit squarely with Finance: they are questions of unit economics and "
         "capital efficiency, not just marketing or operations. Everything else in this case "
         "(competitor pricing, investor sentiment, expansion limits) flows from these two.")

# ==================================================== SLIDE 3: OPTIONS COMPARED
s = prs.slides.add_slide(BLANK)
header(s, 3, "2. The 4 Options — A Financial View")

opt_rows = [
    ["1. Double Down on Growth", "Increases", "Very High", "Not Recommended"],
    ["2. Focus on Profitability", "Decreases", "Low", "Recommended (Primary)"],
    ["3. Pivot to B2B Logistics", "Neutral, then improves", "Medium", "Explore in Parallel"],
    ["4. Hybrid Model", "Decreases, slower", "Medium", "Recommended (Secondary)"],
]
add_table(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(2.6),
          ["Option", "Effect on Burn", "Risk", "CFO View"], opt_rows,
          col_widths=[4, 3, 2, 3.5])

add_note(s, Inches(0.4), Inches(4.4), Inches(12.5), Inches(1.5),
         "With 6 months of runway and investors demanding profitability first, Option 1 is ruled "
         "out immediately — it burns cash the company does not have. Options 2 and 4 both cut "
         "burn; the difference is how much new-revenue-building they attempt while doing it.")

# ==================================================== SLIDE 4: RECOMMENDATION
s = prs.slides.add_slide(BLANK)
header(s, 4, "3. Recommendation — Profitability First, Hybrid Second")

rec_rows = [
    ["Step 1 (0-3 months)", "Exit loss-making cities, cut discount-driven acquisition, freeze hiring",
     "Stops the bleeding — extends runway immediately"],
    ["Step 2 (3-9 months)", "Add subscription, ads, and B2B revenue on top of the leaner base",
     "Builds new margin without re-inflating burn"],
    ["Step 3 (9-12 months)", "Reassess growth and city expansion only in cities already profitable",
     "Growth resumes on a foundation that can afford it"],
]
add_table(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(3.0),
          ["Phase", "Action", "Reasoning"], rec_rows, col_widths=[2.5, 6, 4.5])

add_note(s, Inches(0.4), Inches(4.9), Inches(12.5), Inches(1.6),
         "This is Option 2 executed first, with Option 4's revenue diversification layered in "
         "once burn is under control — not both at once. Sequencing avoids running two hard "
         "changes at the same time on a 6-month cash cushion.")

# ============================================== SLIDE 5: ROLE OF FINANCE TEAM
s = prs.slides.add_slide(BLANK)
header(s, 5, "4. Role of the Finance Department")

role_rows = [
    ["Cash & Runway Management", "Weekly cash-flow tracking; flag any month that breaks the recovery plan"],
    ["Unit Economics Ownership", "Track contribution margin per order, per city — decide what stays open"],
    ["Cost Governance", "Approve/reject spend against the cost-cutting plan, city by city"],
    ["Investor & Board Reporting", "Show a credible, numbers-backed path to profitability every month"],
    ["Fundraising Readiness", "Keep the company fundable later, even while not actively raising now"],
]
add_table(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(3.4),
          ["Finance Function", "What It Does For Survival"], role_rows,
          col_widths=[4, 8.5])

# =================================================== SLIDE 6: ASSUMPTIONS
s = prs.slides.add_slide(BLANK)
header(s, 6, "5. Assumptions & Financial Estimates")

assum_rows = [
    ["Cash in Bank (approx.)", "Rs 1 Crore"],
    ["Monthly Revenue (approx.)", "Rs 20 Lakhs"],
    ["Monthly Expenses (approx.)", "Rs 32 Lakhs"],
    ["Current Runway", "~8 Months"],
    ["Discount-only user share", "Assumed 30-40% of active users"],
]
add_table(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(2.8),
          ["Assumption", "Estimate"], assum_rows, col_widths=[6, 6.5])

add_note(s, Inches(0.4), Inches(4.6), Inches(12.5), Inches(1.6),
         "Customer insight: a large share of users only transact during discount campaigns and "
         "churn afterward. This group is expensive to keep acquiring and rarely reaches positive "
         "lifetime value — it is the main driver of the CAC and burn problem above.")

# =================================================== SLIDE 7: KEY METRICS
s = prs.slides.add_slide(BLANK)
header(s, 7, "6. Key Metrics Finance Will Track (12 Months)")

metric_rows = [
    ["Cash Runway", "8 Months", "18+ Months"],
    ["Monthly Burn Rate", "Rs 12 Lakhs", "Rs 5 Lakhs or lower"],
    ["CAC (Customer Acquisition Cost)", "Up 70% YoY", "Down 30% from today"],
    ["LTV : CAC Ratio", "Below 1", "Above 3"],
    ["Contribution Margin per Order", "Negative", "Positive"],
    ["Cities Operating at Profit", "0 of 12", "6+ of 12"],
]
add_table(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(4.2),
          ["Metric", "Today", "12-Month Target"], metric_rows,
          col_widths=[4.5, 3.5, 4.5])

# =================================================== SLIDE 8: SUMMARY
s = prs.slides.add_slide(BLANK)
header(s, 8, "Summary")

add_text(s, Inches(0.4), Inches(1.6), Inches(12.5), Inches(0.4),
          "Bottom Line", size=16, color=GREEN, bold=True)
add_note(s, Inches(0.4), Inches(2.1), Inches(12.5), Inches(1.6),
         "QuickBasket survives by choosing Profitability First (Option 2), then adding new "
         "revenue lines from the Hybrid Model (Option 4) once burn is controlled. Growth resumes "
         "later, on a base that can actually afford it.")

sum_rows = [
    ["Primary Path", "Focus on Profitability (Option 2)"],
    ["Secondary Layer", "Hybrid revenue streams (Option 4) added after Step 1"],
    ["Ruled Out", "Aggressive growth (Option 1) — not affordable on 6-month runway"],
    ["Finance's Job", "Protect runway, own unit economics, report progress monthly"],
]
add_table(s, Inches(0.4), Inches(3.9), Inches(12.5), Inches(2.3),
          ["Item", "Decision"], sum_rows, col_widths=[3.5, 9])

prs.save(OUT)
print("Wrote", OUT)
