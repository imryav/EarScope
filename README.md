# EarScope — In-Ear Bio-Acoustic Cardiac Monitor (Arduino Nano R4 Edition)

**EarScope** is an ultra-low-noise, compact hardware and software acquisition platform that captures acoustic and micro-mechanical cardiac biosignals (**PCG**, **SCG**, and **GCG**) directly from an occluded ear canal using standard wired earphones (`3.5 mm` AUX), inspired by *LubDubDecoder (ACM CHI '26)*.

> **Project Engineering Documentation:**
> * **[LTspice Finalization, Verification & Simulation Results](docs/ltspice_simulation_guide.md)** — Complete ratiometric `3.30 V` analog front-end schematic (`AFE_Cardiac_5-45Hz.asc`), stage-by-stage design rationale, and full verification plots.
> * **Enclosure & Carrier PCB Co-Design Guide** (`docs/fusion360_enclosure_guide.md` — *Arduino Nano R4 mechanical revision next*).

---

## 1. System Architecture Overview

EarScope converts microscopic tympanic/ear-canal pressure oscillations (`5 Hz – 45 Hz`) into a high-resolution digital stream over **USB-C**:

* **Sensor Input (`3.5 mm` AUX — `PJ-320A`):** Supports standard passive dynamic earphones (`16–32 Ω` voice coil operating in reverse as a zero-bias acoustic transducer via the ear-canal occlusion effect) as well as electret microphone capsules (via optional SMD solder jumper `JP_BIAS`).
* **Cardiac Analog Front-End (`OPA2365` × 2):** Dual ultra-low-noise (`4.5 nV/√Hz`), rail-to-rail CMOS operational amplifiers configured as a breathing-protected `53.2 dB` preamplifier followed by a 4th-order Butterworth `5 Hz – 45 Hz` bandpass filter (`-60 dB/decade` sub-cardiac slope including input coupling).
* **Ratiometric `3.30 V` Analog Island (`VCC_ANA` = `AREF`):** A dedicated low-noise LDO (`MCP1700T-3302E/TT`) steps the noisy USB `+5 V` rail down to a quiet **`3.300 V`** supply powering both `OPA2365` ICs, the symmetric **`1.650 V`** virtual-ground buffer, **and** the external ADC reference pin (**`AREF`**) of the **Arduino Nano R4**.
* **Digital Acquisition & Streaming (`Arduino Nano R4` / `ABX00142`):** Powered by the **Renesas `RA4M1`** (`48 MHz` Arm Cortex-M4F with FPU), sampling at `500 Hz` with a **true 14-bit SAR ADC** (`0–16,383` counts, `1 LSB = 201.4 µV`) and zero Wi-Fi/BLE RF burst interference, streaming real-time packets over onboard **USB-C** to Python DSP & deep-learning waveform reconstruction software.

```text
[Earphones (3.5mm AUX)] ---> [Cardiac AFE (OPA2365, 5–45Hz, 3.30V LDO)] ---> [Arduino Nano R4 14-Bit ADC (Pin A1, AREF=3.30V)] ===(USB-C @ 500Hz)===> [PC / Python UI]
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

## 3. Finalized Analog Front-End (AFE) Design

The production schematic (`AFE_Cardiac_5-45Hz.asc`) comprises five tightly coordinated analog blocks:

### 3.1 Ratiometric Virtual Ground Buffer (`U2B`)
A symmetric `1%` thin-film divider ($R_{\text{REF1}} = 100\text{ k}\Omega$, $R_{\text{REF2}} = 100\text{ k}\Omega$) filtered by $C_{\text{REF}} = 10\text{ }\mu\text{F}$ ($f_c \approx 0.32\text{ Hz}$ on `U2B+`) establishes a rock-solid mid-supply reference:

$$
V_{\text{REF}} = V_{\text{CC\_ANA}} \cdot \frac{R_{\text{REF2}}}{R_{\text{REF1}} + R_{\text{REF2}}} = 3.300\text{ V} \cdot \frac{100\text{ k}\Omega}{100\text{ k}\Omega + 100\text{ k}\Omega} = 1.650\text{ V} \quad (\text{14-bit ADC Code } 8192)
$$

### 3.2 Input Coupling & Breathing Motion Pre-Filter (`C_IN = 68 nF`)
In occluded ear canals, slow respiratory pressure waves (`0.2 – 0.4 Hz`) reach **`~5 mV` peak** — more than `15×` stronger than in-ear cardiac `S1/S2` pulses. Setting $C_{\text{IN}} = 68\text{ nF}$ against $R_{\text{BIAS}} = 1\text{ M}\Omega$ creates a passive high-pass corner ahead of Stage 1:

$$
f_{c,\text{in}} = \frac{1}{2\pi R_{\text{BIAS}} C_{\text{IN}}} = \frac{1}{2\pi \cdot 1\text{ M}\Omega \cdot 68\text{ nF}} \approx 2.34\text{ Hz}
$$

This pre-attenuates `0.25 Hz` breathing artifacts by **`8×` (`-18.0 dB`) *before* preamplification**, completely preventing Stage 1 rail saturation while incurring `< 0.07 dB` loss at `18 Hz`. An optional `R_MIC = 2.2 kΩ` pull-up to `VCC_ANA` ahead of `C_IN` (enabled via flat SMD jumper `JP_BIAS`) supports electret capsules.

### 3.3 Stage 1 Low-Noise Non-Inverting Preamplifier (`U1A`)
Selected production gain uses **$R_G = 220\text{ }\Omega$** with $R_F = 100\text{ k}\Omega$ in parallel with **$C_F = 1\text{ nF}$**:

$$
G_1 = 1 + \frac{R_F}{R_G} = 1 + \frac{100\text{ k}\Omega}{220\text{ }\Omega} = 455.5 \approx 53.2\text{ dB}, \qquad f_{p,\text{EMI}} = \frac{1}{2\pi R_F C_F} \approx 1.59\text{ kHz}
$$

* Balances high SNR for low-impedance passive earphones (`16–32 Ω`) with wide linear headroom (`> 1.38 V` margin to both rails under `5 mV` breathing waves) and rolls off RF/EMI picked up by the earphone cable above `1.59 kHz`.
* Dual `0805` pads (or a low-profile `3 × 3 mm` SMD trimmer) allow easy population of `1 kΩ` (`40.1 dB`) or `100 Ω` (`60.0 dB`).

### 3.4 Stage 2 (`5 Hz` HPF, `U1B`) & Stage 3 (`45 Hz` LPF, `U2A`)
* **Stage 2 — 2nd-Order Butterworth Sallen-Key HPF (`U1B`):** $C_{1H} = C_{2H} = 1\text{ }\mu\text{F}$, $R_{AH} = 22.6\text{ k}\Omega$ (feedback to `U1B` output), $R_{BH} = 45.3\text{ k}\Omega$ (to `VREF`), $f_c \approx 4.97\text{ Hz}$. Strips Stage 1 amplified DC offset ($V_{\text{OS}} \times 455.5$) and combines with $C_{\text{IN}}$ for `-60 dB/decade` sub-cardiac rejection.
* **Stage 3 — 2nd-Order Butterworth Sallen-Key LPF (`U2A`):** $R_{1L} = R_{2L} = 24.9\text{ k}\Omega$, $C_{AL} = 200\text{ nF}$, $C_{BL} = 100\text{ nF}$ (referenced directly to **`VREF`**), $f_c \approx 45.2\text{ Hz}$.

### 3.5 Stage 4 — 14-Bit SAR ADC Charge-Reservoir Filter
A passive output filter (**$R_{\text{OUT}} = 100\text{ }\Omega$**, **$C_{\text{OUT}} = 100\text{ nF}$** to `GND`, $f_c \approx 15.9\text{ kHz}$) isolates `U2A` from capacitive loading and absorbs switched-capacitor sampling kickback from the Renesas `RA4M1` 14-bit SAR ADC (`< 0.35 LSB` settling error at `500 Hz`).

---

## 4. Validated LTspice Simulation Results

Full SPICE verification instructions and waveforms are available in [`docs/ltspice_simulation_guide.md`](docs/ltspice_simulation_guide.md).

| Parameter | Final Simulated Value (`R_G = 220 Ω`, `C_IN = 68 nF`) |
| :--- | :--- |
| **Analog Supply & ADC Reference (`VCC_ANA = AREF`)** | `3.300 V` (`1 LSB = 201.4 µV` @ 14-bit) |
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

## 5. Arduino Nano R4 Interface & Firmware Configuration

### 5.1 Hardware Pin Mapping (`Arduino Nano R4` / `ABX00142`)

| Carrier PCB Signal | Nano R4 Pin | `RA4M1` Pin | Function & Routing Notes |
| :--- | :--- | :--- | :--- |
| **`+5V_USB`** | **`+5V`** (`JP2` Pin 12) | VUSB (via Schottky `D1`) | Feeds input of `U3` (`MCP1700T-3302E/TT` `3.3 V` LDO) |
| **`VCC_ANA` (`3.30 V`)** | **`AREF`** (`JP1` Pin 3) | `P010 / VREFH0` | External precision 14-bit ADC full-scale reference + `100 nF` to `GND` |
| **`ADC_IN`** | **`A1`** (`JP1` Pin 5) | `P000 / AN000` | Dedicated 14-bit SAR ADC input (avoids `A0` DAC mux & `A4/A5` I2C) |
| **`GND`** | **`GND`** (`JP1` Pin 14 / `JP2` Pin 14) | `VSS / AVSS0` | Continuous solid ground plane bond |

### 5.2 Reference Arduino Nano R4 Acquisition Setup (`C++`)

```cpp
#include <Arduino.h>

constexpr uint8_t PIN_CARDIAC_ADC = A1;
constexpr uint32_t SAMPLE_PERIOD_US = 2000; // 500 Hz exact sampling rate

void setup() {
  Serial.begin(230400);
  analogReference(AR_EXTERNAL); // Lock full-scale ADC span to VCC_ANA (3.300 V) on AREF
  analogReadResolution(14);     // Enable true 14-bit SAR resolution (0 .. 16383, mid = 8192)
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

## 6. Production Bill of Materials (BOM)

All passive components use **`0805` SMD** packages for straightforward hand soldering or turnkey PCBA (`JLCPCB` / `PCBWay`).

| Designator | Value / Part Number | Package / Footprint | Qty | Engineering Notes |
| :--- | :--- | :--- | :---: | :--- |
| **MCU** | `Arduino Nano R4` (`ABX00142`) | Castellated SMD (`2×15`, `45×18 mm`) | 1 | Flush-mounted via castellated pads (no pin headers); onboard USB-C |
| **U1, U2** | `OPA2365AIDR` | SOIC-8 | 2 | Dual `4.5 nV/√Hz`, zero-crossover rail-to-rail CMOS op-amp |
| **U3** | `MCP1700T-3302E/TT` | SOT-23-3 | 1 | Low-noise `3.30 V` LDO powering `VCC_ANA` + Nano R4 `AREF` |
| **J1** | `PJ-320A` (3.5 mm TRRS) | SMD (`12.1 × 6.1 × 5.0 mm`) | 1 | Earphone / headset AUX input receptacle |
| **C_IN** | `68 nF` | 0805 (`C0G/NP0` or `X7R`, `≥25 V`) | 1 | `2.34 Hz` breathing pre-filter (`C0G` preferred to eliminate piezo microphonics) |
| **C_F** | `1 nF` | 0805 (`C0G/NP0`) | 1 | Stage 1 feedback HF/EMI roll-off (`1.59 kHz`) across `R_F` |
| **C_1H, C_2H** | `1 µF` | 0805 (`X7R`, `≥16 V`) | 2 | Stage 2 `5 Hz` Sallen-Key HPF capacitors |
| **C_AL** | `200 nF` (or `2 × 100 nF` parallel) | 0805 (`C0G` or `X7R`) | 1 | Stage 3 `45 Hz` Sallen-Key LPF feedback capacitor |
| **C_BL, C_OUT** | `100 nF` | 0805 (`C0G` or `X7R`) | 2 | `C_BL` tied to **`VREF`**; `C_OUT` tied to **`GND`** right at Nano R4 `A1` |
| **C_DEC1, C_DEC2, C_AREF** | `100 nF` | 0805 (`X7R`) | 3 | Local bypass (`< 2 mm`) on `U1`, `U2`, and Nano R4 `AREF` pin |
| **C_REF, C_LDO_IN, C_LDO_OUT** | `10 µF` | 0805 (`X7R`, `≥10 V`) | 3 | `VREF_DIV` noise filter (`U2B+`) and LDO input/output stabilization |
| **R_REF1, R_REF2, R_F** | `100 kΩ` (`1%`) | 0805 (Thin Film) | 3 | Symmetric `1.650 V` divider and Stage 1 feedback resistor |
| **R_BIAS** | `1 MΩ` (`1%`) | 0805 | 1 | Input DC bias reference to `VREF` |
| **R_G** | `220 Ω` (`1%`) | 0805 (+ optional parallel pad) | 1 | Selected Stage 1 gain (`×455.5` / `53.2 dB`) |
| **R_AH, R_BH** | `22.6 kΩ`, `45.3 kΩ` (`1%`) | 0805 | 1 ea | Stage 2 `5 Hz` Butterworth Sallen-Key HPF resistors |
| **R_1L, R_2L** | `24.9 kΩ` (`1%`) | 0805 | 2 | Stage 3 `45 Hz` Butterworth Sallen-Key LPF resistors |
| **R_OUT** | `100 Ω` (`1%`) | 0805 | 1 | Isolates `U2A` output from `C_OUT` SAR charge reservoir |
| **R_MIC + JP_BIAS** | `2.2 kΩ` + `SolderJumper_2_Open` | 0805 + SMD Jumper | 1 | Open = passive earphone (default); Bridged = electret mic bias |

---

## 7. Repository Structure

```text
EarScope/
├── README.md                                       # Main system architecture, BOM & results (English)
├── docs/
│   ├── ltspice_simulation_guide.md                 # Step-by-step LTspice guide & verification benchmark suite
│   ├── figures/                                    # Validated AC, saturation, transient & noise SVG plots
│   │   ├── afe_bode_response.svg
│   │   ├── cin_preamp_saturation_comparison.svg
│   │   ├── transient_startup_and_cardiac_output.svg
│   │   └── input_referred_noise_spectrum.svg
│   └── fusion360_enclosure_guide.md                # Parametric 3D enclosure & PCB co-design guide
├── simulation/                                     # LTspice schematics & SPICE models (AFE_Cardiac_5-45Hz.asc)
├── hardware_pcb/                                   # KiCad / EasyEDA schematic, layout & Gerbers
├── firmware_nano_r4/                               # Arduino Nano R4 (RA4M1) 14-bit 500 Hz USB-C streamer
└── software_pc/                                    # Python real-time visualization & SCG/GCG reconstruction
```