# Full design review: PCU carrier board (WeAct STM32G474 "Long")

Date: 2026-11-12 · Reviewed design: `Routing/PCB PCU routed v2.*` (schematic, board, rules) · Read-only, no project file was changed.

How to read the tags: **[M]** = measured by script on the netlist or board, **[C]** = calculated from netlist values, **[DS]** = read from a datasheet or the WeAct schematic, **[N]** = not verified, see the note.

---

## 1. Executive verdict

**Fab after fixes.** The electrical design is sound: the netlist and board match (0 differences on 148 nets, 266 parts), every MCU pin is on a correct G474 function, and the module pinout matches the WeAct schematic and outline drawing.

One issue should be fixed before ordering, and it comes from today's connector change: J2, J3, J9 and J10 are now four identical 2×4 headers, and the J3 cable carries 50 V. Plugged into any of the other three, it destroys parts on this board and can put 50 V on the Pixhawk CAN bus. The board also has no silkscreen text at all besides reference designators, so nothing tells the user which header is which.

Top 3 risks:

1. **J3 (50 V) cable fits J2, J9 and J10** (finding 1).
2. **No connector labels, no "50 V" mark, no board name or revision on the silkscreen** (finding 2).
3. **System unknowns that decide whether the board does its job:** the fuel cell controller's serial level (true RS-232 or 3.3 V UART), the Hall sensor type, and whether the PCU is a CAN bus end (questions Q1–Q3).

Everything else is minor or already accepted in `README.md`. The BOM still lists the old 2×5 connectors for J2/J3/J9/J10.

---

## 2. Findings

Each fix is marked **required** (function or safety) or **optional**.

| # | Severity | Sheet / area | Problem | Suggested fix |
|---|---|---|---|---|
| 1 | **Critical** | Connectors (J2, J3, J9, J10) | All four are `43045-0800` with the same keying [M]. The J3 cable has 50 V on pins 5 and 6. In **J2**: pin 5 = CAN_L and pin 6 = RS232_RIN get 50 V. TCAN332 bus pins are protected to ±14 V only [DS], PESD1CAN starts to conduct at about 25 V and can't carry a low-impedance source, and the 50 V reaches the Pixhawk CAN bus. In **J9**: 50 V on T_4/T_3 → 100 Ω → op-amp input (about 0.45 A into the ESD diode) and (50 − 5)/1.5 kΩ = 30 mA, 1.35 W in R98/R104 (0603, 0.1 W) [C]. In **J10**: 50 V on DO1 (LVC2G07 output, abs. max 6.5 V, and the output is LOW at power-up, so it shorts the 50 V source) and on DI2. The reverse cases (J2/J9/J10 cables into J3) are harmless because J3 is 20 kΩ/200 kΩ. | **Required.** Give J3 a circuit count no other header has, e.g. 2×6 `43045-1200` (the 4 spare positions can separate the 50 V and 5 V groups). J1 (4), J8 (10) and the other three (8) then can't take the J3 plug. If the footprint can't change: accept in writing, and at least do finding 2 and mark the J3 harness. |
| 2 | **Major** | Layout / silkscreen | The board has 0 text items besides the 266 reference designators [M]. No connector function, no pin 1 or signal names, no "50 V" warning, no board name, revision or date, no module orientation mark, no I²C pull-up note. `PCB_LAYOUT_REMINDERS.md` §4 asks for all of these. With finding 1 this is the only mis-mating safeguard. | **Required.** Add the labels from the reminders §4. The area around H1 and below J1 is free. |
| 3 | **Major** | BOM | `BOM_PCU_G474.csv` lists J2, J3, J9, J10 as `430451000` with the 2×5 footprint (5 pcs). The schematic has `430450800` with the 2×4 footprint [M]. Ordering from this BOM gives parts that don't fit. The "LCSC Part #" column is empty for every line. | **Required.** J8 = 43045-1000 × 1; J2/J3/J9/J10 = 43045-0800 × 4 (or the new J3 part). Fill in the LCSC numbers before PCBA. |
| 4 | Minor | Connectors / mis-mating | Swaps among J2, J9, J10 are not destructive but disturb the vehicle: the J2 cable in J9 ties CAN_H, RS232_DOUT and I2C_SDA to GND; in J10 it ties CAN_H/CAN_L to DO2/DO1, which are LOW at power-up. The PX4 CAN bus and the I²C bus are then stuck while the plug is wrong. | Optional. Covered by finding 2 and a pre-flight check. |
| 5 | Minor | Connection To STM / assembly | R105/R106 are DNP in the schematic, but the board footprints carry no DNP or "exclude from position files" attribute (attribute value 2 = SMD only) [M]. J4/J5 are excluded from the BOM but not from the position files. | Optional. Remove R105, R106, J4, J5 from the CPL by hand, or set the attributes. |
| 6 | Minor | Power-supply / layout | The nearest +5V capacitor to U14 VIN is C54 at 6.8 mm; C40, the intended input cap, is 13.6 mm away [M]. The AP2112 datasheet asks for the input cap close to the pin. The +5V plane keeps the inductance low, so this is unlikely to cause trouble. | Optional. Move C40 next to U14 pin 1 if the area is touched anyway. |
| 7 | Minor | D_IO | DO1–4 are LOW from power-up until the firmware drives the MCU pins high (100 kΩ pull-downs R57/R58/R63/R64 at the buffer inputs, non-inverting open-drain) [M]. Each output has 100 nF directly on the open-drain pin, so every falling edge discharges it through the output FET with no series resistance. The DO pins have no ESD part and no clamp for inductive loads. Sink limit 24 mA at 3.3 V, 5.5 V max [DS]. | Optional, depends on Q4. Logic-level loads only. For a relay or valve, add an external driver stage. |
| 8 | Minor | D_IO | DI: the LVC2G07 input sees a 1 ms rise (10 kΩ × 100 nF) and has no hysteresis; TI specifies a maximum input transition time of 10 ns/V for LVC at 3.3 V [DS]. Accepted in the README with firmware debounce. | Optional. `SN74LVC2G17` (Schmitt) has the same SOT-23-6 pinout. |
| 9 | Minor | Connection To STM | I2C_SCL/I2C_SDA go from J2 straight to PA15/PB7 with no series resistor and no ESD part. They are the only external pins with no protection. The firmware doesn't use I²C. | Optional. Leave pins 4 and 8 out of the J2 harness until I²C is needed. |
| 10 | Minor | ISENSE / connectors | J8 has one +5V pin and one GND pin for four Hall sensors, so the harness needs a 4-way splice on each. The J8 +5V pin is the raw board rail with no fuse; a short in a sensor cable takes the whole board down. | Optional. Polyfuse in the J8 +5V line. |
| 11 | Minor | TSENSE | J9 gives each PT1000 its own GND pin (2-wire). Cable resistance adds directly: 1 Ω ≈ 0.26 K [C]. | Optional. Note it in the harness spec. |
| 12 | Minor | Firmware note | README says "ADC sampling time ≥ 47.5 cycles". DS12288 Table 67 allows 2.2 kΩ at 47.5 cycles; with R_AIN = 4.7 kΩ it asks for 92.5 cycles on fast channels and 247.5 on slow ones (PA4, PA5, PB0, PB2) [DS]. The 100 nF at the pin makes this uncritical at telemetry rates, so it is a documentation point. | Optional. Use 247.5 cycles on all channels. |
| 13 | Minor | Debug | TP44/TP45 (PA9/PA10) are on the bottom side under the module area, and the nearest GND test point TP46 is 21 mm away [M]. A USB-UART adapter that holds PA10 high turns on the 5.1 kΩ pull-down on PB4, and PA9 high the one on PB6 (FORCEON), until the firmware disables it [DS, note 6 of the pin table]. | Optional. Already handled by `HAL_PWREx_DisableUCPDDeadBattery()`. |
| 14 | Minor | Earlier review | `REVIEW_RESULT_4.md` says all 12 ADC pins are TT_a. PA2 is FT_a and PC4 is FT_fa [DS]. No consequence: the clamp is still correct for the other ten. | Documentation only. |
| 15 | Minor | Manufacturability | No fiducials [M]. JLCPCB places without them on a board like this, but three fiducials are the usual practice. | Optional. |

Accepted limitations from `README.md` that I re-checked and agree with: TSENSE range and 5 V dependence, 1 % ISENSE input resistors, J1 window 4.5–5.5 V with no reverse-polarity protection, TVS clamp level above the AP2112 abs. max.

---

## 3. Open questions to the owner

| # | Question | Why it matters | What changes |
|---|---|---|---|
| Q1 | Does the fuel cell controller send **true RS-232 levels** or a **3.3 V/5 V UART**? | The old firmware read USART2 RX on a Nucleo pin directly. On this board the only serial input is RS232_RIN through the MAX3221, which inverts and expects RS-232 levels. | RS-232: nothing. Logic-level UART: the data arrives inverted. Either invert in firmware (`RXPINLEVELINVERT` on USART3) or bypass U4 through R45. |
| Q2 | Which Hall current sensors go on J8 (type, supply current, output swing, allowed capacitive load)? | The input range is ±1.03 V (SIG − REF). The 100 nF across SIG/REF may exceed the sensor's load limit. Four sensors at about 20 mA each are the largest load on +5V. | A different gain (R 16 kΩ) or filter capacitor value. |
| Q3 | Is the PCU at an **end of the CAN bus**? | R79/R80 (2 × 60.4 Ω) are always fitted. A third terminator on the bus lowers the load to 40 Ω. | Not a bus end: R79/R80 = DNP. |
| Q4 | What do DO1–4 and DI1–2 connect to? | DO is LOW at power-up and can sink 24 mA at up to 5.5 V. DI accepts 0–5.5 V. | A relay, valve or 12/24 V signal needs an external stage. |
| Q5 | What is the highest voltage on the "50 V" inputs (open-circuit stack voltage)? | Full scale is 60 V; above that the reading saturates (the clamp protects the MCU). | A different divider if the stack can exceed 60 V. |
| Q6 | What supplies J1, and with what tolerance? | The op-amps need ≥ 4.5 V [DS]. TSENSE is proportional to this voltage: 1 % of 5 V is up to 1.2 K. | A tighter supply spec, or measure the 5 V on a spare ADC channel. |
| Q7 | Is the I²C link to the Pixhawk needed? | See finding 9. | If not: leave it out of the harness. |
| Q8 | **ERC result** in the KiCad GUI after today's connector change? | kicad-cli 7 has no ERC command, so I could not run it. The last recorded clean ERC is from 2026-11-02. | Fix whatever it reports. |
| Q9 | Are the module's SWD header pins soldered pointing up? | The 4-pin header sits between the rows, 9.1 mm from the far end [DS]. Pins pointing down can touch the carrier (socket height 8.5 mm). | Solder them upward or leave them out. |

---

## 4. Interface table

Pin numbering: on the 2×N headers, pin n faces pin n + N/2.

| Conn. | Pin | Net | Function | Level / direction | Goes to |
|---|---|---|---|---|---|
| J1 | 1, 3 | GND | supply return | – | 5 V source |
| J1 | 2, 4 | +5V | board supply | 4.5–5.5 V in | 5 V source |
| J2 | 1 | CAN_H | DroneCAN | CAN, bidirectional | PX4 CAN |
| J2 | 5 | CAN_L | DroneCAN | CAN, bidirectional | PX4 CAN |
| J2 | 2 | RS232_DOUT | serial TX | ±5 V out | fuel cell controller RX |
| J2 | 6 | RS232_RIN | serial RX | ±25 V max in | fuel cell controller TX |
| J2 | 3, 7 | GND | return | – | both cables |
| J2 | 4 | I2C_SDA | I²C1 | 3.3 V, 4.7 kΩ pull-up | Pixhawk (unused today) |
| J2 | 8 | I2C_SCL | I²C1 | 3.3 V, 4.7 kΩ pull-up | Pixhawk (unused today) |
| J3 | 1 / 5 | 50V_2_NEG / POS | voltage 2 | 0–60 V in, 200 kΩ / 211 kΩ | stack or bus |
| J3 | 2 / 6 | 50V_1_NEG / POS | voltage 1 | 0–60 V in | stack or bus |
| J3 | 3 / 7 | 5V_2_NEG / POS | voltage 4 | 0–6.6 V in, 20 kΩ / 30 kΩ | 5 V rail |
| J3 | 4 / 8 | 5V_1_NEG / POS | voltage 3 | 0–6.6 V in | 5 V rail |
| J8 | 3 / 8 | ISENSE_1_SIG / REF | current 1 | analog in, ±1.03 V differential | Hall sensor |
| J8 | 4 / 9 | ISENSE_2_SIG / REF | current 2 | same | Hall sensor |
| J8 | 1 / 6 | ISENSE_3_SIG / REF | current 3 | same | Hall sensor |
| J8 | 2 / 7 | ISENSE_4_SIG / REF | current 4 | same | Hall sensor |
| J8 | 5 | +5V | sensor supply | 5 V out, unfused | 4 Hall sensors |
| J8 | 10 | GND | sensor return | – | 4 Hall sensors |
| J9 | 8, 7, 6, 5 | T_1 … T_4_SIG | PT1000 high side | about 2.0–2.5 V, 2 mA bias | PT1000 |
| J9 | 4, 3, 2, 1 | GND | PT1000 return | – | PT1000 |
| J10 | 5, 1, 3, 7 | DO1, DO2, DO3, DO4 | digital out | open drain, 10 kΩ to 5 V, 100 nF | Q4 |
| J10 | 2, 6 | DI1, DI2 | digital in | 0–5.5 V, 10 kΩ to 5 V, low < 0.8 V, high > 2.0 V | Q4 |
| J10 | 4, 8 | GND | return | – | – |

Fit to the system role:

- **Fuel cell link:** only RS-232 on J2 pins 2/6 can carry it (Q1). The MCU side is USART3 (PC10/PC11), not USART2.
- **PX4 link:** CAN on J2 pins 1/5, facing each other, good for a twisted pair. The Pixhawk CAN connector is a 4-pin JST-GH (5 V, CAN_H, CAN_L, GND), so an adapter cable is needed in any case; don't connect its 5 V wire.
- **Adjacent pins on J3:** 50V_1 sits next to 5V_2 in both rows (pad gap 1.5 mm, rule 0.6 mm). A short there puts 50 V on the measured 5 V rail outside the board. The board itself survives: (50 − 5.5)/20 kΩ ≈ 2.2 mA into the op-amp input [C].

---

## 5. Channel calculations

Common to all channels: 12 bit, VDDA ≈ 3.3 V, 1 LSB = 0.806 mV. Output filter 4.7 kΩ × 100 nF = 0.47 ms (339 Hz). Clamp current at overload: (4.94 − 3.3 − 0.25)/4.7 kΩ ≈ 0.3 mA per channel into the BAT54S.

| | VSENSE 50 V | VSENSE 5 V | ISENSE | TSENSE |
|---|---|---|---|---|
| Parts (netlist) | 200k / 11k, 100k+100k / 11k | 20k / 10k, 10k+10k / 10k | 10k 1 % / 16k 0.1 %, 16k to VREF_1V65 | 1.5k bias, 2.7k / 2.4k / 8.2k, 100 Ω |
| Transfer function | V_ADC = 0.055 × (POS − NEG) | V_ADC = 0.5 × (POS − NEG) | V_ADC = 1.65 V + 1.6 × (SIG − REF) | V_ADC = 7.454 × Vs − 3.037 × V5, Vs = V5 × R/(R + 1500) |
| Input range | 0 … 60 V | 0 … 6.6 V | −1.03 … +1.03 V | 1031 … 1476 Ω (+8 … +124 °C) |
| ADC voltage min / max | 0 / 2.75 V at 50 V | 0 / 2.5 V at 5 V | 0 … 3.3 V | −0.002 / 3.296 V |
| Headroom | 0.55 V at the top, none at 0 | 0.8 V at the top, none at 0 | symmetric | none at either end |
| Resolution per LSB | 14.6 mV | 1.61 mV | 0.50 mV (SIG − REF) | about 0.028 K |
| Worst-case error | gain ±0.2 % (resistors); about 1 V dead zone at 0 (output swing 60 mV typ.) | gain ±0.2 %; about 0.1 V dead zone | gain ±1.1 %; offset up to about 7 mV input-referred from 1 % resistors at 0.85 V common mode, removed by zero calibration | about ±1.2 K from resistors (worst case), plus 1.2 K per 1 % of 5 V error at the top of the range, plus self-heating (4 mW) |
| Matches README formula | yes | yes | yes | yes |

Notes:

- The absolute accuracy of the voltage and current channels also depends on VDDA (module LDO ME6231A33). The README plan to derive VDDA from VREFINT covers this.
- VREF_1V65 is a divider from +3V3_MCU, and the module ties VREF+ to VDDA through 0 Ω [DS]. The zero point is therefore ratiometric and sits at code 2048. The Hall sensor output is not ratiometric to 3.3 V, so the gain term still needs VDDA.
- ADC grouping: ADC1 can take PA0–PA3, PB0, PB1; ADC2 can take PA4–PA7, PB2, PC4. Two ADCs cover all 12 channels. Slow channels (not IN1–IN5): PA4 (IN17), PA5 (IN13), PB0 (IN15), PB2 (IN12); PB1 is slow on ADC1 (IN12) and fast on ADC3 (IN1).

---

## 6. Power budget

| Rail | Load | Current (estimate) |
|---|---|---|
| +5V | 7 × TLV2186 (90 µA per channel [DS]) | 1.3 mA |
| +5V | 4 × PT1000 bias + 4 × offset divider | 8 mA + 4 mA |
| +5V | DO/DI pull-ups, LED D1 (560 Ω) | about 6 mA |
| +5V | 4 Hall sensors on J8 (Q2) | about 80–100 mA |
| +5V → U14 → +3.3V | TCAN332, MAX3221, 3 × LVC2G07, pull-ups | about 20 mA typical, 80 mA peak |
| +5V → D17 → module | G474 at 170 MHz plus LEDs | about 40 mA |
| **Total at J1** | | **about 0.25 A** |

- U14: (5 − 3.3) V × 80 mA = 0.14 W in SOT-23-5, no thermal issue. 600 mA rating.
- Module path: J1 − 0.3 V (D17) → P-FET → ME6231A33, input range 3.3–5.5 V [DS]. Enough dropout margin at 4.5 V.
- USB and J1 together: the module feeds VBUS to its 5 V pin through its own Schottky D4, and D17 blocks the path back to the board [DS]. No back-feed in either direction, unless the module's solder bridge SB1 is closed.
- USB only: the MCU runs, +5V and +3.3V are off. The transceivers and buffers are high-impedance when unpowered [DS for TCAN332 and LVC]. Nothing is damaged; nothing on the carrier works.
- Clamp current into +3V3_MCU: realistic worst case is four open PT1000 inputs, 4 × 0.3 mA = 1.2 mA; all twelve would be 3.6 mA. The running MCU draws more, so the rail doesn't rise. The module's own idle load is small (power LED through 5.1 kΩ ≈ 0.3 mA [DS]), so don't use Stop or Standby mode with sensors unplugged.

---

## 7. MCU pin table for the G474 project

"DS" = checked against the DS12288 Rev 6 pin table; "WeAct" = position checked against the WeAct Long V1.0 schematic and outline drawing.

| Pin | Header | Net | Function | Mode / pull / speed | Initial state | Verified |
|---|---|---|---|---|---|---|
| PA0 | J5-19 | MCU_ISENSE_1 | ADC12_IN1 | analog | – | DS, WeAct |
| PA1 | J5-18 | MCU_ISENSE_2 | ADC12_IN2 | analog | – | DS, WeAct |
| PA2 | J5-17 | MCU_ISENSE_3 | ADC1_IN3 | analog | – | DS (FT_a), WeAct |
| PA3 | J5-16 | MCU_ISENSE_4 | ADC1_IN4 | analog | – | DS, WeAct |
| PA4 | J5-15 | MCU_50V_1 | ADC2_IN17 (slow) | analog | – | DS, WeAct |
| PA5 | J5-14 | MCU_50V_2 | ADC2_IN13 (slow) | analog | – | DS, WeAct |
| PA6 | J5-13 | MCU_5V_1 | ADC2_IN3 | analog | – | DS, WeAct |
| PA7 | J5-12 | MCU_5V_2 | ADC2_IN4 | analog | – | DS, WeAct |
| PB0 | J5-10 | MCU_T1 | ADC1_IN15 (slow) or ADC3_IN12 | analog | – | DS, WeAct |
| PB1 | J5-9 | MCU_T2 | ADC1_IN12 (slow) or ADC3_IN1 | analog | – | DS, WeAct |
| PB2 | J5-8 | MCU_T3 | ADC2_IN12 (slow) | analog | – | DS, WeAct |
| PC4 | J5-11 | MCU_T4 | ADC2_IN5 | analog | – | DS (FT_fa), WeAct |
| PB12 | J4-5 | MCU_CAN_RXD | FDCAN2_RX, AF9 | AF, no pull | – | DS, WeAct |
| PB13 | J4-6 | MCU_CAN_TXD | FDCAN2_TX, AF9 | AF push-pull, high speed | recessive (TCAN pull-up) | DS, WeAct |
| PC10 | J4-16 | MCU_RS232_DIN | USART3_TX, AF7 | AF push-pull | high (R112) | DS, WeAct |
| PC11 | J4-17 | MCU_RS232_ROUT | USART3_RX, AF7 | AF, pull-up | – | DS, WeAct |
| PB3 | J4-18 | MCU_RS232_EN | GPIO out | push-pull, low speed | **0** (R115 pull-down) | DS, WeAct |
| PB4 | J4-19 | MCU_RS232_INVALID | GPIO in | no pull | – | DS (FT_c), WeAct |
| PB5 | J4-20 | MCU_RS232_FORCEOFF | GPIO out | push-pull | **1** (R113 pull-up) | DS, WeAct |
| PB6 | J4-21 | MCU_RS232_FORCEON | GPIO out | push-pull | **1** (R114 pull-up) | DS (FT_c), WeAct |
| PA15 | J4-15 | I2C_SCL | I2C1_SCL, AF4 | AF open drain, no pull | – | DS [N: AF number from memory], WeAct |
| PB7 | J4-22 | I2C_SDA | I2C1_SDA, AF4 | AF open drain, no pull | – | DS [N: AF number from memory], WeAct |
| PB10 | J5-6 | MCU_DI1 | GPIO in | no pull (1 kΩ external) | – | DS (TT_a), WeAct |
| PB11 | J5-5 | MCU_DI2 | GPIO in | no pull | – | DS (TT_a), WeAct |
| PB14 | J4-7 | MCU_DO1 | GPIO out | push-pull, low speed | set **1** first if DO must be off | DS, WeAct |
| PB15 | J4-8 | MCU_DO2 | GPIO out | same | same | DS, WeAct |
| PA8 | J4-10 | MCU_DO3 | GPIO out | same | same | DS, WeAct |
| PB9 | J4-23 | MCU_DO4 | GPIO out | same | same | DS, WeAct |
| PA9 | J4-11 | TP44 | USART1_TX, AF7 | AF push-pull | – | DS, WeAct |
| PA10 | J4-12 | TP45 | USART1_RX, AF7 | AF, pull-up | – | DS, WeAct |

Used on the module and left unconnected on the carrier (correct): PC6 (blue LED), PC13 (key), PB8 (BOOT0, not on the header), PA11/PA12 (USB), PA13/PA14 (SWD), PF0/PF1 (8 MHz crystal), PC14/PC15 (32.768 kHz crystal), VREF+ (tied to VDDA on the module), VBAT, NRST.

### Firmware port: what moves

| Old (U575 Nucleo) | New (G474) | Change needed |
|---|---|---|
| USART2 RX on PA3, 19200 baud | USART3 on PC10/PC11 through the MAX3221 | new instance and IRQ; check the signal polarity (Q1) |
| FDCAN1 on PF7/PF8, 160 MHz kernel clock | FDCAN2 on PB12/PB13 | new instance and IRQ; recompute the 1 Mbps bit timing for the G474 clock; use the 8 MHz HSE as the clock source |
| USART1 debug over ST-Link VCP | USART1 on PA9/PA10 at TP44/TP45 | external USB-UART adapter |
| ADC1/ADC4, I2C2, UCPD1, USB, LEDs on PB7/PC7/PG2 | ADC1/ADC2, I2C1, one LED on PC6 | regenerate from CubeMX for the G474; PB7 is now I²C SDA |

Start-up order: `HAL_Init()` → `HAL_PWREx_DisableUCPDDeadBattery()` → write the DO output latches to 1 and PB5 = 1, PB6 = 1, PB3 = 0 **before** switching those pins to output → clocks → peripherals. The hardware pulls already give a valid RS-232 state before the firmware runs (receiver on, driver on, TX idle). The DO lines are LOW during that time (finding 7).

---

## 8. BOM differences and mating parts

Differences between `BOM/BOM_PCU_G474.csv` and the `Routing/` schematic (script comparison of all 215 BOM designators):

| Ref | BOM | Schematic |
|---|---|---|
| J2, J3, J9, J10 | 430451000, footprint `…43045-1000_2x05…` | 430450800, footprint `…43045-0800_2x04…` |

No other differences: R109 is in the BOM, R105/R106 are marked DNP, J4/J5 are left out as intended. The BOM doesn't give a voltage rating for the 100 nF capacitors; none of them sits on a 50 V net, so 16 V or more is enough.

Parts check: TLV2186IDR and TCAN332GDR are listed as active by TI [DS]. Packages match the footprints for U1–U14, D3, D4, D5–D17 (pin functions checked against the netlist). I did not check stock or JLCPCB basic/extended status [N].

Mating parts for the harness (check the exact terminal suffix against the wire gauge before ordering [N]):

| Header | Receptacle housing | Qty |
|---|---|---|
| J1 (43045-0400) | Molex 43025-0400 | 1 |
| J2, J3, J9, J10 (43045-0800) | Molex 43025-0800 | 4 |
| J8 (43045-1000) | Molex 43025-1000 | 1 |
| all | Micro-Fit 3.0 female crimp terminals, series 43030 | 46 plus spares |
| module | 2 × Würth 61302411821 (1×24 socket) | 2 |

---

## 9. Checked and OK

- **Netlist vs. board:** 148 nets and 266 footprints identical, including J2, J3, J9, J10; values and footprints match.
- **Module pinout:** all 48 header positions of J4/J5 match the WeAct schematic and outline; row spacing 15.24 mm; pin 1 at the USB end; J4 = 5 V row, J5 = 3.3 V row.
- **Power supply:** AP2112K pinout, EN tied to VIN, 10 µF + 2 × 100 nF output; D17 direction; TVS direction; LED current 3–5 mA.
- **VSENSE:** resistor ratios, gains 0.055 and 0.5, 24 V and 11 mW per 100 kΩ at 50 V, no capacitor on a 50 V net.
- **ISENSE:** polarity (SIG to +), VREF buffer, unused op-amp half wired as a follower, no capacitor on the VREF buffer output.
- **TSENSE:** transfer function reproduces the README numbers; an open sensor reads full scale.
- **RS-232:** MAX3221 pinout, 4 × 100 nF for 3.3 V, pull-ups/pull-down R112–R115.
- **CAN:** TCAN332G pinout (pins 5 and 8 NC, no standby pin), split termination, PESD1CAN on the connector side.
- **D_IO:** LVC2G07 pinout, 5 V never reaches the MCU pins.
- **Clamps:** BAT54S pinout and direction on all 12 channels; 5–9 mm from the J5 pins.
- **Decoupling:** every IC supply pin has its capacitor within 1.8–2.2 mm and a GND via within 0.8 mm (except finding 6).
- **Placement:** analog on the J5 side, CAN/RS-232/digital on the J4 side; only C59/C60 under the module.
- **Mechanics:** outline 101.1 × 77.1 mm; H1–H5 3.2 mm holes with 6.4 mm pads on GND; connectors flush with the board edges; every footprint has a 3D model.
- **Manufacturability:** tracks ≥ 0.2 mm, vias 0.6/0.3 and 0.8/0.4 mm, minimum annular ring 0.24 mm, all within JLCPCB 4-layer limits. THT parts: J1–J5, J8–J10. All 44 test points on the bottom, 2.0 mm minimum spacing, excluded from the position files.

Not done: STEP export collision check (the DRC courtyard check passes and the heights are uncritical by inspection), a new DRC run (the result in the prompt was taken as given), and ERC (Q8).

---

## 10. Sources and scripts

Sources:

- STM32G474 datasheet DS12288 Rev 6 (local copy `~/Downloads/DS_stm32g474ce.pdf`): pin table and note 6, Tables 14, 15, 67. <https://www.st.com/resource/en/datasheet/stm32g474ce.pdf>
- WeAct STM32G474 CoreBoard Long V1.0 schematic and outline: <https://github.com/WeActStudio/WeActStudio.STM32G474CoreBoard/tree/master/Hardware/QFN48/WeAct-STM32G474CoreBoard_Long>
- TLV2186: <https://www.ti.com/product/TLV2186>
- TCAN332G: <https://www.ti.com/product/TCAN332G>
- MAX3221, SN74LVC2G07, AP2112K, SMAJ5.0A, BAT54S, PESD1CAN: values taken from `REVIEW_RESULT_4.md` and from memory, not re-read for this review [N].

Scripts (in the session scratchpad, working on a copy of `Routing/`):

- `nl.py`: parses the `kicad-cli sch export netlist` output into JSON (components, nets, pin functions).
- `b1.py`: pcbnew: netlist parity, footprint positions, attributes, track and via statistics, design rule minimums.
- `b2.py`: pcbnew: parts under the module, distance from each IC supply pin to its capacitor and GND via, clamp-to-pin distances, zones, silkscreen texts.
- BOM comparison: CSV designators against the netlist JSON.
- `gs -sDEVICE=txtwrite` on the datasheet, then a search of the pin table for each used pin.

---

## 11. Re-check after the fixes (2026-11-12, 18:20)

Checked on a fresh copy of `Routing/` (board saved 18:16). The sections above describe the state before the fixes; J3 is now 2×6, so the J3 rows in §4 and §8 are superseded by this section.

**Verdict: ready for fab.** Findings 1, 2, 3 and 5 are closed.

| Finding | Status | What I measured |
|---|---|---|
| 1 (J3 mis-mating) | **Closed** | J3 is `43045-1200` (2×6), the only 12-pin header. Pins 1/7 = 50V_2 NEG/POS, 2/8 = 50V_1, 5/11 = 5V_2, 6/12 = 5V_1; 3, 4, 9, 10 unconnected. Each NEG still faces its POS. The 50 V and 5 V groups are 9 mm apart centre to centre (7.5 mm pad gap). Peg holes are 10.70 mm apart, 2.16 mm from pin 1, 3.0 mm drill. |
| 2 (silkscreen) | **Closed** | 10 text items, 1.0 mm high, 0.15 mm stroke. Top: "50V!", "COM", "J1 5V IN", "USB", board name with revision and date. Bottom (mirrored): function labels for J2, J3, J8, J9, J10. |
| 3 (BOM) | **Closed** | All 213 BOM designators match the schematic in value and footprint; quantities match. J8 ×1, J2/J9/J10 ×3, J3 ×1. The LCSC column is still empty. |
| 5 (PCBA attributes) | **Closed** | R105, R106, J4, J5 are excluded from the BOM and the position files on the board. |

Other checks:

- **Netlist:** against the earlier export only the J3 pin numbers changed; no other net or part differs. Schematic vs. board: 0 differences, 266 footprints.
- **DRC** (zones refilled, on the copy): 0 unconnected pads, 0 footprint errors; the 199 reported items are all `lib_footprint_issues` from the missing global library table, as expected outside the GUI.
- **Fit:** J3 has 0.79 mm to J9 and 0.78 mm to J8 (footprint bounding boxes). That is enough for the headers; the three plugs sit close together, so latching the middle one by hand is tight.
- **3D model:** `430451200.stp` is present and assigned to J3.

Still open (none blocks fabrication):

- ERC: the change log says the 30 library warnings are fixed; I can't run ERC from the command line, so I haven't confirmed the result.
- Top-side labels exist only for J1, J2 and J3; J8, J9 and J10 are labelled on the bottom only.
- LCSC part numbers, and Q2–Q6, Q9 above.
- The mating list now needs 43025-0800 × 3 and 43025-1200 × 1 (already in `BOM_PCU_G474.md`).
