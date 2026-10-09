CHANDRAYAAN-2 SAMPLE DATA — PS8 Reference Pack
================================================

SOURCE: ISRO ISSDC + Internet Archive
DATE: June 2026

FOLDER STRUCTURE
----------------
moon data/
├── imagery_OHRC/
│   ├── sample_preview.png        — Archive.org collection preview (OHRC scene)
│   ├── chandrayaan2_official1.webp  — ISRO official image 1
│   └── chandrayaan2_official2.webp  — ISRO official image 2
│
├── radar_DFSAR/
│   └── sar_readme.txt            — DFSAR data readme from ISRO
│
└── manuals/
    ├── DFSAR_user_manual.pdf     — Dual Freq SAR instrument & data guide (1.9 MB)
    ├── OHRC_user_guide.pdf       — Optical High Res Camera data products guide (1.8 MB)
    ├── TMC2_user_guide.pdf       — Terrain Mapping Camera-2 data guide (2.1 MB)
    └── CHACE2_user_manual.pdf    — Chandra Atmospheric Composition Experiment guide

INSTRUMENTS
-----------
DFSAR  — Dual Frequency SAR (L-band + S-band), 25m/pixel, full-polarimetric
         Key for PS8: detects subsurface ice via CPR (Circular Polarization Ratio)
TMC-2  — Terrain Mapping Camera, 5m/pixel, panchromatic, stereo DEM capability
OHRC   — High Res Camera, 0.25m/pixel, 3km swath — used for landing site selection

TO DOWNLOAD FULL SCENE DATA (requires free ISRO account)
---------------------------------------------------------
1. Register at: https://pradan.issdc.gov.in/ch2/
2. DFSAR polar mosaic: https://pradan.issdc.gov.in/ch2/protected/browse.xhtml?id=dfsar
3. TMC-2 scenes:       https://pradan.issdc.gov.in/ch2/protected/browse.xhtml?id=tmc2
4. OHRC scenes:        https://pradan.issdc.gov.in/ch2/protected/browse.xhtml?id=ohrc
5. Map browser (no login): https://chmapbrowse.issdc.gov.in/

DATA FORMAT
-----------
Files are in PDS4 format: .img (raw binary) + .xml (label/metadata)
DFSAR products: SLC (complex), MLC (multi-look), GRD (ground range)
Typical scene size: 100–500 MB compressed
