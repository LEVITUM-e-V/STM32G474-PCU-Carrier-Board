# Routing Plan: PCB PCU G474 (101 × 77 mm, 4 layers)

Every decision is made here **before** routing. The routing must follow this document. Any deviation is recorded in §9.

## 1. Basic assumptions

| Item | Decision | Reason |
|---|---|---|
| Manufacturer | JLCPCB, 4 layers, 1.6 mm, outer copper 1 oz (35 µm), inner 0.5 oz | standard, cheap |
| Highest current | **+5V ≈ 0.3 A** total (module ~0.1 A, CAN dominant ~0.07 A, 4 Hall sensors ~0.08 A, op-amps/logic < 0.03 A) | estimate from datasheets; Hall sensors unknown → reserve |
| Highest voltage | **50 V** (J3, 50V_x_POS/NEG and the divider taps) | everything else ≤ 15 V (RS-232 ±7 V) |
| Fastest signal | CAN 1 Mbps (edges ~50 ns), MCU GPIO edges | no impedance control needed at these lengths (< 5 cm) |
| Most sensitive | op-amp inputs, divider taps, TSENSE node, VREF_1V65, MCU_* ADC lines | high impedance (10–200 kΩ), µV/mV relevant |

Capacity check (IPC-2221, outer layer 1 oz, 10 °C rise): 0.2 mm ≈ 0.6 A, 0.5 mm ≈ 1.2 A, 1.0 mm ≈ 2 A. Every width below therefore has at least 2× margin.

## 2. Layer stack: what each layer is for

| Layer | Use | Rules |
|---|---|---|
| **L1 F.Cu** (top) | All components. **Primary routing layer**. GND pour in all free areas. | All analog and HV50 nets **only here**. |
| **L2 In1.Cu "GND"** | **Solid GND plane, the whole board.** | **No traces, no splits, never.** It is the return path directly under L1. |
| **L3 In2.Cu "PWR"** | Power planes: **+5V** (whole board, lowest priority) and the **+3V3_MCU** island (under the module). | No signal traces. |
| **L4 B.Cu** (bottom) | Test-point pads. **Secondary routing**: only digital signals that must cross. GND pour in all free areas. | No analog high-Z nets, no HV50. |

Plane outlines (L3, board coordinates measured from the top-left corner):
- **+3V3_MCU island:** from the module sockets to the clamp strip right of J5, **x 44.3 … 70.4, y 3 … 57** (changed 2026-11-04: the 12 BAT54S clamps moved right of J5, and their +3V3_MCU vias must land in the island). There are no +5V vias in this area: D17 now sits left of J4, and U9 sits below y 57.
- **+5V:** everything else.
- Gap between the plane pieces: 0.5 mm.
- **No +3.3V plane:** the DO/DI pull-ups and the I²C 5 V option (+5V) sit right between the 3.3 V chips, so a +3.3V island would cut them off from +5V. +3.3V is a **routed net** instead (#5). It carries < 0.1 A.

## 3. Via types

| Type | Size (Ø pad / drill) | Used for |
|---|---|---|
| Signal via | **0.6 / 0.3 mm** | all signal layer changes, GND fan-out of SMD pads, test-point connections |
| Power via | **0.8 / 0.4 mm** | +5V, +3.3V, +3V3_MCU plane connections at decoupling caps and regulators |
| Stitching via (GND) | **0.6 / 0.3 mm** | connect the L1/L4 GND pours to L2. Along the board edge every **5 mm**, plus a grid every **≈ 6 mm** in free areas, plus **1 next to every GND pad** |

No blind/buried vias (cost).

## 4. Decisions per connection type

| # | Connection (nets) | Width | Layer | Vias | Special rules |
|---|---|---|---|---|---|
| 1 | **J1 → +5V input** (J1 pins 2/4 → D3, C39, C40, C54, C55) | **1.0 mm** | L1 | **3 × power via** at C39/C40 into the L3 +5V plane | D3 (TVS) directly at J1, before the caps |
| 2 | **+5V to loads** (op-amp pin 8, U14 VIN/EN, pull-ups, TSENSE R84/R86-type) | 0.3 mm stub | L1 → L3 | 1 power via **at the decoupling cap pad**, IC pin → cap ≤ 2 mm | each op-amp: pin 8 → its 100 nF → via |
| 3 | **+5V to the Hall sensors** (J8 pin 5) | – | – | – | J8 pin 5 is a through-hole pin: it connects to the L3 +5V plane directly (thermal relief). No extra trace. The same applies to every THT pin on GND/+5V/+3V3_MCU (J1, J4, J5, J8, J9, J10, H1–H5). |
| 4 | **+5V → D17 → module 5V** (J4 pins 3/4) | **0.5 mm** | L1 | power via at the D17 anode | D17 within 5 mm of J4 pin 3 |
| 5 | **+3.3V** (U14 VOUT → C41/C42/C43 → digital ICs, pull-ups) | **0.5 mm** U14→C41; **0.4 mm** for the rest | L1/L4 as a routed tree | signal/power vias only where the route changes layer | every IC VCC pin first to its decoupling cap, then the cap into the tree |
| 6 | **+3V3_MCU** (J5 pins 3/4, C59/C60, 12 × BAT54S pin 2, R10) | 0.3 mm stubs; **0.4 mm** to R10 | L1 → L3 island; to R10 on **L4** | 1 power via per BAT54S pin 2 and at C59 | C59/C60 at J5 pins 3/4 |
| 7 | **GND** | 0.3 mm stubs | pours L1/L4 + L2 plane | 1 signal via **≤ 1 mm** from every SMD GND pad | THT GND pads connect directly to all planes (thermal relief) |
| 8 | **HV50** (50V_1/2_POS/NEG, divider taps R17–R9 / R81–R21) | **0.3 mm** | **L1 only** | **none**, except the test-point via (TP3–TP6), which keeps the 0.6 mm clearance | **0.6 mm clearance** to everything; shortest path J3 → resistor; no other net between them |
| 9 | **Analog high-Z nodes** (op-amp IN+/IN−, VSENSE taps, TSENSE node C25-type, ISENSE input nodes after the ferrites) | **0.2 mm** | **L1 only** | **none** (except TP stub vias at the end of a branch) | as short as possible (target < 5 mm); **no digital net running parallel within 1 mm**; GND pour around them |
| 10 | **Op-amp outputs → 4.7 kΩ** (under the module) | **0.25 mm** | **L1**, one track through the gap between two J5 pins | fallback: 2 signal vias + L4 if a gap is blocked | low impedance, so length is uncritical |
| 11 | **MCU_* ADC lines** (4.7 kΩ → 100 nF → BAT54S → J5 pin) | **0.2 mm** | L1 | TP stub via only | clamp and 100 nF **at the J5 pin**; ≤ 3 mm |
| 12 | **VREF_1V65** (U9 pin 1 → R26, R31, R36, R41) | **0.3 mm** | L1 preferred, L4 allowed | signal vias allowed | **star** from U9 (no daisy chain); away from digital nets |
| 13 | **CAN_H / CAN_L** (J2 → D4 → R53/R54 → U6) | **0.25 mm diff pair, 0.25 mm gap** | **L1 only** | **none** | pair routed together; length mismatch < 1 mm; termination R79/R80/C21 as stubs ≤ 3 mm |
| 14 | **CAN TXD/RXD** (J4 → R51/R52 → U6) | 0.2 mm | L1/L4 | allowed | |
| 15 | **RS-232 line side** (J2 → R43/R44 → U4 DOUT/RIN) | **0.25 mm** | L1 | none | ±7 V levels; 0.25 mm clearance |
| 16 | **MAX3221 charge pump** (C1±, C2±, V+, V− with C8, C9, C18, C19) | **0.3 mm** | **L1 only** | **none** | switching nodes: **≤ 3 mm**, caps directly at the pins |
| 17 | **MCU digital signals** (DO1–4, DI1–2, RS-232 logic, EN/FORCEON/FORCEOFF/INVALID, I²C, debug) | **0.2 mm** | L1/L4 | allowed | I²C SDA/SCL routed side by side; never through the analog half (right of J5). **Exception:** MCU_DI1/DI2 end at J5 pins 6/5, so they must cross under the module. They do that on **L4**, shielded from the L1 ADC lines by the L2/L3 planes. |
| 18 | **DO outputs to J10** (DO1–4 after U10/U11) | **0.3 mm** | L1 | allowed | up to 24 mA |
| 19 | **DI inputs from J10** (J10 → E13/E14 → R69/R70) | 0.25 mm | L1 | allowed | |
| 20 | **Test points** (all TPs on L4) | width of their net | via in the TP pad | 1 signal via per TP, **in the centre of the TP pad** | TPs are bare pads (nothing assembled), so they are **moved under their net** (≤ 4 mm from a pad of the net). The L1 connection then follows the rules of the net (e.g. ≤ 5 mm for high-Z). |
| 21 | **I²C pull-ups, MAX3221 pull resistors** | 0.2 mm | L1/L4 | allowed | |

## 5. Pours (copper zones)

| Zone | Layer | Net | Clearance | Connection | Priority |
|---|---|---|---|---|---|
| GND plane | L2 | GND | 0.3 mm (HV50 0.6 mm automatic) | thermal relief THT, solid SMD | 0 |
| +5V | L3 | +5V | 0.3 mm | thermal relief | 0 |
| +3V3_MCU island | L3 | +3V3_MCU | 0.3 mm | thermal relief | 1 |
| GND top | L1 | GND | 0.3 mm | thermal relief | 0 |
| GND bottom | L4 | GND | 0.3 mm | thermal relief | 0 |

Minimum zone width 0.25 mm; remove islands that have no connection.

## 6. Order of work

1. **Zones** (§5), so the planes exist before routing.
2. **Test points:** move the TPs under their nets, with a via in the TP pad (§4 #20).
3. **Critical signal nets, all on L1, in this order:** HV50 (#8) → analog high-Z (#9) → MCU_* ADC lines (#11) → op-amp outputs (#10) → VREF (#12) → CAN pair (#13) → RS-232 line side (#15) → charge pump (#16). They come **before** the power vias so that no via takes their space next to the op-amp pins. Tracks are **locked** after routing.
4. **Power:**
   - GND via next to every SMD GND pad (#7).
   - Power via next to every SMD pad on +5V/+3V3_MCU, inside the matching L3 plane area (#2, #6). Exceptions: IC supply pins, the J1 input group and R10.
   - J1 input group with 3 vias at C39/C40 (#1).
   - D17 → J4 module 5V (#4).
   - IC supply pin → decoupling cap (#2).
   - +3V3_MCU → R10 on L4 (#6).
   - +3.3V tree (#5).
5. **Everything else** (#14, #17–#19, #21): the same router, now allowed to use **L1 and L4 with vias**, longest nets first.

   **Router (decided):** my own grid router. It uses a 0.05 mm grid and finds the shortest path, keeping a distance of clearance + half the track width from other copper. It applies the width, clearance and layers per net exactly as in §4, with 0/45/90° segments only. I'm not using Freerouting as the main router, because it can't hold per-net layer limits (L1 only for analog/HV) or per-net widths that differ from the net class. Freerouting stays a **fallback**, only if a net can't be routed; any use of it is logged in §9.
6. **Stitching vias** (§3), then fill all zones.
7. **DRC** (KiCad Python) until **0 errors, 0 unconnected**. Then render top, bottom and inner layers for review.

## 7. Not done in this step

- Silkscreen cleanup (reference positions, labels "50 V!", connector functions).
- Changes to the placement beyond small turns/shifts (≤ 2 mm) that routing needs. Larger ones are asked about first.
- Changes to the schematic.

## 8. Acceptance criteria

- DRC: 0 errors; 0 unconnected items.
- Every rule in §4 holds (spot check per row, recorded in §9).
- L2 has no tracks and no slots.
- No track of the analog high-Z or HV50 class is on L4 or L3.

## 9. Deviations / results log

**Attempt 1 (2026-11-02), own grid router, NOT written into the project (scratch copy only):**

- **Done:** zones, 44 test points moved, 2153 track segments, 508 vias (130 fan-out, 251 stitching).
- **26 connections failed:** 10 analog nets on L1, MCU_T3, CAN_L, RS-232 DOUT, 5 fan-out vias, D17, U4/U9 supply, the +3.3V tree and 4 RS-232 logic nets.
- **The plan was not met:**
  - 9 of the 41 high-Z nets are longer than 5 mm (up to 7.9 mm), violating #9.
  - Op-amp output Net-(R93-Pad2) takes a 200 mm detour.
  - 50V_1_NEG is 68 mm long instead of the "shortest path" required by #8.
- **DRC:** 30 clearance errors, 27 hole-to-hole, 96 unconnected.
- **Causes:**
  1. With "L1 only" for all analog nets, several channels can't be routed without crossings at the current placement, so the router detours around whole blocks.
  2. The router has no rip-up and reroute, so early nets block later ones.
  3. Bugs in my router: oval THT pads treated as rectangles, and no hole-to-hole check between vias of the same net.
- **Clarification found:** #9 only covers nodes **after** the ferrites/input resistors. The connector-side nets (ISENSE_x_SIG/REF, 5V_x_POS/NEG, T_x_SIG) are low-impedance and are not covered by #9. The router wrongly limited them to L1.

**Placement v3 (2026-11-04), written into the project. Changes that affect this plan:**
- **Op-amps:** each sits next to its connector, with the channels in pin order: U8/U7 at J9, U2/U3 at J3, U5/U1 at J8. Outputs face J5.
- **Long traces:** the long runs are now the low-impedance op-amp outputs (#10) to the clamp strip. They no longer pass between the J5 pins.
- **Clamp groups** (BAT54S + 4.7k + 100 nF): in a strip right of J5, one row per J5 pin (8–19), in pin order. The #11 ADC lines therefore run from the strip to J5 directly (≤ ~7 mm).
- **D17** sits left of J4 pins 3/4 (3.8 mm); **C59/C60** sit at J5 pins 3/4 (3.4 mm).
- **Expected crossings** between op-amp outputs and clamp rows (T4, and 50V vs 5V order) are allowed on L4 (#10 fallback). So are the ISENSE input crossings on the connector-side nets (§9 clarification above).

**Zones + U4 (2026-11-04), written into the project:**
- **The 5 zones from §5 now exist and are filled:**
  - GND plane on L2;
  - +5V plane on L3;
  - +3V3_MCU island on L3 (x 44.3–70.4, y 3–57);
  - GND pours on L1 and L4.

  All with 0.3 mm clearance, 0.25 mm minimum width, thermal reliefs, islands removed.
- **U4 (MAX3221, SSOP-16):** footprint clearance override **0.15 mm**. Its pads are only 0.15 mm apart (JLCPCB minimum 0.1 mm). That removes the 14 clearance errors. Other copper near U4 still needs 0.2 mm, because KiCad uses the larger of the two clearances.
- **DRC afterwards:**
  - 0 clearance errors;
  - 362 unconnected (was 465; the THT pins now connect through the planes; the rest is unrouted);
  - 5 "starved thermal" warnings on GND pads in the DO/DI area (C28, C30, U10, U11, U12). These disappear with their GND vias (§4 #7).

**Routing prep (2026-11-04), written into the project:**
- **Net classes = the §4 decisions** (in the project file, assigned by name patterns, all 197 nets checked):

  | Class | Width | Clearance | Nets |
  |---|---|---|---|
  | GND | 0.3 | 0.2 | GND |
  | Power | 0.3 (vias 0.8/0.4) | 0.2 | +5V, +3V3_MCU |
  | P3V3 | 0.4 | 0.2 | +3.3V |
  | D17_5V | 0.5 | 0.2 | Net-(D17-K) |
  | HV50 | 0.3 | 0.6 | 50V_*, divider taps |
  | AnalogHZ | 0.2 | 0.2 | 40 high-Z nodes |
  | AnalogIn | 0.2 | 0.2 | 16 connector-side analog nets |
  | OpOut | 0.25 | 0.2 | 12 op-amp outputs |
  | ADC | 0.2 | 0.2 | 12 MCU_* ADC lines |
  | VREF | 0.3 | 0.2 | VREF_1V65 |
  | CAN | 0.25 (pair gap 0.25) | 0.2 | CAN nets |
  | RS232L | 0.25 | 0.25 | RS-232 line side |
  | CPump | 0.3 | 0.2 | charge pump |
  | DO | 0.3 | 0.2 | DO1–4 |
  | DI | 0.25 | 0.2 | DI1–2 and nodes |
  | Default | 0.2 | 0.2 | everything else |

- **Decisions changed by this:**
  - #1 J1 input: J1 pins 2/4 are THT and connect straight into the L3 +5V plane, so no 1.0 mm traces are needed. Power stubs are 0.3 mm.
  - #5: U14 → C41 is 0.4 mm instead of 0.5 mm. One class for +3.3V; the current is < 0.1 A.
  - Layer limits ("L1 only" for HV50/AnalogHZ/ADC/OpOut/CAN/CPump) **can't be stored in a KiCad net class**. They are checked after routing and fixed by hand where needed.
- **Old leftover tracks removed** (U14 → C41–43, debug stubs).
- **All 44 test points moved under their nets** (bottom side, ≤ 4 mm from a pad of the net, ≥ 2 mm apart, clear of THT pins).
- **DRC:** 0 errors; 374 unconnected (= the routing still to do); 5 starved thermals (see above).
- **Router:** Freerouting 1.9.0 (Java 17), as the planned fallback, because my own router (attempt 1) wasn't good enough. Its result is checked against §4 afterwards.


### Routing attempt 2 (Freerouting + script post-processing), 2026-11-04

**Result:** `Routing/PCB PCU routed v2.kicad_pcb` (+ `.kicad_pro`, `.kicad_dru`, `DRC routed v2.txt`). **Not yet merged into `PCB PCU.kicad_pcb`.** `Routing/PCB PCU routed v1.kicad_pcb` is the earlier version (same DRC status, longer routes).

- **Steps:**
  1. Locked pre-routes: a 0.6/0.3 via in every TP (44) and fan-out stub + via for every SMD pad on GND/+5V/+3V3_MCU (133). No +5V via in the island.
  2. Freerouting 1.9.0 (3 h). The L1-only classes were restricted to F.Cu in the DSN. It left 18 connections open.
  3. Gap-fill with a grid router (scripts). The U4 nets were ripped up and rerouted in a better order.
  4. Stitching: 194 GND vias 0.6/0.3, along the edge every 5 mm plus a ~6 mm grid. Placed only where both the F.Cu and B.Cu GND pours are present.
  5. Length-improvement pass: each net with a detour > 2 mm vs. its minimum spanning tree was ripped up and rerouted, and kept only if shorter. 37 nets improved, for example MCU_ISENSE_3 101 → 11.6 mm, MCU_T1 72 → 13.3 mm, U1B+ 30.5 → 13.4 mm, R11-Pad1 62 → 13 mm.
- **DRC (v2):** **0 copper errors, 0 unconnected.** What remains is 199 `lib_footprint_issues` + 248 silkscreen warnings, all from before routing.
- **Totals:** 1094 track segments; 420 vias (177 locked TP/fan-out, 243 routed/stitching).
- **Deviations from the plan (to be judged in the review):**

  | Net(s) | Deviation | Reason |
  |---|---|---|
  | MCU_5V_1/5V_2/50V_1/50V_2/ISENSE_2/3/4/T1/T2/T4 (ADC) | B.Cu hop of 5–12 mm, usually through the TP via, sometimes +1 via | The clamp rows (D/C/R every 3.6 mm with GND/+3V3_MCU fan-out on the J5 side) leave no F.Cu path to J5 |
  | 50V_1_NEG (14.5 mm on B.Cu), 50V_2_POS | HV50 on B.Cu | J3 inner-row gap 1.5 mm = 0.6 + 0.3 + 0.6, so there is no path to the outer row on F.Cu; 0.6 mm clearance is kept on B.Cu |
  | R100-Pad1, R11-Pad1, R33-Pad2 (OpOut) | B.Cu with 2 vias (9–21 mm) | Long op-amp output runs across the op-amp column; low impedance |
  | U1B+, U5A+, U5B+ (AnalogHZ) | B.Cu with 2 vias (3–6 mm on B.Cu) | Shorter than the F.Cu-only detour (e.g. U1B+ 30.5 → 13.4 mm) |
  | U4-DOUT (RS232L) | 2 vias, 7.9 mm on B.Cu | DOUT (right pin row) has to cross RIN and the charge-pump side to reach R43 |
  | Net-(C21-Pad1) (CAN split-termination midpoint) | 2 vias | F.Cu-only would be 26 mm |
  | +3.3V at U4.15 | 0.3 mm instead of 0.4 mm (short stub) | 0.65 mm pitch; MAX3221 draws about 1 mA |
  | C2.2, C41.2, C42.2, R101.1, D15.1 (GND) | Solid zone connection instead of thermal | Only 1 spoke was possible; each has its own fan-out via |
  | J4/J5 pin 24 (GND, THT) | `.kicad_dru` rule: 1 spoke allowed | Also tied to L2 + bottom pour through the hole |
- **Still open:** 29 of 40 high-Z nets are > 5 mm (max 15.8 mm, U3A−). For most, the MST alone is already > 5 mm (e.g. U3A− MST 15.4 mm), so this is a **placement** limit, not a routing one.

### v2 update, 2026-11-12: R109 + zones rebuilt

- **R109** (560 Ω, D1 LED resistor; added by hand on the board) is routed:
  - pad 2 → D1.2: 0.2 mm on F.Cu, 4.4 mm;
  - pad 1 → a 0.3 mm stub and a new 0.8/0.4 via into the L3 +5V plane (outside the island).
- **Zones:** the fill was stale, so the F.Cu GND pour ran under the new R109 pads (a short to GND and a mask bridge). All 5 zones were deleted and recreated with identical outlines, priorities and settings, then refilled.
- **13 extra GND vias (0.6/0.3)** go in pour fragments that were enclosed by tracks and therefore deleted by island removal. These include the 54 mm² wedge between U4 and J5, plus fragments near U3, U5 and J4. Smaller fragments where no via fits stay removed.
- **DRC:** 0 copper errors, 0 unconnected. What remains are the 199 library + 248 silkscreen warnings from before routing.
- Backup: `Routing/PCB PCU routed v2-backups/before R109 routing 2026-11-12/`.

### v2 update, 2026-11-12: stitching grid thinned (middle ground)

- **Rule changed vs. §3:** the interior stitching grid is no longer ~6 mm. An interior grid via is removed when another GND via (fan-out, edge, island or another grid via) lies within 5 mm, so spacing is now ~5–10 mm. The fan-out vias (1 per SMD GND pad), the edge row (every 5 mm) and the 13 island vias are kept unchanged.
- **Removed 76 vias** (78 removed, 2 put back): the vias at (118.44, 82.83) under U4 and (119.49, 58.96) were the only anchors of 3 pour pockets.
- **GND vias:** 299 → 223. **GND pour area unchanged** (F.Cu 5066 mm², B.Cu 6254 mm²); no pour piece was lost.
- **DRC:** 0 copper errors, 0 unconnected.
- Backup: `Routing/PCB PCU routed v2-backups/before stitching thin-out 2026-11-12/`.

### v2 update, 2026-11-12: stitching reduced further

- **Interior grid removed:** a via was removed unless it is the last connection of a pour piece to L2. 53 removed; 17 kept as sole anchors, including the island vias.
- **Edge row:** every ~10 mm instead of every 5 mm. 34 removed and 28 kept (a few extra are kept as anchors).
- **Fan-out vias unchanged:** 91, one per SMD GND pad.
- **GND vias:** 223 → 136 (originally 299). The GND pour area is unchanged (F.Cu 5066 mm², B.Cu 6254 mm²), so no pour piece was lost.
- **DRC:** 0 copper errors, 0 unconnected.
- Backup: `Routing/PCB PCU routed v2-backups/before stitching thin-out 2 2026-11-12/`.

### v2 update, 2026-11-12: fixes from the review (`REVIEW_RESULT_ROUTING_FABLE.md`)

- **Via-in-pad (Major): fixed, 64 → 0.** No via hole is closer than 0.2 mm to an assembled SMD pad any more.
  - **Causes:**
    - Test-point vias sat under a top pad of the same net (the TP was placed under its net).
    - Routed hop vias were allowed on same-net pads.
  - **Fixes:**
    - 60 vias moved 0.2–1.8 mm, each with its test point, and reconnected by a stub from the pad. B.Cu tracks that used to end inside the TP pad were extended to the moved via.
    - DO1, DO2, U4-EN, U4-FORCEOFF and U5B+ were rerouted with a no-via-in-pad rule. U4-EN grew from 11.9 to 18.6 mm (a static enable line).
    - TP39 was moved to clear a courtyard overlap with TP40.
- **U7A+ (high-Z):** U7A+ and U7B− were ripped up and rerouted together. U7A+ went from 10.7 to **3.0 mm**; U7B− stayed at 9.1 → 9.3 mm.
- **Return vias:** 29 GND vias were added within 0.9–1.7 mm of every real layer change on analog/ADC/op-amp-output/50 V/CAN/RS-232 nets.
- **GND pour:**
  - 1 second via was added in a 30 mm² single-anchor piece (B.Cu).
  - 1 via was added in a 10 mm² lobe on a narrow neck.
  - 2 vias were added in new enclosed pockets (16 and 4 mm²).
  - The other pieces the review listed were already anchored by the new return vias.
- **D3 (TVS):** the +5V pad-to-via stub is now **1.0 mm**. The GND stub is 0.8 mm (1.0 mm doesn't fit next to C39).
- **Clean-up:**
  - 82 redundant segments were removed: duplicates, segments covered by another segment of the same net, and segments lying inside their own pad. GND in-pad segments were kept because they count for the thermal spokes.
  - 1 acute free joint (DO4) was straightened.
  - There are **0 acute joints in free copper**. The remaining sharp angles (29) are at pads or vias, where the pad or via copper fills the wedge.
- **Totals:**
  - Vias: 271 → 305, of which GND 136 → 169.
  - Segments: 1097 → about 1072.
  - GND pour: F.Cu 5045 mm² (−21 mm², because of the new stubs and the wider D3 tracks), B.Cu 6252 mm².
- **DRC:** 0 copper errors and 0 unconnected. Only the 199 library + 251 silkscreen warnings from before remain.
- Backup: `Routing/PCB PCU routed v2-backups/before review fixes 2026-11-12/`.
- **Not done:**
  - MCU_T3 next to the J5.5/J5.6 DI pads (0.35–0.5 mm). DI is slow and T3 has 100 nF at the pin, so the review accepted it.
  - The small detours on U2B−, U3B+ and C11 (+1.7–2.2 mm). These are optional.

### v2 update, 2026-11-12: silkscreen cleanup

- **Reference designators re-placed by script.**
  - The 196 that collided with pad openings, part outlines, other references or the board edge were moved to the nearest free spot within 3 mm of their part, at full size (1.0 mm / 0.15 mm, the board minimum). References that were already clear stayed in place.
  - **30 references hidden on the silkscreen** because there is no free spot. They remain on the Fab layer and in the assembly drawing: C10, C12, C13, C15, C24, C33, C45, C47, C51, D9–D14, D16, E13, R4, R30, R34, R42, R44, R59, R60, R69, R70, R79, R84, R91, U12. Most are in the dense clamp rows next to J5.
  - 11 visible references sit 1.5–2.9 mm from their part: C16, R40, R38, C27, R13, C48, U7, R90, C30, R73 and R6.
- **Silkscreen warnings:** 251 → 1. The remaining one is a test point's own outline circle on B.Silkscreen at (178.7, 106.2), touching a nearby mask opening. It's footprint graphics and the fab clips it.
- No copper changed. **DRC:** 0 errors, 0 unconnected.
- Backup: `Routing/PCB PCU routed v2-backups/before silkscreen cleanup 2026-11-12/`.

### v2 update, 2026-11-12: last silkscreen warning fixed

- TP27 (ISENSE_2_SIG, bottom side) was moved 0.12 mm away from J8 pin 9, together with its via. Its 3 tracks were re-pointed.
- Before the move, the silk circle (outer radius 0.76 mm) reached into J8.9's mask opening (radius 0.75 mm): the centres were 1.48 mm apart, and 1.60 mm now.
- **DRC: 0 violations, 0 unconnected** (the library warnings only appear when the scripts run).
- Backup: `Routing/PCB PCU routed v2-backups/before TP27 fix 2026-11-12/`.

### v2 update, 2026-11-12: J2, J3, J9, J10 changed to 2×4 Micro-Fit (43045-0800), 3D models

- **Schematic** (`Routing/connectors_PCU.kicad_sch`):
  - Conn_02x05_Top_Bottom → Conn_02x04_Top_Bottom, value 430450800, footprint `Molex_Micro-Fit_3.0_43045-0800_2x04_P3.00mm_Horizontal`.
  - The unused row and its no-connect flags were removed. Checked with a netlist export: every signal is on the same net as before, and no other part changed.
- **New pinout:**
  - **J9:** 1–4 GND, 5 T_4_SIG, 6 T_3_SIG, 7 T_2_SIG, 8 T_1_SIG.
  - **J10:** 1 DO2, 2 DI1, 3 DO3, 4 GND, 5 DO1, 6 DI2, 7 DO4, 8 GND.
  - **J2:** 1 CAN_H, 2 RS232_DOUT, 3 GND, 4 I2C_SDA, 5 CAN_L, 6 RS232_RIN, 7 GND, 8 I2C_SCL.
  - **J3:** 1 50V_2_NEG, 2 50V_1_NEG, 3 5V_2_NEG, 4 5V_1_NEG, 5 50V_2_POS, 6 50V_1_POS, 7 5V_2_POS, 8 5V_1_POS.
  - **Cables:** the mating plug is now 43025-0800 (8 circuits). On J9/J10 the cable pin numbers of the second row shift (old 6–9 → new 5–8). On J2/J3 the pins after the removed row shift as well.
  - **J3:** the empty row between the 50 V and the 5 V pins is gone. The 50V_1 ↔ 5V_2 pad gap is now 1.5 mm (rule 0.6 mm, DRC passes).
- **PCB:**
  - The footprints were swapped with pin 1 at the same place and orientation, and the schematic link was kept.
  - J9/J10 routing is unchanged.
  - On J2/J3, 8 nets were rerouted on F.Cu: 5V_x_POS/NEG, RS232_DOUT/RIN, I2C_SDA/SCL (I2C is about 2 mm shorter now).
  - 2 GND vias were added in new pour pockets.
- **3D models:** the Molex STEP files are in `Routing/3d Models/` (`${KIPRJMOD}/3d Models/...`).
  - 430450400 (J1): offset (1.5, 8.92, 0).
  - 430451000 (J8): offset (6, 8.92, 0).
  - 430450800 (J2, J3, J9, J10): offset (4.5, 3.97, 3.43).
  - All three use rotation (−90, 0, 180).
  - Checked with a KiCad STEP export: every model pin lands on its pad, and the housings sit on the board surface.
- **OPEN, check before fab:** in the Molex 430450800 STEP the two PCB pegs are 1.65 mm / 7.35 mm from pin 1 along the row, i.e. 5.7 mm apart. The KiCad footprint drills the peg holes at 2.16 / 6.86 mm, 4.7 mm apart. That's 0.51 mm off on each side. For 2×5 and 2×2, model and footprint agree. Check the Molex drawing for 43045-0800 (PCB layout); if 5.7 mm is right, move the two NPTH holes on J2, J3, J9 and J10.
- **DRC:** 0 errors, 0 unconnected, 0 silkscreen warnings.
- Backup: `Routing/PCB PCU routed v2-backups/before 2x4 connectors 2026-11-12/` (all schematic sheets, board, .kicad_pro, .kicad_dru).

### v2 update, 2026-11-12: peg question settled, project Molex library

- **Molex drawing SD-43045-001 rev H1** (`Routing/3d Models/430450800_sd.pdf`), 8 circuits:
  - peg spacing C = **4.70 mm**;
  - peg to circuit 1 = **2.15 ±0.05 mm**;
  - peg row to pin row = 4.32 mm;
  - holes Ø3.00 / Ø1.02 mm.

  **So the KiCad 2×4 footprint is correct.** The 2020 STEP `430450800.stp` has its pegs 5.7 mm apart; this is a visual difference only, and the holes stay as they are.
- **Note 7:** the header must sit ≤ 10.16 mm from the board edge. Ours is 9.42 mm (pin row 1 to edge), OK.
- **DRC `lib_footprint_mismatch` (6 warnings):** caused by the custom 3D models on the board copies.
  - Fixed with the project library `Routing/PCU_Molex.pretty` (0400, 0800 and 1000 footprints, each with its Molex model) and `Routing/fp-lib-table`.
  - The board footprints J1, J2, J3, J8, J9 and J10 and the schematic footprint fields now point to `PCU_Molex:...`.
  - Checked with `FootprintNeedsUpdate`: all 6 match the library.
- Backup: `Routing/PCB PCU routed v2-backups/before project Molex library 2026-11-12/`.

### v2 update, 2026-11-12: new 2×4 3D model

- `Routing/3d Models/430450800.stp` is now the TraceParts/Molex model (8 circuits). The 2020 file with the wrong peg spacing was kept as `430450800_2020_old.stp`.
- The new model's pegs are 4.70 mm apart and match the drawing and the footprint holes.
- New settings: offset (4.5, 8.92, 0), rotation (−90, 0, 180), the same convention as the 2×2 and 2×5 models.
  - Checked with a KiCad STEP export: pins on the pads, pegs 2.15 / 6.85 mm from pin 1 (holes at 2.16 / 6.86), housing on the board.
- The library `PCU_Molex` and J2, J3, J9 and J10 were updated identically (parity checked: no footprint needs an update).
- **DRC:** 0 errors, 0 unconnected.
- Backup: `Routing/PCB PCU routed v2-backups/before new 0800 model 2026-11-12/`.

### v2 update, 2026-11-12: fixes from the full review (`REVIEW_RESULT_FULL_FABLE.md`)

- **Finding 1 (critical, mis-mating): J3 → 2×6 Micro-Fit 43045-1200.** It is the only 12-pin header, so no other cable fits.
  - **Pinout:**
    - 1 50V_2_NEG, 2 50V_1_NEG, 7 50V_2_POS, 8 50V_1_POS;
    - 5 5V_2_NEG, 6 5V_1_NEG, 11 5V_2_POS, 12 5V_1_POS;
    - 3, 4, 9, 10 are not connected. They leave a gap of 7.5 mm (two empty columns) between the 50 V and the 5 V group.
  - **Schematic:** symbol Conn_02x06_Top_Bottom. Checked with a netlist export: same nets, no other part changed.
  - **Board:** pin 1 moved to y 72.56 so the part fits between J9 and J8 (0.87 mm courtyard gap on each side). The 8 J3 nets were rerouted; 50V_1_NEG still runs on B.Cu (+1 via).
  - **Library:** the footprint was added to `PCU_Molex` (no 3D model yet; it needs the 430451200 STEP).
- **Finding 2: silkscreen labels.**
  - Top: "50V!" next to J3, "COM" (J2), "J1 5V IN", "USB" at the module's USB end, "LEVITUM PCU G474 REV A 2026-11".
  - Bottom (no room on top): "J3 VSENSE !50V!", "J2 CAN RS232 I2C", "J9 TEMP PT1000", "J10 DI/DO", "J8 ISENSE".
- **Finding 3: BOM** (`BOM/BOM_PCU_G474.csv` and `.md`): J8 43045-1000; J2, J9, J10 43045-0800; J3 43045-1200. The LCSC column is still empty.
- **Finding 5: PCBA.** R105, R106 (DNP), J4 and J5 (hand-soldered by the owner) are now "exclude from BOM + position files". KiCad 7.0.5 has no separate DNP attribute.
- **ERC:** the 30 warnings ("library 'PCU' not configured") are fixed with `Routing/sym-lib-table` → `${KIPRJMOD}/../PCU.kicad_sym`.
- **Owner answers:** Q1, if the fuel cell controller is a logic-level UART: use USART3 RX inversion (RXINV) in firmware and don't wire J2 pin 2 (RS232_DOUT ±5.5 V). Q2–Q4 are unknown: keep R79/R80 fitted and measure 60 Ω vs. 40 Ω on the finished bus, choose Hall sensors with ±1.03 V (SIG − REF) and a 5 V supply, and treat DO1–4 as logic-level only.
- **DRC:** 0 errors, 0 unconnected, 0 silkscreen warnings.
- Backup: `Routing/PCB PCU routed v2-backups/before J3 2x6 + labels 2026-11-12/` (all schematic sheets, board, project files, PCU_Molex, BOM).

### v2 update, 2026-11-12: J3 3D model

- `Routing/3d Models/430451200.stp` (Molex/TraceParts, 12 circuits) is assigned to J3 and to the `PCU_Molex` footprint 43045-1200, with offset (7.5, 8.92, 0) and rotation (−90, 0, 180).
- Checked with a KiCad STEP export: pins on the pads, pegs 2.15 / 12.85 mm from pin 1 (holes at 2.16 / 12.86, drawing C = 10.70 mm).
- Library parity is OK. **DRC:** 0 errors, 0 unconnected.

### v2 update, 2026-11-12: 3 GND vias from the re-check (`REVIEW_RESULT_ROUTING_FABLE.md` §6)

- **3 GND vias (0.6/0.3) added**, each with its copper fully inside the F.Cu and B.Cu GND pours (board-relative mm):
  - (36.6, 17.2): inside the 72 mm² F.Cu lobe at x 27–41, y 10–21 that hung on necks under 0.6 mm.
  - (38.6, 33.2): inside the 48 mm² lobe of the single-anchor F.Cu piece between U4 and J4 (x 30–42, y 23–39).
  - (67.76, 31.52): return via 1.26 mm from the MCU_5V_1 layer change at (68.16, 32.72); inside the island, so it passes the +3V3_MCU plane with an antipad.
- No track or other via was touched. Zones refilled.
- **Result:** no lobe above 9 mm² is left without its own via (the third via also anchors the 9 mm² lobe at x 66–71, y 30–36); the largest single-anchor F.Cu piece is 17 mm².
- **Totals:** vias 308 → 311, GND vias 171 → 174.
- **DRC:** 0 copper errors, 0 unconnected, 0 silkscreen warnings (199 library warnings as before). Schematic vs. board: 0 mismatches.
- Backup: `Routing/PCB PCU routed v2-backups/before 3 GND vias 2026-11-12/` (board only).
