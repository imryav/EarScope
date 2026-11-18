# EarScope XIAO RA4M1 (`Rev 2.0`) — `kicad-happy` Automated Hardware Design Review & Release Gate

**Project:** EarScope In-Ear Bio-Acoustic Cardiac Monitor (`5 Hz – 45 Hz` AFE + `1.58 kHz` USB Power LPF + `JP1` Solder Jumper + Seeed Studio XIAO RA4M1 `102010551`)  
**KiCad Project Directory:** [`hardware_pcb/EarScope_XIAO_RA4M1/`](../hardware_pcb/EarScope_XIAO_RA4M1/)  
**Turnkey Fabrication Package:** [`fabrication_files/`](../fabrication_files/) (`EarScope_XIAO_RA4M1_Gerbers_JLCPCB.zip`, `gerbers/`, `EarScope_JLCPCB_BOM.csv`, `EarScope_JLCPCB_CPL.csv`)  
**Audit Suite:** [`aklofas/kicad-happy`](https://github.com/aklofas/kicad-happy) (Schematic, Full Copper-Graph PCB, Cross-Analysis, Gerber/Excellon CAM, EMC Pre-Compliance, Pairwise Geometric DRC, and Strict Fabrication Release Gate)  
**Release Gate Verdict:** **`PASS — Ready for fabrication` (`fab_release_gate.py --strict`: `11 pass / 0 warn / 0 fail`, EMC Score `100 / 100`)**

---

## 1. Executive Summary & Routed PCB Preview

The `Rev 2.0` production **EarScope Carrier PCB** (`48.0 × 20.0 × 1.6 mm`, `-29.4%` area reduction vs. `Rev 1.0`, 2-layer FR4, single-sided top assembly) has been generated as a native KiCad 8/9 project with complete RS-274X (X2) Gerbers + Excellon drill outputs (including routed oval slots for `J1`) and verified end-to-end against [`aklofas/kicad-happy`](https://github.com/aklofas/kicad-happy) (`--strict`) and exhaustive pairwise geometric DRC (`0` violations).

![EarScope XIAO RA4M1 Routed 2-Layer PCB](figures/earscope_routed_pcb.svg)

| Audit Stage | Analyzer Script | Result | Key Metrics (`Rev 2.0`) |
| :--- | :--- | :--- | :--- |
| **Schematic Audit** | `analyze_schematic.py` | **0 Errors / 0 Warnings** | `38` PCB footprints (`31` BOM parts + `JP1` solder jumper + `TP1–TP6`), `0` unconnected/single-pin nets, `31/31` MPN & footprint coverage |
| **PCB Layout & Copper Graph** | `analyze_pcb.py --full` | **100% Routed** | `30/30` PCB nets routed (`unrouted_count: 0`), `0` courtyard/keepout violations, `262` segments, `33` vias (`17` `GND` stitching vias), `Keepout_XIAO_Underside_Pads` verified clear |
| **Pairwise Geometric DRC** | `drc_check.py` | **0 Violations** | Exhaustive check across all `99` pads, `262` segments, `33` vias, `38` courtyards, `5` keepout zones, and `48.0 × 20.0 mm` `Edge.Cuts` |
| **Schematic ↔ PCB Parity** | `cross_analysis.py` | **0 Total Findings** | `0` error, `0` warning, `0` info — exact 1:1 component, footprint, pin-to-pad, and net synchronization |
| **DFM Capability** | `analyze_pcb.py` (`dfm`) | **Standard Tier (`0` Violations)** | Min track `0.25 mm`, min drill `0.30 mm`, min annular ring `0.15 mm` (fits lowest-cost `$2` JLCPCB 2-layer pool) |
| **Gerber & Drill CAM Audit** | `analyze_gerbers.py` | **0 Findings (`Complete`)** | All `9/9` `.gbrjob` layers present, closed `48.0 × 20.0 mm` `Edge.Cuts` loop, `33` PTH vias + `4` routed `0.6 × 1.5 mm` `J1` oval slots + `2` NPTH holes |
| **EMC Pre-Compliance** | `analyze_emc.py` | **`100 / 100` (`0` Errors, `0` Warnings)** | Unbroken `B.Cu` solid `GND` plane, `1.58 kHz` USB pre-LDO LPF (`R13 + C9 || C13`), zero-crossing North/South barrier (`> 10.6 mm` `+5V_USB` ↔ `/ADC_IN` separation), `VREF` guard ring, `D1` ESD clamp |
| **BOM & PCBA Export** | `EarScope_JLCPCB_BOM/CPL.csv` | **100% Complete** | `19` LCSC SMT lines (`30` PCBA parts, incl. `R13 = 10R` JLCPCB Basic `C17415`; `A1` XIAO RA4M1 hand-soldered; `JP1` bare copper) |
| **Strict Fabrication Gate** | `fab_release_gate.py --strict` | **`PASS`** | **`11 pass, 0 warn, 0 fail`** |

---

## 2. Two-Stage Filtered Power Tree & Analog Architecture

```text
USB-C Host Power (via Seeed Studio XIAO RA4M1 Pad 14 [5V])
 └── +5V_USB (5.0 V, PWR_FLAG #FLG01)
      └── R13 (10 Ω 1% 0805, LCSC C17415 Basic — Pre-LDO Power-Supply Noise LPF)
           └── +5V_FILT (PWR_FLAG #FLG02, fc = 1.576 kHz, ~56 dB rejection @ 1 MHz)
                ├── C9  (10 µF 25V X5R 0805 bulk LPF capacitor)
                ├── C13 (100 nF 50V X7R 0805 low-ESL HF LPF bypass capacitor)
                └── U3: Microchip MCP1700T-3302E/TT (250 mA Low-Noise LDO, Iq = 1.6 µA)
                     └── +3V3_ANA (3.300 V ultra-quiet analog island supply)
                          ├── C10 (10 µF 25V X5R 0805 LDO output stability capacitor)
                          ├── U1: TI OPA2365AIDR #1 (+ C11 = 100 nF local bypass, < 2 mm from Pin 8)
                          ├── U2: TI OPA2365AIDR #2 (+ C12 = 100 nF local bypass, < 2 mm from Pin 8)
                          ├── R5 / R6 (100 kΩ / 100 kΩ 1%) + C8 (10 µF) -> U2B VREF Buffer (1.650 V)
                          └── JP1 (SolderJumper_2_Open: OPEN = EAR, BRIDGE = MIC) -> R12 (2.2 kΩ) -> VIN_RAW
```

* **Total Analog Supply Current (`+3V3_ANA`):** `~4.8 mA` in `EAR` mode (`JP1` open) and `~5.8 mA` in `MIC` mode (`JP1` bridged).
* **DC Drop Across `R13 = 10 Ω`:** `58 mV` at `5.8 mA` (`< 0.19 V` worst-case transient), keeping `+5V_FILT` `> 1.3 V` above `U3`'s `3.48 V` dropout voltage while attenuating `100 kHz – 2 MHz` USB buck converter ripple before it reaches `U3`.
* **XIAO RA4M1 14-Bit ADC Interface:** `A1` Pad `2` (`D1/A1`, `P000/AN000`) samples `/ADC_IN` (`0.000 – 3.300 V`, quiescent `1.650 V` = code `8192`) referenced to XIAO RA4M1's internal `3.3 V` `AVCC0`/`VREFH0` rail (`analogReadResolution(14)`).

---

## 3. Subcircuit Verification (`Rev 2.0` Hardware Updates)

1. **`JP1` 2-Pad SMD Solder Jumper Replacing `SW1` (`EAR / MIC`):**
   * `JP1` (`SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm` at `(41.80, 17.80) mm`) sits on the low-impedance `+3V3_ANA` side of `R12 = 2.2 kΩ`, with `F.Paste` omitted so boards arrive open (`EAR` mode, `0 V` DC) and can be bridged with a solder droplet for electret microphones (`MIC` mode).
2. **`1.58 kHz` USB Power-Supply Noise LPF (`R13`, `C9 || C13`):**
   * `R13 = 10 Ω` (`UNI-ROYAL 0805W8F100JT5E`, LCSC `C17415` Basic) + `C9 = 10 µF` (`C15850`) || `C13 = 100 nF` (`C49678`) on `+5V_FILT` ahead of `U3` (`MCP1700T-3302E/TT`), verified in both [`AFE_Cardiac_5-45Hz.asc`](AFE_Cardiac_5-45Hz.asc) and [`EarScope_SPICE_Sim.kicad_sch`](../hardware_pcb/EarScope_SPICE_Sim/EarScope_SPICE_Sim.kicad_sch).
3. **`Seeed Studio XIAO RA4M1` (`A1`) & Underside Belly-Pad Protection:**
   * Placed flush at `(10.54, 10.00, 180°)` on 14 extended castellated SMD pads (`2.0 × 1.6 mm`).
   * `Keepout_XIAO_Underside_Pads` (`[0.95..16.90] × [4.00..16.10] mm`) enforces zero `F.Cu` copper and zero vias underneath all 16 exposed underside pads (including `BAT+/BAT-` and SWD).
4. **Preserved Cardiac AFE Chain (`5–45 Hz`):**
   * `J1` (`PJ-320A`) + `D1` (`PESD3V3L1BA` ESD clamp) $\rightarrow$ `C1 = 68 nF` / `R1 = 1 MΩ` (`2.34 Hz` breathing pre-filter with active `VREF` guard ring) $\rightarrow$ `U1A` (`×455.5` / `53.2 dB` preamp, `R2 = 220 Ω`, `R4 = 100 kΩ`, `C2 = 1 nF`) $\rightarrow$ `U1B` (`5 Hz` Sallen-Key HPF) $\rightarrow$ `U2A` (`45 Hz` Sallen-Key LPF) $\rightarrow$ `R11 = 100 Ω` + `C7 = 100 nF` SAR ADC anti-kickback filter $\rightarrow$ `A1` Pad `2` (`D1/A1`).

---

## 4. Iterative Issues Caught & Fixed During `Rev 2.0` Build

1. **`power_pin_not_driven` ERC Warning on `+5V_FILT`:** Adding series LPF resistor `R13` decoupled `+5V_FILT` from `+5V_USB`'s `PWR_FLAG` (`#FLG01`), flagging `U3` Pin 3 (`power_in`). Resolved by placing `#FLG02` (`power:PWR_FLAG`) on `+5V_FILT` (`0` ERC warnings).
2. **North/South Barrier Column Ordering (`+5V_USB` vs. `/ADC_IN` Crossing):** Placing `R13/U3` at the top (`Y = 2.15..12.00 mm`) and `R11/C7/TP4/TP6` at the bottom (`Y = 14.05..18.00 mm`) aligned `+5V_USB` directly with `A1` Pad `14` `(2.92, 1.75)` and `/ADC_IN` directly with `A1` Pad `2` `(5.46, 18.25)`, eliminating trace crossings and vias on both nets and boosting the EMC pre-compliance score to **`100 / 100`**.
3. **West Rail Keepout & `TP4` Courtyard Clearance:** Adjusting West snap-fit rail keepouts to `0..0.60 mm` / `19.40..20.0 mm` and nudging `TP4` to `(21.95, 18.00)` cleared `A1`'s courtyard with `0` geometric DRC violations.
4. **Excellon Oval Slot Generation for `J1` (`PJ-320A`):** Updated `PTH.drl` CAM output to emit routed `G00 / M15 / G01 / M16 / G05` Excellon slot paths for `J1`'s four `0.60 × 1.50 mm` oval PTH terminals, passing `analyze_gerbers.py` and `fab_release_gate.py --strict` (`11/11 PASS`).

---

## 5. Generated Project & Manufacturing Files

* **KiCad 8/9 Project:** [`EarScope_XIAO_RA4M1.kicad_pro`](../hardware_pcb/EarScope_XIAO_RA4M1/EarScope_XIAO_RA4M1.kicad_pro)
* **Complete Wired Schematic (`Rev 2.0`):** [`EarScope_XIAO_RA4M1.kicad_sch`](../hardware_pcb/EarScope_XIAO_RA4M1/EarScope_XIAO_RA4M1.kicad_sch)
* **Routed 2-Layer PCB (`48.0 × 20.0 mm`):** [`EarScope_XIAO_RA4M1.kicad_pcb`](../hardware_pcb/EarScope_XIAO_RA4M1/EarScope_XIAO_RA4M1.kicad_pcb)
* **Custom Footprint Library (`.pretty`):** [`EarScope_Footprints.pretty/`](../hardware_pcb/EarScope_XIAO_RA4M1/EarScope_Footprints.pretty/) + [`fp-lib-table`](../hardware_pcb/EarScope_XIAO_RA4M1/fp-lib-table)
* **Master Engineering BOM (`31` BOM Parts):** [`EarScope_Master_BOM.csv`](../fabrication_files/EarScope_Master_BOM.csv)
* **JLCPCB Turnkey PCBA Upload Files (`30` Populated Parts, `A1` Hand-Soldered, `JP1` Bare Copper):**
  * [`EarScope_XIAO_RA4M1_Gerbers_JLCPCB.zip`](../fabrication_files/EarScope_XIAO_RA4M1_Gerbers_JLCPCB.zip)
  * [`EarScope_JLCPCB_BOM.csv`](../fabrication_files/EarScope_JLCPCB_BOM.csv)
  * [`EarScope_JLCPCB_CPL.csv`](../fabrication_files/EarScope_JLCPCB_CPL.csv)
