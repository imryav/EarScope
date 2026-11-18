# EarScope — In-Ear Bio-Acoustic Cardiac Monitor (Seeed Studio XIAO RA4M1 Edition)

**EarScope** is an ultra-low-noise, compact hardware and software acquisition platform that captures acoustic and micro-mechanical cardiac biosignals (**PCG**, **SCG**, and **GCG**) directly from an occluded ear canal using standard wired earphones (`3.5 mm` AUX), inspired by *LubDubDecoder (ACM CHI '26)*.

> **Project Engineering Documentation & Hardware Files:**
> * **[Turnkey PCB Fabrication & JLCPCB PCBA Package (`fabrication_files/`)](fabrication_files/)** — Ready-to-order Gerber/Drill ZIP ([`EarScope_XIAO_RA4M1_Gerbers_JLCPCB.zip`](fabrication_files/EarScope_XIAO_RA4M1_Gerbers_JLCPCB.zip)), unpacked RS-274X Gerbers + Excellon Drills, LCSC BOM + CPL CSVs, and ordering guide.
> * **[LTspice Finalization, Verification & Simulation Results](docs/ltspice_simulation_guide.md)** — Validated `3.30 V` cardiac AFE + `1.58 kHz` USB power-supply LPF schematic ([`AFE_Cardiac_5-45Hz.asc`](docs/AFE_Cardiac_5-45Hz.asc) + [`OPA365.lib`](docs/OPA365.lib)), rationale, and verification plots.
> * **[Fabrication-Ready KiCad 8 / 9 Project (`hardware_pcb/EarScope_XIAO_RA4M1/`)](hardware_pcb/EarScope_XIAO_RA4M1/)** — Complete editable schematic (`.kicad_sch`), `100%` routed `48.0 × 20.0 mm` 2-layer PCB (`.kicad_pcb`), and custom footprint library (`.pretty`).
> * **[KiCad 8 / 9 Integrated SPICE (`ngspice`) Simulation Guide & 1-Click Testbench](docs/kicad_spice_simulation_guide.md)** — Ready-to-run KiCad SPICE project ([`hardware_pcb/EarScope_SPICE_Sim/`](hardware_pcb/EarScope_SPICE_Sim/) with [`OPA2365_Dual.lib`](hardware_pcb/EarScope_SPICE_Sim/OPA2365_Dual.lib)) + step-by-step `OP`, `AC` Bode, and `TRAN` verification instructions.
> * **[`kicad-happy` Automated Design Review & Fabrication Release Gate (`11/11 PASS`)](docs/kicad_happy_design_review.md)** — Full electrical, Gerber/CAM, DFM (`0` violations), and EMC (`100 / 100`) sign-off via [`aklofas/kicad-happy`](https://github.com/aklofas/kicad-happy).
> * **[KiCad 8 / 9 Schematic & PCB Design Guide](docs/kicad_pcb_design_guide.md)** — Complete symbol/footprint mapping, custom castellated XIAO RA4M1 footprint with underside pad keepout, `48.0 × 20.0 mm` 2-layer layout, `1.58 kHz` USB LPF, `JP1` solder jumper, active `VREF` guard ring, and Gerber export.
> * **[Enclosure & Carrier PCB Co-Design Guide](docs/fusion360_enclosure_guide.md)** — Parametric Fusion 360 snap-fit enclosure co-designed for the `48.0 × 20.0 mm` XIAO RA4M1 carrier PCB.

---

## 1. System Architecture Overview

EarScope converts microscopic tympanic/ear-canal pressure oscillations (`5 Hz – 45 Hz`) into a high-resolution digital stream over **USB-C**:

* **Sensor Input (`3.5 mm` AUX `PJ-320A` + `JP1` SMD Solder Jumper):** Supports standard passive dynamic earphones (`16–32 Ω` voice coil operating in reverse as a zero-bias acoustic transducer via the ear-canal occlusion effect) **and** electret microphone capsules via a compact 2-pad SMD solder jumper (**`JP1: OPEN = EAR / BRIDGE = MIC`**, switching `2.2 kΩ` DC bias from `+3V3_ANA` with zero mechanical switch contact bounce or enclosure side cutout).
* **Cardiac Analog Front-End (`OPA2365` × 2):** Dual ultra-low-noise (`4.5 nV/√Hz`), rail-to-rail CMOS operational amplifiers configured as a breathing-protected `53.2 dB` preamplifier followed by a 4th-order Butterworth `5 Hz – 45 Hz` bandpass filter (`-60 dB/decade` sub-cardiac slope including input coupling).
* **Two-Stage Quiet `3.30 V` Analog Power Island (`1.58 kHz` Pre-LPF + Low-Noise LDO):** Noisy `+5V_USB` power first passes through a dedicated passive RC Low-Pass Filter (**`R13 = 10 Ω`** feeding **`+5V_FILT`** decoupled by **`C9 = 10 µF` || `C13 = 100 nF`**, $f_c = 1.576\text{ kHz}$, providing `~56 dB` high-frequency USB switching rejection at `1 MHz` where LDO PSRR degrades) before `U3` (`MCP1700T-3302E/TT`) regulates a clean **`3.300 V`** analog rail (`+3V3_ANA`) and **`1.650 V`** virtual-ground reference.
* **Thumb-Sized Digital Acquisition & Streaming (`Seeed Studio XIAO RA4M1` / `102010551`):** Powered by the **Renesas `RA4M1`** (`R7FA4M1AB3CFM`, `48 MHz` Arm Cortex-M4F with FPU) in a `21.0 × 17.8 mm` 14-pad castellated SMD footprint, shrinking the carrier PCB by `29.4%` (`48.0 × 20.0 mm`) while sampling at `500 Hz` with a **true 14-bit SAR ADC** (`0–16,383` counts, `1 LSB = 201.4 µV`) and zero Wi-Fi/BLE RF burst interference over onboard **USB-C**.

```text
[Earphones / Mic (3.5mm AUX + JP1)] ---> [Cardiac AFE (OPA2365, 5–45Hz, USB LPF + 3.30V LDO)] ---> [Seeed XIAO RA4M1 14-Bit ADC (Pin D1/A1)] ===(USB-C @ 500Hz)===> [PC / Python UI]
```

---

## 2. Target Physiological Signals

1. **Phonocardiography (PCG):** Audible and sub-audible heart valve closure sounds (`S1` *"Lub"* and `S2` *"Dub"*).
2. **Seismocardiography (SCG) & Gyrocardiography (GCG):** Reconstruction of chest-wall micro-mechanical cardiac vibrations coupled acoustically through the vasculature and skull into the sealed ear canal.
3. **Cardiac Fiducial Timing Landmarks:**
   * **MC** — Mitral Valve Closure
   * **IM** — Isovolumetric Moment
   * **AO** — Aortic Valve Opening
   * **MA** — Maximal Acceleration
   * **RE** — Rapid Ejection

---

## 3. Finalized Analog Front-End (AFE) & Power Filtering Design

The production schematic (`AFE_Cardiac_5-45Hz.asc` & `EarScope_XIAO_RA4M1.kicad_sch`) comprises six tightly coordinated analog and power-conditioning blocks:

### 3.1 USB Power-Supply Noise Low-Pass Filter (`R13`, `C9 || C13`) & `3.30 V` LDO (`U3`)
Laptop and phone USB-C `VBUS` rails carry `100 kHz – 2 MHz` DC-DC buck switching ripple where CMOS LDO pass-element capacitance degrades PSRR. Placing a passive RC Low-Pass Filter (**$R_{13} = 10\text{ }\Omega$** feeding net **`+5V_FILT`** decoupled by **$C_9 = 10\text{ }\mu\text{F}$** in parallel with low-ESL **$C_{13} = 100\text{ nF}$**) ahead of `U3` (`MCP1700T-3302E/TT`) establishes a `1.58 kHz` pre-filter pole:

$$
f_{c,\text{USB}} = \frac{1}{2\pi R_{13} (C_9 + C_{13})} = \frac{1}{2\pi \cdot 10\text{ }\Omega \cdot 10.1\text{ }\mu\text{F}} \approx 1.576\text{ kHz}
$$

* **Negligible Dropout Overhead:** At full AFE + LDO quiescent load (`< 5 mA` on `+3V3_ANA`, `< 0.05 V` drop; `< 0.19 V` even at `18.4 mA`), `+5V_FILT` stays well above `U3`'s `3.48 V` dropout threshold.
* **High-Frequency Attenuation:** Suppresses `100 kHz` switching ripple by `-36 dB` and `1 MHz` spikes by `~56 dB` *before* `U3`, while damping ceramic MLCC input ringing ($Q < 0.3$).

### 3.2 Virtual Ground Buffer (`U2B`)
A symmetric `1%` thin-film divider ($R_{\text{REF1}} = 100\text{ k}\Omega$, $R_{\text{REF2}} = 100\text{ k}\Omega$) filtered by $C_{\text{REF}} = 10\text{ }\mu\text{F}$ ($f_c \approx 0.32\text{ Hz}$ on `U2B+`) establishes a quiet mid-supply reference:

$$
V_{\text{REF}} = V_{\text{CC\_ANA}} \cdot \frac{R_{\text{REF2}}}{R_{\text{REF1}} + R_{\text{REF2}}} = 3.300\text{ V} \cdot \frac{100\text{ k}\Omega}{100\text{ k}\Omega + 100\text{ k}\Omega} = 1.650\text{ V} \quad (\text{14-bit ADC Code } 8192)
$$

### 3.3 Input Coupling, Breathing Motion Pre-Filter (`C_IN = 68 nF`) & `JP1` (`EAR / MIC`) Solder Jumper
In occluded ear canals, slow respiratory pressure waves (`0.2 – 0.4 Hz`) reach **`~5 mV` peak** — more than `15×` stronger than in-ear cardiac `S1/S2` pulses. Setting $C_{\text{IN}} = 68\text{ nF}$ against $R_{\text{BIAS}} = 1\text{ M}\Omega$ creates a passive high-pass corner ahead of Stage 1:

$$
f_{c,\text{in}} = \frac{1}{2\pi R_{\text{BIAS}} C_{\text{IN}}} = \frac{1}{2\pi \cdot 1\text{ M}\Omega \cdot 68\text{ nF}} \approx 2.34\text{ Hz}
$$

This pre-attenuates `0.25 Hz` breathing artifacts by **`8×` (`-18.0 dB`) *before* preamplification**, completely preventing Stage 1 rail saturation while incurring `< 0.07 dB` loss at `18 Hz`. Ahead of $C_{\text{IN}}$, a 2-pad flat SMD solder jumper (**`JP1`**, `SolderJumper-2_P1.3mm_Open`) leaves **`R_MIC = 2.2 kΩ`** completely open by default (**`OPEN = EAR`**) so `0.00 mA` DC flows through `16–32 Ω` passive earphone voice coils, or connects `R_MIC` to `+3V3_ANA` when bridged with a solder bead (**`BRIDGE = MIC`**) to power electret microphone capsules. Eliminating the mechanical switch removes contact resistance drift, BOM cost, and any dust/ESD aperture in the enclosure wall.

### 3.4 Stage 1 Low-Noise Non-Inverting Preamplifier (`U1A`)
Selected production gain uses **$R_G = 220\text{ }\Omega$** with $R_F = 100\text{ k}\Omega$ in parallel with **$C_F = 1\text{ nF}$**:

$$
G_1 = 1 + \frac{R_F}{R_G} = 1 + \frac{100\text{ k}\Omega}{220\text{ }\Omega} = 455.5 \approx 53.2\text{ dB}, \qquad f_{p,\text{EMI}} = \frac{1}{2\pi R_F C_F} \approx 1.59\text{ kHz}
$$

* Balances high SNR for low-impedance passive earphones (`16–32 Ω`) with wide linear headroom (`> 1.38 V` margin to both rails under `5 mV` breathing waves) and rolls off RF/EMI picked up by the earphone cable above `1.59 kHz`.
* Dual `0805` pads (`R2` + unpopulated `R3` `DNP`) allow easy population of `1 kΩ` (`40.1 dB`), `100 Ω` (`60.0 dB`), or fine parallel gain trimming.

### 3.5 Stage 2 (`5 Hz` HPF, `U1B`) & Stage 3 (`45 Hz` LPF, `U2A`)
* **Stage 2 — 2nd-Order Butterworth Sallen-Key HPF (`U1B`):** $C_{1H} = C_{2H} = 1\text{ }\mu\text{F}$, $R_{AH} = 22.6\text{ k}\Omega$ (feedback to `U1B` output), $R_{BH} = 45.3\text{ k}\Omega$ (to `VREF`), $f_c \approx 4.97\text{ Hz}$. Strips Stage 1 amplified DC offset ($V_{\text{OS}} \times 455.5$) and combines with $C_{\text{IN}}$ for `-60 dB/decade` sub-cardiac rejection.
* **Stage 3 — 2nd-Order Butterworth Sallen-Key LPF (`U2A`):** $R_{1L} = R_{2L} = 24.9\text{ k}\Omega$, $C_{AL} = 200\text{ nF}$, $C_{BL} = 100\text{ nF}$ (referenced directly to **`VREF`**), $f_c \approx 45.2\text{ Hz}$.

### 3.6 Stage 4 — 14-Bit SAR ADC Charge-Reservoir Filter
A passive output filter (**$R_{\text{OUT}} = 100\text{ }\Omega$**, **$C_{\text{OUT}} = 100\text{ nF}$** to `GND`, $f_c \approx 15.9\text{ kHz}$) isolates `U2A` from capacitive loading and absorbs switched-capacitor sampling kickback from the Renesas `RA4M1` 14-bit SAR ADC (`< 0.35 LSB` settling error at `500 Hz`).

---

## 4. Validated LTspice Simulation Results

Full SPICE verification instructions and waveforms are available in [`docs/ltspice_simulation_guide.md`](docs/ltspice_simulation_guide.md).

| Parameter | Final Simulated Value (`R_G = 220 Ω`, `C_IN = 68 nF`) |
| :--- | :--- |
| **Analog Supply & XIAO ADC Span (`VCC_ANA` / `AVCC0`)** | `3.300 V` (`1 LSB = 201.4 µV` @ 14-bit) |
| **USB Pre-LDO Power LPF (`R13 = 10 Ω`, `C9 || C13 = 10.1 µF`)** | **`f_c = 1.576 kHz`** (`~56 dB` pre-attenuation @ `1 MHz`) |
| **Quiescent Output (`V(ADC_IN)`)** | `1.650 V` (14-bit ADC center code `8192`) |
| **Net Mid-Band Gain (`@ 18 Hz`)** | **`52.95 dB` (`×444.3`)** |
| **System `-3 dB` Passband** | **`5.34 Hz – 46.12 Hz`** |
| **Breathing Rejection (`@ 0.25 Hz`)** | **`-71.2 dB` relative to passband** (`3,630×` attenuation) |
| **Stage 1 Swing under `5 mV`, `0.25 Hz` Breathing** | `1.408 V – 1.892 V` (**zero clipping**, `> 1.38 V` rail margin) |
| **Integrated Input-Referred Noise (`5–45 Hz`)** | **`0.141 µVrms`** (`63.3 µVrms` = **`0.31 LSBrms`** at `ADC_IN`) |
| **Power-Up Soft-Start Time** | **`~2.3 s`** smooth exponential settling |

![EarScope AFE AC Frequency and Phase Response](docs/figures/afe_bode_response.svg)

![Preventing Stage 1 Preamp Saturation with C_IN = 68 nF](docs/figures/cin_preamp_saturation_comparison.svg)

---

## 5. Seeed Studio XIAO RA4M1 Interface & Firmware Configuration

### 5.1 Hardware Pin Mapping (`Seeed Studio XIAO RA4M1` / `102010551`)

| Carrier PCB Signal | XIAO RA4M1 Pad | `RA4M1` Pin | Function & Routing Notes |
| :--- | :--- | :--- | :--- |
| **`+5V_USB`** | **`5V`** (Pad `14`, North-West) | `VBUS` (via onboard Schottky) | Feeds `R13` (`10 Ω`) $\rightarrow$ `+5V_FILT` (`C9 || C13`) $\rightarrow$ `U3` `3.30 V` LDO |
| **`GND`** | **`GND`** (Pad `13`, North-West) | `VSS / AVSS0` | Dual immediate `0.6/0.3 mm` stitching vias straight to solid `B.Cu` `GND` plane |
| **`ADC_IN`** | **`D1 / A1`** (Pad `2`, South-West) | `P000 / AN000` | Dedicated 14-bit SAR ADC input (avoids `D0/A0` DAC mux & `D4/D5` I2C); routed `100%` along South edge `> 10.6 mm` away from `+5V_USB` |
| *Internal `3.3 V` Ref* | *(Internal on XIAO)* | `AVCC0 / VREFH0` | XIAO RA4M1 ties `AVCC0`/`VREFH0` internally to its `3.3 V` rail (no external `AREF` pin); use default `AR_DEFAULT` reference |

### 5.2 Reference Seeed Studio XIAO RA4M1 Acquisition Setup (`C++`)

```cpp
#include <Arduino.h>

constexpr uint8_t PIN_CARDIAC_ADC = A1;     // XIAO RA4M1 Pad 2 (D1 / A1 -> P000 / AN000)
constexpr uint32_t SAMPLE_PERIOD_US = 2000; // 500 Hz exact sampling rate

void setup() {
  Serial.begin(230400);
  // Note: Seeed Studio XIAO RA4M1 ties AVCC0/VREFH0 internally to 3.3 V (default AR_DEFAULT).
  analogReadResolution(14); // Enable true 14-bit SAR resolution (0 .. 16383, mid = 8192)
}

void loop() {
  static uint32_t lastSampleUs = 0;
  uint32_t nowUs = micros();
  if (nowUs - lastSampleUs >= SAMPLE_PERIOD_US) {
    lastSampleUs += SAMPLE_PERIOD_US;
    uint16_t raw14 = analogRead(PIN_CARDIAC_ADC);
    Serial.println(raw14);
  }
}
```

---

## 6. Fabrication-Ready KiCad 8 / 9 Carrier PCB (`Rev 2.0`) & `kicad-happy` Verification (`PASS`)

The editable KiCad 8/9 source project lives in [`hardware_pcb/EarScope_XIAO_RA4M1/`](hardware_pcb/EarScope_XIAO_RA4M1/), while the ready-to-order manufacturing package lives in [`fabrication_files/`](fabrication_files/). All design and CAM files passed **`11 / 11` strict automated release-gate checks** in [`aklofas/kicad-happy`](https://github.com/aklofas/kicad-happy) (full audit in [`docs/kicad_happy_design_review.md`](docs/kicad_happy_design_review.md)):

* **Compact Form Factor & Underside Keepout:** Shrunk by **`29.4%`** to **`48.0 × 20.0 × 1.6 mm`** (`960 mm²`) with a dedicated `Keepout_XIAO_Underside_Pads` (`[0.95..16.90] × [4.00..16.10] mm`) blocking all `F.Cu` copper and vias beneath the XIAO RA4M1's 16 exposed underside pads (`BAT+/BAT-`, SWD, CAN, etc.).
* **Routing & Parity:** `30 / 30` PCB nets `100%` routed (`0` unrouted nets, `0` cross-analysis findings, `262` segments, `33` vias including `17` `GND` stitching vias over an unbroken `B.Cu` `GND` plane), with `+5V_USB` isolated along the North edge and `/ADC_IN` along the South edge (`> 10.6 mm` separation, zero crossings).
* **DFM & Clearances:** **`standard` (`$2`) 2-layer tier** with **`0` geometric DRC/DFM violations**, `0` courtyard overlaps, and `0` keepout violations (`min_track = 0.25 mm`, `min_drill = 0.30 mm`, `min_annular_ring = 0.15 mm`).
* **Gerber & Drill CAM Audit:** **`0` findings (`Complete`)** — all `9/9` RS-274X (X2) Gerber layers + `PTH.drl` (including routed `0.6 × 1.5 mm` oval slots for `J1`) + `NPTH.drl` + `.gbrjob` bundled in [`EarScope_XIAO_RA4M1_Gerbers_JLCPCB.zip`](fabrication_files/EarScope_XIAO_RA4M1_Gerbers_JLCPCB.zip).
* **EMC & ESD Sign-Off:** **`100 / 100` EMC score (`0` errors, `0` warnings)** — `1.58 kHz` pre-LDO USB power LPF (`R13 + C9 || C13`), bidirectional ESD diode **`D1` (`PESD3V3L1BA`, `SOD-323`)** right at `J1` (`PJ-320A`), local `100 nF` decoupling (`C11, C12`) `< 2 mm` from `U1` and `U2`, and active `VREF` guard ring around `U1A+`.
* **Turnkey PCBA Outputs:** Ready-to-upload [`EarScope_JLCPCB_BOM.csv`](fabrication_files/EarScope_JLCPCB_BOM.csv) (`19` LCSC lines / `30` SMD parts, including JLCPCB Basic resistor `R13 = 10 Ω` `C17415`) and [`EarScope_JLCPCB_CPL.csv`](fabrication_files/EarScope_JLCPCB_CPL.csv) (`30` placement rows; `A1` XIAO RA4M1 hand-soldered flush via 14 castellated pads; `JP1` bare copper solder jumper).

![EarScope Routed 2-Layer Carrier PCB](docs/figures/earscope_routed_pcb.svg)

---

## 7. Production Bill of Materials (BOM)

All passive components use **`0805` SMD** packages for straightforward hand soldering or turnkey PCBA (`JLCPCB` / `PCBWay`).

| Designator | Value / Part Number | Package / Footprint | Qty | Engineering Notes |
| :--- | :--- | :--- | :---: | :--- |
| **A1 (MCU)** | `Seeed Studio XIAO RA4M1` (`102010551`) | Castellated SMD (`2×7`, `21.0 × 17.8 mm`) | 1 | Flush-mounted via 14 castellated pads (`F.Cu`/via keepout under 16 belly pads); USB-C |
| **U1, U2** | `OPA2365AIDR` | SOIC-8 | 2 | Dual `4.5 nV/√Hz`, zero-crossover rail-to-rail CMOS op-amp |
| **U3** | `MCP1700T-3302E/TT` | SOT-23-3 | 1 | Low-noise `3.30 V` LDO fed from filtered `+5V_FILT`, powering `+3V3_ANA` (`VCC_ANA`) |
| **D1** | `PESD3V3L1BA` | SOD-323 | 1 | Low-capacitance bidirectional `3.3 V` ESD clamp on `J1` (`VIN_RAW`, LCSC `C15772`) |
| **J1** | `PJ-320A` (3.5 mm TRRS) | `TRRS-PJ-320A` (`12.1 × 6.1 × 5.0 mm`) | 1 | Earphone / headset AUX input receptacle (`Tip` = signal, `Ring2+Sleeve` = `GND`) |
| **JP1** | `SolderJumper_2_Open` (PCB Copper) | `SolderJumper-2_P1.3mm_Open` (`1.0×1.5 mm` pads) | (PCB) | Zero-cost 2-pad SMD solder jumper (`OPEN = EAR` `0 V` DC; `BRIDGE = MIC` `+3V3_ANA` bias; no `F.Paste`) |
| **R13 (`R_LPF`)** | `10 Ω` (`1%`, `0805W8F100JT5E`) | 0805 (LCSC `C17415` Basic) | 1 | `1.58 kHz` USB power-supply LPF series resistor (`+5V_USB` $\rightarrow$ `+5V_FILT`) |
| **C9, C13** | `10 µF` (`C15850`) + `100 nF` (`C49678`) | 0805 (`X5R/X7R`) | 1 + 1 | Parallel bulk + HF ceramic LPF bank on `+5V_FILT` ahead of `U3` (`f_c = 1.576 kHz`) |
| **C8, C10** | `10 µF` (`CL21A106KAYNNNE`) | 0805 (`X5R/X7R`, `25 V`, `C15850`) | 2 | `C8` filters `VREF_DIV` (`U2B+`); `C10` stabilizes `U3` `+3V3_ANA` LDO output |
| **C1 (`C_IN`)** | `68 nF` | 0805 (`X7R`/`C0G`, `50 V`, `C53085`) | 1 | `2.34 Hz` breathing pre-filter ahead of `U1A+` |
| **C2 (`C_F`)** | `1 nF` | 0805 (`C0G/NP0`, `50 V`, `C1588`) | 1 | Stage 1 feedback HF/EMI roll-off (`1.59 kHz`) across `R4` |
| **C3, C4 (`C_1H, C_2H`)** | `1 µF` | 0805 (`X7R`, `50 V`, `C28323`) | 2 | Stage 2 `5 Hz` Sallen-Key HPF capacitors |
| **C5 (`C_AL`)** | `220 nF` / `200 nF` | 0805 (`X7R`, `50 V`, `C315201`) | 1 | Stage 3 `45 Hz` Sallen-Key LPF feedback capacitor |
| **C6, C7 (`C_BL, C_OUT`)** | `100 nF` | 0805 (`X7R`, `50 V`, `C49678`) | 2 | `C6` tied to **`VREF`**; `C7` SAR ADC charge reservoir tied to **`GND`** near `A1` `D1/A1` |
| **C11, C12** | `100 nF` | 0805 (`X7R`, `50 V`, `C49678`) | 2 | Local `+3V3_ANA` bypass (`< 2 mm`) on `U1` and `U2` |
| **R4–R6 (`R_F, R_REF1/2`)** | `100 kΩ` (`1%`) | 0805 (`C149504`) | 3 | Stage 1 feedback resistor and symmetric `1.650 V` divider |
| **R1 (`R_BIAS`)** | `1 MΩ` (`1%`) | 0805 (`C17514`) | 1 | Input DC bias reference to `VREF` |
| **R2 (`R_G`), R3 (`DNP`)** | `220 Ω` (`1%`, `C17557`) + `DNP` pad | 0805 | 1 + 1 | Selected Stage 1 gain (`×455.5` / `53.2 dB`) + parallel trim footprint |
| **R7, R8 (`R_AH, R_BH`)** | `22.6 kΩ` (`C17562`), `45.3 kΩ` (`C25900`) | 0805 (`1%`) | 1 ea | Stage 2 `5 Hz` Butterworth Sallen-Key HPF resistors |
| **R9, R10 (`R_1L, R_2L`)** | `24.9 kΩ` (`1%`) | 0805 (`C17590`) | 2 | Stage 3 `45 Hz` Butterworth Sallen-Key LPF resistors |
| **R11 (`R_OUT`)** | `100 Ω` (`1%`) | 0805 (`C17407`) | 1 | Isolates `U2A` output from `C7` SAR charge reservoir |
| **R12 (`R_MIC`)** | `2.2 kΩ` (`1%`) | 0805 (`C17520`) | 1 | Electret capsule bias pull-up in series with `JP1` (`+3V3_ANA` side) |

---

## 8. Repository Structure

```text
EarScope/
├── README.md                                       # Main system architecture, BOM & results
├── fabrication_files/                              # Ready-to-order PCB & PCBA manufacturing package (Rev 2.0)
│   ├── README.md                                   # JLCPCB / PCBWay ordering, XIAO soldering & JP1 guide
│   ├── EarScope_XIAO_RA4M1_Gerbers_JLCPCB.zip      # Single-upload Gerber RS-274X + Excellon Drill ZIP
│   ├── EarScope_JLCPCB_BOM.csv                     # Turnkey LCSC SMT Bill of Materials (19 lines / 30 parts)
│   ├── EarScope_JLCPCB_CPL.csv                     # Turnkey Pick-and-Place coordinates (mm, Top side)
│   ├── EarScope_Master_BOM.csv                     # Full 31-part engineering BOM (incl. Seeed XIAO RA4M1)
│   └── gerbers/                                    # Unpacked .gbr, .drl & .gbrjob CAM layers
├── docs/
│   ├── AFE_Cardiac_5-45Hz.asc                      # Finalized LTspice schematic (XIAO RA4M1 + USB Power LPF)
│   ├── OPA365.lib                                  # Texas Instruments OPA365 / OPA2365 SPICE macro-model
│   ├── ltspice_simulation_guide.md                 # LTspice verification guide & benchmark results
│   ├── kicad_spice_simulation_guide.md             # KiCad 8/9 integrated ngspice simulation guide
│   ├── kicad_pcb_design_guide.md                   # Step-by-step KiCad 8/9 schematic, PCB layout & Gerber guide
│   ├── kicad_happy_design_review.md                # Automated kicad-happy PCB review & PASS release gate report
│   ├── fusion360_enclosure_guide.md                # Parametric 3D enclosure & 48×20 mm PCB co-design guide
│   └── figures/                                    # Verification waveforms & PCB layout SVG diagrams
│       ├── afe_bode_response.svg
│       ├── cin_preamp_saturation_comparison.svg
│       ├── transient_startup_and_cardiac_output.svg
│       ├── input_referred_noise_spectrum.svg
│       ├── kicad_pcb_floorplan.svg
│       └── earscope_routed_pcb.svg
└── hardware_pcb/
    ├── EarScope_XIAO_RA4M1/                        # Editable KiCad 8/9 manufacturing project (Rev 2.0)
    │   ├── EarScope_XIAO_RA4M1.kicad_pro
    │   ├── EarScope_XIAO_RA4M1.kicad_sch           # 0 ERC warnings, 31 BOM parts + JP1 + TP1–TP6
    │   ├── EarScope_XIAO_RA4M1.kicad_pcb           # 48.0 × 20.0 mm 2-layer 100% routed carrier PCB
    │   ├── fp-lib-table
    │   ├── EarScope_Footprints.pretty/             # 9 custom/verified SMD footprints (.kicad_mod)
    │   └── bom/                                    # Source BOM & CPL exports
    └── EarScope_SPICE_Sim/                         # Standalone KiCad 8/9 ngspice AFE + USB LPF testbench
```