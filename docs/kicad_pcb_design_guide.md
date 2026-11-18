# KiCad 8 / 9 Schematic & PCB Design Guide (Seeed Studio XIAO RA4M1 Edition — `Rev 2.0`)

This guide provides a complete, step-by-step workflow to translate the validated LTspice schematic ([`AFE_Cardiac_5-45Hz.asc`](AFE_Cardiac_5-45Hz.asc)) into a production-ready **2-layer Mixed-Signal Carrier PCB** in **KiCad 8 / KiCad 9**, ready for fabrication at **JLCPCB** or **PCBWay** and mechanical integration in **Fusion 360**.

> [!TIP]
> **Ready-to-Manufacture KiCad 8 / 9 Project Included:** The complete `Rev 2.0` project — schematic ([`EarScope_XIAO_RA4M1.kicad_sch`](../hardware_pcb/EarScope_XIAO_RA4M1/EarScope_XIAO_RA4M1.kicad_sch)), `100%` routed `48.0 × 20.0 mm` 2-layer carrier PCB ([`EarScope_XIAO_RA4M1.kicad_pcb`](../hardware_pcb/EarScope_XIAO_RA4M1/EarScope_XIAO_RA4M1.kicad_pcb)), custom footprint library ([`EarScope_Footprints.pretty/`](../hardware_pcb/EarScope_XIAO_RA4M1/EarScope_Footprints.pretty/)), and turnkey JLCPCB BOM/CPL files ([`bom/`](../hardware_pcb/EarScope_XIAO_RA4M1/bom/)) — is already built and verified in [`hardware_pcb/EarScope_XIAO_RA4M1/`](../hardware_pcb/EarScope_XIAO_RA4M1/). See [`kicad_happy_design_review.md`](kicad_happy_design_review.md) for the full [`aklofas/kicad-happy`](https://github.com/aklofas/kicad-happy) **`PASS`** strict fabrication release gate report (`11/11` checks passed, `0` DRC/DFM violations, `100 / 100` EMC score).

---

## 1. Board Architecture & Manufacturing Specifications

To achieve sub-microvolt analog noise immunity (`0.141 µVrms` across `5–45 Hz`) on an ultra-compact thumb-width 2-layer PCB, `Rev 2.0` uses a **co-planar 2-layer mixed-signal architecture** with strict physical isolation between the `48 MHz` **Seeed Studio XIAO RA4M1** digital domain, a central **USB Power LPF + LDO & ADC Anti-Aliasing Barrier Column**, and the quiet `3.30 V` **OPA2365** analog island:

* **Board Dimensions (`Edge.Cuts`):** **`48.0 mm × 20.0 mm`** (`960 mm²`, `-29.4%` area vs. `Rev 1.0`), `1.6 mm` standard FR-4 thickness (`1 oz` / `35 µm` copper).
* **Layer Stackup:**
  * **`F.Cu` (Top Layer):** All SMD components, Seeed Studio XIAO RA4M1 14-pad castellated flush mount (with strict `F.Cu`/via keepout under all 16 exposed underside belly pads), `1.58 kHz` USB pre-LDO RC LPF (`R13 + C9 || C13`), `JP1` 2-pad SMD solder jumper (`OPEN = EAR / BRIDGE = MIC`), short analog signal traces, and a `VREF` active guard ring around `U1A+`.
  * **`B.Cu` (Bottom Layer):** **100% continuous, unbroken `GND` copper pour** acting as an electromagnetic shield underneath both the AFE and the XIAO RA4M1.
* **Assembly Style:** Single-sided top assembly (`0805` passives, `SOIC-8` op-amps, `SOT-23-3` LDO, `SOD-323` ESD diode, `PJ-320A` jack, bare-copper `JP1` solder jumper, and headerless castellated **Seeed Studio XIAO RA4M1 `102010551`**) — easy to hand-solder or order via turnkey PCBA.

![EarScope KiCad 2-Layer Carrier PCB Floorplan](figures/kicad_pcb_floorplan.svg)

![EarScope Routed 2-Layer Carrier PCB](figures/earscope_routed_pcb.svg)

---

## 2. Step 1 — KiCad Project Creation & Design Rules (`Board Setup`)

1. Open KiCad (`8.0+` or `9.0+`) $\rightarrow$ **File $\rightarrow$ New Project** $\rightarrow$ save inside `hardware_pcb/EarScope_XIAO_RA4M1`.
2. Open the PCB Editor (**`Pcbnew`**) $\rightarrow$ **File $\rightarrow$ Board Setup** and enter these fabrication-safe constraints (compatible with standard `$2` 2-layer rules at JLCPCB and PCBWay):

| Parameter (`Design Rules -> Constraints`) | Recommended Setting | Notes |
| :--- | :--- | :--- |
| **Copper Layers** | `2` (`F.Cu`, `B.Cu`) | `1.6 mm` finished board thickness |
| **Minimum Clearance** | **`0.20 mm`** (`8 mil`) | Generous margin over `0.127 mm` (`5 mil`) fab limit |
| **Minimum Track Width** | **`0.20 mm`** (`8 mil`) | Minimum routed track in `Rev 2.0` is `0.25 mm` |
| **Minimum Via Size / Drill** | **`0.60 mm` diameter / `0.30 mm` drill** | Standard cost-free via size |
| **Copper to Edge Clearance** | **`0.30 mm`** | Prevents exposed copper during V-cut / routing |

3. Under **Board Setup $\rightarrow$ Design Rules $\rightarrow$ Net Classes**, configure three net classes:

| Net Class | Track Width | Clearance | Assigned Nets |
| :--- | :---: | :---: | :--- |
| **`Default` (Analog Signal)** | `0.25 mm` | `0.20 mm` | `VIN_RAW`, `OUT_PRE`, `HPF_MID`, `OUT_HPF`, `LPF_MID`, `OUT_LPF`, `ADC_IN` |
| **`HighZ_Input`** | `0.25 mm` | **`0.35 mm`** | `IN_POS` (between `C1`, `R1`, and `U1` Pin 3) |
| **`Power`** | **`0.35 – 0.50 mm`** | `0.25 mm` | `+5V_USB`, `+5V_FILT`, `+3V3_ANA`, `VREF`, `GND` |

---

## 3. Step 2 — LTspice-to-KiCad Component, Symbol & Footprint Mapping

Every component below maps 1-to-1 to [`docs/AFE_Cardiac_5-45Hz.asc`](AFE_Cardiac_5-45Hz.asc). All footprints are bundled ready-to-use in [`hardware_pcb/EarScope_XIAO_RA4M1/EarScope_Footprints.pretty/`](../hardware_pcb/EarScope_XIAO_RA4M1/EarScope_Footprints.pretty/):

| LTspice Name | KiCad Ref | Value / Part Number | KiCad Symbol | KiCad Footprint (`EarScope_Footprints`) | LCSC Part # |
| :--- | :---: | :--- | :--- | :--- | :---: |
| `MCU` | **`A1`** | `Seeed Studio XIAO RA4M1` (`102010551`) | `MCU_Module:Seeed_XIAO_RA4M1` | `Seeed_XIAO_RA4M1_Castellated_SMD` *(Sec. 4.1)* | Seeed `102010551` |
| `U1` (`U1A, U1B`) | **`U1`** | `OPA2365AIDR` | `Amplifier_Operational:OPA2365xD` | `SOIC-8_3.9x4.9mm_P1.27mm` | `C78566` |
| `U2` (`U2A, U2B`) | **`U2`** | `OPA2365AIDR` | `Amplifier_Operational:OPA2365xD` | `SOIC-8_3.9x4.9mm_P1.27mm` | `C78566` |
| `U3` (LDO) | **`U3`** | `MCP1700T-3302E/TT` | `Regulator_Linear:MCP1700x-3302xx_SOT23` | `SOT-23` | `C39051` |
| ESD Clamp | **`D1`** | `PESD3V3L1BA` (`3.3V` Bidirectional TVS) | `Device:D_TVS` | `SOD-323` | `C15772` |
| `VEAR` (Jack) | **`J1`** | `PJ-320A` (3.5mm TRRS) | `Connector_Audio:AudioJack4` | `TRRS-PJ-320A` | `C95555` |
| Bias Jumper | **`JP1`** | `SolderJumper_2_Open` (`OPEN=EAR / BRIDGE=MIC`) | `Jumper:SolderJumper_2_Open` | `SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm` | Bare PCB Copper |
| `R13` (USB LPF) | **`R13`** | `10 Ω` (`1%`, `0805W8F100JT5E`) | `Device:R` | `R_0805_2012Metric` | `C17415` (Basic) |
| `C9` (USB LPF Bulk) | **`C9`** | `10 µF` (`25V`, `X5R/X7R`, `+5V_FILT`) | `Device:C` | `C_0805_2012Metric` | `C15850` |
| `C13` (USB LPF HF) | **`C13`** | `100 nF` (`50V`, `X7R`, `+5V_FILT`) | `Device:C` | `C_0805_2012Metric` | `C49678` |
| `C10` (LDO Out) | **`C10`** | `10 µF` (`25V`, `X5R/X7R`, `+3V3_ANA`) | `Device:C` | `C_0805_2012Metric` | `C15850` |
| `CIN` | **`C1`** | `68 nF` (`50V`, `X7R`/`C0G`) | `Device:C` | `C_0805_2012Metric` | `C53085` |
| `C1` (`CF` in doc) | **`C2`** | `1 nF` (`50V`, `C0G/NP0`) | `Device:C` | `C_0805_2012Metric` | `C1588` |
| `C1H, C2H` | **`C3, C4`** | `1 µF` (`50V`, `X7R`) | `Device:C` | `C_0805_2012Metric` | `C28323` |
| `CAL` | **`C5`** | `220 nF` / `200 nF` (`50V`, `X7R`) | `Device:C` | `C_0805_2012Metric` | `C315201` |
| `CBL` | **`C6`** | `100 nF` (`50V`, `X7R` $\rightarrow$ **`VREF`**) | `Device:C` | `C_0805_2012Metric` | `C49678` |
| `COUT` | **`C7`** | `100 nF` (`50V`, `X7R` $\rightarrow$ **`GND`**) | `Device:C` | `C_0805_2012Metric` | `C49678` |
| `CREF` | **`C8`** | `10 µF` (`25V`, `X5R/X7R` on `U2B+`) | `Device:C` | `C_0805_2012Metric` | `C15850` |
| `CDEC1, CDEC2` | **`C11, C12`** | `100 nF` (`50V`, `X7R` local op-amp bypass) | `Device:C` | `C_0805_2012Metric` | `C49678` |
| `RBIAS` | **`R1`** | `1 MΩ` (`1%`) | `Device:R` | `R_0805_2012Metric` | `C17514` |
| `RG` | **`R2`** | `220 Ω` (`1%`, selected gain) | `Device:R` | `R_0805_2012Metric` | `C17557` |
| `RG_ALT` *(opt.)* | **`R3`** | `DNP` (parallel gain-trim option) | `Device:R` | `R_0805_2012Metric` | — |
| `RF, RREF1, RREF2` | **`R4, R5, R6`** | `100 kΩ` (`1%`) | `Device:R` | `R_0805_2012Metric` | `C149504` |
| `RAH` | **`R7`** | `22.6 kΩ` (`1%`) | `Device:R` | `R_0805_2012Metric` | `C17562` |
| `RBH` | **`R8`** | `45.3 kΩ` (`1%`) | `Device:R` | `R_0805_2012Metric` | `C25900` |
| `R1L, R2L` | **`R9, R10`** | `24.9 kΩ` (`1%`) | `Device:R` | `R_0805_2012Metric` | `C17590` |
| `ROUT` | **`R11`** | `100 Ω` (`1%`) | `Device:R` | `R_0805_2012Metric` | `C17407` |
| `RMIC` | **`R12`** | `2.2 kΩ` (`1%`, switched via `JP1`) | `Device:R` | `R_0805_2012Metric` | `C17520` |
| Scope Test Pads | **`TP1–TP6`** | `1.2 mm` Flat SMD Test Points | `Connector:TestPoint` | `TestPoint_Pad_D1.2mm` | Bare PCB Copper |

---

## 4. Step 3 — Critical Pinouts & Custom Footprint Details (Must Verify!)

### 4.1 Flush Castellated `Seeed_XIAO_RA4M1_Castellated_SMD` Footprint & Underside Pad Keepout
The **Seeed Studio XIAO RA4M1 (`102010551`)** measures **`21.0 × 17.8 mm`** with `2 × 7` (`14` total) castellated half-holes on a `2.54 mm` pitch and `15.24 mm` (`600 mil`) row-to-row spacing, **plus 16 exposed SMD pads on its bottom side** (`BAT+/BAT-`, SWD, RESET/BOOT, `D11–D18` / CAN). Flush-mounting it cleanly requires two key rules:

1. **Castellated SMD Pads (`1` through `14`):**
   * **Pad Type:** `SMD`, `Rounded Rectangle` (`Corner radius = 20%`), layers `F.Cu`, `F.Paste`, `F.Mask`.
   * **Pad Size:** **`1.60 mm` (along `2.54 mm` pitch) × `2.00 mm` (across edge)** centered on `Y_local = ±8.25 mm` (`16.50 mm` span) so `~0.35 mm` of copper extends outward beyond the `17.8 mm` XIAO edge for quick, inspectable hand fillets.
2. **Mandatory Underside Belly-Pad Keepout (`Keepout_XIAO_Underside_Pads`):**
   * Create a **Rule Area (`Keepout: Tracks, Vias, Copper Pour`)** on `F.Cu` spanning **`X = 0.95 .. 16.90 mm`, `Y = 4.00 .. 16.10 mm`** directly beneath the XIAO body. This guarantees `100%` soldermask-covered bare FR-4 under all 16 exposed bottom pads (`BAT+/BAT-`, SWD, CAN) so zero shorts can ever occur!
3. **XIAO RA4M1 Pin Connections (Placed at `(10.54, 10.00) mm`, Rotation `180°`, USB-C Facing West):**

| XIAO Pad # | XIAO Pad Name | Board Coordinates (`mm`) | `RA4M1` MCU Pin | Carrier PCB Net | Electrical Role |
| :---: | :---: | :---: | :--- | :--- | :--- |
| **Pad 14** | **`5V`** | `(2.92, 1.75)` (North-West) | `VBUS` (via Schottky) | **`+5V_USB`** | Feeds `R13 = 10 Ω` (`1.58 kHz` USB LPF) along North edge |
| **Pad 13** | **`GND`** | `(5.46, 1.75)` (North-West) | `VSS / AVSS0` | **`GND`** | Bonded via dual adjacent `0.6/0.3 mm` vias `(4.19, 1.75)` & `(6.73, 1.75)` to `B.Cu` `GND` plane |
| **Pad 2** | **`D1 / A1`** | `(5.46, 18.25)` (South-West) | `P000 / AN000` | **`/ADC_IN`** | Dedicated 14-bit SAR ADC input (routed `100%` along South edge, `> 10.6 mm` from `+5V_USB`) |
| *Pads 1, 3–12* | `D0, D2–D10, 3V3` | — | — | *Unconnected* | Explicit KiCad **No-Connect (`X`)** flags in `Eeschema` |

> [!NOTE]
> Unlike the larger Nano R4, the **Seeed Studio XIAO RA4M1** ties `AVCC0` / `VREFH0` internally to its onboard `3.3 V` regulator (no external `AREF` pin). Do **not** call `analogReference(AR_EXTERNAL)` in firmware; use the default `AR_DEFAULT` (`3.3 V`) reference with `analogReadResolution(14)`.

---

### 4.2 `OPA2365AIDR` (`U1`, `U2` — `SOIC-8`) Multi-Unit Pinout

> [!IMPORTANT]
> In KiCad `Eeschema`, dual op-amp symbols have **three units**: **Unit A** (Amplifier 1), **Unit B** (Amplifier 2), and **Unit C** (Power Pins `4` and `8`). Ensure `U1C` and `U2C` are placed and wired!

| `SOIC-8` Pin | Function | **`U1` (`OPA2365AIDR`) Net** | **`U2` (`OPA2365AIDR`) Net** |
| :---: | :---: | :--- | :--- |
| **1** | `OUT A` | `OUT_PRE` (Stage 1 Preamp Output) | `OUT_LPF` (Stage 3 `45 Hz` LPF Output $\rightarrow$ `R11`) |
| **2** | `-IN A` | Preamp Feedback (`R2=220Ω`, `R4=100kΩ`, `C2=1nF`) | Tied directly to **Pin 1 (`OUT_LPF`)** |
| **3** | `+IN A` | **`IN_POS`** (`C1=68nF` & `R1=1MΩ` — *Guard Ring!*) | From `R10` (`24.9kΩ`) & `C6` (`100nF` to `VREF`) |
| **4** | **`V-`** | **`GND`** | **`GND`** |
| **5** | `+IN B` | From `C4` (`1µF`) & `R8` (`45.3kΩ` to `VREF`) | **`VREF_DIV`** (`R5=100k`, `R6=100k`, `C8=10µF`) |
| **6** | `-IN B` | Tied directly to **Pin 7 (`OUT_HPF`)** | Tied directly to **Pin 7 (`VREF`)** |
| **7** | `OUT B` | `OUT_HPF` (Stage 2 `5 Hz` HPF Output $\rightarrow$ `R9`) | **`VREF`** (`1.650 V` Buffered Virtual Ground) |
| **8** | **`V+`** | **`+3V3_ANA`** (`3.30 V`, decoupled `<2mm` by `C11`) | **`+3V3_ANA`** (`3.30 V`, decoupled `<2mm` by `C12`) |

---

### 4.3 `1.58 kHz` USB Power-Supply LPF (`R13`, `C9 || C13`) & `MCP1700T-3302E/TT` (`U3` — `SOT-23-3`)

1. **Pre-LDO RC Low-Pass Filter:**
   * Connect **`+5V_USB`** (from `A1` Pad `14`) to Pad 1 of **`R13 = 10 Ω`** (`0805`, `1%`, LCSC `C17415`).
   * Connect Pad 2 of `R13` to net **`+5V_FILT`**, decoupled to `GND` by **`C9 = 10 µF`** (`X5R/X7R`) in parallel with **`C13 = 100 nF`** (`X7R`), forming a `1.576 kHz` low-pass pole (`~56 dB` attenuation at `1 MHz`) with `< 0.06 V` DC drop at normal `~5.8 mA` AFE load.
   * Attach a **`PWR_FLAG`** (`#FLG02`) to `+5V_FILT` in `Eeschema` so KiCad's ERC knows `U3` Pin 3 (`power_in`) is driven through passive series resistor `R13`.
2. **`MCP1700T-3302E/TT` (`U3` — `SOT-23-3`) Pinout:**
   * **Pin 1:** **`GND`**
   * **Pin 2:** **`VOUT`** (`+3V3_ANA = +3.300 V` $\rightarrow$ `C10 = 10 µF` to `GND`)
   * **Pin 3:** **`VIN`** (`+5V_FILT` from `R13` / `C9` / `C13`)

---

### 4.4 `JP1` (`EAR / MIC`) 2-Pad SMD Solder Jumper & Universal `PJ-320A` (`J1`) Wiring

Replacing the mechanical slide switch with a flat 2-pad SMD solder jumper (**`JP1`**: `SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm`) eliminates contact wear, BOM cost, and enclosure side-slot cutouts:

1. **Footprint Geometry (`JP1`):**
   * Two `1.0 × 1.5 mm` rounded-rectangle pads on `F.Cu` + `F.Mask` at `1.30 mm` center pitch (`0.30 mm` solder-bridge gap).
   * **Excluded from `F.Paste`**, BOM (`in_bom no` / copper-only), and Pick-and-Place so PCBA boards arrive **OPEN (`EAR` mode)** by default.
2. **Low-Noise Wiring of `JP1`:**
   * Place `JP1` on the **low-impedance `+3V3_ANA` side** of `R12` (`2.2 kΩ`):
     * **`JP1` Pad 1:** Connected to **`+3V3_ANA`**.
     * **`JP1` Pad 2:** Connected to Pad 1 of **`R12` (`2.2 kΩ`)**; Pad 2 of `R12` connects to **`VIN_RAW`** (ahead of `C1 = 68 nF`).
   * **Default (`OPEN = EAR`):** `R12` floats open-circuit (`0.00 mA` DC into `16–32 Ω` dynamic earphone coils).
   * **Solder-Bridged (`BRIDGE = MIC`):** Supplies `+3.30 V` through `2.2 kΩ` to power electret microphone JFET capsules while `C1` (`68 nF`) blocks DC from `U1A+`.
3. **Universal `PJ-320A` (`J1`) Wiring:**
   * **`Pad 2 (Tip)`** $\rightarrow$ **`VIN_RAW`** (protected by adjacent bidirectional ESD diode `D1` `PESD3V3L1BA` with dual `GND` vias).
   * **`Pad 3 (Ring 1)`** $\rightarrow$ **No-Connect (`X`)**.
   * **`Pad 1 (Sleeve)` AND `Pad 4 (Ring 2)`** $\rightarrow$ **`GND`** (supports both 3-pole TRS earphones/mics and 4-pole CTIA earbuds).

---

## 5. Step 4 — PCB Layout (`48.0 × 20.0 mm`) & Zero-Crossing Barrier Column

### 5.1 Board Outline & Mechanical Keepouts
1. **`Edge.Cuts`:** Closed **`48.0 mm × 20.0 mm`** outline (`X = 0 .. 48.0 mm`, `Y = 0 .. 20.0 mm`).
2. **Enclosure Corner Keepouts:** Bare `F.Cu` keepouts at `(0..2.5, 0..0.60)`, `(0..2.5, 19.40..20.0)`, `(45.5..48.0, 0..2.5)`, and `(45.5..48.0, 17.5..20.0)` for the screwless snap-fit enclosure rails/posts.
3. **XIAO Belly-Pad Keepout:** `Keepout_XIAO_Underside_Pads` at `(0.95..16.90, 4.00..16.10)` blocking all `F.Cu` tracks/pours and all vias beneath `A1`'s 16 bottom pads.

### 5.2 Three-Zone Placement Coordinates
1. **West Digital Zone (`X = 0.0 .. 21.1 mm`):**
   * **`A1` (`Seeed Studio XIAO RA4M1`)** at `(10.54, 10.00) mm`, rotation `180°` (USB-C overhangs `X = -2.0 .. 0.0 mm`).
2. **Center Power LPF + LDO & Anti-Aliasing Barrier Column (`X = 21.1 .. 25.0 mm`, Top-Power / Bottom-ADC):**
   * **North Power Chain:** `R13` `(22.75, 2.15)` $\rightarrow$ `C9` `(22.75, 4.20)` $\rightarrow$ `C13` `(22.75, 6.25)` $\rightarrow$ `U3` `(22.80, 9.10)` $\rightarrow$ `C10` `(22.75, 12.00)`.
   * **South ADC Anti-Aliasing Chain:** `R11` `(22.75, 14.05)` $\rightarrow$ `C7` `(22.75, 16.10)` $\rightarrow$ `TP4` `(21.95, 18.00)` & `TP6` `(23.70, 18.00)`.
   * **Why This Ordering Matters:** Keeping Power at North (`Y ≤ 3.38 mm` for `+5V_USB`) and `/ADC_IN` at South (`Y ≥ 14.05 mm`) separates noisy USB input power from the 14-bit analog output by **`> 10.6 mm` with zero crossings and zero vias on either net!**
3. **East Quiet Analog Island (`X = 25.0 .. 48.0 mm`):**
   * **`U2` (`LPF + VREF`)** at `(31.80, 5.70)` + `C12` (`100 nF` `< 2 mm` from Pin 8); **`U1` (`Preamp + HPF`)** at `(31.80, 14.10)` + `C11` (`100 nF` `< 2 mm` from Pin 8).
   * **Active `VREF` Guard Ring:** Encircles high-impedance node `IN_POS` (`U1` Pin 3, `C1`, `R1`) on `F.Cu` at `1.650 V` (`0 A` surface leakage).
   * **`JP1` (`EAR / MIC` Solder Jumper)** at `(41.80, 17.80)` next to `R12` `(42.50, 13.70)`.
   * **`J1` (`PJ-320A`)** at `(48.00, 8.80, -90°)` with `D1` (`PESD3V3L1BA`) at `(45.20, 4.50)`.

---

## 6. Step 5 — Exporting Fabrication Files & 3D CAD Model

1. **STEP 3D Export for Fusion 360:** In `Pcbnew`, choose **File $\rightarrow$ Export $\rightarrow$ STEP...**, check **`Export board body`**, **`Export components`**, and **`Fuse shapes into single model`**, and save to `hardware_enclosure/EarScope_XIAO_RA4M1_PCB.step`.
2. **Gerber & Excellon Outputs:** Pre-generated and verified in [`fabrication_files/gerbers/`](../fabrication_files/gerbers/) and [`fabrication_files/EarScope_XIAO_RA4M1_Gerbers_JLCPCB.zip`](../fabrication_files/EarScope_XIAO_RA4M1_Gerbers_JLCPCB.zip), alongside turnkey [`EarScope_JLCPCB_BOM.csv`](../fabrication_files/EarScope_JLCPCB_BOM.csv) and [`EarScope_JLCPCB_CPL.csv`](../fabrication_files/EarScope_JLCPCB_CPL.csv).
