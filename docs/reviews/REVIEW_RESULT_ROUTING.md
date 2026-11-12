# Routing review: PCU G474, routed v1

- **Board reviewed:** `Routing/PCB PCU routed v1.kicad_pcb` (+ `.kicad_pro`, `.kicad_dru`). The read-only copy was made on 2026-11-04 at 20:57.
- **Schematic:** the `.kicad_sch` files in the project folder.
- **Plan:** `ROUTING_PLAN.md`.
- **Reviewer:** Claude (Opus 5.5). No project file was changed.
- **Coordinates:** all coordinates are **board coordinates in mm from the top-left board corner**, as in the plan (KiCad page coordinates = board + (91.44, 43.18)).
- **Severity:**
  - **Critical:** must be fixed before ordering.
  - **Major:** a clear plan violation with electrical impact; fix it in this routing pass.
  - **Minor:** cleanup or documentation; fix it if time allows.

> Note: `PCB PCU.kicad_pcb` in the project root is still **unrouted**: 0 tracks, 0 vias, 374 unconnected. It also has no `.kicad_dru` file. The routed board exists only under `Routing/`. Before fabrication, the routed file has to become the project board, or the project has to point to it.

---

## 1. Summary

**DRC** (KiCad 7.0.5 Python, all zones refilled, custom rule active):

| Category | Count |
|---|---|
| Copper errors (clearance, hole clearance, shorts, dangling, starved thermal) | **0** |
| Unconnected items | **0** |
| `lib_footprint_issues` | 199 (from before routing) |
| `silk_overlap` | 131 (130 before routing) |
| `silk_over_copper` | 114 |
| `silk_edge_clearance` | 3 |

**Other checks:**
- **Without the `.kicad_dru` rule:** exactly one extra error, a starved thermal on J5.24 (1 spoke on F.Cu).
- **Netlist vs. board:** 657 of 659 schematic pads match; 0 wrong nets, 0 extra connections. **R109 (power-LED resistor) is not on the board.**
- **Board contents:** 1269 segments, 413 vias (177 locked TP/stitching vias), 0 tracks on In1/In2.

**Plan compliance.** Net classes, track widths and via sizes match §3/§9. The only exceptions:
- 4.3 mm of +3.3V at 0.3 mm (U4.15 neck, partly on B.Cu);
- two 0.6/0.3 mm +5V vias, which are locked TP vias inside U3.8/U5.8.

HV50 0.6 mm and RS232L 0.25 mm are held: DRC is clean, and the closest foreign copper to a J3 50 V pin is 0.61 mm. The +3V3_MCU island matches the plan (x 44.3–70.4, y 3–57), with no +5V via inside it. GND stitching is mostly as planned.

The routing quality, however, does **not** meet §4:

- **ADC lines.** 6 of the 12 MCU_* ADC lines connect their J5 pin to the clamp row through loops of 15–101 mm, instead of the ≤3 mm in #11. These loops run alongside other channels' high-Z nodes.
- **Op-amp outputs.** Two op-amp outputs take detours of 62 mm and 39 mm. One of them wraps around the 50 V connector J3, 0.61 mm from its pins.
- **Via-in-pad.** **52 vias sit in SMD pads**: 42 locked TP vias and 10 router vias, two of them in SSOP pins of U4.
- **High-Z length.** 29 of 40 high-Z nets exceed 5 mm. For 28 of them this is placement-limited (the MST is already > 5 mm). The routing adds a further 6–18 mm on 4 nets.
- **Layer rule.** One high-Z net (U5B+) and three HV/RS-232/CAN nets use B.Cu with router vias.
- **Documentation.** None of these deviations is logged in §9.

**Verdict: NEEDS FIXES. Not ready for fabrication.** The copper is DRC-clean, but the Critical items below (ADC loops, via-in-pad, missing R109) must be fixed first, and the Major items should be fixed in the same pass.

---

## 2. Findings

### Critical

| # | Sheet / Area | Problem (measured) | Suggested fix |
|---|---|---|---|
| C1 | Clamp strip right of J5 (D5–D16 / C / 4.7 k rows), `ConnectionToSTM_PCU`. Nets MCU_ISENSE_3, MCU_T1, MCU_5V_2, MCU_T2, MCU_ISENSE_1, MCU_T3 | **The J5 pin → clamp connection runs as a long loop through the analog area.** Copper path from the J5 pin to the clamp diode pin 3 (straight-line distance in brackets):<br>• J5.17 → D7.3: **100.7 mm** (5.5)<br>• J5.10 → D13.3: **71.9** (7.1)<br>• J5.12 → D12.3: **55.5** (5.8)<br>• J5.9 → D14.3: **32.9** (7.9)<br>• J5.19 → D5.3: **17.6** (6.7)<br>• J5.8 → D15.3: **≈15.9** (8.7)<br>The plan (#11) says ≤ 3 mm. The other six channels manage 5–9 mm.<br>The loops run down to y 75 and around U9/U1 (render `rightlow.png`). They pass within 0.5 mm of other channels' high-Z nodes: Net-(U1B-+) ∥ MCU_ISENSE_3 for 5.6 mm; U7B−, U8A−, U8A+ ∥ MCU_T1 for 3.1, 1.9 and 1.8 mm; U1A− ∥ MCU_ISENSE_3 for 2.2 mm. So the 100 nF/clamp no longer sits "at the J5 pin", and every one of these lines is an antenna across the ISENSE/TSENSE front end. | Delete the six loop chains:<br>• J5.17 ↔ R32.2<br>• J5.10 ↔ R82.2<br>• D12.3 ↔ J5.12<br>• C27.1 ↔ J5.9<br>• D5.3 ↔ J5.19<br>• D15.3 ↔ J5.8<br>Route each J5 pin **directly on F.Cu to its own D.3 pad**, the same way as rows D9/D11/D16 (5–6 mm, 0.2 mm). The rows follow the pin order, so no crossing is needed.<br>Once the loops are gone, the space they used along x≈56–60 and y≈60–76 is free. Lock these 12 nets afterwards. |
| C2 | Whole board: test points and several router vias | **52 vias overlap SMD pads; in 49 of them the drill lies inside the pad.**<br>• **42 locked TP vias:** the TP was moved directly under a top pad. Examples: D9.3, D10.3, C10/C12/C16/C24/C47/C49/C51.1, R2.1, R4.1, R17.2, R81.2, U3.8, U5.8, U6.3, U11.4, E5–E10, R5.1, R8.1.<br>• **10 router vias:** D11.3, D16.3, R26.2, R48.1, R49.1, R79.1, U8.7, **U4.1 and U4.16**, R81.1 (edge only).<br>The U4 vias are Ø 0.6 mm in SSOP pads that are only 0.5 mm wide. Open vias in reflow pads wick solder (0603, SOT-23, SOIC-8, SSOP-16), which leads to dry joints and tombstoning. The plan and the review prompt require **no via-in-pad**. | **Router vias:** move each via ≥ 0.3 mm outside its pad and connect with a 0.2 mm stub. For U4.1 and U4.16, fan out to the left or right of the SSOP row.<br>**TP vias:** shift each bottom TP pad by about 1.0–1.5 mm so that its centre via clears the top pad, then add a short L1 stub. TPs are bare pads, so this is allowed by #20 (≤ 4 mm from the net).<br>Alternative: order filled + capped via-in-pad (POFV). That costs extra and does not fix the 0.6 mm via in the 0.5 mm U4 pads. |
| C3 | `power_supply_PCB` sheet: power LED D1 | **R109 (+5V → Net-(D1-A)) is in the schematic but not on the board.** The board has 265 footprints; the schematic needs 266. D1.A is a single-pad net, so DRC shows no unconnected item. The LED will never light, and the BOM/CPL will not match the schematic. | Run "Update PCB from Schematic" (F8) on the routed board. Place R109 next to D1 at about (26, 66) and route +5V (via to L3) → R109 → D1.A in 0.2–0.3 mm. |

### Major

| # | Sheet / Area | Problem (measured) | Suggested fix |
|---|---|---|---|
| M1 | Op-amp outputs: U3B (`VSENSE`, Net-(R11-Pad1)) and U1A (`ISENSE`, Net-(R33-Pad2)) | **Net-(R11-Pad1):** U3.7 → R11.1 is **61.8 mm** of copper (straight line 14.1 mm). The trace runs above and around J3 and between the J3 pin rows, **0.61–0.66 mm** from 50V_2_NEG, 50V_1_NEG, 50V_1_POS and 50V_2_POS (render `j3.png`). It also runs within 0.5 mm of high-Z nets U2A− (2.3 mm) and U2B− (1.8 mm), and it breaks #8 ("no other net between J3 and its resistors").<br>**Net-(R33-Pad2):** U1.1 → R37.1 is **38.6 mm** (straight line 15.7 mm). | Re-route both after C1 has freed the strip:<br>• R6.2/U3.7 → R11.1 directly, about 15 mm. Use L1 if a path exists; otherwise use the planned #10 fallback (2 signal vias + L4 across U2), never around J3.<br>• U1.1 → R37.1 directly, under 20 mm. |
| M2 | High-Z nodes with avoidable extra length (`ISENSE`/`VSENSE`/`TSENSE`) | Routed length vs. shortest possible tree (MST):<br>• **Net-(U1B-+): 30.5 vs. 12.1 mm** (+18.5)<br>• **Net-(U3B-+): 18.0 vs. 7.7** (+10.4)<br>• **Net-(U5A-+): 18.9 vs. 9.0** (+9.9)<br>• **Net-(U7A-+): 10.7 vs. 4.1** (+6.6; this net could meet the 5 mm rule)<br>• Net-(C17-Pad2): 10.1 vs. 6.0<br>• Net-(C11-Pad1): 10.9 vs. 7.3<br>• Net-(U3A--): 18.8 vs. 15.4<br>Net-(U5A-+) also runs 3.8 mm within 0.5 mm of OpOut Net-(R38-Pad2). | Re-route these 7 nets on L1 as close to their MST as possible, after the loops in C1 and M1 are gone. Targets: U7A+ ≤ 5 mm; U1B+, U3B+ and U5A+ within 2 mm of their MST. Lock them afterwards. |
| M3 | High-Z length rule #9 vs. placement (all three front ends) | **29 of 40 AnalogHZ nets are longer than 5 mm. For 28 of them the shortest possible pad-to-pad tree is already longer than 5 mm** (examples: U3A− 15.4, U5B+ 13.6, U1B+ 12.1, U1A+ 11.6, U2A− 11.5, C13-Pad1 9.7, C17-Pad1 9.1 mm). Routing cannot meet #9 at the current placement. | **This needs a placement change or a plan change; routing alone cannot fix it.** Either move the input/divider resistors (R7/R8, R24/R26, R29/R31, R39/R41, R2/R3) to within about 2 mm of their op-amp pins, or raise the #9 target to about 10 mm and document it in §9. In either case do M2. |
| M4 | Net-(U5B-+) (high-Z, `ISENSE`) | It uses **B.Cu for 6.4 mm with 2 router vias**: R26.2 (via-in-pad) → (69.78, 61.48) → (74.28, 56.98). This violates #9 (L1 only, no vias) and §8 acceptance ("no high-Z track on L4"). | Re-route R26.2 → U5.5 on F.Cu. The obstacles are the ADC and OpOut loops from C1/M1, so this net becomes routable once those are removed. |
| M5 | J3 / 50V_2_POS (`VSENSE`) | J3.6 → R81.1 runs **10.6 mm on B.Cu** with an unlocked via at (84.50, 32.77) whose ring overlaps R81.1. The straight distance is 4.0 mm. The F.Cu path from J3.6 left to R81.1 at y ≈ 32.3 is free: 1.2 mm to 50V_1_POS and ≥ 0.6 mm to the GND via. This breaks #8 and §8 (no HV50 on L4). | Delete the B.Cu loop and the via. Route J3.6 → R81.1 on F.Cu in 0.3 mm, about 4.5 mm long. |
| M6 | §9 log | **§9 has no "Routing v1" entry.** The Freerouting result, the gap-fill/length scripts, and every deviation in this table (B.Cu use by HV50/AnalogHZ/ADC/CAN/RS232L nets, the +3.3V 0.3 mm neck, the long nets) are not documented, although §6.5 and §9 require it. | Add a "Routing v1 (2026-11-04)" entry with the DRC result and the deviation list (§3 below), and record the decision for each item. |

### Minor

| # | Sheet / Area | Problem (measured) | Suggested fix |
|---|---|---|---|
| m1 | MAX3221 U4 charge pump (`RS232`) | Pin → cap copper length, against ≤ 3 mm (#16):<br>• C1+ 4.57 mm (straight 2.90)<br>• C1− 5.57 (4.27)<br>• V− 4.27 (4.27)<br>• V+ 3.55 (3.18)<br>C2+ (3.08) and C2− (2.54) are fine. | Straighten C1+ and C1− (saves about 1.5 mm each). V− and V+ are placement-limited; move C19/C18 about 1 mm closer only if that is cheap. |
| m2 | CAN U6/J2 (`RS232`/CAN sheet) | CAN_H and CAN_L are routed separately, not as a coupled pair. Path J2 → U6: CAN_H 12.7 + 5.1 = **17.7 mm**; CAN_L 6.4 + 3.9 = **10.3 mm**, a mismatch of **7.4 mm** against < 1 mm in #13. At 1 Mbit/s that is about 50 ps, so it has no electrical impact, but it is a plan deviation. | Route CAN_H J2.1 → D4.1 → R54.1 next to CAN_L from D4 onwards, or accept and log it. J2.1 and J2.6 are in different rows, so near the connector the pair cannot be coupled anyway. |
| m3 | Split termination C21 midpoint (CAN) | Net-(C21-Pad1) is 11.8 mm long (8.8 mm on B.Cu, 2 vias, one in R79.1), against "stubs ≤ 3 mm". R79 sits at (19.2, 41.2) and C21/R80 at (16.3, 52.6), so the shortest possible tree is 11.7 mm. **This is placement-limited.** | Electrically acceptable at 1 Mbit/s. Move the via out of R79.1 (C2). Optionally move R79 next to R80/C21; that is a placement change. |
| m4 | RS-232 DOUT (Net-(U4-DOUT)) | 16.4 mm, of which **7.9 mm on B.Cu with 2 vias**, against #15 (L1, no vias). U4.13 → R43.2 is 12.4 mm in a straight line, across the U4 body. | Acceptable: ±7 V, slew-limited, and the RS232L 0.25 mm clearance is held on B.Cu too. Log it in §9. |
| m5 | VREF_1V65 (U9 → R26/R31/R36/R41) | It is routed as a **daisy chain** (U9 → R41 → R36, and R41 → R26 → R31), not as the star in #12. Copper U9.1 → R31.1 is 12.2 mm. | The load is high impedance and DC, so the effect is small. If you want to follow #12, take R26/R31 from a separate branch at U9.1. Otherwise log it. |
| m6 | +3V3_MCU → R10 (VREF divider top) | It runs **20.7 mm on B.Cu, 0.3 mm wide** (#6 says 0.4 mm) from the via at D5 (59.87, 54.82) to (59.54, 75.56). It crosses the island edge (y 57) into the +5V plane area on L3, so the ADC reference supply couples to the +5V plane over 18 mm. | Widen it to 0.4 mm. Better: run it on F.Cu (L1, over the solid GND plane) once the ADC loops in C1 are gone. |
| m7 | B.Cu crossing the L3 island edge | Four nets cross the +3V3_MCU / +5V split on L4: **Net-(R100-Pad1)** (OpOut U8 → R100, 20.9 mm on B.Cu, crossing at x 70.4), **MCU_DI1**, **MCU_DI2** and +3V3_MCU (m6). | All of these are DC or slow signals, so this is acceptable. Note it in §9. R100 → U8 is placement-limited (straight line 21.4 mm). |
| m8 | GND fan-out (#7: via ≤ 1 mm from every SMD GND pad) | **30 pads** are more than 1 mm from their GND via:<br>• U4.14: **2.56 mm**<br>• D3.2: 1.60<br>• U6.2: 1.42<br>• op-amp pin 4 (U1/U2/U3/U5/U7/U8/U9): 1.32<br>• C39/C40/C54/C55.2: 1.25<br>• U14.2: 1.11<br>• U10/U11/U12.2: 1.01<br>• all D5–D16 pin 1: 1.09 | Add a 0.6/0.3 GND via ≤ 1 mm from U4.14 (the 2.56 mm one matters most, because the charge-pump return goes through it), D3.2 and U6.2. The 1.0–1.3 mm cases are acceptable. |
| m9 | GND stitching, bottom edge | The edge vias leave **gaps of 15.7 mm (x 56.4–72.1) and 10.0 mm (x 46.4–56.4) along the bottom edge**. H5 explains part of the second gap. The first one is blocked by the ADC loop and the +3V3_MCU B.Cu trace at y ≈ 75.5. The grid has one hole near (39, 33). All other edges are at ≤ 6 mm, apart from the corners at H1–H4. | Add edge vias at 5 mm spacing along y ≈ 75.5, x 57–72, after C1/m6, plus one via near (39, 33). |
| m10 | U14 AP2112K input | U14.1 (VIN) and U14.3 (EN): the nearest +5V cap is C54 at **6.8 mm / 4.9 mm**. C40 (the planned input cap) is about 14 mm away. | Placement: move C40 (or C54) to within 2 mm of U14.1. The routing cannot fix this. |
| m11 | Track geometry | **25 segments shorter than 0.05 mm** (for example MCU_DO4 at (39.24, 27.29), 0.002 mm; MCU_RS232_DIN at (41.23, 42.60) and (38.23, 39.59); Net-(U3B-+) at (82.83, 45.40)). **2 free 45° acute corners** at MCU_ISENSE_2 (64.17, 51.10) and MCU_ISENSE_4 (64.17, 43.90). 5 overlapping 0° doubled segments inside pads. These are artefacts of the gap-fill script. | Run KiCad "Cleanup Tracks & Vias" (merge collinear, delete redundant) and re-draw the two acute corners. |
| m12 | +3.3V at U4.15 | 4.27 mm at 0.3 mm instead of 0.4 mm: 2.49 mm on F.Cu at the pin and **1.78 mm on B.Cu** from (30.35, 33.65) to (30.00, 35.40). The B.Cu part has no pin-pitch constraint. | Widen the B.Cu segment to 0.4 mm. The 0.3 mm F.Cu neck at the SSOP pin is fine for < 10 mA; log it. |
| m13 | U2B feedback (`VSENSE`) | U2.7 → R3.2 is 5.3 mm and R3.1 → U2.6 is 7.5 mm, a feedback loop of about 12.8 mm. All other op-amp loops are 3.5–5.3 mm (pin → Rf → pin about 2 mm each side). | Placement: move R3 next to U2 pins 6/7, as was done for R1. |

**Checked and found fine (not findings):**
- Tracks: no track on In1/In2. No tracks between fine-pitch pins (U4, J5).
- Vias: no via within 0.5 mm of the board edge or of a THT hole. No +5V via in the island.
- Power: all +3V3_MCU vias inside the island, except the R10 via (m6). Op-amp pin 8 → 100 nF at 1.75 mm.
- Op-amp feedback: pin → Rf → pin about 2 mm per side, except U2B (m13).
- Short and direct as planned:
  - D17 → J4.3 is 3.35 mm at 0.5 mm;
  - C59/C60 are at J5.3/4 with 0.8 mm vias;
  - U14 → C41 is 2.1 mm at 0.4 mm.
- No high-Z trace within 0.5 mm of any digital (Default-class) net. The only aggressor near a high-Z net is 50V_2_NEG beside U2B− (0.7 mm, DC).
- Thermal reliefs: all THT GND/+5V/+3V3_MCU pins have thermals (0.5 mm spoke, 0.5 mm gap) on all planes, which suits hand-soldered J4/J5/Micro-Fit pins.

---

## 3. Deviation check

§9 contains no entry for the routing pass. Below, the routing-relevant §9 entries are checked first, then the deviations the review prompt names and the ones found in the board (which should be added to §9).

| Deviation | Verdict | Reasoning |
|---|---|---|
| §9 Placement v3: OpOut / clamp crossings allowed on L4 (#10 fallback) | **Acceptable** | Only Net-(R100-Pad1) uses L4 (20.9 mm). It is low impedance, and its length is placement-forced (21.4 mm straight). The other OpOut problems are F.Cu detours (M1), not layer issues. |
| §9: ISENSE/connector-side AnalogIn nets on L4 | **Acceptable** | ISENSE_1_REF/SIG, ISENSE_3_SIG, ISENSE_4_SIG, 5V_2_NEG and T_3_SIG have 3.7–14 mm on B.Cu. They are low-impedance connector nets, and §9 clarifies that they are outside #9. |
| §9: ADC clamp groups "≤ ~7 mm" | **Fix** | 6 of 12 lines are 15–101 mm (C1). |
| §9: D17 3.8 mm from J4.3; C59/C60 3.4 mm from J5.3/4 | **Acceptable** | Routed as 3.35 mm at 0.5 mm, and short stubs with 0.8 mm vias into the island. |
| §9: +3V3_MCU island x 44.3–70.4, y 3–57, no +5V vias inside | **Acceptable** | Confirmed in the zone outline; 0 +5V vias inside. |
| §9: U4 footprint clearance override 0.15 mm | **Acceptable** | DRC-clean, and above the JLCPCB minimum. The two router vias in U4.1/U4.16 are a separate problem (C2). |
| §9: 5 starved thermals (C28, C30, U10, U11, U12) | **Acceptable (resolved)** | 0 starved thermals after routing. |
| §9: Net classes = §4 (and #1 J1 0.3 mm stubs, #5 U14 → C41 0.4 mm) | **Acceptable** | Class tables match. J1 pins go straight into the plane, and C39/C40/C54/C55 each have a 0.8 mm via at 1.35 mm. |
| §9: "Layer limits checked after routing and fixed by hand" | **Fix** | Not done: U5B+ (M4), 50V_2_POS (M5), RS-232 DOUT (m4) and C21 midpoint (m3) still have B.Cu copper and router vias. |
| §9: Freerouting used as the fallback router | **Acceptable, with a fix** | Using it is fine, but the "checked against §4 afterwards" step is missing. This review is that check; log the result (M6). |
| `.kicad_dru` rule "pad 24 GND, 1 spoke ok" | **Acceptable** | Without the rule, only J5.24 fails (1 F.Cu spoke). The pin is a THT through-hole connected to the L2 plane and the B.Cu pour, so the electrical connection is solid. The condition also matches J4.24, which does not need it; you could narrow it to `A.Parent.Reference == 'J5'`. |
| U4.15 +3.3V stub at 0.3 mm | **Acceptable** | 2.1 mm to C7, < 10 mA, and the pad is 0.5 mm wide. Widen the 1.78 mm B.Cu continuation to 0.4 mm (m12). |
| J3: 50V_1_NEG reaches the outer row via B.Cu (14.6 mm) | **Acceptable** | J3.2 is boxed in by J3.7 (50 V) and J3.1/J3.3. With 1.5 mm pads at a 3 mm pitch, an L1 neck has 0.0 mm margin for a 0.3 mm trace with 0.6 mm clearance on both sides, so B.Cu is forced. The 0.6 mm clearance is held on B.Cu. |
| J3: 50V_2_POS via B.Cu (10.6 mm + 1 via) | **Fix** | A free 4.5 mm F.Cu path exists (M5). |
| ADC lines hop to B.Cu through the TP vias (MCU_50V_1/2, 5V_1, ISENSE_2/4, T4) | **Acceptable** for the layer, **fix** for the vias | 5–7.4 mm on B.Cu under the +3V3_MCU island, with no aggressor within 1 mm. But the TP vias and router vias land in D.3/C pads (C2). |
| R100 → U8 (OpOut, long) | **Acceptable** | 22.5 mm of copper against a 21.4 mm straight line: placement-limited, low impedance, L4 allowed by #10. It crosses the island edge (m7). |
| CAN pair not coupled; mismatch 7.4 mm | **Acceptable (log it)** | It has no effect at 1 Mbit/s. J2.1 and J2.6 are in different rows (m2). |
| C21 split-termination midpoint 11.8 mm on B.Cu | **Acceptable (log it)** | Placement-limited (11.7 mm straight); the via in R79.1 has to move (C2/m3). |
| RS-232 DOUT on B.Cu with 2 vias | **Acceptable (log it)** | Placement-limited across U4 (12.4 mm straight). RS232L clearance is held (m4). |
| VREF_1V65 daisy chain instead of a star | **Acceptable (log it)** | Low-impedance buffered DC feeding high-impedance loads (m5). |
| +3V3_MCU → R10 on B.Cu at 0.3 mm instead of 0.4 mm | **Fix (minor)** | Widen it, or move it to L1 (m6). |
| High-Z nets > 5 mm (29/40) | **Fix the routing part (M2); placement or plan decision for the rest (M3)** | 28 nets are longer than 5 mm by placement; 7 nets have 3–18 mm of avoidable routing length. |

---

## 4. Commands and scripts used

The scripts are in `review_scripts_routing/`, and the render crops in `review_scripts_routing/renders/`. All of them work on a **copy** of the board. KiCad was closed (`pgrep -ix kicad` returned no process). Board origin offset: (91.44, 43.18) mm.

```zsh
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
W=<scratch>/r ; mkdir -p $W
cp "Routing/PCB PCU routed v1".kicad_{pcb,pro,dru,prl} $W/
B="$W/PCB PCU routed v1.kicad_pcb"

# 1  DRC with zones refilled (also once without the .kicad_dru → only J5.24 starved thermal)
$PY drc.py "$B" drc.txt ; grep -o "^\[[a-z_]*\]" drc.txt | sort | uniq -c

# 8  Schematic netlist vs. board pads + MST per net (lower bound of the routed length)
$CLI sch export netlist --format kicadsexpr -o net.net "PCB PCU.kicad_sch"
$PY analyze.py "$B" net.net

# 2/3/4  Widths, via sizes, B.Cu use per L1-only class, routed length per net and layer
$PY an.py "$B"
# 4/5    Aggressor proximity, island contents and edge crossings on B.Cu,
#        GND-via distance, decoupling distances, power widths
$PY an2.py "$B"
# 7      Tiny segments, acute angles, via-in-pad, edge/hole distance,
#        fine-pitch pads, thermals, pad-24 rule targets
$PY an3.py "$B"
# 5      Via-in-pad detail (locked TP vs. router), edge stitching gaps, 6 mm grid, pour pieces
$PY an4.py "$B"
# Detail tools: break a net into pad-to-pad chains / shortest copper path between two pads
$PY chains.py "$B" "MCU_ISENSE_3,Net-(R11-Pad1),50V_2_POS"
$PY path.py   "$B" J5.17:D7.3 U3.7:R11.1 U4.15:C7.1 J2.1:R54.1
# Renders (tracks coloured by net class; B.Cu dashed; locked vias dark, router vias green)
./crop.sh full 0 0 101 77 ; ./crop.sh j3 70 25 96 47 ; ./crop.sh rightlow 54 30 101 77
```

Other checks:
- Net-class tables in the project root and in `Routing/` were compared as JSON; they are identical.
- The high-Z ∥ OpOut/ADC proximity (< 0.5 mm, same layer) was measured with an inline variant of `an2.py`, sampling every 0.1 mm along each segment.
