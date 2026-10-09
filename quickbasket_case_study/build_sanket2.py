# -*- coding: utf-8 -*-
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "sanket2.pptx")

NAVY = RGBColor(0x0B, 0x24, 0x47)
HEADER_BG = RGBColor(0x0B, 0x24, 0x47)
HEADER_TEXT = RGBColor(0xFF, 0xFF, 0xFF)
ROW_ALT = RGBColor(0xF0, 0xF3, 0xF8)
ROW_MAIN = RGBColor(0xFF, 0xFF, 0xFF)
TEXT = RGBColor(0x22, 0x22, 0x2A)
GRAY = RGBColor(0x5B, 0x64, 0x72)
GREEN = RGBColor(0x1B, 0x7F, 0x5B)
RED = RGBColor(0xB0, 0x2A, 0x2A)
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


def header(slide, page_no, title, kicker="QUICKBASKET — CFO PRESENTATION"):
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
          "QuickBasket: The Runway Challenge", size=40, color=RGBColor(0xFF, 0xFF, 0xFF),
          bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, Inches(0.6), Inches(1.85), SW - Inches(1.2), Inches(0.5),
          "A CFO's Plan to Extend Runway and Reach Profitability",
          size=17, color=RGBColor(0xC9, 0xD4, 0xE6), align=PP_ALIGN.CENTER,
          anchor=MSO_ANCHOR.MIDDLE)

info_rows = [
    ["Role", "Chief Financial Officer (CFO)"],
    ["Prepared By", "Sanket"],
    ["Case", "QuickBasket — Phase 3: The Runway Challenge"],
]
add_table(s, Inches(2.5), Inches(3.6), Inches(8.3), Inches(1.8),
          ["Field", "Details"], info_rows, col_widths=[3, 7],
          header_size=13, body_size=13)

# ================================================= SLIDE 2: FINANCIAL ANALYSIS
s = prs.slides.add_slide(BLANK)
header(s, 2, "1. Financial Analysis — Current Health")

fin_rows = [
    ["Cash in Bank", "Rs 1 Crore", "Total funds available today"],
    ["Monthly Revenue", "Rs 20 Lakhs", "Money coming in each month"],
    ["Monthly Expenses", "Rs 32 Lakhs", "Money going out each month"],
    ["Monthly Burn Rate", "Rs 12 Lakhs", "Loss per month (Expenses - Revenue)"],
    ["Runway", "8 Months", "Cash in Bank / Burn Rate = 1 Cr / 12L"],
    ["Revenue-to-Expense Ratio", "62.5%", "Company earns Rs 0.625 for every Rs 1 spent"],
]
add_table(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(3.6),
          ["Metric", "Value", "What It Means"], fin_rows,
          col_widths=[3, 2, 5])

add_note(s, Inches(0.4), Inches(5.4), Inches(12.5), Inches(1.5),
         "Verdict: The company is not in immediate danger, but it is spending Rs 1.6 for every "
         "Rs 1 it earns. Without action, cash runs out in 8 months. The priority is to increase "
         "the runway before it becomes a crisis.")

# ================================================= SLIDE 3: EXTEND THE RUNWAY
s = prs.slides.add_slide(BLANK)
header(s, 3, "2. Extend the Runway — Action Plan")

runway_rows = [
    ["Cut discount / cashback spend", "Marketing", "+2.0 months"],
    ["Exit 3-4 loss-making cities", "Operations", "+2.5 months"],
    ["Renegotiate delivery & vendor rates", "Operations", "+1.0 month"],
    ["Freeze non-critical hiring", "HR", "+1.0 month"],
    ["Consolidate warehouses in low-density areas", "Operations", "+1.5 months"],
]
add_table(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(3.0),
          ["Action", "Owner", "Runway Gained"], runway_rows,
          col_widths=[6, 3, 3])

target_rows = [
    ["Runway Today", "8 Months"],
    ["Runway After Actions Above", "~15-16 Months"],
]
add_table(s, Inches(0.4), Inches(4.9), Inches(6.0), Inches(1.2),
          ["Stage", "Runway"], target_rows, col_widths=[6, 4], body_size=13)

add_note(s, Inches(6.8), Inches(4.9), Inches(6.1), Inches(1.6),
         "Target: double the runway to 15+ months within 2-3 months of action, "
         "without needing new investor money right away.")

# ================================================= SLIDE 4: COST OPTIMIZATION
s = prs.slides.add_slide(BLANK)
header(s, 4, "3. Cost Optimization")

cost_rows = [
    ["Discounts & cashback offers", "High", "Cut", "Attracts one-time users, not loyal ones"],
    ["Warehouses in low-order cities", "High", "Consolidate / Close", "Fixed rent + staff cost with low order volume"],
    ["Delivery partner payouts", "Medium", "Renegotiate", "Volume-based rates can be re-priced"],
    ["Corporate / head-office overhead", "Medium", "Reduce", "Non-essential during a cash crunch"],
    ["Marketing (brand ads)", "Medium", "Pause", "Low return during a cost-cutting phase"],
    ["Tech & delivery-app infra", "Low", "Keep", "Core to service quality, do not cut"],
]
add_table(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(4.4),
          ["Expense Area", "Impact on Burn", "Action", "Reason"], cost_rows,
          col_widths=[3.2, 1.8, 2.2, 4.8])

# ================================================= SLIDE 5: REVENUE GROWTH
s = prs.slides.add_slide(BLANK)
header(s, 5, "4. Revenue Growth — Without Raising Prices")

rev_rows = [
    ["QuickBasket+ subscription", "Free/priority delivery for a monthly fee", "+Rs 2-3 Lakhs/month"],
    ["Ads for brands on the app", "Sponsored product placement", "+Rs 1-2 Lakhs/month"],
    ["Bundle offers / combos", "Increase average order value", "+Rs 1 Lakh/month"],
    ["Small delivery fee on low-value orders", "Covers delivery cost on small baskets", "+Rs 1 Lakh/month"],
    ["B2B supply to small shops", "New customer segment, larger order sizes", "+Rs 1-2 Lakhs/month"],
]
add_table(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(3.6),
          ["Idea", "How It Works", "Estimated Impact"], rev_rows,
          col_widths=[3.5, 5, 3])

add_note(s, Inches(0.4), Inches(5.4), Inches(12.5), Inches(1.3),
         "Combined effect: Monthly revenue can move from Rs 20 Lakhs toward Rs 26-29 Lakhs "
         "within 6-9 months, without touching product prices.")

# ================================================= SLIDE 6: FUNDING DECISION
s = prs.slides.add_slide(BLANK)
header(s, 6, "5. Funding Decision")

fund_rows = [
    ["Raise New Funding", "Extra cash buffer for growth", "Investors want profit proof first; dilutes ownership; hard to raise now"],
    ["Focus on Profitability", "Keeps control; builds a stronger case for future funding; forces discipline", "Slower growth in the short term"],
]
add_table(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(2.0),
          ["Option", "Pros", "Cons"], fund_rows, col_widths=[2.5, 5, 5])

add_text(s, Inches(0.4), Inches(3.85), Inches(12.5), Inches(0.4),
          "Recommendation: Focus on Profitability First", size=16, color=GREEN, bold=True)
add_note(s, Inches(0.4), Inches(4.35), Inches(12.5), Inches(2.2),
         "Reason: Investors have already said they will not fund without a clear path to profit. "
         "Raising money now, before fixing the burn rate, would mean raising at a weak valuation "
         "and still burning cash the same way. Fixing cost and revenue first (Slides 3-5) builds "
         "a stronger, higher-valued case to raise later, if it is still needed.")

# ================================================= SLIDE 7: SUCCESS METRICS
s = prs.slides.add_slide(BLANK)
header(s, 7, "6. Success Metrics — Next 12 Months")

metric_rows = [
    ["Cash Runway", "8 Months", "18+ Months"],
    ["Monthly Burn Rate", "Rs 12 Lakhs", "Rs 5 Lakhs or lower"],
    ["Monthly Revenue", "Rs 20 Lakhs", "Rs 32+ Lakhs"],
    ["Monthly Expenses", "Rs 32 Lakhs", "Rs 30 Lakhs or lower"],
    ["Contribution Margin per Order", "Negative", "Positive"],
    ["Cities Operating at Profit", "0 of 12", "6+ of 12"],
]
add_table(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(4.2),
          ["Metric", "Today", "12-Month Target"], metric_rows,
          col_widths=[4.5, 3.5, 4.5])

# ================================================= SLIDE 8: SUMMARY ROADMAP
s = prs.slides.add_slide(BLANK)
header(s, 8, "Summary — 12-Month Roadmap")

road_rows = [
    ["0-3 Months", "Cut discounts, exit weak cities, freeze hiring, renegotiate vendor rates"],
    ["3-6 Months", "Launch QuickBasket+, add ads revenue, bundle offers, review warehouse footprint"],
    ["6-12 Months", "Reach positive contribution margin, grow B2B orders, evaluate funding need"],
]
add_table(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(2.7),
          ["Timeline", "Key Actions"], road_rows, col_widths=[3, 9.5])

add_text(s, Inches(0.4), Inches(4.6), Inches(12.5), Inches(0.4),
          "Bottom Line", size=16, color=GREEN, bold=True)
add_note(s, Inches(0.4), Inches(5.1), Inches(12.5), Inches(1.5),
         "QuickBasket survives by spending less, earning more per order, and proving it can run "
         "profitably in a few cities before growing again. Runway extends from 8 months to "
         "18+ months, and the company enters year two with a real path to profit instead of "
         "just more users.")

prs.save(OUT)
print("Wrote", OUT)
