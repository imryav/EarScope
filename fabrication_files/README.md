# EarScope Nano R4 — Turnkey Fabrication & PCBA Package (`Rev 1.0`)

This folder contains the complete, verified **PCB Fabrication (Gerber RS-274X + Excellon Drill)** and **Turnkey SMT Assembly (BOM + Pick-and-Place CPL)** package for the **EarScope Carrier PCB (`Arduino Nano R4 Edition`, `68.0 × 20.0 × 1.6 mm`)**, verified end-to-end with [`aklofas/kicad-happy`](https://github.com/aklofas/kicad-happy) (**`PASS — 11 / 11 Release Gate Checks`, `0` Gerber/DFM Warnings, `97.0 / 100` EMC Score**).

---

## 1. Files Included in This Folder

| File / Directory | Purpose | Upload Target (`JLCPCB` / `PCBWay`) |
| :--- | :--- | :--- |
| **[`EarScope_NanoR4_Gerbers_JLCPCB.zip`](EarScope_NanoR4_Gerbers_JLCPCB.zip)** | Ready-to-upload ZIP archive containing all 9 RS-274X (X2) Gerber layers, `PTH.drl`, `NPTH.drl`, and `.gbrjob` | **Step 1 — Add Gerber File** |
| **[`EarScope_JLCPCB_BOM.csv`](EarScope_JLCPCB_BOM.csv)** | Turnkey SMT Bill of Materials (`19` LCSC lines / `30` SMD components with exact `Cxxxxx` LCSC Part #s) | **Step 2 — Add BOM File** |
| **[`EarScope_JLCPCB_CPL.csv`](EarScope_JLCPCB_CPL.csv)** | Component Placement List / Pick-and-Place (`30` SMD parts in `mm`, Top layer) | **Step 2 — Add CPL File** |
| **[`EarScope_Master_BOM.csv`](EarScope_Master_BOM.csv)** | Full Engineering Master BOM (`31` components, including `A1` `Arduino Nano R4 ABX00142` & `R3` `DNP`) | Engineering / Sourcing Reference |
| **[`gerbers/`](gerbers/)** | Unpacked individual Gerber (`.gbr`), Excellon drill (`.drl`), and job (`.gbrjob`) files | Direct CAM / GitHub Inspection |

### Unpacked Layer Inventory (`gerbers/`)
* `EarScope_NanoR4-F_Cu.gbr` — Top Copper (`F.Cu`: SMD pads, `45°` analog/power routing, `VREF` active guard trace)
* `EarScope_NanoR4-B_Cu.gbr` — Bottom Copper (`B.Cu`: continuous `GND` shield plane + `0.25 mm` anti-pad clearances + short jumpers)
* `EarScope_NanoR4-F_Mask.gbr` / `EarScope_NanoR4-B_Mask.gbr` — Top & Bottom Soldermask (`52` vias tented; `TP1–TP6` exposed)
* `EarScope_NanoR4-F_Paste.gbr` / `EarScope_NanoR4-B_Paste.gbr` — Top & Bottom Solder Paste Stencil (single-sided Top SMT)
* `EarScope_NanoR4-F_Silkscreen.gbr` / `EarScope_NanoR4-B_Silkscreen.gbr` — Top & Bottom Silkscreen (`EAR` / `MIC` switch labels, `Rev 1.0`)
* `EarScope_NanoR4-Edge_Cuts.gbr` — Closed `68.00 × 20.00 mm` Board Outline
* `EarScope_NanoR4-PTH.drl` — Plated Through-Hole Drill (`52` vias @ `0.30 mm` drill / `0.60 mm` pad, including `31` `GND` stitching vias)
* `EarScope_NanoR4-NPTH.drl` — Non-Plated Mechanical Alignment Holes (`2 × 0.80 mm` for `J1` `PJ-320A`, `2 × 0.90 mm` for `SW1` `PCM12SMTR`)
* `EarScope_NanoR4-job.gbrjob` — KiCad Gerber Job stackup & design-rules metadata

---

## 2. Recommended JLCPCB / PCBWay Ordering Settings

1. **PCB Specifications:**
   * **Base Material:** `FR-4` (`TG135` / Standard)
   * **Layers:** **`2 Layers`**
   * **Dimensions:** **`68.0 mm × 20.0 mm`** (auto-detected from `EarScope_NanoR4_Gerbers_JLCPCB.zip`)
   * **PCB Thickness:** **`1.6 mm`**
   * **Outer Copper Weight:** **`1 oz` (`35 µm`)**
   * **Surface Finish:** `HASL (with lead)` / `LeadFree HASL` (or `ENIG` for flattest castellated soldering)
   * **Via Covering:** **`Tented`**
2. **PCB Assembly (`PCBA` — Optional Turnkey SMT):**
   * **Assembly Side:** **`Top Side Only`**
   * **BOM / CPL Upload:** Upload [`EarScope_JLCPCB_BOM.csv`](EarScope_JLCPCB_BOM.csv) and [`EarScope_JLCPCB_CPL.csv`](EarScope_JLCPCB_CPL.csv).
   * **Component Orientation Check:** In JLCPCB's 3D DFM viewer, verify Pin 1 dots on `U1`, `U2` (`OPA2365AIDR`), `U3` (`MCP1700T-3302E/TT`), and ensure `SW1`'s actuator knob faces outward across the South board edge (`EAR ↔ MIC`) and `J1`'s `3.5 mm` barrel faces outward across the East board edge.

---

## 3. Post-PCBA Step — Soldering `A1` (`Arduino Nano R4`)

* **`A1` (`Arduino Nano R4`, `ABX00142`)** is intentionally excluded from automated SMT assembly so you can seat an official headerless Nano R4 module **flush (`0 mm` standoff)** onto the `30` extended castellated SMD pads on `F.Cu` (with its **USB-C port facing West / overhanging the left board edge**).
* Tack one corner castellated pad first, verify flat alignment over all `30` pads, and drag-solder the remaining half-moon castellations with flux (`~2 minutes` total).
* **`R3`** (`DNP`) is an unpopulated parallel `0805` gain-trim pad across `R2 = 220 Ω`; leave `R3` empty for the validated `53.2 dB` (`×455.5`) production gain.
