# Review Result 4: PCU Carrier Board (STM32G474 / WeAct "Long"): "Can this board do its job?"

**Date:** 2026-11-02
**Basis:** netlist exported with kicad-cli 7.0.5 from `PCB PCU.kicad_sch` (authoritative); WeAct schematic `WeAct-STM32G474CoreBoard_Long_V10 SchDoc.pdf` and board outline PDF (from the WeAct GitHub); DS12288 Rev 6 (STM32G474); TI datasheets for TLV2186 (SBOS947A), TCAN33x (SLLSEQ7F), MAX3221 (SLLS348P), SN74LVC2G07; Diodes AP2112.
**Not read (per the prompt):** README.md, PCB_LAYOUT_REMINDERS.md, and earlier REVIEW_* files.
**Marking:** **[C]** = confirmed (netlist, calculation or datasheet). **[S]** = suspected (estimate, typical values, or depends on parts I can't see).

---

## 1. Verdict

**Yes, with limitations.** Every signal reaches a correct MCU pin: 12 ADC-capable pins, FDCAN2, USART3/UART4, I2C1 and USART1 for debug. Every IC is wired to its datasheet, and I found nothing that damages hardware in normal use or in the usual fault cases. So no finding is a hard blocker.

The weakest function is **temperature**. With the fitted values the PT1000 channels only cover **+8 °C to +124 °C**. Anything colder reads as 0 counts, the same as a shorted sensor, which makes these channels useless at cold start or for ambient/electronics temperature on a UAV. The output is also directly proportional to the unmeasured board 5 V (about 1.3 °C per 1 % of 5 V at the top of the range). Fixing the range takes two resistor-value changes per channel, with no new parts.

The current channels accept only **±1.03 V** of (SIG−REF), and each sensor sees 100 nF between SIG and REF. Whether that suits the sensors depends on the sensor model, which is unknown.

Voltage, RS-232, CAN, I2C and the digital I/O all work, with the conditions listed below.

---

## 2. Measurement capability

ADC full scale = module VDDA = VREF+ (the module's ME6231 3.3 V through FB1/R7). 1 LSB = 3.3 V / 4096 = **0.806 mV**.

| Channel | Input → ADC (from netlist) | Measurable range (ADC 0…3.3 V) | Resolution | Est. error (worst case, uncalibrated → calibrated) | Calibratable? | Verdict |
|---|---|---|---|---|---|---|
| **50V_1** (J3.7/J3.2 → U2A → PA4, ADC2_IN17) | V_ADC = 0.055 × (POS−NEG) [11k/200k] | 0 … **60.0 V** differential. Below 0 V it clamps to 0. | 14.6 mV | ±1.3 V (VDDA ±2 % dominates) → **±0.15 V** after VREFINT correction and 2-point cal | Yes (gain/offset). Clamp leakage drift is not. | **OK** |
| **50V_2** (J3.6/J3.1 → U2B → PA5, ADC2_IN13) | same | 0 … 60.0 V | 14.6 mV | same | same | **OK** |
| **5V_1** (J3.10/J3.5 → U3A → PA6, ADC2_IN3) | V_ADC = 0.5 × (POS−NEG) [10k/20k] | 0 … **6.6 V** | 1.61 mV | ±0.14 V → **±25 mV** | Yes | **OK** (5.5 V → 2.75 V) |
| **5V_2** (J3.9/J3.4 → U3B → PA7, ADC2_IN4) | same | 0 … 6.6 V | 1.61 mV | same | Yes | **OK** |
| **ISENSE_1** (J8.3 SIG / J8.8 REF → U1A → PA0, ADC12_IN1) | V_ADC = 1.65 V + 1.6 × (SIG−REF) [16k/10k, VREF = 3V3_MCU/2] | SIG−REF = **−1.031 … +1.031 V** | 0.50 mV of sensor output per LSB | Offset ±9 mV sensor-referred, gain ±1.1 % (+ ±2 % VDDA) → **±2–3 mV** after zero and gain cal. **Plus ΔV5 % of reading if the sensor is ratiometric.** | Offset/gain yes. 5 V-supply dependence no (5 V not measured). | **OK for REF ± 0.625 V sensors. Clips for ±2 V sensors** |
| **ISENSE_2** (J8.4/J8.9 → U1B → PA1, ADC12_IN2) | same | same | same | same | same | same |
| **ISENSE_3** (J8.1/J8.6 → U5A → PA2, ADC1_IN3) | same | same | same | same | same | same |
| **ISENSE_4** (J8.2/J8.7 → U5B → PA3, ADC1_IN4) | same | same | same | same | same | same |
| **T1** (J9.9 → U7A → PB0, ADC1_IN15 / ADC3_IN12) | V_ADC = V5 × [7.4537·Rt/(1500+Rt) − 3.0370] | R_t = 1031 … 1476 Ω → **PT1000 +8.1 … +124.1 °C** (practically +8.9 … +122 °C with output-swing margin) | 0.024 °C (10 °C) … 0.034 °C (120 °C) | ±1 °C (R tol) ±2 °C (VDDA) **±6.6 °C at 120 °C for 5 V ±5 %**, + self-heating +0.4…2 °C [S] | Tolerances/VDDA yes. **5 V dependence and self-heating no.** | **Limited: no reading below +8 °C** |
| **T2** (J9.8 → U7B → PB1, ADC1_IN12 / ADC3_IN1) | same | same | same | same | same | same |
| **T3** (J9.7 → U8A → PB2, ADC2_IN12) | same | same | same | same | same | same |
| **T4** (J9.6 → U8B → PC4, ADC2_IN5) | same | same | same | same | same | same |

### 2.1 Worked calculations

**VSENSE 50 V** (VSENSE.kicad_sch). This is a classic difference amplifier.
- POS → R17 100k + R9 100k → U2A+, with R19 11k to GND.
- NEG → R2 200k → U2A−, with feedback R1 11k.
- Vout = (11k/200k)·(POS−NEG) = 0.055·Vdiff. 3.3 V / 0.055 = **60.0 V** [C]. That covers 50 V nominal plus about 20 % for tolerance and transients. Above 60 V the output saturates; the 4.7 k resistor and the BAT54S clamp protect the pin.
- Op-amp node at 60 V: V+ = 60·11/211 = **3.13 V**, inside the TLV2186 CM range of (V−)−0.2 to (V+)+0.2 V [C, TLV2186 §6.5].
- Ground offset: the circuit works while V+ ≥ −0.2 V, i.e. **POS ≥ −3.8 V** relative to board GND. Upper limit: POS ≤ about 100 V.
- Resistor-mismatch CMRR (0.1 %): 0.5 V NEG offset gives under 1 mV output error. Monte-Carlo worst case: ±0.10 V at 50 V with NEG = 0 or +3 V [C, calc]. Offset 250 µV max × (1+G) is negligible.

**VSENSE 5 V**. Built the same way.
- POS → R73 + R13 (2×10k) → U3A+, with R75 10k to GND.
- NEG → R8 20k → U3A−, with feedback R7 10k.
- Gain = 0.5 → FS **6.6 V**. 5.5 V gives 2.75 V [C].
- Ground offset: works while **POS ≥ −0.6 V**, and V+ = POS/3 stays below 5.2 V up to POS = 15.6 V.
- Worst-case resistor error ±10 mV [C, calc].

**ISENSE** (ISENSE.kicad_sch, all four identical).
- SIG → ferrite → R34 10k 1 % → U1A+, with R36 16k 0.1 % to VREF_1V65.
- REF → ferrite → R35 10k 1 % → U1A−, with feedback R33 16k 0.1 %.
- VREF_1V65 = 3V3_MCU·R12/(R10+R12), 10k/10k 0.1 %, buffered by U9A.
- Vout = 1.65 + 1.6·(SIG−REF). Range ±1.65/1.6 = **±1.031 V** [C].
  - REF ± 0.625 V → 0.65 … 2.65 V (61 % of the ADC span), which fits.
  - 2.5 V ± 2 V clips at about ±1.03 V (52 % of the sensor's range).
- U1A+ ≈ 2.17 V (SIG = REF = 2.5 V), which is in range.
- Because VREF comes from the same 3.3 V as the ADC, **the zero point is ratiometric to the ADC** (good).
- Error from the mixed 1 %/0.1 % network: ±11.6 mV at the output = ±7.2 mV sensor-referred at REF = 2.5 V; up to ±9.4 mV if REF = 1.65 V [C, Monte-Carlo]. This error is fixed, so it calibrates out at zero current.
- A sensor REF output with 200 Ω output impedance adds about 10 mV of output offset (in series with R35, which upsets the bridge balance). Also fixed, also calibratable [C, calc].

**TSENSE** (TSENSE.kicad_sch, all four identical).
- +5V → R86 1.5k 0.1 % → node (C25 100 nF) → PT1000 to GND (J9 GND pins 1–4); node → R85 100 Ω → U7A+.
- U7A− connects to R83 2.4k to GND, R84 2.7k to +5V, and R78 8.2k feedback.
- KCL gives Vout = Vn·(1 + 8.2/2.4 + 8.2/2.7) − 5·8.2/2.7 = **7.4537·Vn − 15.185 V** [C].
- Vout = 0 at Vn = 2.0373 V → R_t = 1031.4 Ω → **+8.06 °C**.
- Vout = 3.3 V at Vn = 2.4800 V → R_t = 1476.2 Ω → **+124.1 °C** (IEC 60751 PT1000) [C].
- Sample points:

  | T (°C) | −40 | −20 | 0 | 25 | 60 | 100 |
  |---|---|---|---|---|---|---|
  | Vout (V) | −1.78 (clipped) | −1.00 (clipped) | −0.28 (clipped) | 0.56 | 1.62 | 2.71 |

- Sensor current = 5 V/(1.5k+1k) = **2.0 mA → 4.0 mW in the PT1000** [C]. IEC 60751 practice is ≤1 mA (typically 0.1–0.3 mA) for PT1000. Typical self-heating coefficients are 0.1…0.5 K/mW in a moving medium and more in still air, so expect **+0.4 … 2 °C** [S].
- The bias (R86) and the offset (R84) both come from +5V, so **Vout ∝ V5 exactly**. The ADC reads Vout/VDDA. ΔT per 1 % ΔV5: 0.02 °C at 10 °C, 0.57 °C at 60 °C, **1.33 °C at 120 °C** [C, calc].

### 2.2 Op-amp limits at every node (TLV2186 on +5V; CM range −0.2 … 5.2 V; output swing 60–100 mV from the rails at 10 kΩ)

| Node | Normal range | OK? |
|---|---|---|
| U2A/B + and − (50 V) | 0 … 3.13 V at 60 V | yes |
| U3A/B + and − (5 V) | 0 … 2.2 V at 6.6 V | yes |
| U1/U5 + and − (I) | about 1.9 … 2.5 V | yes |
| U9A/B (VREF buffer) | 1.65 V | yes |
| U7/U8 + and − (T) | 2.04 … 2.48 V. Open sensor: 5.0 V, still in range. | yes |
| Outputs | used range 0 … 3.3 V; can reach about 4.9 V when overdriven | the clamp takes it (see below) |

- The **low swing** (≈ 20–60 mV) is only relevant at 0 input: about 0.4 V on 50 V channels, 40 mV on 5 V channels, 1 °C on T. None of these are operating points [C].
- **Supply:** TLV2186 needs **V_S ≥ 4.5 V** [C, §6.3]. The op-amps sit directly on J1, so **J1 must stay ≥ 4.5 V**.

### 2.3 Protection and MCU pin (ConnectionToSTM_PCU.kicad_sch)

Each ADC net has: op-amp → 4.7 kΩ → pin, with 100 nF to GND and a BAT54S (A→GND, K→+3V3_MCU, COM→pin). The pinout matches the Nexperia SOT-23 BAT54S.

- Overdrive with the output at 4.9 V: I = (4.9 − 3.3 − 0.25)/4.7k ≈ **0.29 mA** into the Schottky. The pin stays at ≈ 3.3 + 0.25 V = 3.55 V.
  - All 12 ADC pins are **TT_a**: VIN max VDD+0.3 V operating, 4.0 V abs max; positive injection on TT_a is "0 mA / not possible" [C, DS12288 Tables 14/15/53].
  - 3.55 V < 3.6 V, so it is OK but with little margin. The Schottky must carry the current, and it does [C/S].
- The worst-case total current into 3V3_MCU (all 12 overdriven) is about 3.5 mA, far below the MCU's own consumption, so the rail does not rise [C].
- **Clamp leakage:** the BAT54 reverse current rises steeply with temperature (≈ 2 µA max at 25 V/25 °C, roughly 10× more at 85 °C). Estimate ≤ 2 µA at 3 V and 85 °C → **≤ ~10 mV error** through 4.7 kΩ. The error depends on the node voltage and the temperature, so it does not calibrate out [S]. That is ≈ 0.18 V on 50 V, 20 mV on 5 V, 6 mV sensor-referred on I, and 0.4 °C on T. At 25 °C it is under 1 mV.

### 2.4 Dynamics

- Output RC = 4.7 kΩ × 100 nF = **0.47 ms** (f_c = 339 Hz) on every channel [C]. T channels add 600 Ω × 100 nF = 60 µs at the sensor node.
- The G474 sample capacitor is 5.2 pF typ (8.8 pF max). Charge sharing with 100 nF is 5×10⁻⁵, i.e. 0.2 LSB per conversion [C].
- Recovery through 4.7 k: the error stays below about 0.5 LSB up to **≈ 3–5 kS/s per channel**. For 10–1000 Hz telemetry sampling this is irrelevant.
- If you want to stay inside DS12288 Table 67 (R_AIN 4.7 kΩ) even without the capacitor: ≥ 92.5 cycles on fast channels (PA0–PA3, PA6, PA7, PC4, PB1 on ADC3) and ≥ 247.5 cycles on slow channels (PA4 IN17, PA5 IN13, PB0 IN15, PB2 IN12) [C].

### 2.5 Fault behaviour (all channels)

| Case | 50 V / 5 V | ISENSE | TSENSE |
|---|---|---|---|
| Open input / sensor unplugged | POS open → R19/R75 pull V+ to GND → **reads 0 V**, indistinguishable from "no voltage". NEG open → gain changes by about 5 % (50 V) or 33 % (5 V), not detectable. | SIG and REF open → output = **1.65 V = "0 A"**, not detectable | Open → node 5 V → output saturates → **4095 (">124 °C")**, detectable |
| Shorted sensor | n/a | SIG=REF → 0 A | Node 0 V → **0 counts = same as "<8 °C"** |
| NEG ground offset of a few V | 50 V: OK for POS ≥ −3.8 V. 5 V: OK for POS ≥ −0.6 V, ≤ 15.6 V | Differential; CM error with 1 % resistors ≈ 1.4 % of (Vcm−1.65 V) | n/a (single-ended to board GND) |
| Overvoltage | 5 V channel at 50 V: (50−5.5)/20k ≈ 2.2 mA into the op-amp ESD diode (TLV2186 abs max ±0.5 V beyond the rails, current-limited). It survives, the output clamps. 50 V channel to ~100 V: still in CM range. | SIG at 5 V → output saturates → clamp | n/a |
| Reverse voltage | 5 V channel at −5 V: V+ = −1.67 V, ≈ 0.18 mA through the source resistor. The output goes to 0 V, so no negative injection at the MCU. 50 V channel at −50 V: ≈ 0.24 mA. Survives. | output to 0 | — |
| Board powered, no module | 3V3_MCU floats. VREF_1V65 follows whatever the clamps charge it to (≤ ~4.7 V). **No harm, nothing to damage.** Don't hot-plug the module while powered. | | |
| Module on USB, board unpowered | D17 blocks module 5 V → board +5V [C]. Op-amp outputs sit at 0. R10/R12 feed ≈ 0.2 mA into unpowered U9's input ESD path (harmless). External 50 V/5 V present: ≈ 0.2 mA into the +5V rail through the op-amp input diodes (harmless). | | |

---

## 3. Communication & I/O

| Interface | Works? | Conditions / notes |
|---|---|---|
| **RS-232** (MAX3221 U4; PC10 = USART3_TX/UART4_TX → DIN; ROUT → PC11 = USART3_RX/UART4_RX) | **Yes** [C] | Pinout matches TI SLLS348P (EN 1, C1+ 2, V+ 3, C1− 4, C2+ 5, C2− 6, V− 7, RIN 8, ROUT 9, INVALID 10, DIN 11, FORCEON 12, DOUT 13, GND 14, VCC 15, FORCEOFF 16). 4 × 0.1 µF at 3.3 V matches the datasheet test conditions. 19200 baud ≪ 250 kbps. **Before firmware init:** EN pulled low (R115) → receiver enabled. FORCEON/FORCEOFF pulled high (R114/R113) → always on. DIN pulled high (R112) → DOUT idles at mark. So it is already in a valid idle state. INVALID → PB4 gives cable/link detection. |
| **CAN / DroneCAN** (TCAN332G U6, TXD ← PB13 = FDCAN2_TX, RXD → PB12 = FDCAN2_RX) | **Yes** [C] | Pinout per SLLSEQ7F Table 4-1. VCC = board 3.3 V. "G" variant is spec'd to 5 Mbps, so 1 Mbps is fine (loop delay < 135 ns). TXD has an internal pull-up → recessive during reset. Logic and bus pins are high-impedance when unpowered. ESD: PESD1CAN + internal 12 kV IEC. **Termination is fixed:** 2 × 60.4 Ω split + C21 100 nF. Correct only if the PCU is a **bus end** (see Q3). Firmware note: it's FDCAN2, not FDCAN1. |
| **I2C** (PA15 = I2C1_SCL, PB7 = I2C1_SDA, AF4) | **Yes** [C] | Fitted: R107/R108 4.7 k to board +3.3 V. R105/R106 (to 5 V) are DNP, **which is the correct option for a Pixhawk (3.3 V I2C)**. With the Pixhawk's own pull-ups (typ. 1.5–2.2 k) the combined load is < 3 mA. If unused: lines idle high, harmless. PA15 has the JTDI pull-up at reset; no conflict. |
| **Debug UART** (PA9/PA10 = USART1 → TP44/TP45, TP46 GND) | **Yes** | See L7 (UCPD dead-battery side effect). |
| **Programming** | **Yes** | SWD via the module's own 4-pin P5 header (3V3/DIO/CLK/GND); USB-C DFU via the module's BOOT0 button (PA11/PA12/PB8 are not used by the carrier). See O-list for the mechanical point. |
| **DO1–4** (PB14, PB15, PA8, PB9 → 1 k → SN74LVC2G07 at 3.3 V → open drain + 10 k to +5V + 100 nF → J10) | **Yes, logic-level only** | MCU high → output off → **5 V via 10 kΩ** (no load). MCU low → **≈ 0.0–0.05 V**, sinks up to 24 mA. Non-inverting. Reset/no module: R57/R58/R63/R64 100 k pull the inputs low → **DO = LOW**. Power-up glitch with VCC = 0 (Ioff, output off) is limited by τ = 10k·100nF = 1 ms to < ~1 V [S]. See L5. |
| **DI1–2** (J10.2/J10.7 → ferrite → 220 Ω → node with 10 k to +5V and 100 nF → LVC2G07 input → open drain + 1 k to +3.3 V → PB10/PB11) | **Yes** [C] | High ≥ **2.0 V**, low ≤ **0.8 V** (LVC at V_CC 3–3.6 V). Open input = **high** (defined). An external driver must sink ≈ 0.5 mA. **5 V never reaches the MCU:** the MCU-side pull-up goes to 3.3 V, and the LVC input is 5.5 V tolerant (6.5 V abs). Input must stay ≤ 5.5 V (no clamp beyond the 220 Ω). Filter: rise ≈ 1 ms, fall ≈ 22 µs (MCU side 100 µs). |

---

## 4. Findings

> No **[Blocker]** survived verification. Every pin function, IC pinout, polarity and supply was checked against the netlist and the datasheets.

### [Limitation] L1: PT1000 channels cover only +8 °C … +124 °C; below +8 °C they read 0 (same as a shorted sensor). **Fix recommended.**
- **Category:** Measurement range
- **Sheet:** TSENSE (`TSENSE.kicad_sch`), all four channels
- **Problem:** Vout = 7.4537·Vn − 15.185 V (see §2.1). Vout = 0 at R_t = 1031 Ω (+8.1 °C); Vout = 3.3 V at 1476 Ω (+124.1 °C) [C]. At 0 °C the output would need to be −0.28 V; at −20 °C, −1.0 V.
- **Effect:** On a UAV the ambient, electronics and cold-start stack temperatures are routinely below 8 °C (winter, altitude, morning). All four channels then read 0 counts, so firmware can neither show the value nor tell "cold" from "shorted sensor". Over-temperature monitoring of a PEM stack (≈ 60–80 °C) is unaffected.
- **Suggested fix (values only, same footprints):** per channel, change the feedback resistor and the 5 V offset resistor:
  - R78/R87/R93/R99: 8.2 k → **4.75 k 0.1 %**
  - R84/R90/R96/R102: 2.7 k → **2.87 k 0.1 %**

  Keep R83 etc. (2.4 k) and R86 etc. (1.5 k). New transfer: Vout = 4.957·Vn − 8.275 V. Range (with 30 mV/50 mV swing margin) **−41 °C … +126 °C**, resolution ≈ 0.05 °C/LSB [C, calc]. Op-amp nodes 1.80 … 2.48 V, in range. Short then reads 0 and open reads 4095, both outside any plausible temperature, so both are detectable.

### [Limitation] L2: Temperature reading is proportional to the (unmeasured) board 5 V; not calibratable.
- **Category:** Accuracy / supply dependence
- **Sheet:** TSENSE (`TSENSE.kicad_sch`); Power-supply (`power_supply_PCB.kicad_sch`)
- **Problem:** The PT1000 bias (R86) and the offset divider (R84) both come from +5V = J1 directly. Vout = V5·f(R_t), but the ADC references the module's 3.3 V. Error per 1 % of V5: 0.57 °C at 60 °C, 1.33 °C at 120 °C. At 5 V ±5 % that is **±2.9 °C at 60 °C, ±6.6 °C at 120 °C** [C, calc]. The 5 V also moves with load (Hall sensors, CAN dominant current) and cable drop. With the L1 fix the factor stays about the same (Vout ∝ V5).
- **Effect:** The temperature error tracks the supply. It can't be removed by calibration unless the actual V5 is known.
- **Suggested fix (no board change):** measure the board 5 V. Either wire one 5V_x channel at J3 to J1's 5 V/GND (costs one voltage channel), or use a stable, regulated J1 source (≤ ±1 %). Firmware then scales T by 5.000/V5_measured. *(Hardware alternative, only if a channel can't be spared: a 2:1 divider from +5V to PA9 = ADC5_IN2, which would give up the debug-TX test point.)*

### [Limitation] L3: Hall-sensor input range is only ±1.03 V (SIG−REF); 100 nF loads the sensor outputs.
- **Category:** Measurement range / sensor compatibility
- **Sheet:** ISENSE (`ISENSE.kicad_sch`)
- **Problem:** Gain 1.6 around 1.65 V → ±1.031 V differential [C]. C11/C13/C15/C17 (100 nF) sit **directly between SIG and REF on the sensor side** of the 10 k resistors, so the sensor drives 100 nF with nothing in series except the ferrite. Many open-loop Hall ICs/modules specify a maximum capacitive load in the 1–10 nF range [S, sensor unknown]. Ratiometric sensors (SIG−REF ∝ V_CC) also inherit L2: reading error = ΔV5 %.
- **Effect:** REF ± 0.625 V sensors fit with about 65 % headroom. REF ± 0.8 V fits. 2.5 V ± 2 V sensors clip at about 52 % of their range. A sensor with C_load,max < 100 nF may ring or oscillate, giving a noisy or offset reading.
- **Suggested fix:** answer Q1 first. The range is ±1.65 V/G with G = R33/R35 (= R36/R34). For ±2 V sensors, change **both** 16 k resistors of each channel (R23/R26, R28/R31, R33/R36, R38/R41) to **8.2 k 0.1 %**: G = 0.82, range ±2.01 V, resolution 0.98 mV/LSB. If the sensor's C_load,max < 100 nF: change C11/C13/C15/C17 to **≤ the sensor's limit (e.g. 1 nF)**. The ADC-side 4.7 k/100 nF filter already sets the bandwidth.

### [Limitation] L4: Open or unplugged sensors are not detectable on ISENSE and VSENSE.
- **Category:** Fault detection
- **Sheet:** ISENSE / VSENSE
- **Problem:** Open Hall sensor → output 1.65 V = exactly "0 A". Open POS → 0 V [C].
- **Effect:** A broken current-sensor cable reports zero current, and a broken voltage wire reports 0 V. Acceptable if the system logic doesn't rely on these values for protection. Otherwise firmware needs plausibility checks. REF itself is not measured, so a missing sensor can't be seen directly.
- **Suggested fix:** none in hardware (minimal-change scope). Document it and use plausibility checks: current present while the 50 V voltage changes, and so on.

### [Limitation] L5: DO high level is a 10 kΩ pull-up with τ = 1 ms; no short-circuit protection.
- **Category:** Digital I/O
- **Sheet:** Digital EinAusgänge (`D_IO.kicad_sch`)
- **Problem:**
  - High = 5 V via R59/R60/R65/R66 (10 k). A load R_L gives V_OH = 5·R_L/(R_L+10k): a CMOS input (µA) gets ≈ 5 V; 10 kΩ to GND gets 2.5 V (fails V_IH = 3.5 V for 5 V CMOS); an LED or opto-input won't work.
  - Edges: 10 k × 100 nF (C29–C33) → rise 10–90 % ≈ 2.2 ms. PWM is not possible.
  - Low: the LVC2G07 sinks the 100 nF directly with no series resistor, so the discharge peak is limited only by the output transistor [S, momentary, outside the "continuous ±50 mA" rating]. An external short of DO to +5 V or higher (wrong wiring) destroys U10/U11 [C, abs max ±50 mA].
- **Effect:** Fine for static enable/flag signals into logic inputs; not for anything that draws current or needs fast edges.
- **Suggested fix:** if Q4 shows a resistive/opto load, lower R59/R60/R65/R66 to **2.2 k** (2.3 mA at low, still ≪ 24 mA) and/or reduce C29–C33 to **1 nF**. Otherwise accept as is.

### [Limitation] L6: J1 operating window is effectively 4.5 … 5.5 V; the TVS doesn't protect the 3.3 V LDO; there's no reverse-polarity protection.
- **Category:** Power
- **Sheet:** Power-supply (`power_supply_PCB.kicad_sch`), Connection To STM
- **Problem:**
  - Minimum: TLV2186 needs ≥ 4.5 V [C]; typical Hall sensors need 5 V ± 5–10 %. The module gets J1 − V_F(D17 B5819W, ≈ 0.3–0.4 V) ≈ 4.6 V, which is fine for ME6231A33.
  - Maximum: module VDD5V "3.3–5.5 V" (WeAct note) + D17 → J1 ≤ ~5.8 V; AP2112 operating ≤ 6 V, abs max 6.5 V [C].
  - D3 SMAJ5.0A: V_BR(min) 6.4 V, clamping up to ≈ 9.2 V at rated pulse current. **A surge is clamped above the AP2112 6.5 V abs max** [C/S].
  - Reverse polarity on J1 forward-biases D3 directly across the source (no fuse). D3 or the supply fails, and the board sees about −1 V.
- **Effect:** Works from a regulated 5 V BEC/DC-DC (the normal UAV case). Not robust to a mis-plugged or reversed supply or large transients.
- **Suggested fix:** use a regulated 5 V ±5 % source (Q5). Optional: a polyfuse in series with J1 pin 2/4 so D3 can act as reverse-polarity protection.

### [Limitation] L7: UCPD dead-battery pull-downs on PB4/PB6 are active until firmware disables them.
- **Category:** MCU module fit / init state
- **Sheet:** Connection To STM (`ConnectionToSTM_PCU.kicad_sch`) / RS232
- **Problem:** DS12288 (pin-table note): a high level on PA9 (DBCC1) / PA10 (DBCC2) enables a 5.1 kΩ pull-down on PB6 (CC1) / PB4 (CC2) until `UCPD1_DBDIS = 1` in PWR_CR3 [C]. Here PB6 = MAX3221 FORCEON (100 k pull-up) and PB4 = INVALID (driven output). PA9/PA10 go only to test points, so they float, or sit high if a USB-UART adapter is attached.
- **Effect:** Before firmware init only, FORCEON can be pulled to about 0.16 V → the MAX3221 enters auto-power-down (the receiver stays active, the driver turns off without a valid RIN signal). INVALID gets an extra 5.1 k load. Harmless, but surprising when debugging.
- **Suggested fix:** firmware: call `HAL_PWREx_DisableUCPDDeadBattery()` at start-up. No hardware change.

### [Limitation] L8: Absolute voltage and current accuracy depends on the module's 3.3 V LDO (VDDA = ADC reference).
- **Category:** Accuracy
- **Sheet:** Connection To STM; module
- **Problem:** VREF+ = module 3.3 V (ME6231A33 via FB1/R7) [C, WeAct schematic]. Typical LDO tolerance is ±2 % [S]. That is ±1 V on the 50 V channels and ±0.1 V on the 5 V channels if uncorrected. ADC TUE is ≤ 6.9 LSB [C, DS12288 Table 68].
- **Effect:** Gain error, fixed per board, plus a small drift.
- **Suggested fix:** firmware: measure VREFINT (ADC1_IN18, factory-calibrated VREFINT_CAL) and scale. ISENSE offset (VREF_1V65 from the same 3.3 V) is already ratiometric. No hardware change.

### [Limitation] L9: PT1000 self-heating at 2 mA / 4 mW.
- **Category:** Accuracy
- **Sheet:** TSENSE
- **Problem:** I = 5 V/(1.5 k + 1 k) = 2.0 mA → P = 4.0 mW [C]. IEC 60751 recommends ≤ 1 mA for PT1000; typical 0.1–0.5 K/mW in flowing media, more in still air [S].
- **Effect:** +0.4 … 2 °C reading offset that depends on mounting and airflow. Only partly calibratable.
- **Suggested fix:** accept, or calibrate in the mounted position. (Raising R86 to cut the current would need the gain network recomputed, so it falls outside minimal-change scope.)

### [Question] Q1: Which Hall current sensors?
- **Category:** Sensor compatibility
- **Sheet:** ISENSE / connectors (J8)
- **Need:** model/datasheet: output swing (SIG−REF at ±I_max), REF output impedance, max capacitive load, ratiometric or not, supply current.
- **How the answer changes the verdict:**
  - REF ± ≤ 1.0 V, C_load ≥ 100 nF, internal reference → **OK as is**.
  - Larger swing → change the 16 k resistors (L3).
  - C_load < 100 nF → change C11/C13/C15/C17.
  - Ratiometric → L2 applies to current too (measure 5 V).
  - No REF pin (e.g. ACS7xx) → leaving REF open turns the stage into a follower with gain 0.615 and an unknown offset. Then REF must be tied to a 2.5 V reference in the harness.
  - Supply current × 4 > ~300 mA → check J1 and its source.

### [Question] Q2: Required temperature range and sensor type?
- **Category:** Measurement range
- **Sheet:** TSENSE
- **Need:** is it PT1000 (not PT100 or NTC)? Which locations (stack, ambient, electronics, H2 tank) and which min/max?
- **How the answer changes the verdict:**
  - All channels only above +10 °C and ≤ 120 °C → L1 is acceptable as is.
  - Any channel must read below +8 °C → apply the L1 fix.
  - PT100 → the circuit is unusable (100 Ω is far below the 1031 Ω lower limit) → **Blocker**.

### [Question] Q3: CAN topology. Is the PCU at a bus end?
- **Category:** CAN
- **Sheet:** RS232 (`RS232.kicad_sch`), R79/R80/C21
- **Need:** the node list and order on the DroneCAN bus, and whether the Pixhawk port is terminated.
- **How the answer changes the verdict:**
  - Point-to-point Pixhawk ↔ PCU, with termination on the Pixhawk side (or a terminator plug) → **OK**.
  - PCU in the middle of the bus → three terminators → about 40 Ω bus load. Usually still works over short drone harnesses, but out of ISO 11898-2 spec (lower VOD, more transceiver current). Fix: make R79/R80 **DNP** (or a 0 Ω/jumper option) on that unit.

### [Question] Q4: What do DO1–4 and DI1–2 connect to?
- **Category:** Digital I/O
- **Need:** load type (logic input, opto, relay driver, MOSFET gate) and the source type for DI (push-pull 5 V, open collector, dry contact, 12 V?).
- **How the answer changes the verdict:**
  - Logic inputs / open-collector or 5 V sources → **OK**.
  - Resistive/opto loads → L5 fix.
  - DI sources above 5.5 V → add a divider/clamp (otherwise U12 is damaged above 6.5 V).

### [Question] Q5: What supplies J1 (tolerance, transients, polarity)?
- **Category:** Power
- **Need:** the source (BEC/DC-DC from the 50 V bus?), its accuracy, and surge behaviour.
- **How the answer changes the verdict:**
  - A regulated 5 V ±2 % → L2 becomes ±1.3 °C (with the L1 fix, at the top of the range) and L6 is a non-issue.
  - An unregulated or noisy 5 V → measuring 5 V (L2 fix) is mandatory for useful T/I readings.

### [Question] Q6: What is the 50 V NEG / 5 V NEG relative to board GND?
- **Category:** Voltage measurement
- **Need:** whether the NEG inputs are local returns that can sit below board GND.
- **How the answer changes the verdict:** ground offsets keep the channel valid only while 50 V POS ≥ −3.8 V and 5 V POS ≥ −0.6 V (relative to board GND). Larger negative offsets → wrong readings.

---

## 5. [Optional]

- Fit a polyfuse (~0.5 A) in the J8 +5V sensor supply so a sensor-cable short doesn't pull the whole board down.
- Add a series resistor of 47–100 Ω between U10/U11 outputs and J10 (DO1–4) to limit cap-discharge and short currents.
- Swap BAT54S for a lower-leakage clamp (e.g. BAS70-04, or a dual low-leakage diode) if hot-temperature accuracy matters (§2.3 leakage).
- Change the 1 % ISENSE input resistors (R24/R25/R29/R30/R34/R35/R39/R40) to 0.1 % for a ±1 mV-class offset without calibration.
- Make CAN termination R79/R80 a solder-jumper option (only if Q3 says "middle of bus").
- **Layout (PCB is empty):** J4/J5 row spacing must be **15.24 mm** (WeAct outline). Pin 1 of both sockets goes at the USB-C end. The module's SWD header (4 holes, between the rows, ≈ 9 mm from the far end) must have its pins pointing **up**, or the carrier needs a clearance cut-out there.
- DroneCAN firmware note: the transceiver is on **FDCAN2** (PB12/PB13), which shares message RAM and kernel clock with FDCAN1.

---

## 6. Information needed from the user

| # | Question | What the answer changes |
|---|---|---|
| 1 | Hall sensor model(s): output swing, REF, max C_load, ratiometric? | Whether the ISENSE gain (16 k) and C11/13/15/17 must change; whether 5 V must be measured (L3, L2) |
| 2 | Temperature sensor type and required range per channel | Whether the L1 fix is needed (any channel < +8 °C), or whether the board is a blocker (PT100/NTC) |
| 3 | DroneCAN bus topology (PCU at an end? Pixhawk terminated?) | Fit or omit R79/R80 |
| 4 | DO loads and DI sources | Whether R59/60/65/66 and C29–33 need changing (L5), or a DI clamp is needed |
| 5 | J1 source: regulation, tolerance, surge, polarity safety | How large the T/I error is (L2), whether a fuse/reverse protection is needed (L6) |
| 6 | 50 V / 5 V NEG references relative to board GND | Whether the voltage channels' CM range is enough (§2.5) |
| 7 | 50 V system max voltage incl. charge/regen transients | If > 60 V must be *measured* (not just survived), the 50 V gain must drop (R1, R3, R19, R20 11 k → 10 k 0.1 % gives G = 0.05, 66 V FS) |
| 8 | Does the system need to detect a disconnected current or voltage sensor? | Whether L4 needs a hardware change (it can't be fixed in firmware) |
