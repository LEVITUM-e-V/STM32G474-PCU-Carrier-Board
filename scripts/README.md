# Check scripts

Read-only checks on the routed board. They load `kicad/PCB PCU.kicad_pcb`, refill the zones in memory and print compact results. Nothing is written back to the project.

Run them with **KiCad's bundled Python** (it provides the `pcbnew` module), with KiCad closed:

```sh
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3   # macOS
cd scripts
"$PY" 01_drc_zones.py
```

On Linux, the system `python3` works if KiCad is installed. On Windows, use `C:\Program Files\KiCad\7.0\bin\python.exe`. Set `KICAD_CLI` if `kicad-cli` is not at the macOS default path, and `PCU_BOARD` to check a different board file.

Coordinates in the output are board-relative millimetres (origin at the top-left board corner).

| Script | What it checks | Expected result |
|---|---|---|
| `01_drc_zones.py` | Refills zones, runs DRC, lists fill pieces per zone | 0 unconnected; only `lib_footprint_issues` warnings |
| `02_schematic_vs_board.py` | Exports the netlist and compares every pad net with the board | 0 mismatches |
| `03_analog_coupling.py` | Analog tracks within 2 mm of noisy tracks, or within 0.6 mm of noisy pads | Only pairs from the same measurement channel, plus MCU_T3 at J5.5/J5.6 |
| `04_layer_changes.py` | Nearest GND via per signal via, B.Cu hops crossing the island edge, power vias vs. island | No +5V via inside the island |
| `05_thermal_spokes.py` | Spoke count of each through-hole power/GND pin per plane layer | At least 2 spokes everywhere |
| `06_lengths_power.py` | High-impedance net length vs. shortest possible tree, power track widths, cap-to-via distances | No routed-long net with a short tree |
| `07_power_chains.py` | Connected +5V and +3V3_MCU track chains | |
| `08_manufacturability.py` | Short segments, vias near the edge or near holes | Empty lists |
| `09_via_in_pad.py` | Vias inside SMD pads | 0 |
| `10_acute_joints.py` | Acute track joints outside pads and vias | Prints only `done` |
| `11_gnd_pour.py` | Pour pieces with a single via, pour areas hanging on narrow necks | No large pieces |
| `near.py x y r` | Lists pads and vias within `r` mm of a point | |
| `make_production.sh` | Regenerates `production/` and the schematic PDF | |

`08_manufacturability.py` also prints "dangling track ends" and "acute joints": both lists contain false positives (ends inside pads). Use `10_acute_joints.py` and the DRC result instead.
