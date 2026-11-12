# Requirements

Everything needed to open this project, check it, have the board manufactured and bring it up. Use it as a checklist when you copy the project.

## 1. Software

| Tool | Version | Needed for |
|---|---|---|
| KiCad | **7.0.5** | Opening and editing the schematic and board |
| KiCad standard libraries | the ones installed with KiCad 7 | Standard footprints and their 3D models |
| `kicad-cli` | installed with KiCad | `scripts/make_production.sh`, netlist export in the checks |
| KiCad's bundled Python | installed with KiCad | The check scripts in `scripts/` (they need the `pcbnew` module) |
| `zip`, a POSIX shell | any | `scripts/make_production.sh` |
| git | any | Version control |

Notes:

- A newer KiCad version opens the project, but converts the files when you save. After that, KiCad 7 can no longer open them. Decide on one version for everyone who works on the board.
- The check scripts were written for the KiCad 7.0.5 Python API and may need changes on other versions.
- No Python packages have to be installed. The scripts use only the standard library and `pcbnew`.
- The paths in the scripts default to macOS. On other systems, set `KICAD_CLI` and use the Python interpreter that ships with KiCad (see `scripts/README.md`).

## 2. Project libraries

Both project libraries are in `kicad/` and are found automatically through `sym-lib-table` and `fp-lib-table`. Nothing has to be installed globally.

| Library | File | Contents |
|---|---|---|
| Symbols `PCU` | `kicad/PCU.kicad_sym` | MAX3221, TCAN332, 74LVC2G07, the WeAct module halves, the `+3V3_MCU` power symbol |
| Footprints `PCU_Molex` | `kicad/PCU_Molex.pretty/` | Molex Micro-Fit 3.0 right-angle headers 2×2, 2×4, 2×5 and 2×6 |

**3D models (optional):** the Molex STEP files are not in the repository. To see the connectors in the 3D view, download them as described in `kicad/3d Models/README.md`.

## 3. PCB manufacturing

Send `production/PCB_PCU-gerbers.zip`. The manufacturer must be able to do the following:

| Parameter | Value |
|---|---|
| Board size | 101 × 77 mm, rectangular |
| Copper layers | 4 |
| Board thickness | 1.6 mm |
| Layer order | L1 signals + GND pour · L2 solid GND plane · L3 +5V plane with a +3V3_MCU island · L4 test pads + GND pour |
| Smallest track width | 0.2 mm |
| Smallest clearance | 0.2 mm (the 50 V nets use 0.6 mm) |
| Vias | Through-hole only: 0.6 mm pad / 0.3 mm drill and 0.8 mm / 0.4 mm. No blind, buried or micro vias |
| Smallest drill | 0.3 mm |
| Copper to board edge | at least 0.5 mm |
| Vias | Tented (covered by solder mask). There are no vias in pads |
| Mounting holes | 5 × M3 (3.2 mm) |

Not fixed by the design, so choose when ordering:

- **Copper weight and layer build-up:** the project defines no detailed stack-up. The track widths were chosen for standard 1 oz (35 µm) outer copper and less than 0.5 A total current. The manufacturer's standard 4-layer 1.6 mm build-up is fine; there are no controlled-impedance traces.
- **Surface finish:** lead-free HASL or ENIG both work. The finest pitch is 0.65 mm (U4, SSOP-16).
- **Solder mask and silkscreen colour:** free choice.

Design rules that the board is checked against are stored in `kicad/PCB PCU.kicad_pro` and `kicad/PCB PCU.kicad_dru`.

## 4. Assembly

| Item | Value |
|---|---|
| Files | `bom/BOM_PCU_G474.csv` and `production/PCB_PCU-pos.csv` |
| Assembled parts | 213 parts in 37 BOM lines |
| Sides | Top side only. The bottom side has only bare test pads |
| Smallest passive | 0603 |
| Finest pitch | 0.65 mm (SSOP-16) |
| Through-hole parts | 6 Micro-Fit connectors: J1, J2, J3, J8, J9, J10 |

Before ordering:

- [ ] Fill in the "LCSC Part #" column of the BOM, or have the assembler match by manufacturer part number.
- [ ] Confirm that R105, R106, J4 and J5 are **not** in the placement file (`make_production.sh` checks this and stops if they are).
- [ ] Check rotation and polarity of ICs, diodes and the LED in the assembler's preview.
- [ ] Decide whether the assembler fits the six through-hole connectors or you do.

## 5. Parts to buy separately

| Part | Quantity per board | Note |
|---|---|---|
| WeAct STM32G474CoreBoard Long (STM32G474CEU6) | 1 | Plugs into J4/J5 |
| Würth 61302411821, socket 1×24, 2.54 mm | 2 | J4, J5, hand-soldered. Not the dual-row 61302421821 |
| Molex 43025-0400 housing | 1 | Mates with J1 |
| Molex 43025-0800 housing | 3 | Mates with J2, J9, J10 |
| Molex 43025-1000 housing | 1 | Mates with J8 |
| Molex 43025-1200 housing | 1 | Mates with J3 |
| Molex Micro-Fit 3.0 crimp terminals, series 43030 | as needed | Plus the matching crimp tool |
| PT1000 temperature sensors | up to 4 | |
| Hall current sensors, 5 V supply, SIG/REF output | up to 4 | Type still to be chosen, see `docs/PCB_LAYOUT_REMINDERS.md` |

## 6. Bring-up

- A 5 V supply on J1. The board is designed for less than 0.5 A in total.
- A soldering iron for J4/J5 (48 through-hole joints).
- A 3.3 V USB-UART adapter for the debug UART on TP44 (TX), TP45 (RX) and TP46 (GND), or the module's own USB-C port.
- An SWD programmer (for example ST-Link) for the WeAct module.
- Firmware for the STM32G474. It is not in this repository; the existing firmware targets the STM32U575 and has to be ported. The pin mapping and the conversion formulas are in `docs/DESIGN_NOTES.md`.

## 7. Copying the project for a new board

1. Copy or fork the whole repository.
2. Keep the KiCad project file name `PCB PCU`, or re-annotate after renaming: the schematic stores its reference designators under the project name.
3. Open `kicad/PCB PCU.kicad_pro` and check that no library is reported missing.
4. Run `01_drc_zones.py` and `02_schematic_vs_board.py` from `scripts/`. They should report 0 unconnected nets and 0 mismatches before you change anything.
5. After your changes, run all checks again and regenerate the manufacturing files with `sh scripts/make_production.sh`.
