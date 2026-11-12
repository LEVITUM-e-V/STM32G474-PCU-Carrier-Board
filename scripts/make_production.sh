#!/bin/sh
# Regenerates production/ (Gerbers, drill files, placement file) and docs/PCB_PCU_schematic.pdf from the KiCad project.
# Usage: sh scripts/make_production.sh        (KiCad must be closed)
set -e
KICAD_CLI="${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BOARD="$ROOT/kicad/PCB PCU.kicad_pcb"
OUT="$ROOT/production"

rm -rf "$OUT/gerbers" "$OUT/PCB_PCU-gerbers.zip" "$OUT/PCB_PCU-pos.csv"
mkdir -p "$OUT/gerbers"

"$KICAD_CLI" pcb export gerbers -o "$OUT/gerbers/" \
  -l "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts" "$BOARD"
"$KICAD_CLI" pcb export drill -o "$OUT/gerbers/" --format excellon --excellon-units mm \
  --excellon-separate-th --generate-map --map-format gerberx2 "$BOARD"
"$KICAD_CLI" pcb export pos -o "$OUT/PCB_PCU-pos.csv" --format csv --units mm --side both "$BOARD"
"$KICAD_CLI" sch export pdf -o "$ROOT/docs/PCB_PCU_schematic.pdf" "$ROOT/kicad/PCB PCU.kicad_sch"

(cd "$OUT/gerbers" && zip -q -r ../PCB_PCU-gerbers.zip .)

# Parts that must not be placed by the assembler
if grep -q '"R105"\|"R106"\|"J4"\|"J5"' "$OUT/PCB_PCU-pos.csv"; then
  echo "ERROR: R105, R106, J4 or J5 is in the placement file" >&2; exit 1
fi
echo "Done: $OUT"
