# Sourced by run_trig.sh and run_ab.sh. Set E4 (scratch dir outside the repo, Windows-style path) and CODEX_BIN first.
: "${E4:?set E4 to a scratch directory outside the repo, e.g. C:/Users/me/AppData/Local/Temp/ev4}"
: "${CODEX_BIN:?set CODEX_BIN to the native codex exe (see run_cli_eval.py)}"
W="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -W 2>/dev/null || pwd)"
export CLAUDE_EVAL_MODEL=sonnet
export AGY_EVAL_MODEL=gemini-3.8-flash-high
export CODEX_TIMEOUT=480
export AGY_JUDGE_TIMEOUT=480
PY=(python -I -X utf8 "$W/tests/eval/run_cli_eval.py")
# clean <out> <trig|gen|judge>: delete that stage's failed per-call records so the resumable stage redoes them.
# gen: rc != 0 or empty reply; an empty reply that survives both gen passes is kept and judged (excluded by decide_ab)
clean() { python -I -X utf8 - "$1" "$2" <<'PYX'
import json, glob, os, sys
out, stage = sys.argv[1], sys.argv[2]; n = 0
for f in glob.glob(f"{out}/{stage}/*.json"):
    r = json.load(open(f, encoding="utf-8"))
    bad = {"trig": lambda: r["rc"] != 0, "gen": lambda: r["rc"] != 0 or not r["reply"].strip(),
           "judge": lambda: not r["result"]}[stage]()
    if bad:
        os.remove(f); n += 1
        if stage == "gen":  # judge_one skips existing files, so a regenerated reply must not inherit old scores
            target, _, pid, rep = os.path.basename(f)[:-5].split("__")
            for j in glob.glob(f"{out}/judge/*__{target}__{pid}__{rep}.json"): os.remove(j)
for f in glob.glob(f"{out}/{stage}/*.last.txt"): os.remove(f)
print(f"removed failed {stage} records:", n)
PYX
}
