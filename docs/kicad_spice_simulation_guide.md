# KiCad 8 / 9 Integrated SPICE (`ngspice`) Simulation & Verification Guide (`Rev 2.0`)

This guide explains how to verify the **EarScope `5 Hz – 45 Hz` Bio-Acoustic Analog Front-End (AFE)** and **`1.58 kHz` USB Power-Supply Noise LPF** directly inside **KiCad 8 or KiCad 9** using KiCad's built-in **`ngspice`** circuit simulator (`Inspect -> Simulator`), without needing any external simulation software.

To make verification effortless while also teaching the complete KiCad SPICE workflow, this repository provides **both**:
1. **A Ready-to-Run 1-Click KiCad SPICE Project:** [`hardware_pcb/EarScope_SPICE_Sim/`](../hardware_pcb/EarScope_SPICE_Sim/) — pre-wired with Texas Instruments' `OPA365` macromodel wrapped for the 8-pin `SOIC-8` `OPA2365AIDR` (`U1`, `U2`), SPICE-safe passive values, `+3.30 V` analog supply (`V1`), `AC / SIN` bio-acoustic stimulus (`V2`), `+5.0 V` USB supply (`V3`) feeding the **`R13 = 10 Ω` + `C9 = 10 µF || C13 = 100 nF`** power-supply LPF (`+5V_FILT`), and pre-saved Bode & Transient plot tabs (`.wbk`).
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
       - **`V(/ADC_IN)`** (red wave): Clean, unclipped **`25 Hz`** output centered at **`1.650 V`**, swinging smoothly between **`~0.76 V` and `~2.54 V`** (`~1.78 Vpp`, `Gain ≈ ×445`), ready for the **Seeed Studio XIAO RA4M1** 14-bit SAR ADC (`Pad 2: D1/A1`, `0.00 V – 3.30 V`).

---

## 2. Why a Dedicated SPICE Testbench Is Used (Top 4 KiCad `ngspice` Gotchas)

If you open the manufacturing PCB schematic ([`hardware_pcb/EarScope_XIAO_RA4M1/EarScope_XIAO_RA4M1.kicad_sch`](../hardware_pcb/EarScope_XIAO_RA4M1/EarScope_XIAO_RA4M1.kicad_sch)) and click `Inspect -> Simulator` directly without preparation, `ngspice` will refuse to run. Understanding **why** explains the four most important rules of SPICE simulation in KiCad:

### Gotcha 1: Mechanical & Digital Parts Have No Analog SPICE Model
A PCB manufacturing schematic contains physical connectors, solder jumpers, ESD diodes, LDOs, test pads, and microcontrollers (`J1` `PJ-320A`, `JP1` `SolderJumper_2_Open`, `D1` `PESD3V3L1BA`, `U3` `MCP1700`, `TP1–TP6`, and `A1` `Seeed Studio XIAO RA4M1`).
- **Rule:** Either simulate in a dedicated analog testbench ([`EarScope_SPICE_Sim.kicad_sch`](../hardware_pcb/EarScope_SPICE_Sim/EarScope_SPICE_Sim.kicad_sch)) while keeping the PCB schematic untouched for manufacturing, **or** double-click each non-simulatable part (`A1, J1, JP1, D1, U3, TP1–TP6`) in the schematic and check **`Exclude from simulation`** at the bottom of **Symbol Properties**.

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
- Similarly, European resistor notation like **`220R`** (`R2`), **`100R`** (`R11`), or **`10R`** (`R13`) should be written as pure numbers (**`220`**, **`100`**, **`10`**), and **`1M`** must always be written **`1Meg`** in SPICE schematics:

| Component | PCB Silkscreen / BOM Value | SPICE-Safe Value (`ngspice`) | Circuit Role |
| :--- | :--- | :--- | :--- |
| **`R1`** | `1M` | **`1Meg`** | Input bias to `VREF` ($f_c = 2.34\text{ Hz}$ with `C1 = 68n`) |
| **`R2`** | `220R` | **`220`** | Stage 1 gain resistor ($G = 1 + 100\text{k}/220 = 455.5$) |
| **`R11`** | `100R` | **`100`** | SAR ADC anti-kickback series resistor |
| **`R13`** | `10R` | **`10`** | USB power-supply LPF series resistor ($f_c = 1.576\text{ kHz}$ with `C9 \|\| C13`) |
| **`C1–C13`** | `68nF`, `1uF`, `100nF`, `10uF` | **`68n`**, **`1u`**, **`100n`**, **`10u`** | Standard SPICE metric prefixes |

### Gotcha 4: SPICE Requires Explicit Excitation Sources & Reference Ground (`GND`)
On the real PCB, `+5V_USB` comes from the XIAO RA4M1's USB-C port (`Pad 14`), `+3V3_ANA` comes from the LDO (`U3`), and `VIN_RAW` comes from the earphone plugged into `J1`. In [`EarScope_SPICE_Sim.kicad_sch`](../hardware_pcb/EarScope_SPICE_Sim/EarScope_SPICE_Sim.kicad_sch), three sources from **`Simulation_SPICE`** drive the circuit:
- **`V1` (`Simulation_SPICE:VDC`):** `+` connected to **`+3V3_ANA`**, `-` connected to **`GND`**, `Value = 3.3`.
- **`V2` (`Simulation_SPICE:VSIN`):** `+` connected to **`VIN_RAW`**, `-` connected to **`GND`**, configured with **both** `AC = 1` (for normalized `0 dB` Bode sweeps) and `SIN(0 2m 25)` (for `2 mV` peak, `25 Hz` transient heart-sound tests).
- **`V3` (`Simulation_SPICE:VDC`):** `+` connected to **`+5V_USB`**, `-` connected to **`GND`**, `Value = 5.0` — feeding **`R13 = 10`** into **`+5V_FILT`** decoupled by **`C9 = 10u`** || **`C13 = 100n`** to verify the `1.58 kHz` USB power-supply LPF.

---

## 3. Step-by-Step DIY Guide: Setting Up SPICE Yourself in KiCad 8 / 9

Follow these steps whenever you want to build or modify a SPICE simulation schematic in KiCad from scratch:

### Step 1: Assign the `OPA2365AIDR` SPICE Model to `U1` and `U2`
1. In the Schematic Editor, double-click **`U1`** (to open **Symbol Properties**) and click the **`Simulation Model...`** button at the bottom left.
2. Select **`SPICE model from file`**:
   - **File:** Browse to `hardware_pcb/EarScope_SPICE_Sim/OPA2365_Dual.lib` (or `${KIPRJMOD}/OPA2365_Dual.lib`).
   - **Model:** Select **`OPA2365AIDR`** (`Subcircuit`).
3. Click the **`Pin Assignments`** tab and verify the 1-to-1 `SOIC-8` mapping (`1=outa, 2=ina-, 3=ina+, 4=vee, 5=inb+, 6=inb-, 7=outb, 8=vcc`).
4. Click **OK** and repeat for **`U2`**.

### Step 2: Place Supply & Bio-Acoustic Signal Sources (`Simulation_SPICE`)
1. Press **`A`** (*Add Symbol*), search for **`Simulation_SPICE`**, and place:
   - **`VDC`** (`V1`): Wire Pin `+` to **`+3V3_ANA`** and Pin `-` to **`GND`** (`Value = 3.3`).
   - **`VSIN`** (`V2`): Wire Pin `+` to **`VIN_RAW`** and Pin `-` to **`GND`** (`dc=0`, `ampl=2m`, `f=25`, `ac=1`).
   - **`VDC`** (`V3`): Wire Pin `+` to **`+5V_USB`** and Pin `-` to **`GND`** (`Value = 5.0`) ahead of `R13` (`10 Ω`) and `C9` (`10u`) || `C13` (`100n`) on `+5V_FILT`.

---

## 4. Essential Verification Tests & Acceptance Criteria

Open **`Inspect -> Simulator`** and run the following checks to confirm 100% analog and power-filter health:

### Test 1: DC Operating Point (`OP`) — Quiescent Bias & USB LPF Rail
1. Choose **`OP` (Operating Point)** and click **Run (`►`)**:
   - **`+5V_USB`** & **`+5V_FILT`** = **`5.000 V`**
   - **`+3V3_ANA`** = **`3.300 V`**
   - **`VREF_DIV`** & **`VREF`** = **`1.650 V`** (`±0.001 V`)
   - **`OUT_PRE`** = **`~1.68 V`** *(Stage 1 amplifies `OPA2365`'s `~75 µV` input offset by `×455.5` $\rightarrow$ `+34 mV` above `VREF`)*
   - **`OUT_HPF`**, **`OUT_LPF`**, and **`ADC_IN`** = **`1.650 V`** *(Stage 2's `C3`/`C4` capacitors strip `OUT_PRE`'s DC offset completely!)*

### Test 2: AC Small-Signal Sweep (`AC`) — `5 Hz – 45 Hz` Bandpass & USB Power LPF
1. Run **`AC`** (`100` pts/decade, `0.1 Hz` to `1 MHz`):
   - **Mid-Band Peak Gain (`V(/ADC_IN)` @ `16–20 Hz`):** **`52.9 – 53.1 dB`** (`~444 V/V`).
   - **Lower / Upper `-3 dB` Cutoffs:** **`~5.34 Hz`** and **`~46.12 Hz`**.
   - **Sub-Cardiac Breathing Rejection (`@ 0.25 Hz`):** **`> 71 dB` rejection** relative to passband.
   - *(Optional USB LPF Bode Check)*: Set `ac=0` on `V2` and `ac=1` on `V3`, then plot **`V(/+5V_FILT) (gain)`** — confirms `-3 dB` cutoff at **`1.576 kHz`**, **`-36.0 dB`** at `100 kHz`, and **`-56.1 dB`** at `1 MHz`.

### Test 3: Cardiac Transient (`TRAN`) — Linear Output Swing & Zero Distortion
1. Run **`TRAN`** (`step = 200u`, `stop = 250m`):
   - **`V(/ADC_IN)`** is a pure, symmetric sine wave centered at **`1.650 V`**, swinging from **`~0.76 V` to `~2.54 V`** (`~1.78 Vpp`) with zero clipping.

### Test 4: `5 mV`, `0.25 Hz` Breathing Stress Test & `JP1` Bridged (`MIC`) Bias Test
- **Breathing Stress Test:** Set `V2` to `ampl=5m f=0.25`: **`V(/OUT_PRE)`** stays safely inside **`1.41 V – 1.96 V`**, and **`V(/ADC_IN)`** moves by `< ±1.5 mV` around `1.650 V`.
- **`JP1` Bridged (`MIC` Mode, `2.2 kΩ` Bias):** Connect `R12 = 2.2k` between `+3V3_ANA` and `VIN_RAW`: `C1 = 68 nF` blocks 100% of the DC bias, keeping **`V(/ADC_IN) = 1.650 V`** unchanged.

---

## 5. Summary Pass / Fail Verification Checklist

| Test | Signal / Probe | Target Specification | Expected KiCad `ngspice` Reading |
| :--- | :--- | :--- | :--- |
| **DC Bias (`OP`)** | `V(/VREF)` & `V(/ADC_IN)` | `1.650 V ± 5 mV` (ADC Code `8192`) | **`1.6500 V`** |
| **USB Power LPF (`AC`)** | `V(/+5V_FILT)` (`V3` `AC=1`) | $f_c \approx 1.58\text{ kHz}$, `> 50 dB` @ `1 MHz` | **`1.576 kHz` (`-56.1 dB` @ `1 MHz`)** |
| **Mid-Band Gain (`AC`)** | `V(/ADC_IN) (gain)` @ `18 Hz` | `52.0 – 54.0 dB` | **`52.95 dB` (`×444.3`)** |
| **Passband `-3 dB` (`AC`)** | $f_L$ – $f_H$ | `5.0–5.6 Hz` to `44.5–47.0 Hz` | **`5.34 Hz – 46.12 Hz`** |
| **Breathing Rejection (`AC`)** | Gain @ `0.25 Hz` vs. `18 Hz` | `> 65 dB` attenuation | **`71.2 dB` attenuation (`-18.25 dB` abs)** |
| **Cardiac Sine (`TRAN`)** | `V(/ADC_IN)` @ `2 mVpk, 25 Hz` | Symmetric `~1.78 Vpp` around `1.65 V` | **`0.76 V` to `2.54 V` (zero clipping)** |

---

## 6. Troubleshooting Common KiCad Simulator Messages

| Error / Symptom in KiCad Simulator | Root Cause | Quick Fix |
| :--- | :--- | :--- |
| `Error: no such subcircuit: opa2365aidr` | Model path not resolved | Open `U1`/`U2` $\rightarrow$ `Simulation Model...` and verify `File` points to `${KIPRJMOD}/OPA2365_Dual.lib` |
| `Too few / too many parameters for subcircuit type "opa365"` | Pointed `U1` directly at 5-pin `docs/OPA365.lib` instead of 8-pin wrapper | Point `U1` and `U2` to `OPA2365_Dual.lib` (`Model: OPA2365AIDR`) |
| Gain is `-60 dB` instead of `+53 dB`! | `R1` typed as `1M` (`0.001 Ω`) instead of `1Meg` (`1,000,000 Ω`) | Change `R1` value to **`1Meg`** |
| `Warning: singular matrix: check nodes ...` | Missing `GND` symbol on a voltage source or floating capacitor node | Ensure `V1-`, `V2-`, `V3-`, `U1.4`, `U2.4`, `R6.2`, `C7.2`, `C8.2`, `C9.2`, `C13.2` connect to `power:GND` |
| `No simulation data for A1 / J1 / JP1` | Running Simulator on PCB schematic `EarScope_XIAO_RA4M1.kicad_sch` directly | Open [`hardware_pcb/EarScope_SPICE_Sim/EarScope_SPICE_Sim.kicad_pro`](../hardware_pcb/EarScope_SPICE_Sim/EarScope_SPICE_Sim.kicad_pro), or check `Exclude from simulation` on mechanical/MCU parts |
