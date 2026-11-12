# PCB PCU

Carrier board for the Levitum PCU (Power Control Unit), revision A, 2026-11. The board takes a WeAct STM32G474 module and brings out the PCU's measurement and communication interfaces: voltage, current and temperature sensing, CAN, RS-232, I²C and digital I/O.

It is a 4-layer board, 101 × 77 mm, designed in KiCad 7.0.5.

**Status:** routed and checked. DRC shows 0 errors and 0 unconnected nets, and the schematic matches the board. The board has not been manufactured yet, so it is untested in hardware.

## What is on the board

| Function | Details |
|---|---|
| MCU | WeAct STM32G474CoreBoard Long (STM32G474CEU6), plugged into two 1×24 sockets (J4, J5) |
| Supply | 5 V in on J1, TVS protection, 3.3 V LDO (AP2112K-3.3) for the on-board logic |
| Voltage sensing | 2 × 50 V and 2 × 5 V differential inputs (J3) |
| Current sensing | 4 × Hall sensor inputs, SIG/REF, bidirectional around 1.65 V (J8) |
| Temperature sensing | 4 × PT1000 inputs (J9) |
| Communication | CAN (FDCAN2), RS-232 (MAX3221), I²C (J2) |
| Digital I/O | 4 outputs, 2 inputs (J10) |
| Debug | 44 test pads on the bottom side, including a debug UART (TP44 TX, TP45 RX, TP46 GND) |

### Connectors

All board connectors are Molex Micro-Fit 3.0, right angle. Each function has its own size where possible, so cables cannot be swapped by accident.

| Ref | Size | Molex part | Function |
|---|---|---|---|
| J1 | 2×2 | 43045-0400 | 5 V supply in |
| J2 | 2×4 | 43045-0800 | CAN, RS-232, I²C |
| J3 | 2×6 | 43045-1200 | Voltage sensing, 50 V and 5 V. The only 12-pin header on the board |
| J8 | 2×5 | 43045-1000 | Hall current sensors |
| J9 | 2×4 | 43045-0800 | PT1000 temperature sensors |
| J10 | 2×4 | 43045-0800 | Digital inputs and outputs |

J2, J9 and J10 share the same 8-pin size. Label those three cables.

## Repository layout

| Folder | Contents |
|---|---|
| `kicad/` | The KiCad project: `PCB PCU.kicad_pro`, schematic (root sheet plus 8 sub-sheets), routed board, project symbol library `PCU.kicad_sym`, footprint library `PCU_Molex.pretty` |
| `production/` | Ready-to-upload manufacturing files: Gerbers and drill files (also zipped) and the placement file |
| `bom/` | Parts list as CSV (JLCPCB column layout) and as a readable Markdown table |
| `docs/` | Schematic PDF, design notes, routing plan with the full change log, layout checklist, review reports |
| `scripts/` | Read-only check scripts and the script that regenerates `production/` |

## Ordering the board

What you need to open, check and order the board is listed in [REQUIREMENTS.md](REQUIREMENTS.md). In short:

1. Upload `production/PCB_PCU-gerbers.zip` to the PCB manufacturer. Choose 4 layers and 1.6 mm thickness.
2. For assembly, upload `bom/BOM_PCU_G474.csv` and `production/PCB_PCU-pos.csv`. The "LCSC Part #" column in the BOM is still empty: fill it in, or let the assembler match the parts by manufacturer part number.
3. Check the assembler's placement preview, especially the rotation of ICs and diodes, before confirming.

### Parts that are not assembled by the manufacturer

| Parts | What happens |
|---|---|
| R105, R106 | Left empty on purpose. They are the 5 V I²C pull-ups. The 3.3 V pull-ups R107 and R108 are fitted instead. Fit **either** pair, never both. |
| J4, J5 | Soldered by hand after delivery: Würth 61302411821 (1×24 socket, 2.54 mm). |

These four parts are excluded from the placement file and from the assembled lines of the BOM.

Bought separately: the WeAct STM32G474 module, the Micro-Fit mating housings (43025 series) with crimp terminals (43030 series), and the sensors.

## Changing the design

1. Open `kicad/PCB PCU.kicad_pro` in KiCad 7.0.5.
2. Make the change in the schematic, then update the board from the schematic.
3. Run DRC, then the checks in `scripts/` (see [scripts/README.md](scripts/README.md)).
4. Run `sh scripts/make_production.sh` to regenerate the manufacturing files.

Keep the project file name `PCB PCU`. The reference designators in the schematic are stored under that project name.

## Documentation

- [docs/PCB_PCU_schematic.pdf](docs/PCB_PCU_schematic.pdf): the schematic.
- [docs/DESIGN_NOTES.md](docs/DESIGN_NOTES.md): why the circuit is the way it is, known limitations, and the conversion formulas for the firmware.
- [docs/ROUTING_PLAN.md](docs/ROUTING_PLAN.md): layer stack, routing rules per net type, and a dated log of every change to the board.
- [docs/PCB_LAYOUT_REMINDERS.md](docs/PCB_LAYOUT_REMINDERS.md): layout checklist with the open decisions.
- [docs/reviews/](docs/reviews/): review reports.

These documents were written while the board was developed in a different folder structure. Paths in them such as `Routing/…` or `../PCB PCU/` refer to that working folder, not to this repository.

## Open points

- The board has not been built or tested yet.
- The firmware still targets the previous MCU (STM32U575) and has to be ported to the STM32G474. It is not part of this repository.
- Unanswered system questions are listed in `docs/PCB_LAYOUT_REMINDERS.md`: whether the PCU is a CAN bus end, what the digital outputs drive, and which Hall sensor type is used.
