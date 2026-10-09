# -*- coding: utf-8 -*-
import os
from PIL import Image as PILImage

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, NextPageTemplate,
    Paragraph, Spacer, Image, Table, TableStyle, PageBreak,
    KeepTogether, HRFlowable, ListFlowable, ListItem
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

HERE = os.path.dirname(__file__)
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "Sustainable_Resource_Marketplace_Technical_Design_Report.pdf")

# ------------------------------------------------------------------ fonts --
FONT_DIR = r"C:\Windows\Fonts"

pdfmetrics.registerFont(TTFont("SegoeUI", os.path.join(FONT_DIR, "segoeui.ttf")))
pdfmetrics.registerFont(TTFont("SegoeUI-Bold", os.path.join(FONT_DIR, "segoeuib.ttf")))
pdfmetrics.registerFont(TTFont("SegoeUI-Italic", os.path.join(FONT_DIR, "segoeuii.ttf")))
pdfmetrics.registerFont(TTFont("SegoeUI-BoldItalic", os.path.join(FONT_DIR, "segoeuiz.ttf")))
addMapping("SegoeUI", 0, 0, "SegoeUI")
addMapping("SegoeUI", 1, 0, "SegoeUI-Bold")
addMapping("SegoeUI", 0, 1, "SegoeUI-Italic")
addMapping("SegoeUI", 1, 1, "SegoeUI-BoldItalic")

pdfmetrics.registerFont(TTFont("CenturyGothic", os.path.join(FONT_DIR, "CENTURY.TTF")))
pdfmetrics.registerFont(TTFont("CenturyGothic-Bold", os.path.join(FONT_DIR, "GOTHICB.TTF")))
pdfmetrics.registerFont(TTFont("CenturyGothic-Italic", os.path.join(FONT_DIR, "GOTHICI.TTF")))
pdfmetrics.registerFont(TTFont("CenturyGothic-BoldItalic", os.path.join(FONT_DIR, "GOTHICBI.TTF")))
addMapping("CenturyGothic", 0, 0, "CenturyGothic")
addMapping("CenturyGothic", 1, 0, "CenturyGothic-Bold")
addMapping("CenturyGothic", 0, 1, "CenturyGothic-Italic")
addMapping("CenturyGothic", 1, 1, "CenturyGothic-BoldItalic")

# ---------------------------------------------------------------- palette --
# Sampled from the reference deck (ISRO Bharatiya Antariksh Hackathon style):
# navy headings, near-black body text, black header bar, green/orange/purple
# accent blocks, and an orange -> purple -> blue gradient rule.
NAVY = colors.HexColor("#0B2447")
GREEN = colors.HexColor("#1B7F5B")
ORANGE = colors.HexColor("#E06A1F")
BLUE = colors.HexColor("#4658C9")
PURPLE = colors.HexColor("#5E4198")
GRAY = colors.HexColor("#5B6472")
LIGHT_BG = colors.HexColor("#F3F4F8")
BORDER = colors.HexColor("#D7DCE8")
TEXT = colors.HexColor("#22222A")
HEADER_BLACK = colors.HexColor("#000000")
WHITE = colors.white

GRADIENT_STOPS = [
    (255, 101, 1), (255, 102, 0), (238, 105, 4), (221, 105, 54),
    (203, 107, 82), (184, 108, 108), (167, 108, 136), (148, 110, 159),
    (130, 109, 184), (108, 111, 206), (89, 111, 231),
]

def gradient_color_at(t):
    n = len(GRADIENT_STOPS) - 1
    t = min(max(t, 0), 1)
    idx = min(int(t * n), n - 1)
    local_t = t * n - idx
    c1, c2 = GRADIENT_STOPS[idx], GRADIENT_STOPS[idx + 1]
    return tuple((c1[k] + (c2[k] - c1[k]) * local_t) / 255.0 for k in range(3))

def draw_gradient_bar(c, x, y, w, h, steps=140):
    step_w = w / steps
    for i in range(steps):
        t = i / (steps - 1)
        c.setFillColorRGB(*gradient_color_at(t))
        c.rect(x + i * step_w, y, step_w + 0.7, h, stroke=0, fill=1)

PAGE_W, PAGE_H = LETTER
MARGIN = 0.72 * inch
CONTENT_W = PAGE_W - 2 * MARGIN

# ---------------------------------------------------------------- styles --
ss = getSampleStyleSheet()

def style(name, **kw):
    base = kw.pop("parent", ss["Normal"])
    return ParagraphStyle(name, parent=base, **kw)

S_CoverMeta = style("CoverMeta", fontName="SegoeUI", fontSize=10.5,
                     leading=17, textColor=TEXT, alignment=TA_LEFT)

S_H1 = style("H1", fontName="CenturyGothic-Bold", fontSize=19, leading=23,
             textColor=NAVY, spaceBefore=6, spaceAfter=12)
S_H2 = style("H2", fontName="CenturyGothic-Bold", fontSize=14, leading=18,
             textColor=GREEN, spaceBefore=16, spaceAfter=8)
S_H3 = style("H3", fontName="CenturyGothic-Bold", fontSize=12, leading=15,
             textColor=PURPLE, spaceBefore=10, spaceAfter=6)

S_Body = style("Body", fontName="SegoeUI", fontSize=10, leading=14.5,
               textColor=TEXT, alignment=TA_JUSTIFY, spaceAfter=8)
S_BodyTight = style("BodyTight", parent=S_Body, spaceAfter=4)
S_Bullet = style("Bullet", parent=S_Body, leftIndent=14, bulletIndent=2,
                  spaceAfter=4)
S_Caption = style("Caption", fontName="SegoeUI-Italic", fontSize=9,
                   leading=12, textColor=GRAY, alignment=TA_CENTER,
                   spaceBefore=6, spaceAfter=14)
S_TOCHeading = style("TOCHeading", fontName="CenturyGothic-Bold", fontSize=19,
                      textColor=NAVY, spaceAfter=14)
S_TableCell = style("TableCell", fontName="SegoeUI", fontSize=9,
                     leading=12.5, textColor=TEXT)
S_TableCellBold = style("TableCellBold", parent=S_TableCell,
                         fontName="SegoeUI-Bold", textColor=WHITE)
S_TableHead = style("TableHead", fontName="SegoeUI-Bold", fontSize=9.5,
                     leading=12, textColor=WHITE)
S_Quote = style("Quote", fontName="SegoeUI-Italic", fontSize=10.5,
                 leading=15, textColor=NAVY, alignment=TA_LEFT,
                 leftIndent=16, spaceBefore=6, spaceAfter=10)

# --------------------------------------------------------------- helpers --
def fitted_image(filename, max_w, max_h=None):
    path = os.path.join(ASSETS, filename)
    im = PILImage.open(path)
    w, h = im.size
    ratio = max_w / float(w)
    new_w = max_w
    new_h = h * ratio
    if max_h and new_h > max_h:
        ratio2 = max_h / float(new_h)
        new_w *= ratio2
        new_h = max_h
    return Image(path, width=new_w, height=new_h)

def figure(filename, caption, max_w=CONTENT_W, max_h=6.6 * inch):
    img = fitted_image(filename, max_w, max_h)
    cap = Paragraph(caption, S_Caption)
    return KeepTogether([img, cap])

def bullets(items, style_=S_Bullet, bullet_char="•"):
    return ListFlowable(
        [ListItem(Paragraph(f"<i>{t}</i>", style_), leftIndent=6) for t in items],
        bulletType="bullet", bulletChar=bullet_char, start=None,
        leftIndent=16, bulletFontSize=8, bulletColor=ORANGE,
        spaceBefore=2, spaceAfter=8
    )

def make_table(data, col_widths, header_bg=NAVY, zebra=LIGHT_BG,
                font_size=9):
    rows = []
    for r, row in enumerate(data):
        if r == 0:
            rows.append([Paragraph(c, S_TableHead) for c in row])
        else:
            rows.append([Paragraph(c, S_TableCell) for c in row])
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.6, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), zebra))
    t.setStyle(TableStyle(style_cmds))
    return t

def section_heading(text, level=1, toc_text=None):
    """Paragraph tagged so afterFlowable can register it for TOC + bookmarks."""
    s = S_H1 if level == 1 else S_H2
    bm = f"bm_{abs(hash(text))}"
    p = Paragraph(text, s)
    p._bookmarkName = bm
    p._tocLevel = level - 1
    p._tocText = toc_text or text
    return p

# -------------------------------------------------------- doc / template --
class ReportDoc(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and hasattr(flowable, "_bookmarkName"):
            level = flowable._tocLevel
            text = flowable._tocText
            key = flowable._bookmarkName
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=level, closed=False)
            self.notify("TOCEntry", (level, text, self.page, key))


HEADER_H = 0.5 * inch

def on_page(canvas, doc):
    canvas.saveState()
    # black running header bar
    canvas.setFillColor(HEADER_BLACK)
    canvas.rect(0, PAGE_H - HEADER_H, PAGE_W, HEADER_H, stroke=0, fill=1)
    canvas.setFont("SegoeUI-Bold", 9)
    canvas.setFillColor(colors.white)
    canvas.drawString(MARGIN, PAGE_H - HEADER_H / 2 - 3,
                       "SUSTAINABLE RESOURCE MARKETPLACE")
    canvas.setFont("SegoeUI-Italic", 9)
    canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - HEADER_H / 2 - 3,
                            "Technical Design Report")
    # thin gradient rule under the header
    draw_gradient_bar(canvas, 0, PAGE_H - HEADER_H - 0.045 * inch, PAGE_W, 0.045 * inch)
    # footer gradient bar
    draw_gradient_bar(canvas, 0, 0, PAGE_W, 0.09 * inch)
    canvas.setFont("SegoeUI-Bold", 8.5)
    canvas.setFillColor(NAVY)
    canvas.drawCentredString(PAGE_W / 2, 0.22 * inch, f"{doc.page}")
    canvas.restoreState()


COVER_BAND_H = 2.15 * inch

def on_cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(HEADER_BLACK)
    canvas.rect(0, PAGE_H - COVER_BAND_H, PAGE_W, COVER_BAND_H, stroke=0, fill=1)
    draw_gradient_bar(canvas, 0, PAGE_H - COVER_BAND_H - 0.09 * inch, PAGE_W, 0.09 * inch)
    draw_gradient_bar(canvas, 0, 0, PAGE_W, 0.11 * inch)
    canvas.setFont("CenturyGothic-Bold", 29)
    canvas.setFillColor(colors.white)
    canvas.drawCentredString(PAGE_W / 2, PAGE_H - COVER_BAND_H / 2 + 16,
                              "Sustainable Resource Marketplace")
    canvas.setFont("SegoeUI-Italic", 14.5)
    canvas.setFillColor(colors.HexColor("#FF9A4D"))
    canvas.drawCentredString(PAGE_W / 2, PAGE_H - COVER_BAND_H / 2 - 16,
                              "A Technical Design Report")
    canvas.restoreState()


doc = ReportDoc(OUT, pagesize=LETTER,
                 topMargin=HEADER_H + 0.35 * inch, bottomMargin=0.6 * inch,
                 leftMargin=MARGIN, rightMargin=MARGIN,
                 title="Sustainable Resource Marketplace — Technical Design Report",
                 author="Chief Technology Officer")

frame_normal = Frame(MARGIN, doc.bottomMargin, CONTENT_W,
                      PAGE_H - doc.topMargin - doc.bottomMargin, id="normal")
frame_cover = Frame(MARGIN, doc.bottomMargin, CONTENT_W,
                     PAGE_H - doc.topMargin - doc.bottomMargin, id="cover")

doc.addPageTemplates([
    PageTemplate(id="Cover", frames=[frame_cover], onPage=on_cover),
    PageTemplate(id="Normal", frames=[frame_normal], onPage=on_page),
])

story = []

# ============================================================ COVER PAGE ==
def cover_field(label, value):
    return Paragraph(
        f'<font name="SegoeUI-Bold" color="#0B2447">{label} :</font>&nbsp;&nbsp;'
        f'<font name="SegoeUI-Italic" color="#22222A">{value}</font>',
        S_CoverMeta)

story.append(Spacer(1, COVER_BAND_H + 0.09 * inch + 0.55 * inch))
story.append(cover_field("Report Scope",
    "User Experience &amp; Information Architecture &nbsp;|&nbsp; System Architecture "
    "&nbsp;|&nbsp; Technology Stack &amp; Data Management"))
story.append(Spacer(1, 0.22 * inch))
story.append(cover_field("Prepared By", "Keshav"))
story.append(Spacer(1, 0.22 * inch))
story.append(cover_field("Submission", "CTO Design Challenge &mdash; July 2026"))
story.append(NextPageTemplate("Normal"))
story.append(PageBreak())

# =============================================================== TOC ======
toc = TableOfContents()
toc.levelStyles = [
    style("TOC1", fontName="CenturyGothic-Bold", fontSize=11.5, leading=16,
          textColor=NAVY, spaceBefore=8),
    style("TOC2", fontName="SegoeUI", fontSize=10, leading=13.5,
          textColor=TEXT, leftIndent=16, spaceBefore=2),
]
story.append(Paragraph("Table of Contents", S_TOCHeading))
story.append(toc)
story.append(PageBreak())

# ===================================================== EXECUTIVE SUMMARY ==
story.append(section_heading("Executive Summary", level=1))
story.append(Paragraph(
    "The Sustainable Resource Marketplace is a B2B platform that lets businesses list, discover, and "
    "exchange surplus or reusable materials &mdash; industrial byproducts, packaging, textiles, metal and "
    "wood offcuts, decommissioned equipment, and certified recycled inputs &mdash; instead of sending them "
    "to landfill or over-purchasing virgin resources. The platform's job is to make it as easy to source a "
    "verified sustainable resource as it is to buy from a conventional supplier, while making the "
    "environmental impact of every transaction visible and auditable.", S_Body))
story.append(Paragraph(
    "This report sets out the technical direction across three areas: how users experience the product "
    "end-to-end, how the system is architected to support that experience reliably, and which technologies "
    "and data structures underpin it. Four guiding principles run through every decision below:", S_Body))
story.append(bullets([
    "<b>Trust is the product.</b> Business verification, transaction escrow, and transparent sustainability "
    "metrics are treated as core features, not add-ons &mdash; without them the marketplace has no "
    "credibility.",
    "<b>Sustainability data is first-class.</b> CO2e avoided and waste diverted are computed and stored "
    "alongside every listing and transaction, not bolted on as a marketing report.",
    "<b>Modular before distributed.</b> The system starts as a well-factored modular monolith with clear "
    "service boundaries, so it can be split into independently deployed services only when real load "
    "demands it &mdash; avoiding premature infrastructure cost.",
    "<b>Buy commodity, build differentiation.</b> Payments, KYC, maps, and messaging infrastructure are "
    "bought from managed providers; engineering effort is spent on matching, sustainability scoring, and "
    "marketplace trust mechanics, which are the platform's actual differentiators.",
]))

# =========================================== DELIVERABLE I: UX & IA =======
story.append(section_heading("Deliverable I — User Experience &amp; Information Architecture", level=1,
                              toc_text="Deliverable I — UX &amp; Information Architecture"))

story.append(section_heading("1.1 Who Uses the Platform", level=2))
story.append(Paragraph(
    "Three primary personas drive every design decision. Suppliers and buyers are frequently the same "
    "organization wearing different hats on different listings, so account roles are additive rather than "
    "exclusive.", S_Body))

persona_data = [
    ["Persona", "Who they are", "Primary goal", "Key needs"],
    ["Supplier\n(Seller)",
     "Operations or sustainability manager at a business with surplus material, byproducts, or "
     "decommissioned assets.",
     "Turn a liability (waste, storage cost, disposal fees) into revenue or a documented sustainability "
     "outcome.",
     "Fast listing creation, credible buyer inquiries, simple negotiation, proof of pickup/delivery."],
    ["Buyer\n(Procurer)",
     "Procurement or sustainability manager sourcing lower-cost or lower-impact material inputs.",
     "Find verified, fit-for-purpose resources quickly and document the sustainability impact for "
     "internal/ESG reporting.",
     "Reliable search and filtering, seller credibility signals, predictable logistics and pricing."],
    ["Platform Admin",
     "Trust &amp; safety / operations staff employed by the marketplace.",
     "Keep the marketplace safe, resolve disputes, and keep verification and content quality high.",
     "Moderation queues, dispute tooling, audit trails, aggregate analytics."],
]
story.append(make_table(persona_data,
                         [0.9 * inch, 1.9 * inch, 2.0 * inch, 1.9 * inch]))
story.append(Spacer(1, 4))

story.append(section_heading("1.2 Information Architecture", level=2))
story.append(Paragraph(
    "The site is organized around six public-facing sections plus an isolated admin area. Public marketing "
    "and discovery content (Home, Marketplace browse, Company profiles, Resources) is reachable without an "
    "account so search engines and first-time visitors can evaluate the platform. Anything transactional "
    "(listing creation, dashboards, messaging, orders) sits behind an authenticated, KYC-verified business "
    "account. Admin tooling is not linked from the public navigation at all and is reached through a "
    "separate, role-gated console.", S_Body))
story.append(figure("diagram_sitemap.png",
                     "Figure 1. Site map / information architecture, showing public vs. authenticated vs. "
                     "internal surfaces."))

page_table = [
    ["Page", "Purpose"],
    ["Home", "Value proposition, category shortcuts, featured listings, aggregate impact stats "
             "(tonnes of waste diverted platform-wide) to build trust on arrival."],
    ["Marketplace (Browse &amp; Search)", "Faceted search over listings: category, location/radius, quantity, "
             "condition, exchange type (sell / donate / swap), certifications."],
    ["Listing Detail", "Full specs, photos, seller profile summary, computed sustainability metrics "
                        "(CO2e avoided, waste diverted), and the primary RFQ / message CTA."],
    ["Create Listing (wizard)", "Guided multi-step form: category &amp; specs → quantity/condition → "
                                 "photos &amp; documents → sustainability tagging → pricing/exchange terms."],
    ["Seller / Buyer Dashboard", "Active listings or open RFQs, unread messages, orders in flight, and a "
                                  "running sustainability impact tally."],
    ["Messaging &amp; Negotiation", "Real-time thread per transaction; structured fields for offer price, "
                                     "quantity, and pickup window alongside free-text chat."],
    ["Transaction / Checkout", "Reviews agreed terms, initiates escrow payment, and schedules logistics."],
    ["Order Tracking", "Shipment status, carrier tracking, delivery confirmation, dispute entry point."],
    ["Company Profile", "Verification badge, certifications, ratings, transaction history — the platform's "
                         "core trust signal."],
    ["Sustainability Impact Report", "Per-transaction and cumulative CO2e / waste-diverted figures, "
                                      "exportable for ESG reporting."],
    ["Admin Console", "Business verification queue, listing moderation, dispute resolution, platform "
                       "analytics. Not linked from public nav; role-restricted."],
]
story.append(make_table(page_table, [1.9 * inch, 4.8 * inch]))

story.append(PageBreak())
story.append(section_heading("1.3 Core User Journey", level=2))
story.append(Paragraph(
    "Buyers and suppliers move through parallel journeys that converge at a single shared transaction "
    "flow, then diverge again into shared post-transaction outcomes (reviews, reputation, and the impact "
    "report). Keeping transaction and fulfillment logic in one shared flow &mdash; rather than duplicating it "
    "per role &mdash; is what keeps escrow, logistics, and dispute handling consistent regardless of who "
    "initiated the deal.", S_Body))
story.append(figure("diagram_journey.png",
                     "Figure 2. End-to-end buyer and supplier journeys, converging on a shared transaction "
                     "and fulfillment flow.", max_h=6.9 * inch))

story.append(section_heading("1.4 UX Principles", level=2))
story.append(bullets([
    "<b>Sustainability data up front, not buried.</b> Impact metrics appear on the listing card in search "
    "results, not just the detail page, so they factor into the buyer's decision from the first scan.",
    "<b>Low-friction listing creation.</b> The listing wizard pre-fills sustainability tags from category "
    "selection (e.g. “metal offcuts” auto-suggests a diversion-from-landfill metric) so suppliers "
    "aren't required to be sustainability experts to list correctly.",
    "<b>Trust signals everywhere a decision is made.</b> Verification badges, ratings, and response-time "
    "indicators appear on listing cards, profiles, and inside negotiation threads.",
    "<b>Mobile-responsive by default.</b> Warehouse and facilities staff who physically handle the material "
    "are frequently the ones photographing and listing it on-site; the listing wizard and camera capture "
    "must work well on a phone.",
])),

# ================================================ DELIVERABLE II: ARCH ====
story.append(section_heading("Deliverable II — System Architecture", level=1,
                              toc_text="Deliverable II — System Architecture"))

story.append(section_heading("2.1 Architectural Approach", level=2))
story.append(Paragraph(
    "The system is a modular monolith at launch: one deployable backend, organized internally into the same "
    "service boundaries it would have as microservices, communicating through well-defined interfaces and an "
    "internal event bus rather than shared database tables. This keeps operational overhead low for a small "
    "engineering team while preserving the seams needed to extract any module &mdash; Payments and Search are "
    "the most likely first candidates &mdash; into an independently scaled service once real traffic demands "
    "it. State changes (an RFQ is created, a payment is captured, a shipment updates) are published as events "
    "so that notification, matching, and analytics logic stay decoupled from the transactional path.",
    S_Body))
story.append(figure("diagram_architecture.png",
                     "Figure 3. High-level system architecture: client layer, edge/gateway, core services, "
                     "async event bus, data layer, and cross-cutting/external concerns.", max_h=7.3 * inch))

story.append(PageBreak())
story.append(section_heading("2.2 Component Responsibilities", level=2))
comp_table = [
    ["Component", "Responsibility"],
    ["API Gateway", "TLS termination, JWT authentication, rate limiting, and routing to internal services; "
                     "the single entry point for all client traffic."],
    ["Identity &amp; Business KYC", "Account auth, role management, and the business-verification workflow "
                                     "(document upload → third-party KYC check → verified badge)."],
    ["Listings &amp; Catalog", "CRUD for listings, category taxonomy, media references."],
    ["Search &amp; Discovery", "Indexes listings into OpenSearch; serves faceted search and filtering."],
    ["Matching &amp; Recommendation", "Surfaces relevant listings to buyers and relevant buyers to new "
                                       "listings using category, location, and past-transaction signals."],
    ["Messaging / Negotiation", "Real-time chat over WebSocket, with structured offer fields attached to "
                                 "each transaction thread."],
    ["Transactions &amp; Orders", "Owns transaction state machine (RFQ → negotiating → paid → "
                                   "fulfilled → closed) and coordinates the other services around it."],
    ["Payments", "Thin adapter over Stripe Connect; holds funds in escrow and releases on delivery "
                 "confirmation."],
    ["Logistics Orchestration", "Coordinates pickup/delivery scheduling with third-party carrier APIs and "
                                 "tracks shipment status."],
    ["Sustainability Metrics Engine", "Computes CO2e-avoided and waste-diverted figures per listing "
                                       "and transaction from category-level conversion factors."],
    ["Reviews &amp; Reputation", "Post-transaction ratings and the aggregate reputation score shown on "
                                  "profiles."],
    ["Notification", "Fans out events to email, SMS, and in-app push."],
    ["Admin &amp; Moderation", "Verification review queue, listing moderation, dispute resolution tooling."],
]
story.append(make_table(comp_table, [2.0 * inch, 4.7 * inch]))

story.append(section_heading("2.3 Non-Functional Considerations", level=2))
story.append(bullets([
    "<b>Scalability.</b> Stateless services behind the gateway scale horizontally; Search and Payments are "
    "isolated behind their own interfaces so they can be pulled out and scaled independently first.",
    "<b>Reliability.</b> Event-driven decoupling means a Notification-service outage never blocks a payment "
    "or an RFQ; the queue retries with a dead-letter path for manual triage.",
    "<b>Security.</b> Business KYC verification gates listing and purchasing; payments are handled entirely "
    "by Stripe Connect so the platform never touches raw card data (PCI scope stays minimal); secrets and "
    "IAM are centrally managed rather than embedded per-service.",
    "<b>Observability.</b> Centralized structured logging and distributed tracing across services, with "
    "alerting on transaction-flow error rates and payment/escrow anomalies specifically, since those are the "
    "highest-trust-cost failures.",
]))

# ============================================= DELIVERABLE III: STACK =====
story.append(PageBreak())
story.append(section_heading("Deliverable III — Technology Stack &amp; Data Management", level=1,
                              toc_text="Deliverable III — Technology Stack &amp; Data"))

story.append(section_heading("3.1 Recommended Technology Stack", level=2))
stack_table = [
    ["Layer", "Technology", "Why"],
    ["Frontend (web)", "Next.js (React) + TypeScript, Tailwind CSS",
     "Server-side rendering gives fast first paint and SEO for public listing/marketing pages, which matters "
     "for organic discovery; TypeScript keeps a large codebase maintainable across a growing team."],
    ["Mobile (future)", "React Native",
     "Shares component logic and the team's existing React/TypeScript skillset with the web app, minimizing "
     "the cost of a second client."],
    ["Backend services", "Node.js (NestJS), TypeScript",
     "TypeScript end-to-end reduces context-switching and lets frontend and backend share type definitions "
     "for API contracts; NestJS's module system maps cleanly onto the modular-monolith service boundaries."],
    ["Sustainability Metrics Engine", "Python (FastAPI)",
     "Impact calculations and future ML-based matching benefit from Python's data/ML ecosystem; isolating "
     "this as its own service keeps the core Node.js codebase uniform."],
    ["Realtime messaging", "WebSocket via Socket.IO",
     "Low-latency negotiation chat and live order-status updates without polling."],
    ["Async event bus", "Amazon EventBridge + SQS (Kafka as a later scale option)",
     "Fully managed, no cluster to operate at launch; SQS's dead-letter queues give free retry/failure "
     "handling. Kafka is a straightforward later swap if event volume or replay needs grow."],
    ["Primary database", "PostgreSQL (Amazon RDS)",
     "Strong relational integrity for transactions and payments, native JSONB for the variable attributes "
     "different resource categories need, and a mature managed offering."],
    ["Cache / sessions", "Redis (Amazon ElastiCache)",
     "Session storage, rate-limit counters, and hot-path caching (e.g. category trees, search facets)."],
    ["Search index", "OpenSearch",
     "Faceted, typo-tolerant search over listings at a scale Postgres full-text search won't comfortably "
     "cover; AWS-native and open-source (avoids Elasticsearch licensing complications)."],
    ["Object storage", "Amazon S3 + CloudFront",
     "Durable, cheap storage for listing photos, certification documents, and KYC files, served through a "
     "CDN for fast image loads globally."],
    ["Payments", "Stripe Connect",
     "Purpose-built for marketplaces: escrow-style holds, split payments between buyer/seller/platform fee, "
     "and PCI compliance handled by Stripe rather than us."],
    ["Auth &amp; identity", "Auth0 (or Amazon Cognito)",
     "Managed auth with role-based access control, so engineering time goes into the business-KYC workflow "
     "rather than reimplementing session security."],
    ["Hosting / compute", "AWS ECS on Fargate",
     "Containerized services without managing servers or a Kubernetes control plane; a natural upgrade path "
     "to EKS if the team later needs Kubernetes-specific tooling."],
    ["Infrastructure as code", "Terraform", "Reproducible environments and auditable infrastructure changes "
     "across dev/staging/production."],
    ["CI/CD", "GitHub Actions", "Tight integration with the source repo; sufficient for a small team without "
     "standing up separate CI infrastructure."],
    ["Observability", "Datadog (or Grafana + Prometheus) and Sentry",
     "Unified logs/metrics/traces plus dedicated error tracking, so incidents in the payment or transaction "
     "path surface immediately."],
    ["Analytics / BI", "Segment → Snowflake or BigQuery → Metabase",
     "Decouples product analytics and ESG-style aggregate reporting from the transactional database."],
]
story.append(make_table(stack_table,
                         [1.05 * inch, 1.75 * inch, 3.9 * inch], font_size=8.7))

story.append(Spacer(1, 6))
story.append(section_heading("3.2 Hosting &amp; Cloud Platform", level=2))
story.append(Paragraph(
    "AWS is the recommended cloud platform: it has the deepest bench of managed services used above "
    "(RDS, ElastiCache, OpenSearch Service, SQS/EventBridge, Fargate), reducing the operational surface a "
    "small platform team has to own directly. The same architecture maps onto GCP or Azure with equivalent "
    "managed services if the founding team has stronger existing expertise there — the service "
    "boundaries and data model in this report are cloud-agnostic by design.", S_Body))

story.append(section_heading("3.3 Core Data Model", level=2))
story.append(Paragraph(
    "Each service owns its own tables and exposes data through its API rather than allowing cross-service "
    "joins, which keeps the modular-monolith boundaries real even though everything currently runs against "
    "one PostgreSQL instance. <b>Listing</b> and <b>Transaction</b> are the two central entities: a Listing "
    "belongs to an Organization and a Category and has exactly one computed SustainabilityMetric; a "
    "Transaction links a Listing to a buyer and seller Organization and fans out to Messages, a Payment, a "
    "Shipment, and Reviews.", S_Body))
story.append(figure("diagram_datamodel.png",
                     "Figure 4. Core entity-relationship model.", max_h=6.6 * inch))

story.append(section_heading("3.4 Data Organization Principles", level=2))
story.append(bullets([
    "<b>Flexible attributes via JSONB.</b> Resource categories vary too widely for a single rigid schema "
    "(a steel offcut and a pallet of packaging film have almost nothing in common); category-specific spec "
    "fields live in a JSONB column on Listing rather than as sparse dedicated columns.",
    "<b>Search and analytics are derived, not primary.</b> Listing and Transaction changes are streamed via "
    "change-data-capture into OpenSearch (for search) and the data warehouse (for BI/ESG reporting) &mdash; "
    "Postgres remains the single system of record.",
    "<b>Sustainability metrics are computed twice.</b> Once at listing creation (an estimate, for buyer "
    "decision-making) and once at transaction close (a validated figure, once actual quantity and condition "
    "are confirmed), so impact reports reflect what actually happened, not just what was listed.",
    "<b>Sensitive documents are access-scoped, not just stored.</b> KYC documents and certifications sit in "
    "a private S3 prefix with signed, time-limited URLs issued per request — never a public bucket.",
]))

# =============================================================== CLOSING ==
story.append(PageBreak())
story.append(section_heading("Closing: Roadmap &amp; Trade-offs", level=1))

story.append(section_heading("Phased Roadmap", level=2))
roadmap_table = [
    ["Phase", "Scope"],
    ["MVP", "Web app only; core marketplace (browse, list, RFQ, negotiate); Stripe Connect payments; "
             "manually coordinated logistics (platform facilitates, doesn't automate carrier booking); "
             "basic sustainability metric calculation."],
    ["V2", "React Native mobile app; automated carrier/logistics API integration; recommendation engine "
             "using real transaction signal; expanded certification/verification partners."],
    ["V3", "Enterprise ERP/procurement-system integrations (API access for large buyers); marketplace-wide "
             "sustainability intelligence and benchmarking; potential carbon-credit/offset marketplace "
             "extension."],
]
story.append(make_table(roadmap_table, [0.9 * inch, 5.8 * inch]))

story.append(section_heading("Key Trade-offs &amp; Assumptions", level=2))
story.append(bullets([
    "A modular monolith is chosen over microservices at launch to prioritize engineering velocity for a "
    "small team; the explicit service boundaries and event-driven communication mean this is a deliberately "
    "reversible decision, not a dead end.",
    "Logistics is treated as an orchestration/integration problem (carrier APIs) rather than something the "
    "platform operates directly — owning trucks or warehouses is out of scope for this design.",
    "Sustainability metrics rely on category-level conversion factors (an accepted industry approach) rather "
    "than per-item lifecycle assessment, trading some precision for a launch-ready implementation.",
    "Payments assume a commission or subscription revenue model compatible with Stripe Connect's split-"
    "payment support; the specific monetization model is a product decision outside this report's scope.",
]))

story.append(Spacer(1, 10))
story.append(HRFlowable(width=CONTENT_W, thickness=0.6, color=BORDER, spaceAfter=10))
story.append(Paragraph(
    "This report intentionally favors clarity and defensible reasoning over exhaustive implementation "
    "detail, per the challenge's evaluation focus: a logical, well-justified design that a team could "
    "start building from directly.", S_Caption))

# ---------------------------------------------------------------- build ---
doc.multiBuild(story)
print("Wrote", OUT)
