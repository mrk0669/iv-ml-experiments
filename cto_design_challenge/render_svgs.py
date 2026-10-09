import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

ASSETS = os.path.join(os.path.dirname(__file__), "assets")

FILES = [
    "diagram_sitemap.svg",
    "diagram_journey.svg",
    "diagram_architecture.svg",
    "diagram_datamodel.svg",
]

for f in FILES:
    src = os.path.join(ASSETS, f)
    dst = os.path.join(ASSETS, f.replace(".svg", ".png"))
    drawing = svg2rlg(src)
    renderPM.drawToFile(drawing, dst, fmt="PNG", dpi=220)
    print(f"Rendered {dst}")
