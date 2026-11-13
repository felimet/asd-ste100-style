"""Merge the held-out 3 per-call records into one file that heldout3_decide.py reads.

Usage: python -I -B -X utf8 consolidate.py <E4> <out_json> <models_json>
<models_json> is a JSON object of CLI versions and notes recorded when the runs happened.
Part B keys (gen, judge, arms_ab) are added only when E4/about exists.
"""
import json
import sys
from pathlib import Path

ev, dest, models = Path(sys.argv[1]), Path(sys.argv[2]), json.loads(sys.argv[3])


def load(d):
    return [json.loads(f.read_text(encoding="utf-8")) for f in sorted(d.glob("*.json"))]


rec = {"date": "2026-11-13", "protocol": "tests/eval/heldout3-protocol.md (commit 0d67863)", "models": models,
       "trig": load(ev / "tout" / "trig"), "arms_trig": json.loads((ev / "twork" / "arms.json").read_text(encoding="utf-8"))}
if (ev / "about").exists():
    gens = load(ev / "about" / "gen")
    for g in gens:
        g.pop("mech", None)  # recomputed from the reply and the prompt file
    rec.update(prompts="tests/eval/heldout3-prompts.json", samples_per_cell=3,
               judges="cross only: each generator's replies judged by the other two CLIs",
               arms_ab=json.loads((ev / "abwork" / "arms.json").read_text(encoding="utf-8")),
               gen=gens, judge=load(ev / "about" / "judge"))
dest.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"wrote {dest}: {len(rec['trig'])} trig, {len(rec.get('gen', []))} gen, {len(rec.get('judge', []))} judge")
