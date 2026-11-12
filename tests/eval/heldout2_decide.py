"""Apply the pre-registered rules in heldout2-protocol.md to a held-out 2 results record.

Usage (from the repo root):
  python -I -B -X utf8 tests/eval/heldout2_decide.py tests/heldout2-eval-2026-11-12.json [--sensitivity]
Prints JSON with every number the rules use. Thresholds are tested on unrounded values.
--sensitivity adds post-hoc checks of R1 for every generator (not part of the pre-registered decision).
"""
import itertools
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # -I drops the script dir from sys.path
from run_cli_eval import boot_ci_raw, mech, skill_reads  # noqa: E402  same bootstrap and mechanical checks as the report

TARGETS, ARMS = ["agy", "codex", "claude"], ["base", "lean", "v120"]
CROSS = {"agy": {"codex", "claude"}, "codex": {"agy", "claude"}, "claude": {"agy", "codex"}}
ROBUST_EXCLUDE = {"progress", "emotional", "short_qa"}


def judge_scores(rec, key="atoms"):
    """(target, arm, id) -> {judge: score}, cross judges only, plus failed judge calls. key "atoms" gives the atom ratio."""
    atoms, fail = defaultdict(dict), []
    for j in rec["judge"]:
        if j["judge"] not in CROSS[j["gen_target"]]:
            continue  # the protocol excludes self-judging
        if not j["result"]:
            fail.append([j["judge"], j["gen_target"], j["id"]])
            continue
        for r in j["result"]["replies"]:
            arm = j["mapping"].get(r["label"])
            if arm:
                v = sum(r["atoms_met"]) / len(r["atoms_met"]) if key == "atoms" else r[key]
                atoms[(j["gen_target"], arm, j["id"])][j["judge"]] = v
    return atoms, fail


def item_diffs(atoms, empty, t, a, b, ids, judges=None):
    def item(arm, i):
        v = [x for jn, x in atoms.get((t, arm, i), {}).items() if judges is None or jn in judges]
        return sum(v) / len(v) if v and (t, arm, i) not in empty else None
    return {i: item(a, i) - item(b, i) for i in ids if item(a, i) is not None and item(b, i) is not None}


def paired(d):
    d = list(d)
    return {"n": len(d), "mean": sum(d) / len(d) if d else None, "ci": boot_ci_raw(d)}


def decide(rec, specs, mech_fn=mech):
    gens = {(g["target"], g["arm"], g["id"]): g for g in rec["gen"]}
    atoms, judge_fail = judge_scores(rec)
    missing = sorted([t, a, i, sorted(CROSS[t] - set(atoms.get((t, a, i), {})))] for t in TARGETS for a in ARMS
                     for i in specs if CROSS[t] - set(atoms.get((t, a, i), {})))
    empty = {k for k, g in gens.items() if not g["reply"].strip()}

    def mech_all(t, a):
        # items without mechanical checks count as passing (all() of no checks), the same for every arm
        v = [all(mech_fn(g["reply"], specs[i]).values()) for (tt, aa, i), g in gens.items() if tt == t and aa == a]
        return sum(v) / len(v) if v else None

    ids = sorted(specs)
    robust = [i for i in ids if specs[i]["kind"] not in ROBUST_EXCLUDE]
    pt = {t: {"v120-lean": paired(item_diffs(atoms, empty, t, "v120", "lean", ids).values()),
              "v120-lean_robust": paired(item_diffs(atoms, empty, t, "v120", "lean", robust).values()),
              "v120-base": paired(item_diffs(atoms, empty, t, "v120", "base", ids).values()),
              "lean-base": paired(item_diffs(atoms, empty, t, "lean", "base", ids).values()),
              "mech_all": {a: mech_all(t, a) for a in ARMS}} for t in TARGETS}
    r1 = [t for t in TARGETS if r1_holds(item_diffs(atoms, empty, t, "v120", "lean", ids).values())]
    pooled = sum(pt[t]["v120-lean"]["mean"] for t in TARGETS) / len(TARGETS)
    r2 = pooled <= -0.02
    r3 = [t for t in TARGETS if pt[t]["mech_all"]["lean"] - pt[t]["mech_all"]["v120"] > 0.08]
    sign = lambda x: 0 if x is None or abs(x) <= 1e-12 else (1 if x > 0 else -1)  # float noise is not a direction
    flips = [t for t in TARGETS if sign(pt[t]["v120-lean"]["mean"]) * sign(pt[t]["v120-lean_robust"]["mean"]) < 0]
    return {"n_gen": len(gens), "empty_replies": sorted(list(k) for k in empty), "judge_failures": judge_fail,
            "missing_cross_judges": missing, "per_target": pt,
            "rules": {"R1_regression_targets": r1, "R2_pooled_mean": pooled, "R2_triggered": r2,
                      "R3_mech_drop_targets": r3},
            "decision": "revert SKILL.md to 1.1.1" if (r1 or r2 or r3) else "adopt v120",
            "claude_v120_base_ci_upper_below_0": pt["claude"]["v120-base"]["ci"][1] < 0,
            "robust_direction_flips": flips}


def r1_holds(d):
    p = paired(d)
    return p["mean"] is not None and p["mean"] <= -0.03 and p["ci"][1] < 0


def sensitivity(rec, specs, t):
    """Post-hoc fragility checks of R1 (v120 - lean) for one generator."""
    gens = {(g["target"], g["arm"], g["id"]): g for g in rec["gen"]}
    atoms, _ = judge_scores(rec)
    empty = {k for k, g in gens.items() if not g["reply"].strip()}
    ids = sorted(specs)
    diffs = item_diffs(atoms, empty, t, "v120", "lean", ids)
    d = list(diffs.values())
    nz = [x for x in d if abs(x) > 1e-12]
    obs = abs(sum(d))
    # exact sign-flip test: zero diffs do not change the sum, so enumerate signs of the nonzero ones only
    flips = [abs(sum(s * x for s, x in zip(signs, nz))) >= obs - 1e-12 for signs in itertools.product((1, -1), repeat=len(nz))]
    return {"item_diffs": {i: round(x, 4) for i, x in diffs.items()},
            "signs": {"negative": sum(x < 0 for x in nz), "positive": sum(x > 0 for x in nz), "zero": len(d) - len(nz)},
            "seeds_0_499_upper_below_0": sum(boot_ci_raw(d, seed=s)[1] < 0 for s in range(500)) / 500,
            "upper_B100000": boot_ci_raw(d, n=100000)[1],
            "sign_flip_p_two_sided": sum(flips) / len(flips),
            "per_judge": {jn: paired(item_diffs(atoms, empty, t, "v120", "lean", ids, {jn}).values()) for jn in sorted(CROSS[t])},
            "item_diffs_by_judge": {jn: {i: round(x, 4) for i, x in item_diffs(atoms, empty, t, "v120", "lean", ids, {jn}).items()
                                         if abs(x) > 1e-12} for jn in sorted(CROSS[t])},
            "per_judge_r1": {jn: r1_holds(item_diffs(atoms, empty, t, "v120", "lean", ids, {jn}).values()) for jn in sorted(CROSS[t])},
            # only meaningful where R1 holds on all items: which single removal stops it from holding
            "leave_one_out_breaks_r1": [i for i in diffs if not r1_holds(x for k, x in diffs.items() if k != i)] if r1_holds(d) else []}


def descriptives(rec):
    """Counts the results record quotes: fabricated flags per judge, reference reads, Claude input tokens."""
    fab = defaultdict(int)
    for j in rec["judge"]:
        if j["judge"] in CROSS[j["gen_target"]] and j["result"]:
            for r in j["result"]["replies"]:
                fab[f'{j["gen_target"]}/{j["judge"]}/{j["mapping"][r["label"]]}'] += bool(r["fabricated"])
    refs = defaultdict(int)
    for g in rec["gen"]:
        for ref in set(skill_reads(g.get("tools", []))["refs"]):
            refs[f'{g["target"]}/{g["arm"]}/{ref}'] += 1
    tok = {}
    for a in ARMS:  # Claude usage is summed over every model request in one CLI call
        gs = [g for g in rec["gen"] if g["target"] == "claude" and g["arm"] == a]
        nt = [g["ctx_tokens"] for g in gs if not g.get("tools")]
        tok[a] = {"n": len(gs), "mean": sum(g["ctx_tokens"] for g in gs) / len(gs), "no_tool_n": len(nt),
                  "no_tool_mean": sum(nt) / len(nt) if nt else None}
    return {"fabricated_by_target_judge_arm": dict(sorted(fab.items())), "reference_reads": dict(sorted(refs.items())),
            "claude_input_tokens": tok}


def readability_vs_length(rec, specs, t):
    """Spearman over items of log(chars lean / chars base) against the lean - base readability difference."""
    gens = {(g["target"], g["arm"], g["id"]): g for g in rec["gen"]}
    empty = {k for k, g in gens.items() if not g["reply"].strip()}
    rd = item_diffs(judge_scores(rec, "readability")[0], empty, t, "lean", "base", sorted(specs))
    x = [math.log(gens[(t, "lean", i)]["chars"] / gens[(t, "base", i)]["chars"]) for i in rd]
    return {"n": len(rd), "spearman": statistics.correlation(x, list(rd.values()), method="ranked")}


def selftest():
    # two items; agy loses one atom on both under v120, every other cell is equal
    specs = {"x1": {"kind": "debug"}, "x2": {"kind": "short_qa"}}
    gen = [{"target": t, "arm": a, "id": i, "reply": "ok"} for t in TARGETS for a in ARMS for i in specs]
    judge = [{"judge": jn, "gen_target": t, "id": i, "mapping": {"A": "base", "B": "lean", "C": "v120"},
              "result": {"replies": [{"label": "A", "atoms_met": [True, True]}, {"label": "B", "atoms_met": [True, True]},
                                     {"label": "C", "atoms_met": [True, t != "agy"]}]}}
             for t in TARGETS for jn in CROSS[t] for i in specs]
    no_mech = lambda reply, spec: {}  # the fixture has no mechanical checks
    r = decide({"gen": gen, "judge": judge}, specs, no_mech)
    assert r["rules"]["R1_regression_targets"] == ["agy"] and r["decision"] == "revert SKILL.md to 1.1.1", r["rules"]
    assert r["missing_cross_judges"] == [] and r["robust_direction_flips"] == []
    drop = [j for j in judge if not (j["gen_target"] == "codex" and j["id"] == "x1" and j["judge"] == "agy")]
    assert decide({"gen": gen, "judge": drop}, specs, no_mech)["missing_cross_judges"] == [["codex", a, "x1", ["agy"]] for a in ARMS]
    s = sensitivity({"gen": gen, "judge": judge}, specs, "agy")
    assert s["signs"] == {"negative": 2, "positive": 0, "zero": 0} and s["sign_flip_p_two_sided"] == 0.5, s
    # pin the thresholds and filters that drive the decision
    assert abs(r["rules"]["R2_pooled_mean"] + 1 / 6) < 1e-12 and r["rules"]["R2_triggered"]
    assert s["leave_one_out_breaks_r1"] == ["x1", "x2"] and r["per_target"]["agy"]["v120-lean_robust"]["n"] == 1
    assert r1_holds([-0.05] * 24) and not r1_holds([-0.025] * 24) and not r1_holds([-1.0] + [0.0] * 23)
    j2 = [dict(j, result={"replies": [dict(x, atoms_met=[True, j["judge"] == "codex"]) if x["label"] == "C" else x
                                      for x in j["result"]["replies"]]}) if j["gen_target"] == "agy" else j for j in judge]
    assert decide({"gen": gen, "judge": j2}, specs, no_mech)["per_target"]["agy"]["v120-lean"]["mean"] == -0.25
    selfj = [{"judge": "codex", "gen_target": "codex", "id": i, "mapping": {"A": "base", "B": "lean", "C": "v120"},
              "result": {"replies": [{"label": "A", "atoms_met": [True]}, {"label": "B", "atoms_met": [True]},
                                     {"label": "C", "atoms_met": [False]}]}} for i in specs]
    assert decide({"gen": gen, "judge": judge + selfj}, specs, no_mech)["per_target"]["codex"]["v120-lean"]["mean"] == 0
    g2 = [dict(g, reply="") if (g["target"], g["arm"], g["id"]) == ("claude", "v120", "x2") else g for g in gen]
    assert decide({"gen": g2, "judge": judge}, specs, no_mech)["per_target"]["claude"]["v120-lean"]["n"] == 1
    flat = [dict(j, result={"replies": [dict(x, atoms_met=[True, True]) for x in j["result"]["replies"]]}) for j in judge]
    bad = lambda reply, spec: {"c": reply != "bad"}
    g3 = [dict(g, reply="bad") if (g["target"], g["arm"], g["id"]) == ("codex", "v120", "x1") else g for g in gen]
    r3 = decide({"gen": g3, "judge": flat}, specs, bad)
    assert r3["rules"]["R3_mech_drop_targets"] == ["codex"] and not r3["rules"]["R1_regression_targets"] and not r3["rules"]["R2_triggered"]
    assert r3["decision"] == "revert SKILL.md to 1.1.1" and decide({"gen": gen, "judge": flat}, specs, bad)["decision"] == "adopt v120"
    # R2 alone: every generator loses 1 of 40 atoms on v120 (-0.025 each), so R1 never holds but the pooled mean does
    j4 = [dict(j, result={"replies": [dict(x, atoms_met=[True] * 39 + [x["label"] != "C"]) for x in j["result"]["replies"]]})
          for j in judge]
    r4 = decide({"gen": gen, "judge": j4}, specs, no_mech)
    assert not r4["rules"]["R1_regression_targets"] and r4["rules"]["R2_triggered"] and r4["decision"] == "revert SKILL.md to 1.1.1"
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        selftest()
    else:
        rec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        specs = {s["id"]: s for s in json.loads((HERE / "heldout2-prompts.json").read_text(encoding="utf-8"))}
        out = decide(rec, specs)
        if "--sensitivity" in sys.argv[2:]:
            out["sensitivity_post_hoc"] = {t: sensitivity(rec, specs, t) for t in TARGETS}
            out["readability_vs_length_lean_base"] = {t: readability_vs_length(rec, specs, t) for t in TARGETS}
            out["descriptives"] = descriptives(rec)
        print(json.dumps(out, ensure_ascii=False, indent=1))
