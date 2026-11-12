# PCB layout reminders (PCB PCU G474)

Checklist for the layout of the **PCB PCU G474** project. Source: reviews 1–3 (`../PCB PCU/`), `README.md`, `BOM/BOM_PCU_G474.md`. Tick each item as you go.

## 0. Before you start (decisions)

- [ ] **Connector keying (FUN-2):** J2/J3/J8/J9/J10 are identical 2×5 Micro-Fit connectors, so cables can be swapped. That can destroy parts (e.g. J2 cable into J8 puts +5 V on the FC's I²C SDA). Decide first (e.g. J3 → 2×4, coded/coloured housings), because it changes the footprints.
- [x] **ADC series resistors (MIG-2):** done, 4.7 kΩ (2026-10-31).
- [ ] **CAN termination:** is the PCU a bus end? If not, R79/R80 = DNP.
- [ ] **What do DO1–4 drive?** If anything safety-relevant (arm/kill/valve), the power-up glitch needs fixing first (FUN-3).
- [x] ERC clean (2026-11-02).

## 1. Starting the board

- [x] Board outline **101 × 77 mm** and mounting holes H1–H5 placed (draft placement, 2026-11-02).
- [ ] "Update PCB from Schematic" (F8) once: all 266 footprints are already on the board (draft). F8 should only sync fields/attributes (DNP R105/R106, J4/J5 exclude from BOM/position files), **no new parts**.
- [ ] **Stack-up:** 4 copper layers already set (In1 = GND, In2 = PWR). Check Board Setup → Board Stackup →, 1.6 mm (signal / GND / power / signal). **Solid GND plane.** *(Design rules for JLCPCB are already in the project file, 2026-11-02.)*
- [x] Net classes set in the project file (2026-11-02): **Default** 0.2/0.2 mm, via 0.6/0.3 · **Power** (+5V, +3.3V, +3V3_MCU, GND, module 5V) 0.5 mm · **HV50** (50V_*) 0.3 mm, **0.6 mm clearance** · **CAN** (CAN_H/L) 0.25 mm diff pair. Check them once in Board Setup → Net Classes.

## 2. WeAct module (J4/J5)

- [ ] **Row spacing J4 ↔ J5 = 15.24 mm** (confirmed against the module drawing).
- [ ] **Orientation:** check against the top view of the module. J4 = LEFT (pin 1 = GND, 3/4 = 5V, … B9, 24 = GND); J5 = RIGHT (1/2 = GND, 3/4 = 3V3, … A0, NR, C13, VB, 3V3, GND).
- [ ] Keep the module's **SWD header** and **USB-C** reachable (don't cover them, leave room for the plug).
- [ ] Under the module (≈ 8.5 mm socket height) only place low SMD parts. Check the fit in the 3D view.
- [ ] **J4/J5 footprints: set "Exclude from position files"** (they are already "exclude from BOM" in the schematic). JLCPCB only drills the holes; the sockets (Würth 61302411821) are soldered by hand.

## 3. Placement: what goes where

**Power**
- [ ] J1 at the board edge; **D3 (TVS)** and C54/C55 close to J1.
- [ ] **U14 (AP2112K)** with C40 (in) and **C41 (out)** right at the pins.
- [ ] **D17** close to J4 pins 3/4 (module 5V).
- [ ] **C59 (1 µF) + C60 (100 nF)** right at **J5 pins 3/4** (+3V3_MCU).
- [ ] Power LED D1/R109 visible.

**Analog (keep it in one area, away from CAN/RS-232/DO)**
- [ ] VSENSE (U2/U3), ISENSE (U1/U5), TSENSE (U7/U8) close to their connectors J3/J8/J9 and on the J5 side of the module.
- [ ] Each op-amp's **0.1 µF on V+** (C5/C6/C22/C23/C26/C53/C2) right at pin 8.
- [ ] **BAT54S D5–D16 right next to J5** (the MCU analog pins); 4.7 kΩ between op-amp and clamp, 100 nF on the MCU side.
- [ ] **U9 (VREF_1V65)** close to ISENSE; route VREF_1V65 cleanly.
- [ ] Ferrite beads E1–E12 and the input caps close to their connectors.
- [ ] **50 V inputs (J3, R17/R81, R9/R21):** observe **clearance/creepage** to low-voltage nets (≈ 50–60 V); keep the 50 V traces short and away from MCU nets.
- [ ] Route +3V3_MCU (ADC reference, clamps, VREF_1V65) away from digital noise. TSENSE runs from +5V (as in Fusion).

**Communication**
- [ ] **TCAN332 (U6)** close to J2; route **CAN_H/CAN_L as a differential pair**; R79/R80/C21 and **PESD1CAN (D4)** right at the connector.
- [ ] **MAX3221 (U4)** close to J2; **charge-pump caps C8/C9/C18/C19 and C7** right at the IC.
- [ ] **I²C:** J2 → J4 (PA15/PB7) directly; R107/R108 pull-ups (R105/R106 = DNP).

**Digital I/O**
- [ ] U10/U11 (DO) and U12 (DI, LVC2G07) close to J10; ferrites E13/E14 at the connector.

**Debug / test**
- [ ] **TP44 (PA9 TX), TP45 (PA10 RX), TP46 (GND)** reachable, ideally at the board edge, for a USB-UART adapter.
- [ ] Analog test points reachable with a probe (add a GND point near the analog area if needed).

## 4. Silkscreen

- [ ] Label every connector with its **function** (POWER 5V, COMM, VSENSE 50V, ISENSE, TSENSE, DIO) and pin 1, especially J3 "50 V!".
- [ ] Module orientation (outline + "USB" arrow) at J4/J5.
- [ ] Note "I²C pull-ups: R107/R108 = 3.3 V (default), R105/R106 = 5 V (DNP)".
- [ ] Board name, version, date.

## 5. Before ordering (JLCPCB)

- [ ] **DRC** with no errors; check the 3D view (module, connectors, heights).
- [ ] **Fill in the LCSC numbers** (`BOM/BOM_PCU_G474.csv`, column "LCSC Part #"), e.g. with the KiCad plugin **"JLCPCB Tools"** or the LCSC BOM tool.
- [ ] Watch for **extended parts** (≈ $3 each per order) and **0.1 % resistors** (cost).
- [ ] Export Gerber + BOM + **CPL**. In JLCPCB's preview, **check component rotations** (especially diodes, SOT-23, LED, electrolytic, Micro-Fit).
- [ ] DNP parts (R105/R106) not in the BOM/CPL.
- [ ] Micro-Fit connectors (THT): fitted by JLCPCB (THT surcharge) or by hand?
- [ ] **Order separately:** 2 × Würth 61302411821 (sockets), plus the Micro-Fit housings and contacts for the cables.

## 6. Not layout, but don't forget

- [ ] Firmware port U575 → G474 (porting table in `../PCB PCU/REVIEW_RESULT_3_2026-10-31.md` §4.2). First line after `HAL_Init()`: `HAL_PWREx_DisableUCPDDeadBattery()`, then PB5 = 1, PB6 = 1, PB3 = 0.
- [ ] Specify the J1 supply as **5.0–5.25 V** (the TLV2186 needs ≥ 4.5 V).
- [ ] Bring-up: check +5V and +3.3V first **without the module**, then measure the analog outputs at the test points (< 3.3 V), then plug the module in.
