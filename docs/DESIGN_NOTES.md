# PCB PCU G474: PCU carrier board, migrated from the Fusion design to the WeAct STM32G474

**Goal:** the original Fusion design (screenshots in `../PCB PCU/Fusion Sheets/`), migrated to KiCad, with the **NUCLEO-U575ZI-Q replaced by the WeAct STM32G474CoreBoard Long**. Only **migration-necessary** changes and **essential bug fixes** are included; no optional extras.

**How it was built (2026-11-02):** copy of the KiCad project `../PCB PCU`, then every change not needed for the migration was **reverted to Fusion**. Every step was checked against the KiCad netlist (`kicad-cli`); no annotation warnings. The old project `../PCB PCU` was not changed.

**Contents:** KiCad project `PCB PCU.kicad_pro` (sheets: Connectors, Power-supply, Connection To STM, VSENSE, ISENSE, TSENSE, RS232, Digital EinAusgänge), project library `PCU.kicad_sym` + `sym-lib-table`, parts list `BOM/BOM_PCU_G474.{csv,md}`, layout checklist `PCB_LAYOUT_REMINDERS.md`. The PCB is still empty.

---

## Deviations from the Fusion design (and why)

Categories: **[Migration]** = needed because of the G474 module · **[Fix]** = an error in the original or in the KiCad conversion that stops the board from working · **[KiCad]** = no electrical change.

### Connection To STM (`ConnectionToSTM_PCU.kicad_sch`)
| Change | Fusion | Now | Why |
|---|---|---|---|
| MCU board | 4 Nucleo sockets J4–J7 | **J4/J5 female sockets 1×24** for the WeAct module (Würth **61302411821**, "exclude from BOM", hand-soldered) | [Migration] |
| Pin mapping | U575 pins | G474: ISENSE PA0–PA3, 50V PA4/PA5, 5V PA6/PA7, T1–T4 PB0/PB1/PB2/PC4, DI PB10/PB11, DO PB14/PB15/PA8/PB9, CAN FDCAN2 PB12/PB13, RS-232 USART3 PC10/PC11, MAX3221 control PB3–PB6, I²C1 PA15/PB7 | [Migration] (checked against DS12288) |
| Module supply | +5V **and** +3.3V into the Nucleo (two 3.3 V regulators in parallel) | +5V via **D17 B5819W** → module 5V (J4-3/4); module 3V3 = separate net **+3V3_MCU** | [Migration] (D17 blocks USB back-feed) |
| ADC protection | none | **12 × BAT54S** (D5–D16) to +3V3_MCU, **C59 1 µF + C60 100 nF** on +3V3_MCU | [Migration]: G474 ADC pins are TT_a, **abs. max 4.0 V** (DS12288 Table 14); the op-amps can output 5 V |
| Debug UART | ST-Link VCP on the Nucleo | test pads **TP44 PA9 (TX) / TP45 PA10 (RX) / TP46 GND** | [Migration] |
| MAX3221 control lines | MCU pins only | **R112–R114 100k pull-up** (DIN, /FORCEOFF, FORCEON), **R115 100k pull-down** (/EN) | [Migration]: defined state while the G474 is in reset (PB3 = JTDO, PB5/PC10 Hi-Z) |
| I²C pull-ups | R105/R106 (5 V) or R107/R108 (3.3 V), "fit one pair" | same; **R107/R108 fitted, R105/R106 DNP** | as intended in Fusion (3.3 V Pixhawk) |

### Power-supply (`power_supply_PCB.kicad_sch`)
| Change | Fusion | Now | Why |
|---|---|---|---|
| 3.3 V regulator | R-78K3.3-0.5 + L1 100 µH (in KiCad wrongly R-78E, which needs ≥ 6 V) | **U14 AP2112K-3.3** (LDO), no L1 | [Fix] |
| C41 | 1 µF **between 5 V and 3.3 V** | **10 µF between +3.3V and GND** | [Fix]: wiring error in the original |
| D3 | clamp diode, part unclear | **SMAJ5.0A** (TVS, SMA) | [Fix]: correct part |

### ISENSE (`ISENSE.kicad_sch`)
| Change | Fusion | Now | Why |
|---|---|---|---|
| Polarity / zero point | output = 1.6 × (REF − SIG), zero point 0 V: **only one current direction, the wrong one** | SIG to the + input, R26/R31/R36/R41 to **VREF_1V65** → **V_ADC = 1.65 V + 1.6 × (SIG − REF)**, both directions | [Fix] |
| VREF_1V65 (zero point, box "Referenzspannung 1,65 V") | – | **U9 TLV2186** (U9A buffer, U9B unused, wired as a follower) + **R10/R12 10k 0.1 %** (divider from +3V3_MCU) + **C1** 0.1 µF (filter) + **C2** 0.1 µF (U9 supply) | [Fix]: needed for both current directions |
| Output resistors R27/R32/R37/R42 | 100 Ω | **4.7 kΩ** | [Migration]: limits the clamp current |

### VSENSE (`VSENSE.kicad_sch`)
| Change | Fusion | Now | Why |
|---|---|---|---|
| Topology | divider (56k/10k, 3.3k/82k) + difference amp: **not differential** (CMRR −5 dB / 15 dB) | **true difference amps**: 50 V: 100k+100k / 200k / 11k / 11k (G = 0.055); 5 V: 10k+10k / 20k / 10k / 10k (G = 0.5). The Fusion divider parts R10/R12/R14/R16 and C1/C2/C44/C46 are **removed** (not needed in a difference amp) | [Fix]: the Fusion version shows ≈ −1.85 V (50 V) / −0.18 V (5 V) of error per volt of NEG offset; the difference amp is correct whether NEG is at board GND or not |
| Output resistors R11/R18/R22/R74 | 100 Ω | **4.7 kΩ** | [Migration] |

### TSENSE (`TSENSE.kicad_sch`)
| Change | Fusion | Now | Why |
|---|---|---|---|
| Circuit / values | 1.5k pull-up to +5V, 2.7k/2.4k offset, 8.2k, 100 Ω | **unchanged (Fusion)** | – |
| Output resistors R82/R88/R94/R100 | 100 Ω | **4.7 kΩ** | [Migration] |
| T4 op-amp | – | T4 on **U8 unit B** (was doubled on unit A after the KiCad conversion) | [Fix] (KiCad conversion error) |

### Digital EinAusgänge (`D_IO.kicad_sch`)
| Change | Fusion | Now | Why |
|---|---|---|---|
| DI input divider | 1k pull-up + 1k series: **a grounded input still reads high** | pull-ups **R67/R68 = 10 kΩ**, series **R69/R70 = 220 Ω** | [Fix] |
| Designator | R68 twice | DI2 series resistor = **R69** | [Fix] (KiCad annotation) |
| Everything else (LVC2G07, R71/R72, C37/C38, DO caps 100 nF) | | unchanged (Fusion) | – |

### RS232 (`RS232.kicad_sch`)
| Change | Fusion | Now | Why |
|---|---|---|---|
| CAN TXD/RXD | in KiCad both labelled `MCU_CAN_RXD` (short) | R51 = `MCU_CAN_TXD`, R52 = `MCU_CAN_RXD` | [Fix] (KiCad conversion error) |
| Values | "60", "MAX3221IDBRDB16-M", "PESD1CAN,215SOT23_…" | **60.4 Ω**, **MAX3221IDBR**, **PESD1CAN,215** | orderable part numbers |
| MAX3221 symbol | pins off the grid | pins on the grid, wiring redrawn (netlist identical) | [KiCad] |

### Connectors (`connectors_PCU.kicad_sch`)
| Change | Fusion | Now | Why |
|---|---|---|---|
| GND on J2/J10 | none | **J2 pins 4/9, J10 pins 4/9 = GND** | [Fix]: RS-232/I²C/DIO need a return path |
| ERC hygiene | – | NC flag J9 pin 5, `T_x_RTN` labels → GND, PWR_FLAGs | [KiCad] |

### General
- Root sheet: stray MCU symbols (`MCUBLong`/`MCUShort`) removed. [KiCad]
- Comment labels turned into text items (they had been net labels). [KiCad]
- Project library `PCU.kicad_sym`: custom MAX3221, TCAN332, 74LVC2G07, WeAct LEFT/RIGHT, power symbol `+3V3_MCU`. [KiCad]

---

## Deliberately **not** included (compared with `../PCB PCU`)

C56 (47 µF electrolytic) · D18 SP0502BAHT + R110/R111 47 Ω (I²C ESD) · TP42/TP43 · Schmitt buffer at DI (back to SN74LVC2G07 with R71/R72, C37/C38) · DO caps 10 nF (back to 100 nF) · CAN split cap 4.7 nF (back to 100 nF) · ISENSE input resistors 0.1 % (back to 1 %) · TSENSE rescale/+3V3_MCU/4.99k/4.7k (back to Fusion) · fuse/reverse-polarity FET.

## Known limitations (accepted)

- **TSENSE:** range ≈ **+8 … +124 °C** (PT1000), ratiometric to the **external 5 V** (5 V error → temperature error); PT1000 self-heating ≈ 4 mW; an open sensor drives the output to ≈ 5 V (taken by the clamp).
- **DI:** LVC2G07 without hysteresis behind an RC (10k × 100 nF): slow edges can give multiple edges → **debounce in firmware**.
- **ISENSE:** 1 % input resistors → limited CMRR; the offset is removed by the zero calibration.
- **DO:** short high pulse at power-up/down (FUN-3); only critical for safety-relevant loads.

## Open points (before / during the layout)

- [x] **ERC in KiCad:** clean (2026-11-02, after the VREF move).
- [ ] **VSENSE:** check where the J3 NEG wires actually go (board GND or a remote/shunt-side ground). The difference amp works either way, so no change is needed. Just confirm it.
- [ ] Connector keying (FUN-2), CAN termination (bus end?), what do DO1–4 drive, Hall sensor type, is I²C needed at all → see `PCB_LAYOUT_REMINDERS.md`.
- [ ] Firmware port U575 → G474 (porting table: `../PCB PCU/REVIEW_RESULT_3_2026-10-31.md` §4.2). First line after `HAL_Init()`: `HAL_PWREx_DisableUCPDDeadBattery()`, then PB5 = 1, PB6 = 1, PB3 = 0.

## Conversion formulas (firmware)

- **50 V:** U = code · VDDA/4096 / 0.055  (FS ≈ 60 V) · **5 V:** U = code · VDDA/4096 / 0.5  (FS 6.6 V) · VDDA from VREFINT.
- **Current:** (SIG − REF) = (code − code₀) · VDDA/4096 / 1.6; code₀ measured at I = 0 (≈ 2048).
- **Temperature (Fusion circuit):** Vs = V5 · R/(R + 1500 Ω); V_ADC = 7.454 · Vs − 3.037 · V5  (with V5 = the board's 5 V, e.g. 5.0 V) → R = 1500 · k/(1 − k) with k = (V_ADC/V5 + 3.037)/7.454.
- ADC sampling time ≥ 47.5 cycles; output filter 4.7 kΩ × 100 nF ≈ 0.47 ms.
