# EarScope XIAO RA4M1 — Turnkey Fabrication & PCBA Package (`Rev 2.2`)

> **Rev 2.2 changes (2026-11-25):** board shrunk back by `20%` from `48.0 × 25.0 mm` to **`48.0 × 20.0 mm`** while keeping all analog/power components (`U1`, `U2`, `U3`, `J1`, `D1`, `C1–C15`, `R1–R15`, `JP1`) single-sided on `F.Cu` and moving **only** the two status LEDs + resistors (`LED1`, `LED2`, `R16`, `R17`) onto **`B.Cu`** beneath `A1` (`Seeed Studio XIAO RA4M1`). Converted both LEDs to **`0805` active-low (current-sinking)** driven from XIAO Pin `12` (`3V3` $\rightarrow$ **`+3V3_DIG`**, `100%` isolated from quiet `+3V3_ANA`) through `220 Ω` (`R16`, `R17` `RC0805FR-07220RL`, LCSC `C17557`, unified with `R2`) into North Middle-Drive (`8 mA` `IOL`) GPIOs **`D7/RX` (Pad `8`, `P301`)** for `LED1` (`KT-0805YG`, LCSC `C2292`, `~5.7 mA`) and **`D8/SCK` (Pad `9`, `P111`)** for `LED2` (`KT-0805R`, LCSC `C2295`, `~5.9 mA`, pin `LOW` = LED ON). KiCad 10 ERC: `0` electrical errors/warnings; DRC: **`0` errors, `0` warnings, `0` unconnected pads, `0` schematic parity issues**. Only `OPA2388IDR` (`U1`, `U2`) remains user-sourced / blank in the LCSC column (`OPA2365AIDR` remains a pin-compatible SOIC-8 backup).

This folder contains the complete, verified **PCB Fabrication (Gerber RS-274X + Excellon Drill)** and **Turnkey SMT Assembly (BOM + Pick-and-Place CPL)** package for the **EarScope Carrier PCB (`Seeed Studio XIAO RA4M1 Edition`, `48.0 × 20.0 × 1.6 mm`)**.

---

## 1. Files Included in This Folder

| File / Directory | Purpose | Upload Target (`JLCPCB` / `PCBWay`) |
| :--- | :--- | :--- |
| **[`EarScope_XIAO_RA4M1_Gerbers_JLCPCB.zip`](EarScope_XIAO_RA4M1_Gerbers_JLCPCB.zip)** | Ready-to-upload ZIP archive containing all 9 RS-274X (X2) Gerber layers, `PTH.drl`, `NPTH.drl`, and `.gbrjob` | **Step 1 — Add Gerber File** |
| **[`EarScope_JLCPCB_BOM.csv`](EarScope_JLCPCB_BOM.csv)** | Turnkey SMT Bill of Materials (`21` lines / `38` populated `0805`/SMD components with exact `Cxxxxx` LCSC Part #s) | **Step 2 — Add BOM File** |
| **[`EarScope_JLCPCB_CPL.csv`](EarScope_JLCPCB_CPL.csv)** | Component Placement List / Pick-and-Place (`38` parts in `mm`: `34` `T` Top parts + `4` `B` Bottom LED parts, `48.0 × 20.0 mm` frame) | **Step 2 — Add CPL File** |
| **[`EarScope_Master_BOM.csv`](EarScope_Master_BOM.csv)** | Full Engineering Master BOM (`22` BOM lines / `39` parts incl. `A1` `Seeed Studio XIAO RA4M1 102010551`; `R3` is `DNP`; `JP1` is bare PCB copper) | Engineering / Sourcing Reference |
| **[`EarScope_AliExpress_BOM.csv`](EarScope_AliExpress_BOM.csv)** | DIY Hand-Soldering BOM (`22` orderable lines, all passives & LEDs unified on `0805`) with direct AliExpress search/order links | DIY / AliExpress Component Ordering |
| **[`gerbers/`](gerbers/)** | Unpacked individual Gerber (`.gbr`), Excellon drill (`.drl`), and job (`.gbrjob`) files | Direct CAM / GitHub Inspection |

### Unpacked Layer Inventory (`gerbers/`)
* `EarScope_XIAO_RA4M1-F_Cu.gbr` — Top Copper (`F.Cu`: `34` analog/power SMD footprints, `45°` analog/power routing, `JP1` solder jumper, `VREF` active guard trace, bare keepout under XIAO belly pads)
* `EarScope_XIAO_RA4M1-B_Cu.gbr` — Bottom Copper (`B.Cu`: continuous `GND` shield plane + active-low `0805` status LED subcircuit `LED1`, `LED2`, `R16`, `R17` under XIAO + short local underpasses)
* `EarScope_XIAO_RA4M1-F_Mask.gbr` / `EarScope_XIAO_RA4M1-B_Mask.gbr` — Top & Bottom Soldermask (all vias tented; `JP1` & `TP1–TP6` exposed; continuous soldermask insulation under XIAO RA4M1)
* `EarScope_XIAO_RA4M1-F_Paste.gbr` / `EarScope_XIAO_RA4M1-B_Paste.gbr` — Top & Bottom Solder Paste Stencil (`JP1` excluded from `F.Paste` so it ships open by default; `B.Paste` has apertures for `LED1`, `LED2`, `R16`, `R17`)
* `EarScope_XIAO_RA4M1-F_Silkscreen.gbr` / `EarScope_XIAO_RA4M1-B_Silkscreen.gbr` — Top & Bottom Silkscreen (`JP1` `OPEN / MIC`, `B.Silkscreen` polarity marks for `LED1` & `LED2`, `Rev 2.2`)
* `EarScope_XIAO_RA4M1-Edge_Cuts.gbr` — Closed `48.00 × 20.00 mm` Board Outline
* `EarScope_XIAO_RA4M1-PTH.drl` — Plated Through-Hole Drill (`0.30 mm` drill / `0.60 mm` pad vias + `4` routed `0.60 × 1.50 mm` oval slots for `J1` `PJ-320A`)
* `EarScope_XIAO_RA4M1-NPTH.drl` — Non-Plated Mechanical Alignment Holes (`2 × 1.60 mm` locating bosses for `J1` `PJ-320A`)
* `EarScope_XIAO_RA4M1-job.gbrjob` — KiCad Gerber Job stackup & design-rules metadata

---

## 2. Recommended JLCPCB / PCBWay Ordering Settings

1. **PCB Specifications:**
   * **Base Material:** `FR-4` (`TG135` / Standard)
   * **Layers:** **`2 Layers`**
   * **Dimensions:** **`48.0 mm × 20.0 mm`** (auto-detected from `EarScope_XIAO_RA4M1_Gerbers_JLCPCB.zip`)
   * **PCB Thickness:** **`1.6 mm`**
   * **Outer Copper Weight:** **`1 oz` (`35 µm`)**
   * **Surface Finish:** `HASL (with lead)` / `LeadFree HASL` (or `ENIG` for ultra-flat castellated soldering)
   * **Via Covering:** **`Tented`**
2. **PCB Assembly (`PCBA` — Flexible Top-Only or Double-Sided SMT):**
   * **Cost-Saving Option (`Top Side Only` Economic PCBA):** Select **`Top Side`** in JLCPCB PCBA so JLCPCB places all `34` top-side analog/power components without double-sided setup fees, then hand-solder the `4` roomy `0805` bottom parts (`LED1`, `LED2`, `R16`, `R17`) on `B.Cu` at the same time you hand-solder `A1` (`XIAO RA4M1`).
   * **Full Turnkey Option (`Both Sides` PCBA):** Select **`Both Sides`** to have JLCPCB assemble all `38` SMD parts across both `F.Cu` (`34` parts) and `B.Cu` (`4` parts).
   * **BOM / CPL Upload:** Upload [`EarScope_JLCPCB_BOM.csv`](EarScope_JLCPCB_BOM.csv) and [`EarScope_JLCPCB_CPL.csv`](EarScope_JLCPCB_CPL.csv).
   * **Component Orientation Check:** In JLCPCB's 3D DFM viewer, verify Pin 1 dots on `U1`, `U2` (`OPA2388IDR`), cathode marks on `D1` (`PESD3V3L1BA`), `LED1` (`KT-0805YG`), and `LED2` (`KT-0805R` — cathodes face North toward `Y = 9.06 mm`), SOT-23 tab on `U3` (`MCP1700T-3302E/TT`), and ensure `J1`'s `3.5 mm` barrel faces outward across the East board edge (`X = 48.0 mm`).

---

## 3. Post-PCBA Steps — Soldering `A1` (`Seeed Studio XIAO RA4M1`), LED Firmware & `JP1`

* **Soldering `A1` (`Seeed Studio XIAO RA4M1`, SKU `102010551`):**
  * `A1` is intentionally excluded from automated SMT assembly so you can seat a headerless XIAO RA4M1 module **flush (`0 mm` standoff)** onto the `14` extended castellated SMD pads (`2.0 × 1.6 mm`) on `F.Cu`, with its **USB-C port facing West** (overhanging the `X = 0.0 mm` left board edge by `2.0 mm`).
  * The carrier PCB enforces a strict `F.Cu` and via keepout (`[0.95..16.90] × [4.00..16.10] mm`) covered by soldermask directly beneath the XIAO RA4M1's 16 exposed underside pads (`BAT+/BAT-`, SWD, CAN, etc.). Even the `3` North LED vias (`(9.18, 1.75)`, `(16.79, 1.75)`, `(19.45, 1.75)`) sit completely outside this keepout.
  * Tack one corner castellated pad first, verify flat alignment over all `14` pads, and drag-solder the remaining half-moon castellations with flux (`~1 minute` total).
* **Driving the Active-Low Status LEDs (`LED1` & `LED2` on `B.Cu`):**
  * **`LED1` (Yellow-Green, `X = 14.0 mm, Y = 10.0 mm`):** Anode fed from XIAO Pin `12` (`+3V3_DIG`) via `R16 = 220 Ω`; cathode sunk by **`D7 / RX` (Pad `8`, `P301`)** at `~5.7 mA`.
  * **`LED2` (Red, `X = 9.5 mm, Y = 10.0 mm`):** Anode fed from XIAO Pin `12` (`+3V3_DIG`) via `R17 = 220 Ω`; cathode sunk by **`D8 / SCK` (Pad `9`, `P111`)** at `~5.9 mA`.
  * **Firmware Logic:** Active-Low — `digitalWrite(pin, LOW)` turns the LED **ON**, `digitalWrite(pin, HIGH)` (or `INPUT`) turns the LED **OFF**. Both `P301` and `P111` support Renesas RA4M1 **Middle Drive (`8 mA` `IOL`)** via `R_PFS->PORT[3].PIN[1].PmnPFS_b.DSCR = 1` and `R_PFS->PORT[1].PIN[11].PmnPFS_b.DSCR = 1`.
* **Configuring `JP1` (`EAR / MIC` SMD Solder Jumper at `(45.1, 16.1) mm`):**
  * **Passive Dynamic Earphones (Default — Leave `JP1` OPEN):** `JP1` has no `F.Paste` aperture and arrives open from PCBA, keeping `R12 = 2.2 kΩ` disconnected (`0.00 mA` DC through `16–32 Ω` earphone coils).
  * **Electret Microphone Capsule (Bridge `JP1`):** Melt a small solder bead across `JP1`'s `0.30 mm` gap to connect `+3V3_ANA` through `R12 = 2.2 kΩ` to `VIN_RAW`. To revert back to passive earphones later, wick the solder bead off with desoldering braid.
* **`R3` (`DNP`):** Unpopulated parallel `0805` gain-trim pad across `R2 = 220 Ω`; leave `R3` empty for the validated `53.2 dB` (`×455.5`) production gain.
