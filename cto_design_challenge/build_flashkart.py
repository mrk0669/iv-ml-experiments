# -*- coding: utf-8 -*-
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "FlashKart_CTO_BlackFriday.pptx")

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


def scaffold(slide, kicker, title, page_no, subtitle="CTO Presentation"):
    header_h = Inches(0.62)
    add_rect(slide, 0, 0, SW, header_h, BLACK)
    add_text(slide, Inches(0.4), 0, Inches(7.5), header_h,
              "FLASHKART — THE BLACK FRIDAY CRASH", size=13, color=WHITE,
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


def flow_row(slide, x, y, w, h, boxes, gap=0.18, box_color=NAVY,
             text_color=WHITE, arrow_color=GRAY, size=11.5):
    n = len(boxes)
    gap_in = Inches(gap)
    box_w = (w - gap_in * (n - 1)) / n
    cx = x
    for i, label in enumerate(boxes):
        color = box_color[i] if isinstance(box_color, list) else box_color
        add_rect(slide, cx, y, box_w, h, color, round_=True)
        add_text(slide, cx + Inches(0.05), y, box_w - Inches(0.1), h, label,
                  size=size, color=text_color, bold=True, font=BODY_FONT,
                  align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.05)
        if i < n - 1:
            add_text(slide, cx + box_w, y, gap_in, h, "→", size=16,
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
add_text(s, Inches(0.6), band_h / 2 - Inches(0.85), SW - Inches(1.2), Inches(1.0),
          "The Black Friday Crash", size=42, color=WHITE, bold=True,
          font=HEAD_FONT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, Inches(0.6), band_h / 2 + Inches(0.2), SW - Inches(1.2), Inches(0.6),
          "Engineering FlashKart for a 50x Traffic Day — Without Failing Again", size=16,
          color=RGBColor(0xFF, 0x9A, 0x4D), italic=True, font=BODY_FONT,
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

fy = band_h + Inches(0.85)
for label, val in [
    ("Perspective", "Chief Technology Officer"),
    ("Prepared By", "Keshav"),
    ("Scale Target", "20,000 daily users → 1,000,000 users in a single day"),
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

add_rect(s, Inches(1.2), fy + Inches(0.05), Inches(6.9), Inches(0.42), RED, round_=True)
add_text(s, Inches(1.2), fy + Inches(0.05), Inches(6.9), Inches(0.42),
          "\"The platform cannot fail again.\" — 3 months, fixed budget.", size=13,
          color=WHITE, bold=True, font=BODY_FONT, align=PP_ALIGN.CENTER,
          anchor=MSO_ANCHOR.MIDDLE)

# ============================================ SLIDE 2: TECHNICAL RISKS =====
s = prs.slides.add_slide(BLANK)
scaffold(s, "1. Technical Risks", "What Actually Breaks at 50x Peak Traffic", 2)
add_text(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(0.5),
          "Last sale's five symptoms all trace back to three root causes — fixing the "
          "symptoms individually would just move the failure point.",
          size=13, color=TEXT, italic=True, font=BODY_FONT)

risk_rows = [
    ("Website crashes / slow loading", RED, "Compute + database can't scale horizontally under a spike",
     "Fixed server counts and one primary DB take the full weight of every request, including repetitive catalog reads."),
    ("Failed payments", ORANGE, "Payment gateway calls made synchronously, no timeout/retry handling",
     "A slow gateway response blocks the whole checkout thread instead of failing gracefully or retrying."),
    ("Duplicate orders", BLUE, "No idempotency on order/payment submission",
     "A user's retried click (or a client-side retry after a timeout) is processed as a brand-new order."),
    ("Customer complaints", GRAY, "No real-time visibility or customer-facing status during failure",
     "Users get a blank error with no explanation, and the team learns about the outage from complaints, not alerts."),
]
headers = ["Symptom (Last Sale)", "Root Cause", "Why It Happens"]
col_x = [Inches(0.4), Inches(3.4), Inches(7.0)]
col_w = [Inches(2.9), Inches(3.5), Inches(5.5)]
hy = Inches(2.15)
for cx, cw, h in zip(col_x, col_w, headers):
    add_rect(s, cx, hy, cw, Inches(0.4), NAVY)
    add_text(s, cx + Inches(0.12), hy, cw - Inches(0.24), Inches(0.4), h,
              size=12, color=WHITE, bold=True, font=BODY_FONT, anchor=MSO_ANCHOR.MIDDLE)
ry = hy + Inches(0.4)
row_h = Inches(1.05)
for i, (sym, color, cause, why) in enumerate(risk_rows):
    bg = LIGHT_BG if i % 2 == 0 else WHITE
    add_rect(s, col_x[0], ry, col_x[2] + col_w[2] - col_x[0], row_h, bg, line=True)
    add_rect(s, col_x[0], ry, Inches(0.1), row_h, color)
    add_text(s, col_x[0] + Inches(0.22), ry, col_w[0] - Inches(0.3), row_h, sym,
              size=12, color=NAVY, bold=True, font=BODY_FONT, anchor=MSO_ANCHOR.MIDDLE,
              line_spacing=1.05)
    add_text(s, col_x[1] + Inches(0.12), ry, col_w[1] - Inches(0.24), row_h, cause,
              size=11, color=TEXT, bold=True, italic=True, font=BODY_FONT,
              anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.1)
    add_text(s, col_x[2] + Inches(0.12), ry, col_w[2] - Inches(0.24), row_h, why,
              size=11, color=GRAY, italic=True, font=BODY_FONT, anchor=MSO_ANCHOR.MIDDLE,
              line_spacing=1.1)
    ry += row_h

add_text(s, Inches(0.4), ry + Inches(0.2), Inches(12.5), Inches(0.4),
          "Three fixes — elastic compute/caching, async payment handling, and idempotent "
          "writes — address all five symptoms at the source.",
          size=12.5, color=PURPLE, bold=True, italic=True, font=BODY_FONT)

# ==================================================== SLIDE 3: INFRA STRAT =
s = prs.slides.add_slide(BLANK)
scaffold(s, "2. Infrastructure Strategy", "Redesigning the Request Path for Scale", 3)
add_text(s, Inches(0.4), Inches(1.45), Inches(12.5), Inches(0.4),
          "Design principle: 90%+ of peak traffic is browsing, not buying — cache it "
          "aggressively so only real purchase intent reaches the database.",
          size=12.5, color=TEXT, italic=True, font=BODY_FONT)

layers = ["CDN / Edge Cache\n(static + catalog)", "Load Balancer\n+ Waiting Room",
          "Auto-Scaling\nStateless App Tier", "Redis Cache\n(hot reads)",
          "Async Order Queue\n(checkout writes)", "Sharded DB +\nRead Replicas"]
flow_row(s, Inches(0.4), Inches(2.05), Inches(12.5), Inches(0.95), layers,
          box_color=[GREEN, NAVY, ORANGE, GREEN, PURPLE, NAVY], size=10.5)

add_text(s, Inches(0.4), Inches(3.3), Inches(6.0), Inches(0.35),
          "Key Architecture Decisions", size=14.5, color=GREEN, bold=True, font=HEAD_FONT)
add_bullets(s, Inches(0.4), Inches(3.75), Inches(6.0), Inches(3.3), [
    ("Cache the catalog, not just the CDN:", "product/browse pages served from CDN + Redis, "
     "so browsing traffic never touches the primary database."),
    ("Decouple checkout from fulfillment:", "\"place order\" writes to a queue and returns "
     "immediately; inventory/fulfillment processes it asynchronously — smooths the spike "
     "instead of forcing the DB to absorb it in real time."),
    ("Auto-scale stateless compute only:", "app servers hold no session state, so Kubernetes "
     "HPA (or equivalent) can add capacity in seconds without sticky-session complexity."),
    ("Shard or read-replica the database:", "writes go to a right-sized primary; reads (the "
     "vast majority) are served from replicas."),
], size=11.5)

add_rect(s, Inches(6.9), Inches(3.3), Inches(6.0), Inches(3.75), LIGHT_BG)
add_text(s, Inches(7.1), Inches(3.45), Inches(5.6), Inches(0.3),
          "Trade-off, Stated Plainly", size=13, color=PURPLE, bold=True, font=HEAD_FONT)
add_text(s, Inches(7.1), Inches(3.8), Inches(5.6), Inches(3.1),
          "Async checkout means a customer's order confirmation may lag by a few seconds "
          "during peak load rather than being instant — an acceptable trade against the "
          "alternative of the entire site going down. This is disclosed on the confirmation "
          "screen (\"processing your order\") rather than hidden, which also softens the "
          "customer-complaints risk from Slide 2. With a 3-month timeline and fixed budget, "
          "this architecture reuses managed cloud services (managed Kubernetes, managed "
          "Redis/queue, managed Postgres read replicas) instead of building custom "
          "infrastructure — buy proven scale, don't build it from scratch under deadline.",
          size=11.5, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.25)

# ================================================ SLIDE 4: RELIABILITY =====
s = prs.slides.add_slide(BLANK)
scaffold(s, "3. Reliability Measures", "High Availability and Graceful Degradation", 4)
add_text(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(0.5),
          "The goal isn't zero load-shedding — it's making sure that when something has to "
          "give, it's never checkout.",
          size=13, color=TEXT, italic=True, font=BODY_FONT)

wr_flow = ["Incoming\nRequest", "Virtual Waiting\nRoom (token queue)", "Rate-Limited\nEntry",
           "Checkout\n(protected)"]
flow_row(s, Inches(0.4), Inches(2.2), Inches(6.0), Inches(0.95), wr_flow,
          box_color=[GRAY, ORANGE, NAVY, GREEN], size=10.5)
add_text(s, Inches(0.4), Inches(3.3), Inches(6.0), Inches(0.6),
          "Users past capacity wait in a queue with a visible position/ETA instead of "
          "hammering a struggling backend — the same pattern large retailers use on drop days.",
          size=11, color=GRAY, italic=True, font=BODY_FONT, line_spacing=1.15)

add_text(s, Inches(0.4), Inches(4.05), Inches(6.0), Inches(0.35),
          "Other HA Measures", size=14, color=GREEN, bold=True, font=HEAD_FONT)
add_bullets(s, Inches(0.4), Inches(4.5), Inches(6.0), Inches(2.4), [
    ("Multi-AZ redundancy:", "no single data-center failure takes the platform down."),
    ("Circuit breakers,", "so one failing dependency (e.g. recommendations service) can't cascade into checkout."),
], size=11.5)

add_text(s, Inches(6.9), Inches(2.2), Inches(6.0), Inches(0.35),
          "Graceful Degradation Ladder", size=14, color=PURPLE, bold=True, font=HEAD_FONT)
degrade_rows = [
    ("First to go", ORANGE, "Recommendations, reviews, \"related products\" — non-critical, cache-safe to disable."),
    ("Second", BLUE, "Search relevance ranking falls back to simple/cached results."),
    ("Never", RED, "Checkout, payment, and order confirmation — protected above all else."),
]
ry = Inches(2.65)
for label, color, desc in degrade_rows:
    add_rect(s, Inches(6.9), ry, Inches(1.7), Inches(0.85), color, round_=True)
    add_text(s, Inches(7.0), ry, Inches(1.5), Inches(0.85), label, size=12, color=WHITE,
              bold=True, font=BODY_FONT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
              line_spacing=1.05)
    add_rect(s, Inches(8.75), ry, Inches(4.15), Inches(0.85), LIGHT_BG)
    add_text(s, Inches(8.9), ry, Inches(3.9), Inches(0.85), desc, size=11, color=TEXT,
              italic=True, font=BODY_FONT, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.1)
    ry += Inches(1.0)
add_text(s, Inches(6.9), ry + Inches(0.05), Inches(6.0), Inches(0.9),
          "Feature flags make each tier a single toggle, tested during load-test game days "
          "(Slide 7) so no one is deciding this live under pressure.",
          size=11, color=GRAY, italic=True, font=BODY_FONT, line_spacing=1.15)

# =========================================== SLIDE 5: SECURITY & PAYMENTS =
s = prs.slides.add_slide(BLANK)
scaffold(s, "4. Security & Payments", "Protecting Customer Data and Money Under Load", 5)
add_text(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(0.5),
          "A high-traffic sale is also the highest-value day of the year for an attacker — "
          "security and reliability are the same workstream here, not two.",
          size=13, color=TEXT, italic=True, font=BODY_FONT)

add_text(s, Inches(0.4), Inches(2.2), Inches(6.0), Inches(0.35),
          "Fixing Duplicate Orders & Failed Payments", size=14, color=GREEN, bold=True, font=HEAD_FONT)
add_bullets(s, Inches(0.4), Inches(2.65), Inches(6.0), Inches(2.4), [
    ("Idempotency keys", "on every order/payment request — a retried click resolves to the "
     "same order, never a duplicate."),
    ("Multi-provider payment failover:", "if the primary gateway times out, retry through a "
     "secondary provider instead of failing the sale outright."),
], size=12)

add_text(s, Inches(0.4), Inches(4.75), Inches(6.0), Inches(0.35),
          "Protecting Customer Data", size=14, color=GREEN, bold=True, font=HEAD_FONT)
add_bullets(s, Inches(0.4), Inches(5.2), Inches(6.0), Inches(1.7), [
    ("Tokenized payments (PCI-DSS scope):", "card data never touches FlashKart's own "
     "servers — handled by the payment processor's vault."),
    ("WAF + DDoS protection at the edge,", "since a high-profile sale is a bigger target on the one day it can least afford downtime."),
], size=11.5)

add_text(s, Inches(6.9), Inches(2.2), Inches(6.0), Inches(0.35),
          "Protecting Inventory From Bots", size=14, color=PURPLE, bold=True, font=HEAD_FONT)
add_rect(s, Inches(6.9), Inches(2.65), Inches(6.0), Inches(3.9), LIGHT_BG)
add_text(s, Inches(7.1), Inches(2.8), Inches(5.6), Inches(3.6),
          "Scalper bots checking out high-demand items faster than real customers is a "
          "security problem that shows up as a customer-trust problem — real users see "
          "\"sold out\" seconds after launch and blame the platform, not the bots. Rate "
          "limiting per account/IP and basic bot-detection heuristics on the checkout "
          "endpoint (paired with the waiting-room queue from Slide 4) keep the sale fair, "
          "which is as much a reliability measure for customer trust as it is a security "
          "control.",
          size=12, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.25)

# ===================================== SLIDE 6: MONITORING & INCIDENT =====
s = prs.slides.add_slide(BLANK)
scaffold(s, "5. Monitoring & Incident Response", "If It Crashes Anyway, Here's What Happens", 6)
add_text(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(0.5),
          "\"It cannot fail again\" also means: if it does degrade, the team's response is "
          "rehearsed, not improvised.",
          size=13, color=TEXT, italic=True, font=BODY_FONT)

loop = ["Real-Time\nDashboards", "Alert Fires\n(threshold breach)", "On-Call +\nIncident Commander",
        "Runbook: Kill\nSwitch / Rollback", "Status Page\nUpdated", "Postmortem →\nFix Root Cause"]
flow_row(s, Inches(0.4), Inches(2.25), Inches(12.5), Inches(0.95), loop,
          box_color=[GREEN, ORANGE, NAVY, RED, PURPLE, GREEN], size=10)

add_text(s, Inches(0.4), Inches(3.55), Inches(6.0), Inches(0.35),
          "What's Being Watched Live", size=14, color=GREEN, bold=True, font=HEAD_FONT)
add_bullets(s, Inches(0.4), Inches(4.0), Inches(6.0), Inches(2.6), [
    ("Error rate & p95/p99 latency", "per service — the earliest signal something's degrading."),
    ("Payment success rate", "and queue depth on the order-processing pipeline."),
    ("Autoscaler activity,", "so capacity additions are visible, not assumed."),
], size=11.5)

add_text(s, Inches(6.9), Inches(3.55), Inches(6.0), Inches(0.35),
          "Roles, Defined Before Sale Day", size=14, color=PURPLE, bold=True, font=HEAD_FONT)
add_rect(s, Inches(6.9), Inches(4.0), Inches(6.0), Inches(2.6), LIGHT_BG)
add_text(s, Inches(7.1), Inches(4.15), Inches(5.6), Inches(2.3),
          "Incident Commander (single decision-maker), subsystem leads for infra/payments/"
          "checkout, and a comms lead who owns the status page — assigned in advance, not "
          "volunteered live. Every degradation tier from Slide 4's ladder maps to a specific "
          "runbook step, so the team executes a checklist under pressure instead of debating "
          "options.",
          size=11.5, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.25)

# ============================================== SLIDE 7: 3-MONTH TIMELINE ==
s = prs.slides.add_slide(BLANK)
scaffold(s, "Execution", "The 3-Month Path to Sale Day", 7)

phases = [
    ("Month 1", GREEN, ["Redesign request path (caching, queue, autoscaling)",
                         "Idempotency + payment failover implemented",
                         "Monitoring dashboards + alert thresholds live"]),
    ("Month 2", ORANGE, ["Load test at simulated 1M users", "Chaos-engineering game days",
                          "rehearsing the incident runbook end to end"]),
    ("Month 3", RED, ["Load test at 1.5x expected peak", "Feature freeze on non-critical changes",
                        "Go/no-go review with roles + kill switches confirmed"]),
]
cw = Inches(3.95)
cx = Inches(0.4)
for label, color, items in phases:
    add_rect(s, cx, Inches(1.6), cw, Inches(0.55), color, round_=True)
    add_text(s, cx, Inches(1.6), cw, Inches(0.55), label, size=15, color=WHITE,
              bold=True, font=HEAD_FONT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_rect(s, cx, Inches(2.25), cw, Inches(2.4), LIGHT_BG)
    iy = Inches(2.4)
    for it in items:
        add_text(s, cx + Inches(0.18), iy, cw - Inches(0.36), Inches(0.75),
                  "•  " + it, size=11, color=TEXT, italic=True, font=BODY_FONT,
                  line_spacing=1.1)
        iy += Inches(0.7)
    if cx + cw < SW - Inches(1):
        add_text(s, cx + cw, Inches(1.6), Inches(0.35), Inches(0.55), "→", size=18,
                  color=GRAY, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    cx += cw + Inches(0.35)

add_text(s, Inches(0.4), Inches(4.9), Inches(12.5), Inches(0.35),
          "Budget Discipline", size=14, color=PURPLE, bold=True, font=HEAD_FONT)
add_text(s, Inches(0.4), Inches(5.35), Inches(12.5), Inches(1.0),
          "Every component above is a managed cloud service, not custom-built infrastructure "
          "— the fixed budget goes into engineering time on caching, queueing, and testing, "
          "not into standing up and operating new systems from scratch under a 3-month clock.",
          size=12, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.2)

# ============================================== SLIDE 8: SUCCESS METRICS ===
s = prs.slides.add_slide(BLANK)
scaffold(s, "6. Success Metrics", "How We'll Know It Actually Worked", 8)

metrics = [
    ("Uptime during sale window", GREEN, "Target: 99.9%+ — effectively zero customer-visible downtime."),
    ("p95 page load time", ORANGE, "Target: under 2 seconds, even at peak concurrent load."),
    ("Payment success rate", BLUE, "Target: 99%+, with automatic failover absorbing gateway blips."),
    ("Order duplication rate", RED, "Target: ~0% — the direct proof idempotency worked."),
    ("Autoscaling response time", PURPLE, "Time from traffic spike to added capacity online."),
    ("Mean time to recovery (MTTR)", NAVY, "If an incident does occur, how fast the runbook resolves it."),
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
          "Success isn't \"nothing broke\" — it's that every number above is visible in "
          "real time on sale day, so if something does start to degrade, it's caught and "
          "handled before a customer ever notices. That's what turns \"the platform cannot "
          "fail again\" from a mandate into an engineering plan.",
          size=13, color=TEXT, italic=True, font=BODY_FONT, line_spacing=1.25)

prs.save(OUT)
print("Wrote", OUT)
