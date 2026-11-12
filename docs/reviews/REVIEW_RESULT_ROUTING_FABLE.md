# Routing review result: PCU G474 (v2)

Board reviewed: `Routing/PCB PCU routed v2.kicad_pcb` (copy, zones refilled). Date: 2026-11-12. No project file was changed.

## 1. Verdict

**Needs one fix before fab if the board is reflow-assembled; otherwise ready.** The routing is electrically sound: DRC is clean (0 copper errors, 0 unconnected), the schematic and board match, and no analog track runs near a noisy net. The one item that can cause assembly defects is 28 vias sitting inside SMD pads; the rest are minor clean-ups.

Analog integrity in numbers: the only analog track within 1 mm of a noisy track is U2B− next to 50V_2_NEG (0.7 mm long, 0.84 mm gap), and those belong to the same measurement channel (R4 joins them). No ADC or high-Z B.Cu hop crosses the island edge on L3.

## 2. Findings

Coordinates are board-relative (mm).

| Sev. | Sheet/Area | Problem (measured numbers) | Suggested fix |
|---|---|---|---|
| **Major** | Whole board, mostly ADC clamp rows (x 62–68) and U4/U12 | **Via-in-pad:** 28 vias (0.6/0.3, open) have their centre inside an assembled SMD pad: 18 routed hop vias and 10 test-point vias. Another 30 have the hole partly on a pad. Affected pads are 0603 R/C/L (14), SOT-23 and SOT-23-6 (8), SOIC-8 (4), SSOP-16 (2). In reflow, solder drains into the hole (and onto the bare TP on the bottom). | Move each via off its pad with a 0.5 mm stub (hole edge ≥ 0.2 mm from the pad), or order plugged/capped vias. If the board is hand-soldered, this can be accepted as is. |
| Minor | TSENSE, U7 | **Net-(U7A-+)** is routed 10.7 mm; its pad-to-pad MST is 4.1 mm. The track leaves R85.2, runs east to x = 81.3 and comes back to U7.3. This is the one high-Z net where the length is a routing detour, not a placement limit. | Reroute R85.2 → U7.3 directly (about 4.5 mm). |
| Minor | Whole board | **Return vias:** 42 of 88 signal vias have no GND via or GND pin within 3 mm (median 2.9 mm). Worst real layer changes: R33-Pad2 5.4 / 4.2 mm, 50V_1_NEG 5.0, R100-Pad1 4.7 / 3.8, U1B+ 4.7 / 4.1, MCU_CAN_RXD 4.7, T_3_SIG 4.5, U6-RXD/TXD 4.0 / 3.9 / 3.6, U4-DOUT 3.5, MCU_T2 and MCU_5V_1 3.4, C21 midpoint 3.2. All signals are slow or DC, so this costs little today. | Add one GND via within 1.5 mm of each layer change of the analog hops and of CAN TXD/RXD: about 15 vias. No need to bring the grid back. |
| Minor | F.Cu GND pour, DI/DO area | **Pour lobe on narrow necks:** a 72 mm² piece of the F.Cu pour (x 23–42, y 10–21) hangs on necks narrower than 0.6 mm and has no via of its own. Nine more lobes of 5–14 mm² are in the same state, e.g. x 65.7–76.9, y 18.9–22.9 (14 mm²) and x 73–80, y 32–35 (10 mm²). | One GND via in the 72 mm² lobe and in each lobe above 9 mm² (5 vias). |
| Minor | GND pours | **Single-via pour pieces:** 33 F.Cu and 11 B.Cu pour pieces connect to L2 through one via or pin only. Largest: F.Cu 79 mm² (x 30–42, y 23–40), 54 mm² (x 21–42, y 40–52), 27 and 26 mm² (x 69–81, y 32–46); B.Cu 30 mm² (x 43–57, y 9–14), 25 mm² (x 24–28, y 30–47). | Second via in each piece above 25 mm² (6 vias). |
| Minor | Under module, J5 | **MCU_T3** (ADC, 17.4 mm on F.Cu) passes the J5.6 pad (MCU_DI1) at 0.35 mm over 2.7 mm and the J5.5 pad (MCU_DI2) at 0.50 mm over 1.5 mm. Rule 9/11 asks for 1 mm to digital nets. DI is slow and T3 has 100 nF at the pin. | Accept, or shift the track to the other side of the pin gap if it frees up. |
| Minor | Power input, J1/D3 | **Plan widths not applied:** every +5V track is a 0.3 mm stub (rule 1: 1.0 mm for J1 → D3/C39). D3 (TVS) shares a 7.9 mm, 0.3 mm chain with U14.1/U14.3 and one via. +3.3V is 0.4 mm throughout (rule 5: 0.5 mm U14 → C41). +3V3_MCU → R10 is 0.3 mm, 27.6 mm on B.Cu (rule 6: 0.4 mm). All are adequate for < 0.5 A. | Widen the D3 pad-to-via stubs (both pads) to 1.0 mm so the TVS clamps through a short, wide path. Log the rest as deviations. |
| Minor | U3, U2, ISENSE | Smaller detours on high-Z nets: U2B− +2.2 mm, U3B+ +2.1 mm, C11-Pad1 +1.7 mm over the 45° MST. | Optional reroute. |
| Minor | DI/DO area | Two 45° acute joints: +3.3V on B.Cu at (17.5, 14.2) and Net-(C34-Pad2) on F.Cu at (24.7, 22.0). Five stubs double back on themselves (4 GND, 1 +3.3V near x 17–20). 42 segments are 0.05–0.15 mm long; none is below 0.05 mm. | Clean up the two joints and delete the doubled stubs. |

Checked and clean: no +5V via inside the island, no via within 0.5 mm of the edge or of a THT hole, every decoupling cap has its GND via within 1.25 mm, and every THT GND pin has at least 3 spokes on L2.

**Schematic vs. board:** 266 of 266 components match, with 0 pad-net mismatches. **R109 is in the schematic** (`power_supply_PCB.kicad_sch`, +5V / Net-(D1-A)), matching the board.

## 3. Deviation verdicts

- **ADC lines on B.Cu into J5:** acceptable. Every hop stays inside the island, none crosses its edge, and no noisy net is within 2 mm on B.Cu. Their TP vias are part of the via-in-pad finding.
- **50V_1_NEG and 50V_2_POS on B.Cu:** acceptable. The 0.6 mm clearance holds and the signal is DC.
- **R100, R11, R33 (op-amp outputs) on B.Cu:** acceptable. All three cross the island edge on L3 (at (70.4, 16.6), (69.8, 31.1), (68.8, 56.6)), but they are low-impedance and filtered by 4.7 kΩ / 100 nF afterwards.
- **U1B+, U5A+, U5B+ on B.Cu:** acceptable. The hops are 3.3–6.4 mm, stay outside the island and have no noisy neighbour. Add a GND via at the U1B+ vias (4.1 and 4.7 mm to the nearest today).
- **U4-DOUT with 2 vias:** acceptable. It is a ±7 V, slow line and nothing analog is near it.
- **C21 CAN midpoint with 2 vias:** acceptable. The node is AC ground through C21, not part of the differential pair.
- **+3.3V stub at U4.15, 0.3 mm:** acceptable. About 1 mA over a short stub.
- **Solid GND connection on C2, C41, C42, R101, D15:** acceptable. Each has its own fan-out via; they only take longer to hand-solder.
- **`.kicad_dru` single spoke for J4/J5 pin 24:** acceptable. The same pins have 3–4 spokes on L2.
- **29 of 40 AnalogHZ nets over 5 mm:** the placement claim holds for 28 of them (MST over 5 mm). **Fix** U7A+, which is a routing detour (see findings).

## 4. Scripts used

All run with KiCad's Python on a copy of the board. Cleaned-up versions of these scripts are in `scripts/` of this repository (renamed `01_…` to `11_…`; see `scripts/README.md`). The names below are the original working names.

| Script | What it does |
|---|---|
| `common.py` | Loads the board, board-relative coordinates, net-class lookup from `.kicad_pro` |
| `s3_drc_zones.py` | Refills zones, writes the DRC report, lists fill pieces per zone and layer |
| `s2_coupling.py`, `s2b_coupling_pads.py` | Samples analog tracks every 0.1 mm; length and minimum gap to noisy tracks, vias and pads on the same layer |
| `s6_vias.py` | Nearest GND via per signal via, B.Cu length per net, island-edge crossings, power vias vs. island |
| `s4_spokes.py` | Spoke count per THT power/GND pin on each plane layer |
| `s8_mst_power.py` | AnalogHZ routed length vs. MST, power track widths, cap-to-via distances |
| `s12_chains.py` | Connected +5V and +3V3_MCU track chains with length and pads |
| `s9_mfg.py`, `s10_vip.py` | Acute joints, short segments, via-in-pad, via-to-edge and via-to-hole distances |
| `s11_pour.py` | Pour pieces with one anchor; lobes left without a via after eroding the fill by 0.3 mm |
| `s7_netcmp.py` | `kicad-cli sch export netlist`, then schematic pins vs. board pad nets |

## 5. Re-check after the fixes (2026-11-12, board saved 15:39)

**Verdict: ready for fab.** All checks from section 4 were rerun on a fresh copy with refilled zones. DRC: 0 copper errors, 0 unconnected, 0 silkscreen warnings; only the 199 `lib_footprint_issues` remain. Schematic vs. board: still 266 of 266 components, 0 pad-net mismatches.

| Finding | Status | Measured now |
|---|---|---|
| Via-in-pad (Major) | **Fixed** | 0 vias with centre or hole on an assembled SMD pad (was 28 + 30). All 44 TP vias are clear of top pads. |
| U7A+ detour | **Fixed** | No longer above 5 mm. 28 high-Z nets are above 5 mm and all 28 have an MST above 5 mm. U7B− is 9.3 mm (MST 8.9). |
| Return vias | **Fixed, one left** | Median distance to the nearest GND via fell from 2.9 to 1.5 mm; 14 vias are above 3 mm (was 42). The only analog layer change left is **MCU_5V_1 at (68.2, 32.7): 3.6 mm**. The rest are test-point vias without a layer change, or static/slow digital lines (U4 FORCEON/FORCEOFF, MCU_DI2, MCU_DO4, DO2, +3.3V). |
| 72 mm² pour lobe on narrow necks | **Still open** | The F.Cu lobe at x 27–41, y 10–21 still has no via of its own; the 8 GND vias around it all sit outside the necks. Five smaller lobes of 5–9 mm² remain. |
| Single-via pour pieces | **Fixed** | No single-anchor piece above 17 mm² on F.Cu or 15 mm² on B.Cu (was 79 and 30 mm²). |
| D3 stub width | **Fixed** | 1.7 mm of +5V track is now 1.0 mm wide. |
| Acute joints, doubled stubs | **Fixed** | 0 acute joints in free copper; the 21 sharp angles left are all inside a same-net pad or via. 0 segments below 0.05 mm. |
| MCU_T3 next to J5.5/J5.6 | Unchanged, accepted | 0.35 mm over 2.7 mm and 0.50 mm over 1.5 mm. |
| Detours on U2B−, U3B+, C11 | Unchanged, optional | +2.2, +2.1, +1.7 mm. |

New since the fixes, both harmless:
- Net-(C50-Pad1) grew from 8.5 to 9.1 mm and U1B+ from 13.4 to 14.3 mm, because their vias moved off the pads.
- Analog-to-noisy spacing did not get worse: no analog track is within 1 mm of a noisy track or via (the closest is U2B− to 50V_2_NEG at 1.05 mm, same channel).

Optional last touches, neither blocks fab: one GND via inside the 72 mm² lobe, and one GND via next to the MCU_5V_1 via at (68.2, 32.7).

Added script: `s13_acute_where.py` (tests whether each acute joint lies inside a same-net pad or via).

## 6. Re-check after the connector change (2026-11-12, board saved 18:16)

**Verdict: still ready for fab.** All checks were rerun on a fresh copy, against the updated schematic in `Routing/`. Board now: J2/J9/J10 are 2×4, J3 is 2×6, J8 stays 2×5; 1072 segments, 308 vias (171 GND).

- **DRC:** 0 copper errors, 0 unconnected, 0 silkscreen warnings; only the 199 `lib_footprint_issues`.
- **Schematic vs. board:** 266 of 266 components, 0 pad-net mismatches. R105/R106 and J4/J5 are excluded from BOM and position files, as intended (R105/R106 unpopulated, J4/J5 hand-soldered).
- **Analog integrity:** unchanged. No analog track is within 1 mm of a noisy track or via; the closest is U2B− to 50V_2_NEG at 1.05 mm (same channel).
- **Rerouted J3 nets:** 50V_1_NEG runs 16.5 mm on B.Cu with 2 vias, both with a GND via within 2.5 mm; 50V_2_NEG is 19.0 mm on F.Cu; all 50 V tracks are 0.3 mm wide and the 0.6 mm clearance passes DRC. The 50 V and 5 V pin groups on J3 are two empty columns apart.
- **Manufacturability:** 0 vias on SMD pads, 0 acute joints in free copper, 0 segments below 0.05 mm, no via within 0.5 mm of the edge or a THT hole.
- **High-Z lengths, power widths, decoupling, return vias:** same numbers as section 5.

One thing changed for the worse, minor:

| Area | Problem | Suggested fix |
|---|---|---|
| F.Cu GND pour between U4 and J4 (x 30–42, y 23–39) | This 68.5 mm² piece is now anchored by one via only (it had at least two at 15:39, when it was 79 mm²). Inside it, a 48 mm² lobe (x 31–42, y 25–39) hangs on necks under 0.6 mm. | One GND via inside the lobe. |

Still open from section 5, both optional: one GND via in the 72 mm² lobe at x 27–41, y 10–21, and one next to the MCU_5V_1 via at (68.2, 32.7).

Not covered here: the root-folder schematic sheets are still the 2 November versions with 2×5 connectors; only the copies in `Routing/` match the board.

## 7. Three GND vias added (2026-11-12, board saved 20:31)

The three open items from sections 5 and 6 are closed. GND vias (0.6/0.3) were added at (36.6, 17.2), (38.6, 33.2) and (67.76, 31.52), board-relative mm; nothing else was changed. Details are in `ROUTING_PLAN.md` §9.

Verified on the saved board: DRC 0 copper errors and 0 unconnected, 0 schematic mismatches, 0 vias on SMD pads, no via closer than 0.5 mm to the edge or a THT hole. No pour lobe above 9 mm² is without its own via, and the largest single-anchor F.Cu piece is 17 mm². The MCU_5V_1 layer change now has a GND via 1.26 mm away.

Script: `s14_find_via_spots.py` (finds spots inside both pours), `s15_add_vias.py` (adds the vias, refills, runs DRC).
