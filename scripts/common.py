"""Shared helpers for the board check scripts. Run with KiCad's bundled Python (it provides pcbnew).

The board is only read; zones are refilled in memory and nothing is written back to the project.
Coordinates printed by the scripts are board-relative millimetres (origin = top-left board corner).
"""
import pcbnew, sys, math, json, re, fnmatch, os, tempfile, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KICAD_DIR = os.path.join(HERE, '..', 'kicad')
BRD = os.environ.get('PCU_BOARD', os.path.join(KICAD_DIR, 'PCB PCU.kicad_pcb'))
SCH = os.path.join(os.path.dirname(BRD), os.path.basename(BRD).replace('.kicad_pcb', '.kicad_sch'))
W = os.environ.get('PCU_WORK', os.path.join(tempfile.gettempdir(), 'pcu_checks'))
os.makedirs(W, exist_ok=True)
KICAD_CLI = os.environ.get('KICAD_CLI', '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
OX, OY = 91.44, 43.18          # board origin on the KiCad sheet, mm
mm = pcbnew.ToMM


def load():
    """Board as saved."""
    return pcbnew.LoadBoard(BRD)


def filled():
    """Board with all zones refilled in memory."""
    b = pcbnew.LoadBoard(BRD)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    return b


def P(p):
    return (round(mm(p.x) - OX, 3), round(mm(p.y) - OY, 3))


def netclass_map():
    pro = json.load(open(BRD.replace('.kicad_pcb', '.kicad_pro')))
    ns = pro['net_settings']
    return (ns.get('netclass_patterns') or []), ns['classes']


def cls_of(name, pats):
    for p in pats:
        if fnmatch.fnmatchcase(name, p['pattern']) or name == p['pattern']:
            return p['netclass']
    return 'Default'


def tracks(b):
    segs = []; vias = []
    for t in b.GetTracks():
        (vias if t.Type() == pcbnew.PCB_VIA_T else segs).append(t)
    return segs, vias
