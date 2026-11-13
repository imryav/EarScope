# KiCad 8 / 9 Integrated SPICE (`ngspice`) Simulation & Verification Guide

This guide explains how to verify the **EarScope `5 Hz – 45 Hz` Bio-Acoustic Analog Front-End (AFE)** directly inside **KiCad 8 or KiCad 9** using KiCad's built-in **`ngspice`** circuit simulator (`Inspect -> Simulator`), without needing any external simulation software.

To make verification effortless while also teaching the complete KiCad SPICE workflow, this repository provides **both**:
1. **A Ready-to-Run 1-Click KiCad SPICE Project:** [`hardware_pcb/EarScope_SPICE_Sim/`](../hardware_pcb/EarScope_SPICE_Sim/) — pre-wired with Texas Instruments' `OPA365` macromodel wrapped for the 8-pin `SOIC-8` `OPA2365AIDR` (`U1`, `U2`), SPICE-safe passive values, `+3.30 V` DC supply (`V1`), `AC / SIN` bio-acoustic stimulus (`V2`), and pre-saved Bode & Transient plot tabs (`.wbk`).
2. **A Complete DIY Setup Walkthrough (Section 3):** Step-by-step instructions showing how to configure SPICE models, pin mappings, sources, and analyses from scratch on any KiCad schematic.

---

## 1. Quick-Start: Run the Pre-Configured KiCad SPICE Testbench in 30 Seconds

If you already pulled or downloaded the repository onto your computer:

1. Open **KiCad 8.0+** (or **KiCad 9.0+**) and click **`File -> Open Project...`**.
2. Navigate to **`hardware_pcb/EarScope_SPICE_Sim/`** and open **[`EarScope_SPICE_Sim.kicad_pro`](../hardware_pcb/EarScope_SPICE_Sim/EarScope_SPICE_Sim.kicad_pro)**.
3. Double-click **`EarScope_SPICE_Sim.kicad_sch`** in the left Project Tree to open the **Schematic Editor**.
   - *(Optional)* Open **`Inspect -> Electrical Rules Checker`** and click **`Run ERC`** — it passes with **`0 Errors`**.
4. In the top menu bar of the Schematic Editor, click **`Inspect -> Simulator`** to launch the integrated **`ngspice`** window.
5. Because [`EarScope_SPICE_Sim.wbk`](../hardware_pcb/EarScope_SPICE_Sim/EarScope_SPICE_Sim.wbk) is included in the folder, **two pre-configured simulation tabs** load automatically:
   - **Tab 1 (`AC` — Bode Frequency & Phase Sweep, `0.1 Hz – 100 kHz`):**
     - Click the blue **Run / Play (`►`)** button in the top-left toolbar of the Simulator window.
     - You will immediately see:
       - **`V(/ADC_IN) (gain)`** (red solid curve): Flat **`~53.0 dB` (`×444`)** passband plateau across **`~5.3 Hz – 46.1 Hz`**, steep `-60 dB/decade` breathing rejection below `5 Hz`, and `-40 dB/decade` anti-aliasing roll-off above `45 Hz`.
       - **`V(/ADC_IN) (phase)`** (red dashed curve): Smooth phase transition passing through `0°` near the geometric center of the cardiac passband (`~15–18 Hz`).
       - **`V(/OUT_PRE) (gain)`** (blue curve): Stage 1 preamplifier response (`53.17 dB` rolling off below `2.34 Hz` due to `C1 = 68 nF` and above `1.59 kHz` due to `C2 = 1 nF`).
   - **Tab 2 (`TRAN` — Time-Domain Cardiac Sine Wave, `0 – 250 ms`):**
     - Click the second tab (**`TRAN`**) at the top of the Simulator plot area and click **Run (`►`)**.
     - `V2` injects a **`2 mV` peak (`4 mVpp`) `25 Hz`** wave (representing an in-ear `S1`/`S2` heart sound).
     - You will immediately see:
       - **`V(/VREF)`** (green line): Rock-steady virtual ground at **`1.650 V`**.
       - **`V(/ADC_IN)`** (red wave): Clean, unclipped **`25 Hz`** output centered at **`1.650 V`**, swinging smoothly between **`~0.76 V` and `~2.54 V`** (`~1.78 Vpp`, `Gain ≈ ×445`), ready for the Renesas `RA4M1` 14-bit SAR ADC (`0.00 V – 3.30 V`).

---

## 2. Why a Dedicated SPICE Testbench Is Used (Top 4 KiCad `ngspice` Gotchas)

If you open the manufacturing PCB schematic ([`hardware_pcb/EarScope_NanoR4/EarScope_NanoR4.kicad_sch`](../hardware_pcb/EarScope_NanoR4/EarScope_NanoR4.kicad_sch)) and click `Inspect -> Simulator` directly without preparation, `ngspice` will refuse to run. Understanding **why** explains the four most important rules of SPICE simulation in KiCad:

### Gotcha 1: Mechanical & Digital Parts Have No Analog SPICE Model
A PCB manufacturing schematic contains physical connectors, switches, ESD diodes, LDOs, test pads, and microcontrollers (`J1` `PJ-320A`, `SW1` `PCM12SMTR`, `D1` `PESD3V3L1BA`, `U3` `MCP1700`, `TP1–TP6`, and `A1` `Arduino Nano R4`).
- **Rule:** Either simulate in a dedicated analog testbench ([`EarScope_SPICE_Sim.kicad_sch`](../hardware_pcb/EarScope_SPICE_Sim/EarScope_SPICE_Sim.kicad_sch)) while keeping the PCB schematic untouched for manufacturing, **or** double-click each non-simulatable part (`A1, J1, SW1, D1, U3, TP1–TP6`) in the schematic and check **`Exclude from simulation`** at the bottom of **Symbol Properties**.

### Gotcha 2: 5-Pin Single Op-Amp Model (`OPA365`) vs. 8-Pin Dual Package (`OPA2365AIDR`)
Texas Instruments distributes the SPICE macromodel ([`docs/OPA365.lib`](OPA365.lib)) as a **5-pin single op-amp** subcircuit:
```spice
.SUBCKT OPA365 3 4 5 2 1
* Pin order: +IN(3)  -IN(4)  +V(5)  -V(2)  OUT(1)
```
However, on the PCB schematic, `U1` and `U2` are **8-pin `SOIC-8` dual op-amps** (`OPA2365AIDR`: `1=OUTA, 2=-INA, 3=+INA, 4=V-, 5=+INB, 6=-INB, 7=OUTB, 8=V+`). Attaching a 5-pin `.SUBCKT` directly to an 8-pin symbol causes an immediate `ngspice` pin-count mismatch error.
- **Solution ([`OPA2365_Dual.lib`](../hardware_pcb/EarScope_SPICE_Sim/OPA2365_Dual.lib)):** Wrap two `OPA365` instances inside an 8-port `OPA2365AIDR` subcircuit that matches the exact `SOIC-8` physical pin numbering `1..8`:
  ```spice
  .SUBCKT OPA2365AIDR outa ina- ina+ vee inb+ inb- outb vcc
  XA ina+ ina- vcc vee outa OPA365
  XB inb+ inb- vcc vee outb OPA365
  .ENDS OPA2365AIDR
  ```

### Gotcha 3: The Classic SPICE `"1M"` Trap (`1 milli-ohm` vs. `1 Mega-ohm`!)
 SPICE (`ngspice`) is **case-insensitive**:
- Writing **`1M`** on input bias resistor `R1` is interpreted by raw SPICE as **`1 milli-ohm` (`0.001 Ω`)** instead of **`1 Mega-ohm` (`1,000,000 Ω`)**! That shifts the input high-pass cutoff $f_{c,\text{in}} = \frac{1}{2\pi R_1 C_1}$ from **`2.34 Hz`** to **`2.34 GHz`**, killing the entire cardiac signal!
- Similarly, European resistor notation like **`220R`** (`R2`) or **`100R`** (`R11`) should be written as pure numbers (**`220`**, **`100`**), and **`1M`** must always be written **`1Meg`** in SPICE schematics:

| Component | PCB Silkscreen / BOM Value | SPICE-Safe Value (`ngspice`) | Circuit Role |
| :--- | :--- | :--- | :--- |
| **`R1`** | `1M` | **`1Meg`** | Input bias to `VREF` ($f_c = 2.34\text{ Hz}$ with `C1 = 68n`) |
| **`R2`** | `220R` | **`220`** | Stage 1 gain resistor ($G = 1 + 100\text{k}/220 = 455.5$) |
| **`R11`** | `100R` | **`100`** | SAR ADC anti-kickback series resistor |
| **`C1–C12`** | `68nF`, `1uF`, `100nF` | **`68n`**, **`1u`**, **`100n`** | Standard SPICE metric prefixes |

### Gotcha 4: SPICE Requires Explicit Excitation Sources & Reference Ground (`GND`)
On the real PCB, `+3V3_ANA` comes from the USB-powered LDO (`U3`) and `VIN_RAW` comes from the earphone plugged into `J1`. In SPICE, you must drive those two nets explicitly from KiCad's built-in **`Simulation_SPICE`** symbol library:
- **`V1` (`Simulation_SPICE:VDC`):** `+` connected to **`+3V3_ANA`**, `-` connected to **`GND`**, `Value = 3.3`.
- **`V2` (`Simulation_SPICE:VSIN`):** `+` connected to **`VIN_RAW`**, `-` connected to **`GND`**, configured with **both** `AC = 1` (for normalized `0 dB` Bode sweeps) and `SIN(0 2m 25)` (for `2 mV` peak, `25 Hz` transient heart-sound tests).

---

## 3. Step-by-Step DIY Guide: Setting Up SPICE Yourself in KiCad 8 / 9

Follow these steps whenever you want to build or modify a SPICE simulation schematic in KiCad from scratch:

### Step 1: Assign the `OPA2365AIDR` SPICE Model to `U1` and `U2`
1. In the Schematic Editor, double-click **`U1`** (to open **Symbol Properties**) and click the **`Simulation Model...`** button at the bottom left.
2. Select **`SPICE model from file`**:
   - **File:** Browse to `hardware_pcb/EarScope_SPICE_Sim/OPA2365_Dual.lib` (or `${KIPRJMOD}/OPA2365_Dual.lib`).
   - **Model:** Select **`OPA2365AIDR`** (`Subcircuit`).
3. Click the **`Pin Assignments`** tab and verify the 1-to-1 `SOIC-8` mapping:
   - Symbol Pin `1` (`OUTA`) $\rightarrow$ Model Pin `1` (`outa`)
   - Symbol Pin `2` (`-INA`) $\rightarrow$ Model Pin `2` (`ina-`)
   - Symbol Pin `3` (`+INA`) $\rightarrow$ Model Pin `3` (`ina+`)
   - Symbol Pin `4` (`V-`) $\rightarrow$ Model Pin `4` (`vee`)
   - Symbol Pin `5` (`+INB`) $\rightarrow$ Model Pin `5` (`inb+`)
   - Symbol Pin `6` (`-INB`) $\rightarrow$ Model Pin `6` (`inb-`)
   - Symbol Pin `7` (`OUTB`) $\rightarrow$ Model Pin `7` (`outb`)
   - Symbol Pin `8` (`V+`) $\rightarrow$ Model Pin `8` (`vcc`)
4. Click **OK** and repeat for **`U2`**.

### Step 2: Place Supply & Bio-Acoustic Signal Sources (`Simulation_SPICE`)
1. Press **`A`** (*Add Symbol*), search for **`Simulation_SPICE`**, and place:
   - **`VDC`** (`V1`): Wire Pin `+` to **`+3V3_ANA`** and Pin `-` to **`GND`**. Double-click `V1` and set `Value` to **`3.3`**.
   - **`VSIN`** (`V2`): Wire Pin `+` to **`VIN_RAW`** and Pin `-` to **`GND`**. Double-click `V2` $\rightarrow$ **`Simulation Model...`** and set:
     - **DC offset (`dc`):** `0`
     - **Amplitude (`ampl`):** `2m` (`2 mV` peak = `4 mVpp`)
     - **Frequency (`f`):** `25` (`25 Hz`, center of `S1`/`S2` cardiac energy)
     - **AC magnitude (`ac`):** `1` (`1 V` small-signal reference so `V(/ADC_IN)` directly displays gain in `dB`)

---

## 4. Four Essential Verification Tests & Acceptance Criteria

Open **`Inspect -> Simulator`** and run the following four checks to confirm 100% analog health:

### Test 1: DC Operating Point (`OP`) — Quiescent Virtual-Ground Bias
 verifies that every op-amp stage is properly biased at mid-supply (`1.650 V` = 14-bit ADC code `8192`) without rail latch-up.
1. In the Simulator window, click **`Simulation -> New Analysis Tab...`** (or click the gear icon **`Simulation Command`**).
2. Choose **`OP` (Operating Point)** and click **OK**, then click **Run (`►`)**.
3. Look directly at the schematic canvas (KiCad annotates DC node voltages right on the wires!):
   - **`+3V3_ANA`** = **`3.300 V`**
   - **`VREF_DIV`** & **`VREF`** = **`1.650 V`** (`±0.001 V`)
   - **`OUT_PRE`** = **`~1.68 V`** *(Note: Stage 1 amplifies `OPA2365`'s tiny `~75 µV` input offset by `×455.5` $\rightarrow$ `+34 mV` above `VREF` — completely normal!)*
   - **`OUT_HPF`**, **`OUT_LPF`**, and **`ADC_IN`** = **`1.650 V`** *(Stage 2's `C3`/`C4` capacitors strip `OUT_PRE`'s DC offset completely!)*

### Test 2: AC Small-Signal Sweep (`AC`) — `5 Hz – 45 Hz` Bandpass & Breathing Rejection
1. Configure **`AC` (Small-Signal AC)** analysis:
   - **Number of points per decade:** `100`
   - **Start frequency:** `0.1` (`0.1 Hz`)
   - **Stop frequency:** `100k` (`100 kHz`)
2. Click **Run (`►`)** and check **`V(/ADC_IN) (gain)`** and **`V(/OUT_PRE) (gain)`** in the right-hand **Signals** panel.
3. Right-click `V(/ADC_IN) (gain)` in the Signals list $\rightarrow$ **`Show Cursor`** and drag the cursor to verify:
   - **Mid-Band Peak Gain (`@ 16–20 Hz`):** **`52.9 – 53.1 dB`** (`~444 V/V`).
   - **Lower `-3 dB` Cutoff ($f_L$, where gain drops to `~50.0 dB`):** **`~5.3 Hz`**.
   - **Upper `-3 dB` Cutoff ($f_H$, where gain drops to `~50.0 dB`):** **`~46.1 Hz`**.
   - **Sub-Cardiac Breathing Rejection (`@ 0.25 Hz`):** **`< -18 dB` absolute** (**`> 71 dB` rejection** relative to the `53 dB` passband!).

### Test 3: Cardiac Transient (`TRAN`) — Linear Output Swing & Zero Distortion
1. Configure **`TRAN` (Transient)** analysis:
   - **Time step:** `200u` (`200 µs`)
   - **Final time:** `250m` (`250 ms` — shows `6.25` clean cycles of `25 Hz`)
   - Leave *"Use initial conditions (`uic`)"* **unchecked** so `ngspice` starts cleanly from the `1.650 V` steady-state DC operating point.
2. Click **Run (`►`)** and plot **`V(/VREF)`** and **`V(/ADC_IN)`**:
   - **`V(/ADC_IN)`** must be a pure, symmetric sine wave centered at **`1.650 V`**, swinging from **`~0.76 V` to `~2.54 V`** (`~1.78 Vpp`) with zero flat-topping near `0 V` or `3.3 V`.

### Test 4: `5 mV`, `0.25 Hz` Breathing Artifact Stress Test & `MIC` Bias Test
- **Breathing Stress Test:** Edit `V2` (`Sim.Params`) to **`dc=0 ampl=5m f=0.25 ac=1`** (`5 mV` peak slow breathing pressure wave) and set `TRAN` Final time to **`8`** (`8 s`, step `5m`).
  - Plot **`V(/OUT_PRE)`** and **`V(/ADC_IN)`**:
    - Because `C1 = 68 nF` pre-attenuates `0.25 Hz` by `8×` ahead of `U1A`, **`V(/OUT_PRE)`** stays safely inside **`1.41 V – 1.96 V`** (over `1.3 V` away from clipping!).
    - After Stage 2 (`5 Hz` HPF), **`V(/ADC_IN)`** barely moves by **`±1.4 mV`** around `1.650 V`!
- **`MIC` Mode (`2.2 kΩ` Bias) Verification:** Connect a `2.2k` resistor (`R12`) between `+3V3_ANA` and `VIN_RAW` (in series with an electret model or `2.2k` load to `GND`). Re-run `OP` or `TRAN`: `C1 = 68 nF` blocks 100% of the DC bias on `VIN_RAW`, keeping **`V(/ADC_IN) = 1.650 V`** unchanged.

---

## 5. Summary Pass / Fail Verification Checklist

| Test | Signal / Probe | Target Specification | Expected KiCad `ngspice` Reading |
| :--- | :--- | :--- | :--- |
| **DC Bias (`OP`)** | `V(/VREF)` | `1.650 V ± 5 mV` | **`1.6500 V`** |
| **DC Output (`OP`)** | `V(/ADC_IN)` | `1.650 V ± 5 mV` (ADC Code `8192`) | **`1.6500 V`** |
| **Mid-Band Gain (`AC`)** | `V(/ADC_IN) (gain)` @ `18 Hz` | `52.0 – 54.0 dB` | **`52.95 dB` (`×444.3`)** |
| **High-Pass Corner (`AC`)** | `-3 dB` point below `18 Hz` | `5.0 – 5.6 Hz` | **`5.34 Hz`** |
| **Low-Pass Corner (`AC`)** | `-3 dB` point above `18 Hz` | `44.5 – 47.0 Hz` | **`46.12 Hz`** |
| **Breathing Rejection (`AC`)** | Gain @ `0.25 Hz` vs. `18 Hz` | `> 65 dB` attenuation | **`71.2 dB` attenuation (`-18.25 dB` abs)** |
| **Cardiac Sine (`TRAN`)** | `V(/ADC_IN)` @ `2 mVpk, 25 Hz` | Symmetric `~1.78 Vpp` around `1.65 V` | **`0.76 V` to `2.54 V` (zero clipping)** |
| **Breathing Headroom (`TRAN`)** | `V(/OUT_PRE)` @ `5 mVpk, 0.25 Hz` | Within `[0.20 V, 3.10 V]` | **`1.41 V` to `1.96 V` (`> 1.3 V` margin)** |

---

## 6. Troubleshooting Common KiCad Simulator Messages

| Error / Symptom in KiCad Simulator | Root Cause | Quick Fix |
| :--- | :--- | :--- |
| `Error: no such subcircuit: opa2365aidr` | Model path not resolved | Open `U1`/`U2` $\rightarrow$ `Simulation Model...` and verify `File` points to `${KIPRJMOD}/OPA2365_Dual.lib` |
| `Too few / too many parameters for subcircuit type "opa365"` | Pointed `U1` directly at 5-pin `docs/OPA365.lib` instead of 8-pin wrapper | Point `U1` and `U2` to `OPA2365_Dual.lib` (`Model: OPA2365AIDR`) |
| Gain is `-60 dB` instead of `+53 dB`! | `R1` typed as `1M` (`0.001 Ω`) instead of `1Meg` (`1,000,000 Ω`) | Change `R1` value to **`1Meg`** |
| `Warning: singular matrix: check nodes ...` | Missing `GND` symbol on a voltage source or floating capacitor node | Ensure `V1-`, `V2-`, `U1.4`, `U2.4`, `R6.2`, `C7.2`, `C8.2` all connect to `power:GND` |
| `No simulation data for A1 / J1 / SW1` | Running Simulator on the PCB schematic `EarScope_NanoR4.kicad_sch` directly | Open [`hardware_pcb/EarScope_SPICE_Sim/EarScope_SPICE_Sim.kicad_pro`](../hardware_pcb/EarScope_SPICE_Sim/EarScope_SPICE_Sim.kicad_pro), or check `Exclude from simulation` on mechanical/MCU parts |
