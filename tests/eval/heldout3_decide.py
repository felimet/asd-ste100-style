"""Apply the pre-registered rules in heldout3-protocol.md to a held-out 3 results record.

Usage (from the repo root):
  python -I -B -X utf8 tests/eval/heldout3_decide.py <record.json>
  python -I -B tests/eval/heldout3_decide.py selftest
  python -I -B -X utf8 tests/eval/heldout3_decide.py simulate   # part A choice rates under no difference (about 1 min)
Part A (description trigger test) is decided when the record has "trig"; part B (length-rule A/B) when it has
"gen" and "judge". Prints JSON with every number the rules use; thresholds are tested on unrounded values.
"""
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # -I drops the script dir from sys.path
from run_cli_eval import boot_ci_raw, count_sentences, is_dup, mech  # noqa: E402

TARGETS = ["agy", "codex", "claude"]
CROSS = {"agy": {"codex", "claude"}, "codex": {"agy", "claude"}, "claude": {"agy", "codex"}}
DESC_ARMS = ["old", "descA", "descB"]
LENGTH_CHECKS = ("max_chars", "max_sentences")
# Codex lists ~248 other skills on the author's machine and shows only the first 77 characters of each description
# (`codex debug prompt-input`), which cuts descB's trigger clause but not old's or descA's; agy and the isolated
# Claude see the full text. Codex counts are reported, not decisive.
DECIDERS = ("agy", "claude")
TOL_POS, TOL_NEG, B_MARGIN = 5, 3, 6  # calibrated with simulate(): see heldout3-protocol.md


# ---------- part A: which SKILL.md description ships ----------
def decide_triggers(trig):
    by = {(r["target"], r["arm"], r["id"]): r for r in trig}
    ids = sorted({r["id"] for r in trig})
    expect = {r["id"]: r["expect"] for r in trig}
    # a call that still fails after the rerun drops that item for every arm of that generator, so arms stay paired
    excluded = sorted([t, i] for t in TARGETS for i in ids
                      if any(by.get((t, a, i)) is None or by[(t, a, i)]["rc"] != 0 for a in DESC_ARMS))
    ex = {tuple(x) for x in excluded}

    def n(a, t, want):
        return sum(by[(t, a, i)]["loaded"] for i in ids if expect[i] == want and (t, i) not in ex)

    counts = {a: {t: {"pos": n(a, t, True), "neg": n(a, t, False)} for t in TARGETS} for a in DESC_ARMS}
    tot = {a: {k: sum(counts[a][t][k] for t in DECIDERS) for k in ("pos", "neg")} for a in DESC_ARMS}

    def ok(a):
        return tot[a]["pos"] >= tot["old"]["pos"] - TOL_POS and tot[a]["neg"] <= tot["old"]["neg"] + TOL_NEG
    # descA (the smaller change) is the default; descB has to beat it clearly, never win because descA failed
    b_wins = (ok("descB") and tot["descB"]["pos"] - tot["descA"]["pos"] >= B_MARGIN
              and tot["descB"]["neg"] <= tot["descA"]["neg"] + TOL_NEG)
    choice = "descB" if b_wins else "descA" if ok("descA") else "old"
    return {"excluded_target_items": excluded, "counts": counts, "decider_totals": tot,
            "acceptable": [a for a in ("descA", "descB") if ok(a)], "choice": choice}


SCENARIOS = {  # per decider: P(load) for the 12 should-trigger and the 12 should-not items, identical in every arm
    "N1 agy .95, claude .70, neg .03": {"agy": ([.95] * 12, [.03] * 12), "claude": ([.7] * 12, [.03] * 12)},
    "N2 8 items .97 + 4 items .5, neg 10 x .01 + 2 x .3": {
        t: ([.97] * 8 + [.5] * 4, [.01] * 10 + [.3] * 2) for t in DECIDERS},
    "N3 agy .80, claude .50, neg .10": {"agy": ([.8] * 12, [.1] * 12), "claude": ([.5] * 12, [.1] * 12)},
    "N4 agy 1, claude 6 x 1 + 6 x .5, neg 0": {"agy": ([1] * 12, [0] * 12), "claude": ([1] * 6 + [.5] * 6, [0] * 12)},
}


def simulate(n=4000, seed=1, scenarios=SCENARIOS, shift=None):
    """Choice rates of decide_triggers when every arm loads with the scenario's probabilities.
    shift[(arm, decider)] adds to the should-trigger probabilities of the first k items: (delta, k)."""
    import random
    rng = random.Random(seed)
    out = {}
    for name, sc in scenarios.items():
        hits = {a: 0 for a in DESC_ARMS}
        for _ in range(n):
            recs = []
            for t in TARGETS:
                pos, neg = sc.get(t, sc[DECIDERS[-1]])
                for a in DESC_ARMS:
                    d, k = (shift or {}).get((a, t), (0, 0))
                    for i, p in enumerate(pos):
                        recs.append({"target": t, "arm": a, "id": f"p{i:02d}", "expect": True, "rc": 0,
                                     "loaded": rng.random() < min(1, max(0, p + (d if i < k else 0)))})
                    for i, p in enumerate(neg):
                        recs.append({"target": t, "arm": a, "id": f"n{i:02d}", "expect": False, "rc": 0,
                                     "loaded": rng.random() < p})
            hits[decide_triggers(recs)["choice"]] += 1
        out[name] = {a: v / n for a, v in hits.items()}
    return out


# ---------- part B: does the 1.2.0 length paragraph go into SKILL.md ----------
def scores(rec, key="atoms"):
    """(target, arm, id, rep) -> {judge: value}, cross judges only, plus failed judge calls."""
    sc, fail = defaultdict(dict), []
    for j in rec["judge"]:
        if j["judge"] not in CROSS[j["gen_target"]]:
            continue  # the protocol excludes self-judging
        if not j["result"]:
            fail.append([j["judge"], j["gen_target"], j["id"], j["rep"]])
            continue
        for r in j["result"]["replies"]:
            arm = j["mapping"].get(r["label"])
            if arm:
                v = sum(r["atoms_met"]) / len(r["atoms_met"]) if key == "atoms" else r[key]
                sc[(j["gen_target"], arm, j["id"], j["rep"])][j["judge"]] = v
    return sc, fail


def cell_means(values):
    """(target, arm, id, rep) -> value  =>  (target, arm, id) -> mean over the reps that have a value."""
    acc = defaultdict(list)
    for (t, a, i, _), v in values.items():
        acc[(t, a, i)].append(v)
    return {k: sum(v) / len(v) for k, v in acc.items()}


def diffs(cm, t, ids, a="len", b="ship"):
    return {i: cm[(t, a, i)] - cm[(t, b, i)] for i in ids if (t, a, i) in cm and (t, b, i) in cm}


def paired(d):
    d = list(d)
    return {"n": len(d), "mean": sum(d) / len(d) if d else None, "ci": boot_ci_raw(d)}


def r1_holds(d):
    p = paired(d)
    return p["mean"] is not None and p["mean"] <= -0.03 and p["ci"][1] < 0


def length_pass(reply, spec, mech_fn=mech):
    return all(v for k, v in mech_fn(reply, spec).items() if k in LENGTH_CHECKS)


def decide_ab(rec, specs, mech_fn=mech):
    gens = {(g["target"], g["arm"], g["id"], g["rep"]): g for g in rec["gen"]}
    empty = {k for k, g in gens.items() if not g["reply"].strip()}
    sc, judge_fail = scores(rec)
    atoms = {k: sum(v.values()) / len(v) for k, v in sc.items() if v and k not in empty}
    missing = sorted([*k, sorted(CROSS[k[0]] - set(sc.get(k, {})))] for k in gens
                     if k not in empty and CROSS[k[0]] - set(sc.get(k, {})))
    ids = sorted(specs)
    brev = [i for i in ids if specs[i]["kind"] == "length_limited"]
    general = [i for i in ids if i not in brev]
    passed = {k: float(length_pass(g["reply"], specs[k[2]], mech_fn)) for k, g in gens.items()
              if k[2] in brev and k not in empty}
    am, pm = cell_means(atoms), cell_means(passed)

    def rate(t, a):
        v = [x for k, x in passed.items() if k[0] == t and k[1] == a]
        return sum(v) / len(v) if v else None

    pt = {t: {"atoms_len-ship": paired(diffs(am, t, ids).values()),
              "atoms_len-ship_length_items": paired(diffs(am, t, brev).values()),
              "atoms_len-ship_general_items": paired(diffs(am, t, general).values()),
              "length_pass": {a: rate(t, a) for a in ("ship", "len")},
              "length_pass_item_diff": paired(diffs(pm, t, brev).values())} for t in TARGETS}
    per_item = {}  # primary: per length-limited item, mean over generators of the len - ship pass-rate difference
    for i in brev:
        v = [pm[(t, "len", i)] - pm[(t, "ship", i)] for t in TARGETS if (t, "len", i) in pm and (t, "ship", i) in pm]
        if v:
            per_item[i] = sum(v) / len(v)
    primary = paired(per_item.values())
    p_holds = primary["mean"] is not None and primary["mean"] >= 0.05 and primary["ci"][0] > 0
    # the swapped sentence only applies to length-limited prompts, so the regression rules also look at those alone
    r1 = [t for t in TARGETS if r1_holds(diffs(am, t, ids).values()) or r1_holds(diffs(am, t, brev).values())]
    pooled = sum(pt[t]["atoms_len-ship"]["mean"] for t in TARGETS) / len(TARGETS)
    pooled_len = sum(pt[t]["atoms_len-ship_length_items"]["mean"] for t in TARGETS) / len(TARGETS)
    r2 = pooled <= -0.02 or pooled_len <= -0.02
    r3 = [t for t in TARGETS if pt[t]["length_pass"]["len"] - pt[t]["length_pass"]["ship"] < -0.08]
    adopt = p_holds and not (r1 or r2 or r3)
    return {"n_gen": len(gens), "empty_replies": sorted(list(k) for k in empty), "judge_failures": judge_fail,
            "missing_cross_judges": missing, "per_target": pt,
            "primary": {"per_item": per_item, **primary, "holds": p_holds},
            "rules": {"R1_regression_targets": r1, "R2_pooled_mean": pooled, "R2_pooled_mean_length_items": pooled_len,
                      "R2_triggered": r2, "R3_length_drop_targets": r3},
            "decision": "adopt the length paragraph" if adopt else "keep SKILL.md without the length paragraph"}


def descriptives(rec, specs):
    """Reported, not part of the decision: lengths, sentence counts, pass rates by subkind, per-judge atoms, dups."""
    gens = [g for g in rec["gen"] if g["reply"].strip()]
    out = {"median_chars": {}, "pass_by_subkind": {}, "dup": defaultdict(int), "log_chars_len_over_ship_general": {}}
    for t in TARGETS:
        for a in ("ship", "len"):
            for kind in ("length_limited", "general"):
                c = [len(g["reply"].strip()) for g in gens if g["target"] == t and g["arm"] == a and specs[g["id"]]["kind"] == kind]
                out["median_chars"][f"{t}/{a}/{kind}"] = statistics.median(c) if c else None
            for sub in sorted({s["subkind"] for s in specs.values() if s["kind"] == "length_limited"}):
                v = [length_pass(g["reply"], specs[g["id"]]) for g in gens
                     if g["target"] == t and g["arm"] == a and specs[g["id"]].get("subkind") == sub and specs[g["id"]]["kind"] == "length_limited"]
                out["pass_by_subkind"][f"{t}/{a}/{sub}"] = sum(v) / len(v) if v else None
        by = {(g["arm"], g["id"], g["rep"]): len(g["reply"].strip()) for g in gens if g["target"] == t}
        lr = [math.log(by[("len", i, r)] / by[("ship", i, r)]) for (a, i, r) in by
              if a == "ship" and ("len", i, r) in by and specs[i]["kind"] == "general"]
        out["log_chars_len_over_ship_general"][t] = statistics.median(lr) if lr else None
    for g in gens:
        out["dup"][f'{g["target"]}/{g["arm"]}'] += bool(g.get("dup", is_dup(g["reply"])))
    ids = sorted(specs)
    empty = {(g["target"], g["arm"], g["id"], g["rep"]) for g in rec["gen"] if not g["reply"].strip()}
    for key in ("atoms", "directness", "readability", "tone", "fabricated"):  # fabricated: difference in flag rate
        sc, _ = scores(rec, key)
        out[f"per_judge_{key}_len-ship"] = {
            f"{t}/{jn}": paired(diffs(cell_means({k: float(v[jn]) for k, v in sc.items() if jn in v and k not in empty}),
                                      t, ids).values())
            for t in TARGETS for jn in sorted(CROSS[t])}
    out["sentences_over_limit"] = sum(count_sentences(g["reply"]) > specs[g["id"]]["max_sentences"]
                                      for g in gens if "max_sentences" in specs[g["id"]])
    out["dup"] = dict(out["dup"])
    return out


def selftest():
    # part A
    def trig(delta_pos=None, delta_neg=None, fail=()):
        recs = []
        for t in TARGETS:
            for a in DESC_ARMS:
                for k in range(12):
                    pos = k < 6 + (delta_pos or {}).get((a, t), 0)
                    neg = k < (delta_neg or {}).get((a, t), 0)
                    recs.append({"target": t, "arm": a, "id": f"p{k:02d}", "expect": True, "loaded": pos, "rc": 0})
                    recs.append({"target": t, "arm": a, "id": f"n{k:02d}", "expect": False, "loaded": neg,
                                 "rc": 1 if (t, a, f"n{k:02d}") in fail else 0})
        return recs
    def choice(*a, **k):
        return decide_triggers(trig(*a, **k))["choice"]
    b6 = {("descB", "agy"): 3, ("descB", "claude"): 3}  # descB +6 over descA: exactly B_MARGIN
    assert choice() == "descA"  # no difference: the smaller change
    assert choice(b6) == "descB" and choice({("descB", "agy"): 3, ("descB", "claude"): 2}) == "descA"
    assert choice(b6, {("descB", "agy"): 3}) == "descB" and choice(b6, {("descB", "agy"): 4}) == "descA"
    assert choice({("descB", "codex"): 6}) == "descA"  # codex is reported, not decisive
    assert choice({("descA", "agy"): -3, ("descA", "claude"): -2}) == "descA"  # -5 is within TOL_POS
    assert choice({("descA", "agy"): -3, ("descA", "claude"): -3, ("descB", "agy"): -3, ("descB", "claude"): -3}) == "old"
    assert choice({("descA", "agy"): -3, ("descA", "claude"): -3}) == "descB"  # descA really worse, descB +6 over it
    assert choice({("descA", "agy"): -3, ("descA", "claude"): -3, ("descB", "agy"): -1}) == "old"  # +5 is not enough
    assert choice(None, {("descA", "claude"): 3}) == "descA" and choice(None, {("descA", "claude"): 4}) == "old"
    r = decide_triggers(trig(fail={("codex", "descB", "n03")}))
    assert r["excluded_target_items"] == [["codex", "n03"]] and r["counts"]["old"]["codex"]["neg"] == 0
    r = decide_triggers(trig(None, {("old", "agy"): 4}, fail={("agy", "descA", "n00")}))  # dropped in all three arms
    assert r["excluded_target_items"] == [["agy", "n00"]] and r["decider_totals"]["old"]["neg"] == 3
    rates = simulate(n=400, scenarios={k: SCENARIOS[k] for k in list(SCENARIOS)[:1]})
    assert all(v["descA"] >= 0.9 and v["descB"] <= 0.05 for v in rates.values()), rates
    # part B: two length-limited items (max 10 chars) and one general item, three reps
    specs = {"b1": {"kind": "length_limited", "subkind": "chars", "max_chars": 10},
             "b2": {"kind": "length_limited", "subkind": "vague", "max_chars": 10},
             "g1": {"kind": "general", "subkind": "explain"}}
    LONG, SHORT = "這是一則明顯超過十個字元的回覆內容", "短答"
    RUBRIC = {"directness": 4, "readability": 4, "tone": 4, "fabricated": False}

    def gen(fails):
        return [{"target": t, "arm": a, "id": i, "rep": r, "reply": LONG if (t, a) in fails and i != "g1" else SHORT}
                for t in TARGETS for a in ("ship", "len") for i in specs for r in range(3)]

    def judge(lose=lambda t, i, arm: False, n=2):
        return [{"judge": jn, "gen_target": t, "id": i, "rep": r, "mapping": {"A": "ship", "B": "len"},
                 "result": {"replies": [{"label": "A", "atoms_met": [True] * n, **RUBRIC},
                                        {"label": "B", "atoms_met": [True] * (n - 1) + [not lose(t, i, "len")], **RUBRIC}]}}
                for t in TARGETS for jn in CROSS[t] for i in specs for r in range(3)]
    ship_fails = {(t, "ship") for t in TARGETS}
    r = decide_ab({"gen": gen(ship_fails), "judge": judge()}, specs)
    assert r["primary"]["holds"] and r["primary"]["mean"] == 1 and r["decision"] == "adopt the length paragraph", r
    assert r["per_target"]["agy"]["length_pass"] == {"ship": 0.0, "len": 1.0}
    r = decide_ab({"gen": gen(set()), "judge": judge()}, specs)  # no length gain: keep
    assert not r["primary"]["holds"] and r["decision"].startswith("keep")
    r = decide_ab({"gen": gen(ship_fails), "judge": judge(lambda t, i, a: t == "agy")}, specs)  # R1 on agy
    assert r["rules"]["R1_regression_targets"] == ["agy"] and r["decision"].startswith("keep")
    mixed = {("agy", "ship"), ("claude", "ship"), ("codex", "len")}  # pooled +1/3 per item, but codex gets worse
    r = decide_ab({"gen": gen(mixed), "judge": judge()}, specs)
    assert r["primary"]["holds"] and r["rules"]["R3_length_drop_targets"] == ["codex"] and r["decision"].startswith("keep")
    r = decide_ab({"gen": gen(ship_fails), "judge": judge(lambda t, i, a: True, n=40)}, specs)  # R2 alone: -0.025 each
    assert not r["rules"]["R1_regression_targets"] and r["rules"]["R2_triggered"] and r["decision"].startswith("keep")
    assert not r1_holds([-0.5, -0.5, 0.0]) and r1_holds([-0.5, -0.5])  # 3 items: the CI upper bound reaches 0
    r = decide_ab({"gen": gen(ship_fails), "judge": judge(lambda t, i, a: t == "agy" and i != "g1")}, specs)
    assert r["rules"]["R1_regression_targets"] == ["agy"], r["rules"]  # the length items alone catch it
    r = decide_ab({"gen": gen(ship_fails), "judge": judge(lambda t, i, a: i != "g1", n=40)}, specs)
    assert r["rules"]["R2_pooled_mean"] > -0.02 and r["rules"]["R2_pooled_mean_length_items"] <= -0.02
    assert r["rules"]["R2_triggered"] and not r["rules"]["R1_regression_targets"]
    selfj = [{"judge": "codex", "gen_target": "codex", "id": i, "rep": 0, "mapping": {"A": "ship", "B": "len"},
              "result": {"replies": [{"label": "A", "atoms_met": [True]}, {"label": "B", "atoms_met": [False]}]}} for i in specs]
    r = decide_ab({"gen": gen(ship_fails), "judge": judge() + selfj}, specs)
    assert r["per_target"]["codex"]["atoms_len-ship"]["mean"] == 0  # self-judging is ignored
    g = [dict(x, reply="") if (x["target"], x["arm"], x["id"], x["rep"]) == ("claude", "len", "b1", 0) else x for x in gen(ship_fails)]
    r = decide_ab({"gen": g, "judge": judge()}, specs)
    assert r["empty_replies"] == [["claude", "len", "b1", 0]] and r["per_target"]["claude"]["length_pass"]["len"] == 1.0
    assert length_pass("一句。兩句。", {"max_sentences": 1}) is False and length_pass("x", {"first_line_regex": "^y"}) is True
    d = descriptives({"gen": gen(ship_fails), "judge": judge()}, specs)
    assert d["pass_by_subkind"]["agy/ship/chars"] == 0.0 and d["pass_by_subkind"]["agy/len/vague"] == 1.0
    assert d["log_chars_len_over_ship_general"]["codex"] == 0.0 and d["per_judge_atoms_len-ship"]["agy/codex"]["mean"] == 0
    jd = judge()
    for j in jd:
        for rr in j["result"]["replies"]:
            rr.update(directness=5 if rr["label"] == "A" else 3, readability=4, tone=4, fabricated=rr["label"] == "B")
    d = descriptives({"gen": gen(ship_fails), "judge": jd}, specs)
    assert d["per_judge_directness_len-ship"]["codex/agy"]["mean"] == -2 and d["per_judge_fabricated_len-ship"]["claude/codex"]["mean"] == 1
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        selftest()
    elif sys.argv[1:] == ["simulate"]:  # the null and power rates cited in heldout3-protocol.md
        out = {"null": simulate()}
        n3 = {k: v for k, v in SCENARIOS.items() if k.startswith("N3")}
        out["descB +0.5 on 8 should-trigger items, both deciders (N3)"] = simulate(
            scenarios=n3, shift={("descB", t): (0.5, 8) for t in DECIDERS})
        out["descA -0.25 on all should-trigger items, both deciders (N1)"] = simulate(
            scenarios={k: v for k, v in SCENARIOS.items() if k.startswith("N1")}, shift={("descA", t): (-0.25, 12) for t in DECIDERS})
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        rec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        out = {}
        if rec.get("trig"):
            out["part_a"] = decide_triggers(rec["trig"])
        if rec.get("gen"):
            specs = {s["id"]: s for s in json.loads((HERE / "heldout3-prompts.json").read_text(encoding="utf-8"))}
            out["part_b"] = decide_ab(rec, specs)
            out["part_b_descriptives"] = descriptives(rec, specs)
        print(json.dumps(out, ensure_ascii=False, indent=1))
