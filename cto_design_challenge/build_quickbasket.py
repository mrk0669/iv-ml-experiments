# -*- coding: utf-8 -*-
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "QuickBasket_CTO_Strategy.pptx")

NAVY = RGBColor(0x0B, 0x24, 0x47)
GREEN = RGBColor(0x1B, 0x7F, 0x5B)
ORANGE = RGBColor(0xE0, 0x6A, 0x1F)
BLUE = RGBColor(0x46, 0x58, 0xC9)
PURPLE = RGBColor(0x5E, 0x41, 0x98)
RED = RGBColor(0xB3, 0x30, 0x2C)
GRAY = RGBColor(0x5B, 0x64, 0x72)
TEXT = RGBColor(0x22, 0x22, 0x2A)
BLACK = RGBColor(0x00, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BG = RGBColor(0xF3, 0xF4, 0xF8)
BORDER = RGBColor(0xD7, 0xDC, 0xE8)

HEAD_FONT = "Century Gothic"
BODY_FONT = "Segoe UI"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]


def add_gradient_bar(slide, x, y, w, h, c1=RGBColor(0xFF, 0x65, 0x01), c2=BLUE):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shp.line.fill.background()
    shp.shadow.inherit = False
    fill = shp.fill
    fill.gradient()
    stops = fill.gradient_stops
    stops[0].color.rgb = c1
    stops[0].position = 0.0
    stops[1].color.rgb = c2
    stops[1].position = 1.0
    try:
        fill.gradient_angle = 0.0
    except Exception:
        pass
    return shp


def add_rect(slide, x, y, w, h, color, line=False, round_=False):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if round_ else MSO_SHAPE.RECTANGLE
    shp = slide.shapes.add_shape(shape_type, x, y, w, h)
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
             italic=False, font=BODY_FONT, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, line_spacing=1.0):
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


def add_bullets(slide, x, y, w, h, items, size=13, color=TEXT,
                 font=BODY_FONT, bullet_color=ORANGE, space_after=8,
                 line_spacing=1.05):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for i, (label, desc) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = line_spacing
        p.space_after = Pt(space_after)
        r0 = p.add_run()
        r0.text = "●  "
        r0.font.size = Pt(size)
        r0.font.name = font
        r0.font.color.rgb = bullet_color
        if label:
            r1 = p.add_run()
            r1.text = label + "  "
            r1.font.size = Pt(size)
            r1.font.bold = True
            r1.font.italic = True
            r1.font.name = font
            r1.font.color.rgb = NAVY
        if desc:
            r2 = p.add_run()
            r2.text = desc
            r2.font.size = Pt(size)
            r2.font.italic = True
            r2.font.name = font
            r2.font.color.rgb = color
    return box


def scaffold(slide, kicker, title, page_no, subtitle="CTO Case Study Response"):
    header_h = Inches(0.62)
    add_rect(slide, 0, 0, SW, header_h, BLACK)
    add_text(slide, Inches(0.4), 0, Inches(7.5), header_h,
              "QUICKBASKET — PATH TO PROFITABILITY", size=13, color=WHITE,
              bold=True, font=BODY_FONT, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, SW - Inches(4.4), 0, Inches(4.0), header_h, subtitle,
              size=12, color=RGBColor(0xE8, 0xE8, 0xEC), italic=True,
              font=BODY_FONT, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    add_gradient_bar(slide, 0, header_h, SW, Inches(0.06))
    add_gradient_bar(slide, 0, SH - Inches(0.09), SW, Inches(0.09))
    add_text(slide, SW - Inches(1.0), SH - Inches(0.42), Inches(0.7), Inches(0.3),
              str(page_no), size=11, color=NAVY, bold=True, align=PP_ALIGN.RIGHT)
    if kicker:
        add_text(slide, Inches(0.4), header_h + Inches(0.1), Inches(11.5), Inches(0.3),
                  kicker.upper(), size=11.5, color=ORANGE, bold=True, font=BODY_FONT)
        title_y = header_h + Inches(0.38)
    else:
        title_y = header_h + Inches(0.16)
    add_text(slide, Inches(0.4), title_y, Inches(12.5), Inches(0.55),
              title, size=22.5, color=NAVY, bold=True, font=HEAD_FONT)


def flow_row(slide, x, y, w, h, boxes, gap=0.2, box_color=NAVY,
             text_color=WHITE, arrow_color=GRAY, size=11.5):
    n = len(boxes)
    gap_in = Inches(gap)
    box_w = (w - gap_in * (n - 1)) / n
    cx = x
    for i, label in enumerate(boxes):
        color = box_color[i] if isinstance(box_color, list) else box_color
        add_rect(slide, cx, y, box_w, h, color, round_=True)
        add_text(slide, cx + Inches(0.06), y, box_w - Inches(0.12), h, label,
                  size=size, color=text_color, bold=True, font=BODY_FONT,
                  align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.05)
        if i < n - 1:
            add_text(slide, cx + box_w, y, gap_in, h, "→", size=18,
                      color=arrow_color, bold=True, align=PP_ALIGN.CENTER,
                      anchor=MSO_ANCHOR.MIDDLE)
        cx += box_w + gap_in
    return box_w


# ========================================================= SLIDE 1: TITLE ==
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, SW, SH, WHITE)
band_h = Inches(3.3)
add_rect(s, 0, 0, SW, band_h, BLACK)
add_gradient_bar(s, 0, band_h, SW, Inches(0.1))
add_gradient_bar(s, 0, SH - Inches(0.12), SW, Inches(0.12))
add_text(s, Inches(0.6), band_h / 2 - Inches(0.8), SW - Inches(1.2), Inches(1.0),
          "Saving QuickBasket", size=44, color=WHITE, bold=True,
          font=HEAD_FONT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, Inches(0.6), band_h / 2 + Inches(0.22), SW - Inches(1.2), Inches(0.6),
          "A Technology Path to Profitability in 12 Months", size=17,
          color=RGBColor(0xFF, 0x9A, 0x4D), italic=True, font=BODY_FONT,
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

fy = band_h + Inches(0.85)
for label, val in [
    ("Perspective", "Chief Technology Officer"),
    ("Prepared By", "Keshav"),
    ("Case", "QuickBasket Leadership Case Study — 6-Month Runway"),
]:
    box = s.shapes.add_textbox(Inches(1.2), fy, Inches(11), Inches(0.45))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r1 = p.add_run(); r1.text = label + " :  "
    r1.font.bold = True; r1.font.size = Pt(15); r1.font.name = BODY_FONT
    r1.font.color.rgb = NAVY
    r2 = p.add_run(); r2.text = val
    r2.font.italic = True; r2.font.size = Pt(15); r2.font.name = BODY_FONT
    r2.font.color.rgb = TEXT
    fy += Inches(0.5)

add_rect(s, Inches(1.2), fy + Inches(0.05), Inches(6.6), Inches(0.42), RED, round_=True)
add_text(s, Inches(1.2), fy + Inches(0.05), Inches(6.6), Inches(0.42),
          "Six months of cash runway remain.", size=13, color=WHITE, bold=True,
          font=BODY_FONT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# ============================================ SLIDE 2: CTO LENS ============
s = prs.slides.add_slide(BLANK)
scaffold(s, "Framing", "The Two Levers That Are Actually Mine to Pull", 2)
add_text(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(0.6),
          "With six months of runway, Technology's job is not to chase growth — it's to make "
          "unit economics positive. Two of the seven challenges on the table are mine to fix directly.",
          size=13, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.15)

chal_cols = [
    (GREEN, "Rising Delivery &\nWarehouse Cost",
     "Every order costs more to fulfil than it earns — the direct, controllable half of "
     "\"losing money on almost every order.\""),
    (ORANGE, "Discount-Only\nRetention",
     "Users who only return during campaigns are not loyal customers — they're rented "
     "attention, and rented attention doesn't survive a cash crunch."),
]
cx = Inches(0.4)
cw = Inches(6.0)
for color, title, desc in chal_cols:
    add_rect(s, cx, Inches(2.3), cw, Inches(0.85), color, round_=True)
    add_text(s, cx + Inches(0.2), Inches(2.3), cw - Inches(0.4), Inches(0.85), title,
              size=16, color=WHITE, bold=True, font=HEAD_FONT, anchor=MSO_ANCHOR.MIDDLE,
              line_spacing=1.05)
    add_rect(s, cx, Inches(3.25), cw, Inches(1.5), LIGHT_BG)
    add_text(s, cx + Inches(0.2), Inches(3.4), cw - Inches(0.4), Inches(1.2), desc,
              size=12, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.2)
    cx += cw + Inches(0.5)

add_text(s, Inches(0.4), Inches(5.0), Inches(12.5), Inches(0.35),
          "Working Assumptions", size=15, color=PURPLE, bold=True, font=HEAD_FONT)
add_bullets(s, Inches(0.4), Inches(5.45), Inches(12.5), Inches(1.6), [
    ("No per-order profitability visibility today:", "a 3-year-old, growth-built engineering org "
     "typically has usage and GMV dashboards, not contribution-margin dashboards."),
    ("Engineering capacity is fixed, not growing:", "every initiative below competes for the same "
     "limited team — sequencing matters as much as the ideas themselves."),
], size=12.5)

# ================================================ SLIDE 3: UNIT ECON ENGINE
s = prs.slides.add_slide(BLANK)
scaffold(s, "First Move", "Before Cutting Anything, See Where the Money Is Actually Going", 3)
add_text(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(0.55),
          "Exiting cities blind is how good markets get cut and bad ones get kept. Week one "
          "deliverable: a Unit-Economics Engine that turns \"we're losing money\" into \"we're "
          "losing ₹X per order in these 4 cities, and making money in these 3.\"",
          size=12.5, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.15)

flow3 = ["Order + Delivery\n+ Warehouse Cost\nData", "Unit-Economics\nEngine\n(contribution margin)",
         "City / Dark-Store /\nCohort Ranking", "Leadership Decision:\nExit, Keep, or\nDouble Down"]
flow_row(s, Inches(0.4), Inches(2.35), Inches(12.5), Inches(1.15), flow3,
          box_color=[NAVY, GREEN, ORANGE, PURPLE], size=12)

add_text(s, Inches(0.4), Inches(3.85), Inches(6.0), Inches(0.35),
          "Why This Comes First", size=14, color=GREEN, bold=True, font=HEAD_FONT)
add_bullets(s, Inches(0.4), Inches(4.3), Inches(6.0), Inches(2.6), [
    ("Resolves the internal disagreement", "with data instead of opinions — leadership stops "
     "debating strategy in the abstract and starts deciding city by city."),
    ("Makes Option 2 executable, not just directional:", "\"exit unprofitable cities\" is only "
     "safe advice once you know precisely which ones those are."),
], size=12)

add_rect(s, Inches(6.9), Inches(3.85), Inches(6.0), Inches(3.1), LIGHT_BG)
add_text(s, Inches(7.1), Inches(4.0), Inches(5.6), Inches(0.3),
          "Build Cost", size=13, color=PURPLE, bold=True, font=HEAD_FONT)
add_text(s, Inches(7.1), Inches(4.35), Inches(5.6), Inches(2.5),
          "This is a reporting layer over data QuickBasket already generates (orders, delivery "
          "logs, warehouse costs) — a small dedicated squad, roughly 2-3 weeks, not a new "
          "platform. It is the highest-leverage two weeks of engineering time available right now.",
          size=12, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.25)

# ========================================= SLIDE 4: COST PER ORDER =========
s = prs.slides.add_slide(BLANK)
scaffold(s, "Fix #1", "Cutting Delivery & Warehouse Cost Per Order", 4)
add_text(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(0.5),
          "Retention fixes are worthless if every order is still underwater — cost per order has "
          "to fall in the cities QuickBasket keeps.",
          size=13, color=TEXT, italic=True, font=BODY_FONT)

add_text(s, Inches(0.4), Inches(2.2), Inches(6.0), Inches(0.35),
          "Four Levers, in Priority Order", size=15, color=GREEN, bold=True, font=HEAD_FONT)
add_bullets(s, Inches(0.4), Inches(2.65), Inches(6.0), Inches(3.8), [
    ("1. Delivery batching / route optimization:", "fewer single-order rider trips — the single "
     "biggest lever on last-mile cost per order."),
    ("2. Demand forecasting per dark store:", "right-size inventory to cut grocery spoilage/waste, "
     "a direct, avoidable cost unique to quick-commerce."),
    ("3. Dynamic rider allocation:", "staff riders to the predicted demand curve, not a flat "
     "roster — cuts idle-time cost."),
    ("4. Packaging & last-mile cost tuning:", "smaller, cheaper packaging tiers by basket size."),
], size=12)

add_text(s, Inches(6.9), Inches(2.2), Inches(6.0), Inches(0.35),
          "Sequencing Logic", size=15, color=PURPLE, bold=True, font=HEAD_FONT)
add_rect(s, Inches(6.9), Inches(2.65), Inches(6.0), Inches(3.8), LIGHT_BG)
add_text(s, Inches(7.1), Inches(2.8), Inches(5.6), Inches(3.5),
          "Route optimization and demand forecasting are prioritised first because they act on "
          "data the Unit-Economics Engine (Slide 3) already surfaces, and they pay back within "
          "weeks, not quarters. Rider allocation and packaging follow once the first two are "
          "live and their savings are visible in the same dashboard — proof compounds the case "
          "for further investment instead of asking leadership to trust the plan up front.",
          size=12, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.25)

# ====================================== SLIDE 5: RETENTION TECH ============
s = prs.slides.add_slide(BLANK)
scaffold(s, "Fix #2", "Replacing Discounts With Product-Led Retention", 5)
add_text(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(0.5),
          "CAC is up 70% and blanket discounts are training users to wait for the next one — "
          "the fix is to make the product itself the reason they return.",
          size=13, color=TEXT, italic=True, font=BODY_FONT)

add_text(s, Inches(0.4), Inches(2.2), Inches(6.0), Inches(0.35),
          "Three Retention Levers", size=15, color=GREEN, bold=True, font=HEAD_FONT)
add_bullets(s, Inches(0.4), Inches(2.65), Inches(6.0), Inches(3.4), [
    ("Predictive reorder prompts:", "\"milk again?\" — nudge restocking of habitual essentials "
     "before the user thinks to open a competitor's app."),
    ("Light loyalty / subscription tier:", "small predictable recurring revenue and a habit "
     "loop, instead of one-off discount hunting."),
    ("Targeted, not blanket, promotions:", "an ML model scores churn risk and spends discount "
     "budget only on users about to leave — same retention effect, a fraction of the cost."),
], size=12)

add_text(s, Inches(6.9), Inches(2.2), Inches(6.0), Inches(0.35),
          "Customer Insight Behind This", size=15, color=PURPLE, bold=True, font=HEAD_FONT)
add_rect(s, Inches(6.9), Inches(2.65), Inches(6.0), Inches(3.4), LIGHT_BG)
add_text(s, Inches(7.1), Inches(2.8), Inches(5.6), Inches(3.1),
          "College students and young professionals — QuickBasket's original core — value "
          "speed and habit, not the lowest price on a given order. A discount-trained user is "
          "actually a mispriced retention strategy: it's optimising for the customer who cares "
          "least about the product and most about the coupon, which is exactly the segment "
          "large competitors can outspend. Targeted retention wins back the segment that "
          "discounting alone can't hold.",
          size=11.5, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.22)

# =============================================== SLIDE 6: 4 OPTIONS VIEW ===
s = prs.slides.add_slide(BLANK)
scaffold(s, "Strategic Recommendation", "Reading the Four Options Through a Tech Lens", 6)

opt_rows = [
    ("Option 1 — Double Down on Growth", RED, "Rejected.",
     "Tech cannot fix unit economics fast enough to fund a growth push on 6 months of runway."),
    ("Option 2 — Focus on Profitability", GREEN, "Primary recommendation.",
     "This is exactly what the Unit-Economics Engine and cost fixes (Slides 3-4) are built to execute well."),
    ("Option 3 — Pivot to B2B Logistics", ORANGE, "Feasible, but Phase 2.",
     "Existing warehouse/delivery infra is reusable — but a net-new build now competes for the same engineering capacity Option 2 needs first."),
    ("Option 4 — Hybrid Model", PURPLE, "The sequencing answer.",
     "Execute Option 2 now; layer subscription/B2B revenue from month 4-6 onward by reusing infra, not building net-new."),
]
ry = Inches(1.6)
for label, color, verdict, why in opt_rows:
    add_rect(s, Inches(0.4), ry, Inches(3.3), Inches(1.15), color, round_=True)
    add_text(s, Inches(0.55), ry + Inches(0.1), Inches(3.0), Inches(0.55), label,
              size=12, color=WHITE, bold=True, font=BODY_FONT, line_spacing=1.05)
    add_text(s, Inches(0.55), ry + Inches(0.68), Inches(3.0), Inches(0.35), verdict,
              size=11.5, color=WHITE, bold=True, italic=True, font=BODY_FONT)
    add_rect(s, Inches(3.9), ry, Inches(9.0), Inches(1.15), LIGHT_BG)
    add_text(s, Inches(4.1), ry, Inches(8.6), Inches(1.15), why, size=12, color=TEXT,
              italic=True, font=BODY_FONT, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.15)
    ry += Inches(1.3)

# ============================================== SLIDE 7: ROADMAP ===========
s = prs.slides.add_slide(BLANK)
scaffold(s, "Execution", "What Engineering Ships, and When", 7)

phases = [
    ("Months 0-2", RED, ["Unit-Economics Engine live", "City/cohort profitability ranking",
                          "Route optimization + demand forecasting begin"]),
    ("Months 2-4", ORANGE, ["Dynamic rider allocation", "Packaging cost tuning",
                             "Predictive reorder prompts ship"]),
    ("Months 4-8", GREEN, ["Loyalty / subscription tier", "Targeted churn-risk promotions",
                            "Cost-per-order trending down city by city"]),
    ("Months 8-12", PURPLE, ["Reuse infra to pilot B2B logistics", "In 1-2 stabilized cities only",
                              "Funded by savings, not new capital"]),
]
cw = Inches(2.95)
cx = Inches(0.4)
for label, color, items in phases:
    add_rect(s, cx, Inches(1.55), cw, Inches(0.5), color, round_=True)
    add_text(s, cx, Inches(1.55), cw, Inches(0.5), label, size=13, color=WHITE,
              bold=True, font=HEAD_FONT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_rect(s, cx, Inches(2.15), cw, Inches(2.6), LIGHT_BG)
    iy = Inches(2.3)
    for it in items:
        add_text(s, cx + Inches(0.15), iy, cw - Inches(0.3), Inches(0.85),
                  "•  " + it, size=10.3, color=TEXT, italic=True, font=BODY_FONT,
                  line_spacing=1.1)
        iy += Inches(0.8)
    if cx + cw < SW - Inches(0.7):
        add_text(s, cx + cw, Inches(1.55), Inches(0.3), Inches(0.5), "→", size=16,
                  color=GRAY, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    cx += cw + Inches(0.3)

add_text(s, Inches(0.4), Inches(5.05), Inches(12.5), Inches(0.35),
          "Every phase is funded by the previous one's savings — no new capital is assumed "
          "beyond the current runway.", size=12.5, color=PURPLE, bold=True, italic=True,
          font=BODY_FONT)

# ============================================== SLIDE 8: METRICS ===========
s = prs.slides.add_slide(BLANK)
scaffold(s, "Accountability", "What Technology Will Track Over the Next 12 Months", 8)

metrics = [
    ("Contribution margin / order", GREEN, "Target: positive within 4 months in kept cities."),
    ("Cost per order (delivery + warehouse)", ORANGE, "Must trend down monthly, city by city."),
    ("Repeat-order rate excluding discount periods", BLUE, "The real test of retention, not vanity DAUs."),
    ("Rider utilization %", PURPLE, "Idle-time cost is a direct lever on margin."),
    ("Demand-forecast accuracy / spoilage %", NAVY, "Ties inventory tech directly to cash saved."),
    ("Engineering cost as % of revenue", RED, "Keeps tech investment itself inside the profitability story."),
]
col_x = [Inches(0.4), Inches(4.75), Inches(9.1)]
mw, mh = Inches(4.15), Inches(1.55)
for i, (metric, color, note) in enumerate(metrics):
    cx = col_x[i % 3]
    cy = Inches(1.65) + Inches(1.75) * (i // 3)
    add_rect(s, cx, cy, mw, mh, LIGHT_BG, line=True)
    add_rect(s, cx, cy, Inches(0.12), mh, color)
    add_text(s, cx + Inches(0.28), cy + Inches(0.12), mw - Inches(0.5), Inches(0.6), metric,
              size=13, color=NAVY, bold=True, font=BODY_FONT, line_spacing=1.05)
    add_text(s, cx + Inches(0.28), cy + Inches(0.75), mw - Inches(0.5), Inches(0.7), note,
              size=11, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.1)

add_text(s, Inches(0.4), Inches(5.35), Inches(12.5), Inches(1.3),
          "Technology's contribution to survival is simple to state: turn \"losing money on "
          "almost every order\" into a number leadership can see improve every week, and give "
          "the product a reason to be used that isn't a coupon. That is what buys QuickBasket "
          "its next 12 months.",
          size=13, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.25)

prs.save(OUT)
print("Wrote", OUT)
