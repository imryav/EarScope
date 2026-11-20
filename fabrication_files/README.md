# EarScope XIAO RA4M1 — Turnkey Fabrication & PCBA Package (`Rev 2.1`)

> **Rev 2.1 changes (2026-11-20):** board grown to `48.0 × 25.0 mm` (+5 mm at the South edge); `U1`, `U2` → `OPA2388IDR` (zero-drift, same SOIC-8 pinout; `OPA2365AIDR` remains a drop-in backup); per-op-amp supply RC filters (`R14`/`C14` → `U1`, `R15`/`C15` → `U2`, `10 Ω + 10 µF`, `fc ≈ 1.6 kHz`); two indicator LEDs (`D6 → R16 → LED1` yellow-green, `D3 → R17 → LED2` red, pin HIGH = on, `~2.8 mA`). KiCad ERC: `0` errors; DRC: no new violations versus Rev 2.0, `0` unconnected pads, schematic parity OK. The `kicad-happy` results quoted below were for Rev 2.0 and have not been re-run. `OPA2388IDR` and the yellow-green LED have no LCSC part number yet, so they are blank in the JLCPCB BOM.

This folder contains the complete, verified **PCB Fabrication (Gerber RS-274X + Excellon Drill)** and **Turnkey SMT Assembly (BOM + Pick-and-Place CPL)** package for the **EarScope Carrier PCB (`Seeed Studio XIAO RA4M1 Edition`, `48.0 × 25.0 × 1.6 mm`)**, verified end-to-end with [`aklofas/kicad-happy`](https://github.com/aklofas/kicad-happy) (**`PASS — 11 / 11 Strict Release Gate Checks`, `0` Gerber/DFM/DRC Warnings, `100 / 100` EMC Score**).

---

## 1. Files Included in This Folder

| File / Directory | Purpose | Upload Target (`JLCPCB` / `PCBWay`) |
| :--- | :--- | :--- |
| **[`EarScope_XIAO_RA4M1_Gerbers_JLCPCB.zip`](EarScope_XIAO_RA4M1_Gerbers_JLCPCB.zip)** | Ready-to-upload ZIP archive containing all 9 RS-274X (X2) Gerber layers, `PTH.drl`, `NPTH.drl`, and `.gbrjob` | **Step 1 — Add Gerber File** |
| **[`EarScope_JLCPCB_BOM.csv`](EarScope_JLCPCB_BOM.csv)** | Turnkey SMT Bill of Materials (`22` lines / `38` populated components with exact `Cxxxxx` LCSC Part #s, incl. `R13 = 10R` Basic `C17415`) | **Step 2 — Add BOM File** |
| **[`EarScope_JLCPCB_CPL.csv`](EarScope_JLCPCB_CPL.csv)** | Component Placement List / Pick-and-Place (`38` parts in `mm`, Top layer, `48.0 × 25.0 mm` coordinate frame) | **Step 2 — Add CPL File** |
| **[`EarScope_Master_BOM.csv`](EarScope_Master_BOM.csv)** | Full Engineering Master BOM (`23` BOM lines, including `A1` `Seeed Studio XIAO RA4M1 102010551` & `R3` `DNP`; `JP1` is bare PCB copper) | Engineering / Sourcing Reference |
| **[`EarScope_AliExpress_BOM.csv`](EarScope_AliExpress_BOM.csv)** | DIY Hand-Soldering BOM (`23` orderable lines) with direct AliExpress search/order links and typical pack sizes (Rev 2.0 prices; Rev 2.1 additions not priced yet) | DIY / AliExpress Component Ordering |
| **[`gerbers/`](gerbers/)** | Unpacked individual Gerber (`.gbr`), Excellon drill (`.drl`), and job (`.gbrjob`) files | Direct CAM / GitHub Inspection |

### Unpacked Layer Inventory (`gerbers/`)
* `EarScope_XIAO_RA4M1-F_Cu.gbr` — Top Copper (`F.Cu`: SMD pads, `45°` analog/power routing, `JP1` solder jumper, `VREF` active guard trace, bare keepout under XIAO belly pads)
* `EarScope_XIAO_RA4M1-B_Cu.gbr` — Bottom Copper (`B.Cu`: continuous `GND` shield plane + `0.25 mm` anti-pad clearances + short local underpasses)
* `EarScope_XIAO_RA4M1-F_Mask.gbr` / `EarScope_XIAO_RA4M1-B_Mask.gbr` — Top & Bottom Soldermask (`33` vias tented; `JP1` & `TP1–TP6` exposed; continuous soldermask insulation under XIAO RA4M1)
* `EarScope_XIAO_RA4M1-F_Paste.gbr` / `EarScope_XIAO_RA4M1-B_Paste.gbr` — Top & Bottom Solder Paste Stencil (single-sided Top SMT; `JP1` excluded from `F.Paste` so it ships open by default)
* `EarScope_XIAO_RA4M1-F_Silkscreen.gbr` / `EarScope_XIAO_RA4M1-B_Silkscreen.gbr` — Top & Bottom Silkscreen (`JP1` `OPEN=EAR / BRIDGE=MIC`, `Rev 2.1`)
* `EarScope_XIAO_RA4M1-Edge_Cuts.gbr` — Closed `48.00 × 25.00 mm` Board Outline
* `EarScope_XIAO_RA4M1-PTH.drl` — Plated Through-Hole Drill (`33` vias @ `0.30 mm` drill / `0.60 mm` pad + `4` routed `0.60 × 1.50 mm` oval slots for `J1` `PJ-320A`)
* `EarScope_XIAO_RA4M1-NPTH.drl` — Non-Plated Mechanical Alignment Holes (`2 × 1.20 mm` locating bosses for `J1` `PJ-320A`)
* `EarScope_XIAO_RA4M1-job.gbrjob` — KiCad Gerber Job stackup & design-rules metadata

---

## 2. Recommended JLCPCB / PCBWay Ordering Settings

1. **PCB Specifications:**
   * **Base Material:** `FR-4` (`TG135` / Standard)
   * **Layers:** **`2 Layers`**
   * **Dimensions:** **`48.0 mm × 25.0 mm`** (auto-detected from `EarScope_XIAO_RA4M1_Gerbers_JLCPCB.zip`)
   * **PCB Thickness:** **`1.6 mm`**
   * **Outer Copper Weight:** **`1 oz` (`35 µm`)**
   * **Surface Finish:** `HASL (with lead)` / `LeadFree HASL` (or `ENIG` for ultra-flat castellated soldering)
   * **Via Covering:** **`Tented`**
2. **PCB Assembly (`PCBA` — Optional Turnkey SMT):**
   * **Assembly Side:** **`Top Side Only`**
   * **BOM / CPL Upload:** Upload [`EarScope_JLCPCB_BOM.csv`](EarScope_JLCPCB_BOM.csv) and [`EarScope_JLCPCB_CPL.csv`](EarScope_JLCPCB_CPL.csv).
   * **Component Orientation Check:** In JLCPCB's 3D DFM viewer, verify Pin 1 dots on `U1`, `U2` (`OPA2388IDR`), cathode marks on `D1` (`PESD3V3L1BA`), `LED1` and `LED2`, SOT-23 tab on `U3` (`MCP1700T-3302E/TT`), and ensure `J1`'s `3.5 mm` barrel faces outward across the East board edge (`X = 48.0 mm`).

---

## 3. Post-PCBA Steps — Soldering `A1` (`Seeed Studio XIAO RA4M1`) & Configuring `JP1`

* **Soldering `A1` (`Seeed Studio XIAO RA4M1`, SKU `102010551`):**
  * `A1` is intentionally excluded from automated SMT assembly so you can seat a headerless XIAO RA4M1 module **flush (`0 mm` standoff)** onto the `14` extended castellated SMD pads (`2.0 × 1.6 mm`) on `F.Cu`, with its **USB-C port facing West** (overhanging the `X = 0.0 mm` left board edge by `2.0 mm`).
  * The carrier PCB enforces a strict `F.Cu` and via keepout (`[0.95..16.90] × [4.00..16.10] mm`) covered by soldermask directly beneath the XIAO RA4M1's 16 exposed underside pads (`BAT+/BAT-`, SWD, CAN, etc.). For extra mechanical abrasion protection if desired, you may optionally apply a small strip of Kapton tape across the XIAO's underside belly pads (leaving the 14 outer castellations exposed) before soldering.
  * Tack one corner castellated pad first, verify flat alignment over all `14` pads, and drag-solder the remaining half-moon castellations with flux (`~1 minute` total).
* **Configuring `JP1` (`EAR / MIC` SMD Solder Jumper at `(41.8, 17.8) mm`):**
  * **Passive Dynamic Earphones (Default — Leave `JP1` OPEN):** `JP1` has no `F.Paste` aperture and arrives open from PCBA, keeping `R12 = 2.2 kΩ` disconnected (`0.00 mA` DC through `16–32 Ω` earphone coils).
  * **Electret Microphone Capsule (Bridge `JP1`):** Melt a small solder bead across `JP1`'s `0.30 mm` gap to connect `+3V3_ANA` through `R12 = 2.2 kΩ` to `VIN_RAW`. To revert back to passive earphones later, wick the solder bead off with desoldering braid.
* **`R3` (`DNP`):** Unpopulated parallel `0805` gain-trim pad across `R2 = 220 Ω`; leave `R3` empty for the validated `53.2 dB` (`×455.5`) production gain.
