# Parts list (BOM): PCU carrier board, WeAct G474 (`PCB PCU G474`)

Generated from the KiCad netlist. Quantities **per board**. `BOM_PCU_G474.csv` is in JLCPCB format. The "LCSC Part #" column is filled for the ICs, diodes, ferrites, J1–J3/J11–J13 and the 10k 0.1 % resistors; the other passives are still open.

**Summary:** 206 parts for assembly in 39 line items (plus one DNP line) · 2 DNP · 2 hand-soldered · 40 test-point pads · 5 mounting holes.

## Assembled parts

| # | Value | Qty | Designators | Package | Description |
|---|---|---|---|---|---|
| 1 | TLV2186IDR | 6 | U1–U3, U5, U7, U9 | SOIC-8_3.9x4.9mm_P1.27mm | Dual op-amp, rail-to-rail, 24 V (TI) |
| 2 | MAX3221IDBR | 1 | U4 | SSOP-16_5.3x6.2mm_P0.65mm | RS-232 transceiver 3.3 V, 1 ch. (TI) |
| 3 | TCAN332GDR | 2 | U6, U15 | SOIC-8_3.9x4.9mm_P1.27mm | CAN transceiver 3.3 V (TI) |
| 4 | SN74LVC2G07DBVR | 3 | U10–U12 | SOT-23-6 | Dual buffer, open-drain (TI) |
| 5 | AP2112K-3.3 | 1 | U14 | SOT-23-5 | LDO 3.3 V 600 mA (Diodes Inc.) |
| 6 | 150060VS55040 | 1 | D1 | LED_0603_1608Metric | LED 0603 (Würth) |
| 7 | SMAJ5.0A | 1 | D3 | D_SMA | TVS 5 V unidirectional |
| 8 | PESD1CAN,215 | 2 | D4, D18 | SOT-23 | CAN ESD protection (Nexperia) |
| 9 | BAT54S | 10 | D5–D14 | SOT-23 | Dual Schottky (series), ADC clamp |
| 10 | B5819W | 1 | D17 | D_SOD-123 | Schottky 40 V 1 A |
| 11 | 430451000 | 1 | J8 | Molex_Micro-Fit_3.0_43045-1000_2x05_P3.00mm_Horizontal | Molex Micro-Fit 3.0, 2×5, right angle |
| 12 | 430450800 | 2 | J9, J10 | Molex_Micro-Fit_3.0_43045-0800_2x04_P3.00mm_Horizontal | Molex Micro-Fit 3.0, 2×4, right angle |
| 13 | 430450400 | 5 | J1, J2, J3, J11, J12 | Molex_Micro-Fit_3.0_43045-0400_2x02_P3.00mm_Horizontal | Molex Micro-Fit 3.0, 2×2, right angle (J1 5 V in, J2 CAN1, J3 50 V sense, J11 CAN2, J12 5 V sense) |
| 14 | 430450600 | 1 | J13 | Molex_Micro-Fit_3.0_43045-0600_2x03_P3.00mm_Horizontal | Molex Micro-Fit 3.0, 2×3, right angle (J13 RS-232 + I²C) |
| 15 | 100nF | 46 | C1–C38, C42, C43, C45, C47, C48, C60–C62 | C_0603_1608Metric | Capacitor 100nF 0603 X7R |
| 16 | 10uF | 4 | C39, C40, C54, C55 | C_1206_3216Metric | Capacitor 10uF 1206 X5R/X7R ≥10 V |
| 17 | 10uF | 1 | C41 | C_0603_1608Metric | Capacitor 10uF 0603 X5R/X7R ≥10 V |
| 18 | 1uF | 1 | C59 | C_0603_1608Metric | Capacitor 1uF 0603 X5R/X7R ≥10 V |
| 19 | HZ0603B102R-10 | 12 | E3–E14 | L_0603_1608Metric | Ferrite bead 1 kΩ@100 MHz (Laird) |
| 20 | 11k 0.1% | 4 | R1, R3, R19, R20 | R_0603_1608Metric | Resistor 11k Ω 0.1% (precision) 0603 |
| 21 | 200k 0.1% | 2 | R2, R4 | R_0603_1608Metric | Resistor 200k Ω 0.1% (precision) 0603 |
| 22 | 20k 0.1% | 2 | R5, R8 | R_0603_1608Metric | Resistor 20k Ω 0.1% (precision) 0603 |
| 23 | 10k 0.1% | 10 | R6, R7, R10, R12, R13, R15, R73, R75–R77 | R_0603_1608Metric | Resistor 10k Ω 0.1% (precision) 0603 |
| 24 | 100k 0.1% | 4 | R9, R17, R21, R81 | R_0603_1608Metric | Resistor 100k Ω 0.1% (precision) 0603 |
| 25 | 4.7k | 12 | R11, R18, R22, R27, R32, R37, R42, R74, R82, R88, R107, R108 | R_0603_1608Metric | Resistor 4.7k Ω 1% 0603 |
| 26 | 16k 0.1% | 8 | R23, R26, R28, R31, R33, R36, R38, R41 | R_0603_1608Metric | Resistor 16k Ω 0.1% (precision) 0603 |
| 27 | 10k 1% | 8 | R24, R25, R29, R30, R34, R35, R39, R40 | R_0603_1608Metric | Resistor 10k Ω 1% 0603 |
| 28 | 0 | 16 | R43–R54, R116–R119 | R_0603_1608Metric | Resistor 0 Ω (jumper) 0603 |
| 29 | 1k | 7 | R55, R56, R61, R62, R71, R72, R122 | R_0603_1608Metric | Resistor 1k Ω 1% 0603 |
| 30 | 100k | 8 | R57, R58, R63, R64, R112–R115 | R_0603_1608Metric | Resistor 100k Ω 1% 0603 |
| 31 | 10k | 7 | R59, R60, R65–R68, R123 | R_0603_1608Metric | Resistor 10k Ω 1% 0603 |
| 32 | 220 | 2 | R69, R70 | R_0603_1608Metric | Resistor 220 Ω 1% 0603 |
| 33 | 8.2k 0.1% | 2 | R78, R87 | R_0603_1608Metric | Resistor 8.2k Ω 0.1% (precision) 0603 |
| 34 | 60.4 | 4 | R79, R80, R120, R121 | R_0603_1608Metric | Resistor 60.4 Ω 1% 0603 |
| 35 | 2.4k 0.1% | 2 | R83, R89 | R_0603_1608Metric | Resistor 2.4k Ω 0.1% (precision) 0603 |
| 36 | 2.7k 0.1% | 2 | R84, R90 | R_0603_1608Metric | Resistor 2.7k Ω 0.1% (precision) 0603 |
| 37 | 100 | 2 | R85, R91 | R_0603_1608Metric | Resistor 100 Ω 1% 0603 |
| 38 | 1.5k 0.1% | 2 | R86, R92 | R_0603_1608Metric | Resistor 1.5k Ω 0.1% (precision) 0603 |
| 39 | 560 | 1 | R109 | R_0603_1608Metric | Resistor 560 Ω 1% 0603 |

## Not fitted (DNP)

| Value | Qty | Designators |
|---|---|---|
| 4.7k | 2 | R105, R106 |

## Hand-soldered, bought separately (not in the JLCPCB BOM)

| Designator | Qty | Part |
|---|---|---|
| J4, J5 | 2 | **Würth Elektronik 61302411821** (WR-PHD, female socket 1×24, 2.54 mm, straight THT, 8.5 mm). Not 61302421821 (dual row) or 61302011821 (20 pins). |

## No parts

- Test points: TP1–TP18, TP23–TP41, TP44–TP46 (TP44/TP45/TP46 = debug UART PA9 TX / PA10 RX / GND)
- Mounting holes M3: H1–H5

## Not on the board

- WeAct STM32G474CoreBoard Long (STM32G474CEU6), plugs into J4/J5.
- Micro-Fit 3.0 mating housings: 43025-0400 ×5 (J1, J2, J3, J11, J12), 43025-0600 (J13), 43025-0800 ×2 (J9, J10), 43025-1000 (J8), plus crimp terminals (series 43030).
- Sensors: 2 × PT1000 temperature sensor, 4 × Hall current sensor (SIG/REF, 5 V).


**Update 2026-11-12:** J2/J9/J10 → 43045-0800 (2×4), J3 → 43045-1200 (2×6), J8 stays 43045-1000. Mating housings: 43025-0400 (J1), 43025-0800 ×3, 43025-1000 (J8), 43025-1200 (J3), plus Micro-Fit 3.0 crimp terminals (series 43030). R105/R106 and J4/J5 are excluded from the PCBA position file (DNP / hand-soldered). The LCSC Part # column is still empty: fill it, or let JLCPCB match by MPN, before ordering PCBA.

**Update 2026-11-13:** temperature sensing reduced to 2 channels (U8, R93–R104, C49–C53, E1, E2, D15, D16 removed). Second CAN interface added: U15 (TCAN332), R116–R121, R122 (1k pull-up on CAN2 TXD), C61, C62, D18, and J11 (43045-0600, 2×3). The LCSC Part # column is still empty.

**Update 2026-11-13 (connectors):** J3 split into J3 (2×2, 50 V sense) and J12 (2×2, 5 V sense); J11 (CAN2) changed from 2×3 to 2×2. All three use 43045-0400, the same part as J1. The four 2×2 plugs fit each other's headers, so the cables must be colour-coded (owner decision).

**Update 2026-11-13 (J2 split):** J2 split into J2 (2×2, CAN1, same pinout as J11: 1 CAN_H, 2 GND, 3 CAN_L, 4 GND) and the new J13 (43045-0600, 2×3, RS-232 + I²C: 1 RS232_DOUT, 2 RS232_RIN, 3 GND, 4 I2C_SDA, 5 GND, 6 I2C_SCL). J1 moved 3.8 mm down to make room. 204 parts in 41 lines.

**Update 2026-11-14:** J1 value unified to 430450400 (was written 43045-0400), so all five 2×2 headers share one BOM line. 204 parts in 40 lines.

**Update 2026-11-14 (review fixes):** R123 (10k, pull-up on CAN1 TXD) added, so both CAN TXD lines are held recessive during reset. LCSC numbers added: TLV2186IDR C2057856, MAX3221IDBR C105243, TCAN332GDR C191010 (low stock; TCAN332DR C73651 is fine for 1 Mbit/s), SN74LVC2G07DBVR C37708, AP2112K-3.3TRG1 C51118, 150060VS55040 C6390388, SMAJ5.0A C83329, PESD1CAN C15771, BAT54S C8592, B5819W C8598, 43045-0400 C779799, 43045-0600 C127367, ferrite C35061 (Sunlord GZ1608D102TF, equivalent to HZ0603B102R-10, which LCSC does not carry), 10k 0.1 % C95204. Not at LCSC: 43045-0800 and 43045-1000. 206 parts in 39 lines plus one DNP line.
