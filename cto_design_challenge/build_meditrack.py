# -*- coding: utf-8 -*-
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "MediTrack_CTO_Brief.pptx")

NAVY = RGBColor(0x0B, 0x24, 0x47)
GREEN = RGBColor(0x1B, 0x7F, 0x5B)
ORANGE = RGBColor(0xE0, 0x6A, 0x1F)
BLUE = RGBColor(0x46, 0x58, 0xC9)
PURPLE = RGBColor(0x5E, 0x41, 0x98)
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


def scaffold(slide, kicker, title, page_no, subtitle="CTO Product & Technology Brief"):
    header_h = Inches(0.62)
    add_rect(slide, 0, 0, SW, header_h, BLACK)
    add_text(slide, Inches(0.4), 0, Inches(7), header_h,
              "MEDITRACK", size=13, color=WHITE,
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
              title, size=23, color=NAVY, bold=True, font=HEAD_FONT)


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
          "MediTrack", size=48, color=WHITE, bold=True,
          font=HEAD_FONT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, Inches(0.6), band_h / 2 + Inches(0.22), SW - Inches(1.2), Inches(0.6),
          "CTO Product & Technology Brief", size=18,
          color=RGBColor(0xFF, 0x9A, 0x4D), italic=True, font=BODY_FONT,
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

fy = band_h + Inches(0.9)
for label, val in [
    ("Perspective", "Chief Technology Officer"),
    ("Prepared By", "Keshav"),
    ("Challenge", "MediTrack — Family Medicine Tracking Platform"),
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
    fy += Inches(0.55)

# ============================================ SLIDE 2: PROBLEM & THESIS ====
s = prs.slides.add_slide(BLANK)
scaffold(s, "Framing", "Four Problems, One Platform — Not an Ad-Hoc Feature List", 2)
add_text(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(0.6),
          "Every module below exists because it closes one of these four failure modes — "
          "nothing shipped in v1 is there for any other reason.",
          size=13, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.15)

trace_rows = [
    ("Forgetfulness", "Missed doses; no reliable prompt at the right time.",
     "Schedule + Reminders", GREEN),
    ("Lost prescriptions", "Paper is lost; patient re-guesses dosage instead of seeing a doctor.",
     "Prescription Mgmt.\n(manual + camera)", ORANGE),
    ("Stock-outs", "Medicine runs out unnoticed until a dose is missed.",
     "Dashboard low-stock\n+ escalating alerts", BLUE),
    ("No family visibility", "No way to confirm a parent or child actually took their dose.",
     "Linked Family Profiles\n+ Today Dashboard", PURPLE),
]
headers = ["Core Problem", "Why It Matters", "Solved By"]
col_x = [Inches(0.4), Inches(3.1), Inches(9.4)]
col_w = [Inches(2.6), Inches(6.2), Inches(3.5)]
hy = Inches(2.25)
for cx, cw, h in zip(col_x, col_w, headers):
    add_rect(s, cx, hy, cw, Inches(0.4), NAVY)
    add_text(s, cx + Inches(0.12), hy, cw - Inches(0.24), Inches(0.4), h,
              size=12.5, color=WHITE, bold=True, font=BODY_FONT, anchor=MSO_ANCHOR.MIDDLE)
ry = hy + Inches(0.4)
row_h = Inches(0.98)
for i, (prob, why, solved, color) in enumerate(trace_rows):
    bg = LIGHT_BG if i % 2 == 0 else WHITE
    add_rect(s, col_x[0], ry, col_x[2] + col_w[2] - col_x[0], row_h, bg, line=True)
    add_text(s, col_x[0] + Inches(0.12), ry, col_w[0] - Inches(0.24), row_h, prob,
              size=12.5, color=color, bold=True, font=BODY_FONT, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, col_x[1] + Inches(0.12), ry, col_w[1] - Inches(0.24), row_h, why,
              size=11.5, color=TEXT, italic=True, font=BODY_FONT, anchor=MSO_ANCHOR.MIDDLE,
              line_spacing=1.1)
    add_text(s, col_x[2] + Inches(0.12), ry, col_w[2] - Inches(0.24), row_h, solved,
              size=11.5, color=NAVY, bold=True, font=BODY_FONT, anchor=MSO_ANCHOR.MIDDLE,
              line_spacing=1.05)
    ry += row_h

add_text(s, Inches(0.4), ry + Inches(0.2), Inches(12.5), Inches(0.4),
          "Product thesis: one platform, usable by any household member regardless of age or "
          "technical comfort — not five disconnected tools.",
          size=12.5, color=PURPLE, bold=True, italic=True, font=BODY_FONT)

# ==================================================== SLIDE 3: FLOW/MODULES ==
s = prs.slides.add_slide(BLANK)
scaffold(s, "Product", "The Must-Have Loop, End to End", 3)
add_text(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(0.45),
          "This is the exact sequence that runs live in the demo — every step maps to a "
          "required module.", size=13, color=TEXT, italic=True, font=BODY_FONT)

flow1 = ["Family\nProfile", "Add Prescription\n(manual / camera)", "Auto-Generated\nSchedule",
         "Escalating\nReminder"]
flow_row(s, Inches(0.4), Inches(2.15), Inches(12.5), Inches(1.0), flow1,
          box_color=[NAVY, GREEN, GREEN, ORANGE], size=12.5)

add_text(s, Inches(5.85), Inches(3.3), Inches(1.0), Inches(0.35), "↓", size=22,
          color=GRAY, bold=True, align=PP_ALIGN.CENTER)
flow2 = ["Mark Taken /\nSkipped", "Today Dashboard\nUpdates", "Low Stock\nDetected", "Refill\nReminder"]
flow_row(s, Inches(0.4), Inches(3.7), Inches(12.5), Inches(1.0), flow2,
          box_color=[ORANGE, NAVY, BLUE, BLUE], size=12.5)

add_text(s, Inches(0.4), Inches(5.05), Inches(6.0), Inches(0.35),
          "Required Modules", size=15, color=GREEN, bold=True, font=HEAD_FONT)
add_bullets(s, Inches(0.4), Inches(5.5), Inches(6.0), Inches(1.7), [
    ("Profiles —", "individual + linked family-unit accounts."),
    ("Prescriptions —", "manual entry and camera-based capture."),
    ("Schedule —", "dosage, frequency, timing → auto-generated calendar."),
], size=11.5)
add_bullets(s, Inches(6.9), Inches(5.5), Inches(6.0), Inches(1.7), [
    ("Reminders —", "escalating in-app / push notifications."),
    ("Dashboard —", "unified \"Today\" view: upcoming, overdue, low-stock."),
], size=11.5)

# =================================================== SLIDE 4: ARCHITECTURE ==
s = prs.slides.add_slide(BLANK)
scaffold(s, "Technology", "Every Choice Tied to a Specific Requirement", 4)

add_text(s, Inches(0.4), Inches(1.5), Inches(5.9), Inches(0.35),
          "Compact Architecture", size=15, color=GREEN, bold=True, font=HEAD_FONT)
add_rect(s, Inches(0.4), Inches(1.95), Inches(5.9), Inches(0.55), NAVY, round_=True)
add_text(s, Inches(0.4), Inches(1.95), Inches(5.9), Inches(0.55),
          "Client — Responsive PWA (installable, no app store)", size=11.5, color=WHITE,
          bold=True, font=BODY_FONT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, Inches(3.0), Inches(2.5), Inches(0.7), Inches(0.25), "↓", size=16,
          color=GRAY, align=PP_ALIGN.CENTER)
add_rect(s, Inches(0.4), Inches(2.75), Inches(5.9), Inches(0.5), GREEN, round_=True)
add_text(s, Inches(0.4), Inches(2.75), Inches(5.9), Inches(0.5), "API Layer (REST)",
          size=11.5, color=WHITE, bold=True, font=BODY_FONT, align=PP_ALIGN.CENTER,
          anchor=MSO_ANCHOR.MIDDLE)
add_text(s, Inches(3.0), Inches(3.25), Inches(0.7), Inches(0.25), "↓", size=16,
          color=GRAY, align=PP_ALIGN.CENTER)
svc = ["Profile\nService", "Prescription\n+ OCR", "Schedule\nEngine", "Notification\n(escalation)", "Dashboard\nAggregator"]
flow_row(s, Inches(0.4), Inches(3.5), Inches(5.9), Inches(0.85), svc,
          box_color=ORANGE, size=9.5, gap=0.12)
add_text(s, Inches(3.0), Inches(4.42), Inches(0.7), Inches(0.25), "↓", size=16,
          color=GRAY, align=PP_ALIGN.CENTER)
add_rect(s, Inches(0.4), Inches(4.65), Inches(5.9), Inches(0.5), PURPLE, round_=True)
add_text(s, Inches(0.4), Inches(4.65), Inches(5.9), Inches(0.5),
          "PostgreSQL — family-linked relational schema", size=11.5, color=WHITE,
          bold=True, font=BODY_FONT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_text(s, Inches(6.7), Inches(1.5), Inches(6.2), Inches(0.35),
          "Choice → Requirement It Satisfies", size=15, color=GREEN, bold=True, font=HEAD_FONT)
stack_rows = [
    ("Responsive PWA, not native app", "\"Any household member, regardless of age or technical comfort\" — one link, no install/app-store barrier."),
    ("OCR capture + manual-edit fallback", "\"Camera-based capture\" is required, but OCR is never 100% — manual fallback keeps it usable for every comfort level."),
    ("Rule-based schedule engine", "Converts dosage + frequency into the required \"auto-generated calendar,\" not a manual calendar entry chore."),
    ("Escalating notification queue", "Directly implements the \"escalating in-app / push\" reminder requirement (gentle → repeat → caregiver alert)."),
    ("Family-linked relational schema", "Backs both \"linked family-unit profiles\" and the shared \"Today\" dashboard from one data model."),
]
ry = Inches(1.95)
for choice, why in stack_rows:
    add_text(s, Inches(6.7), ry, Inches(6.2), Inches(0.3), choice, size=11.5,
              color=NAVY, bold=True, font=BODY_FONT)
    add_text(s, Inches(6.7), ry + Inches(0.28), Inches(6.2), Inches(0.6), why,
              size=10.5, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.1)
    ry += Inches(0.95)

# ============================================== SLIDE 5: PRIORITIZATION ====
s = prs.slides.add_slide(BLANK)
scaffold(s, "Scope Discipline", "Feature Prioritization: What Ships When, and Why", 5)

prio_rows = [
    ("Must-Have", GREEN, "Profiles, prescriptions, schedule, reminders, dashboard",
     "Forgetfulness / lost prescriptions",
     "The full loop has to work live in the demo — none of it is optional."),
    ("Should-Have", ORANGE, "Low-stock alerts, Smart Scan, Care Circle",
     "Stock-outs / no family visibility",
     "High value, but the product is still demonstrable without them — ships weeks after v1."),
    ("Could-Have", PURPLE, "Doctor/pharmacy portal, wearable integration",
     "Future roadmap",
     "Depends on external partnerships/SDKs outside a prototype timeline."),
]
headers2 = ["Priority", "Feature", "Solves", "Why This Tier"]
col_x2 = [Inches(0.4), Inches(2.1), Inches(5.6), Inches(8.6)]
col_w2 = [Inches(1.7), Inches(3.5), Inches(3.0), Inches(4.3)]
hy2 = Inches(1.65)
for cx, cw, h in zip(col_x2, col_w2, headers2):
    add_rect(s, cx, hy2, cw, Inches(0.4), NAVY)
    add_text(s, cx + Inches(0.12), hy2, cw - Inches(0.24), Inches(0.4), h,
              size=12, color=WHITE, bold=True, font=BODY_FONT, anchor=MSO_ANCHOR.MIDDLE)
ry2 = hy2 + Inches(0.4)
row_h2 = Inches(1.35)
for i, (prio, color, feat, solves, why) in enumerate(prio_rows):
    bg = LIGHT_BG if i % 2 == 0 else WHITE
    add_rect(s, col_x2[0], ry2, col_x2[3] + col_w2[3] - col_x2[0], row_h2, bg, line=True)
    add_rect(s, col_x2[0] + Inches(0.15), ry2 + Inches(0.28), Inches(1.4), Inches(0.4), color, round_=True)
    add_text(s, col_x2[0] + Inches(0.15), ry2 + Inches(0.28), Inches(1.4), Inches(0.4), prio,
              size=11.5, color=WHITE, bold=True, font=BODY_FONT, align=PP_ALIGN.CENTER,
              anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, col_x2[1] + Inches(0.12), ry2, col_w2[1] - Inches(0.24), row_h2, feat,
              size=11.5, color=TEXT, italic=True, font=BODY_FONT, anchor=MSO_ANCHOR.MIDDLE,
              line_spacing=1.1)
    add_text(s, col_x2[2] + Inches(0.12), ry2, col_w2[2] - Inches(0.24), row_h2, solves,
              size=11.5, color=NAVY, bold=True, font=BODY_FONT, anchor=MSO_ANCHOR.MIDDLE,
              line_spacing=1.1)
    add_text(s, col_x2[3] + Inches(0.12), ry2, col_w2[3] - Inches(0.24), row_h2, why,
              size=10.5, color=GRAY, italic=True, font=BODY_FONT, anchor=MSO_ANCHOR.MIDDLE,
              line_spacing=1.1)
    ry2 += row_h2

add_text(s, Inches(0.4), ry2 + Inches(0.25), Inches(12.5), Inches(0.6),
          "Prioritisation rule: a feature earns Must-Have only if the product is broken without it "
          "on day one — everything else is sequenced by how directly it closes one of the four core problems.",
          size=12, color=PURPLE, bold=True, italic=True, font=BODY_FONT, line_spacing=1.15)

# ============================================ SLIDE 6: ORIGINAL FEATURE ====
s = prs.slides.add_slide(BLANK)
scaffold(s, "Creativity", "Original Feature: The Doctor-Ready Adherence Brief", 6)
add_text(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(0.6),
          "The brief names the failure mode directly: once a prescription is lost, patients "
          "re-guess dosage rather than going back to a doctor. Every dose-tracking app logs "
          "data — almost none close the loop back to the clinical relationship. This does.",
          size=13, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.2)

add_text(s, Inches(0.4), Inches(2.55), Inches(6.0), Inches(0.35),
          "How It Works", size=15, color=GREEN, bold=True, font=HEAD_FONT)
brief_flow = ["Dose logs +\nprescriptions\n(already captured)", "Tap \"Prepare\nVisit Summary\"\non Dashboard", "Auto-generated\none-page brief"]
flow_row(s, Inches(0.4), Inches(3.0), Inches(6.0), Inches(1.1), brief_flow,
          box_color=[NAVY, ORANGE, GREEN], size=11.5)
add_bullets(s, Inches(0.4), Inches(4.35), Inches(6.0), Inches(2.0), [
    ("Contents:", "adherence %, missed-dose pattern, current stock, upcoming renewals."),
    ("Output:", "shareable PDF/link — show it on-phone or send ahead of the appointment."),
    ("Cost to build:", "near-zero — it's a report over data the Must-Have loop already captures."),
], size=12)

add_text(s, Inches(6.9), Inches(2.55), Inches(6.0), Inches(0.35),
          "Why It's the Differentiator", size=15, color=PURPLE, bold=True, font=HEAD_FONT)
add_rect(s, Inches(6.9), Inches(3.0), Inches(6.0), Inches(3.35), LIGHT_BG)
add_text(s, Inches(7.1), Inches(3.2), Inches(5.6), Inches(3.0),
          "Competing apps optimise for \"did you take your pill today.\" MediTrack optimises for "
          "the actual downstream harm named in the brief — patients guessing dosages because "
          "going back to a doctor feels like starting over. By turning three months of adherence "
          "history into a one-tap, doctor-ready brief, the app removes the exact friction that "
          "keeps people from returning to care. It's not a bolt-on feature; it's the payoff for "
          "having built the other four modules correctly.",
          size=12.5, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.25)

# ============================================ SLIDE 7: ROADMAP & DEMO ======
s = prs.slides.add_slide(BLANK)
scaffold(s, "Delivery", "Roadmap & What the Live Demo Shows", 7)

phases = [
    ("v1 — Now", GREEN, ["Profiles, prescriptions (manual + camera)", "Auto schedule + escalating reminders",
                          "Today dashboard", "Doctor-Ready Brief (original feature)"]),
    ("v1.1 — Weeks after", ORANGE, ["Low-stock alert tuning", "Smart Scan accuracy improvements",
                                     "Care Circle shared visibility"]),
    ("Future", PURPLE, ["Doctor / pharmacy portal", "Wearable integration",
                         "Requires external partnerships / SDKs"]),
]
cw = Inches(3.95)
cx = Inches(0.4)
for label, color, items in phases:
    add_rect(s, cx, Inches(1.6), cw, Inches(0.55), color, round_=True)
    add_text(s, cx, Inches(1.6), cw, Inches(0.55), label, size=15, color=WHITE,
              bold=True, font=HEAD_FONT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_rect(s, cx, Inches(2.25), cw, Inches(2.15), LIGHT_BG)
    iy = Inches(2.4)
    for it in items:
        add_text(s, cx + Inches(0.18), iy, cw - Inches(0.36), Inches(0.65),
                  "•  " + it, size=11, color=TEXT, italic=True, font=BODY_FONT,
                  line_spacing=1.1)
        iy += Inches(0.55)
    if cx + cw < SW - Inches(1):
        add_text(s, cx + cw, Inches(1.6), Inches(0.35), Inches(0.55), "→", size=18,
                  color=GRAY, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    cx += cw + Inches(0.35)

add_text(s, Inches(0.4), Inches(4.75), Inches(12.5), Inches(0.35),
          "Live Demo Sequence (Must-Have Loop, End to End)", size=15, color=NAVY,
          bold=True, font=HEAD_FONT)
add_text(s, Inches(0.4), Inches(5.2), Inches(12.5), Inches(1.6),
          "Create a family profile  →  scan a paper prescription with the camera  →  watch the "
          "schedule auto-generate  →  a reminder fires and escalates  →  mark the dose taken  →  "
          "the Today dashboard updates live  →  generate a Doctor-Ready Brief from the same data. "
          "Every step traces back to one of the four problems in the brief — nothing shown is a "
          "detour from the core loop.",
          size=12.5, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.25)

prs.save(OUT)
print("Wrote", OUT)
