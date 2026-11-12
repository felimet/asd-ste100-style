#!/usr/bin/env python3
"""Cross-CLI A/B eval for the asd-ste100-zh-tw skill (agy Gemini 4 Argon, Codex, Claude Code).

Stages: setup -> gen -> judge -> report. Stdlib only. Every stage is resumable:
a result file that already exists is skipped. `selftest` checks the mechanical metrics.
Raw per-call files live in --out; only the consolidated report is meant for the repo.
--work and --out must be outside the repo: agy and Codex load the repo's AGENTS.md into every arm otherwise.
"""
import argparse, difflib, hashlib, itertools, json, os, random, re, shutil, subprocess, sys, zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parents[1]
SKILL = "asd-ste100-zh-tw"
SKILL_MD_RE = re.compile(r"asd-ste100-zh-tw[\\/]+SKILL\.md")
REF_RE = re.compile(r"asd-ste100-zh-tw[\\/]+references[\\/]+(\w+)\.md")
AGY_MODEL = os.environ.get("AGY_EVAL_MODEL", "gemini-4-argon-medium")  # `agy models` lists the ids
# memories and hooks off: the user's own Codex memories mention this project and would leak into every arm
# On Windows, subprocess("codex") can resolve to the desktop app's bundled older exe, which rejects the user's
# config.toml. Set CODEX_BIN to the native exe of the codex you actually use (e.g. the npm global one).
CODEX_BASE = [os.environ.get("CODEX_BIN", "codex"), "exec", "--skip-git-repo-check", "-s", "read-only", "--ephemeral",
              "-c", 'model_reasoning_effort="medium"', "-c", "features.memories=false",
              "-c", "memories.use_memories=false", "-c", "memories.generate_memories=false",
              "-c", "features.hooks=false"]
# Claude Code: user settings (plugins, hooks), MCP, every CLAUDE.md and auto memory stay out of all arms;
# project skills (.claude/skills/) still load. The prompt goes through stdin: a leading "/skill" argv is rewritten
# into a Windows path by Git Bash (MSYS), and long judge prompts can exceed the 32K Windows command line.
CLAUDE_MODEL = os.environ.get("CLAUDE_EVAL_MODEL", "sonnet")
CLAUDE_BASE = [os.environ.get("CLAUDE_BIN", "claude"), "-p", "--setting-sources", "project,local", "--strict-mcp-config",
               "--no-session-persistence", "--effort", "medium"]
CLAUDE_ENV = {"CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1", "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}
PREFIX = {"agy": f"/{SKILL} ", "codex": f"${SKILL} ", "claude": f"/{SKILL} "}

JUDGE_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["replies", "best"],
    "properties": {
        "best": {"type": "string"},
        "replies": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["label", "atoms_met", "directness", "readability", "tone", "fabricated"],
            "properties": {
                "label": {"type": "string"},
                "atoms_met": {"type": "array", "items": {"type": "boolean"}},
                "directness": {"type": "integer"}, "readability": {"type": "integer"},
                "tone": {"type": "integer"}, "fabricated": {"type": "boolean"}}}}}}


def dec(b: bytes) -> str:
    for enc in ("utf-8", "cp950"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            pass
    return b.decode("utf-8", "replace")


def run(cmd, cwd, timeout=300, env=None, stdin_text=None):
    io = {"input": stdin_text.encode("utf-8")} if stdin_text is not None else {"stdin": subprocess.DEVNULL}
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=timeout,
                       env={**os.environ, **env} if env else None, **io)
    return dec(p.stdout), dec(p.stderr), p.returncode


# ---------- mechanical metrics (no LLM) ----------
LIST_RE = re.compile(r"^\s*(?:[-*•]|\d+[.)、])\s+")


def list_ratio(text):
    lines = [l for l in text.splitlines() if l.strip()]
    return round(sum(bool(LIST_RE.match(l)) for l in lines) / len(lines), 3) if lines else 0.0


def mech(text, spec):
    t = text.strip()
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    checks = {}
    for i, rx in enumerate(spec.get("must_regex", [])):
        checks[f"re{i}"] = bool(re.search(rx, t))
    if "first_line_regex" in spec:
        checks["first_line"] = bool(lines and re.search(spec["first_line_regex"], lines[0]))
    if "last_line_regex" in spec:
        checks["last_line"] = bool(lines and re.search(spec["last_line_regex"], lines[-1]))
    if "max_chars" in spec:
        checks["max_chars"] = len(t) <= spec["max_chars"]
    if spec.get("json_only"):
        try:
            json.loads(t)
            checks["json_only"] = True
        except ValueError:
            checks["json_only"] = False
    return checks


def is_dup(text):
    """True when the whole answer appears twice (seen in agy output). Flag only: judges see the raw reply."""
    t = re.sub(r"\s+", "", text)
    n = len(t)
    if n < 200:
        return False
    half = difflib.SequenceMatcher(None, t[: n // 2], t[n // 2:], autojunk=False).ratio()
    k = n // 3
    return half >= 0.85 or t.find(t[:k], k) != -1


def skill_reads(tools):
    """Which files of this skill the tool log shows were read; other skills' SKILL.md files do not count."""
    return {"skill_md": any(SKILL_MD_RE.search(t) for t in tools),
            "refs": sorted({m.group(1) for t in tools for m in REF_RE.finditer(t)})}


def outside_repo(p):
    if p.resolve().is_relative_to(REPO.resolve()):
        sys.exit(f"{p} is inside the repo; agy and Codex would load the repo's AGENTS.md into every arm")


# ---------- generation ----------
def gen_agy(prompt, cwd):
    out, err, rc = run(["agy", "-p", prompt, "--model", AGY_MODEL, "--output-format", "stream-json",
                        "--print-timeout", "240s"], cwd, 300)
    reply, tools = "", []
    for l in out.splitlines():
        try:
            e = json.loads(l)
        except ValueError:
            continue
        if e.get("event") == "result":
            reply = e["result"].get("response", "")
        su = e.get("step_update") or {}
        if su.get("step_type") == "tool" and su.get("state") == "DONE":
            tools.append(json.dumps(su.get("tool_info", {}), ensure_ascii=False))
    return reply, tools, rc


def gen_codex(prompt, cwd, outfile):
    outfile.unlink(missing_ok=True)  # never read a previous call's output when this call fails
    out, err, rc = run(CODEX_BASE + ["--json", "-o", str(outfile), prompt], cwd, int(os.environ.get("CODEX_TIMEOUT", "240")))
    reply = outfile.read_text(encoding="utf-8") if outfile.exists() else ""
    tools = []
    for l in out.splitlines():
        try:
            e = json.loads(l)
        except ValueError:
            continue
        it = e.get("item") or {}
        if it.get("type") == "command_execution":
            tools.append(it.get("command", ""))
    return reply, tools, rc


def gen_claude(prompt, cwd):
    out, err, rc = run(CLAUDE_BASE + ["--model", CLAUDE_MODEL, "--output-format", "stream-json", "--verbose"],
                       cwd, 300, CLAUDE_ENV, prompt)
    reply, tools, ctx = "", [], None
    for l in out.splitlines():
        try:
            e = json.loads(l)
        except ValueError:
            continue
        if e.get("type") == "result":
            reply = e.get("result") or ""
            # a /skill prefix is expanded into the prompt, so it shows up here, not as a tool call;
            # this usage is cumulative over every model request in the call, not the context size of one request
            u = e.get("usage") or {}
            ctx = sum(u.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        elif e.get("type") == "assistant":
            for c in (e.get("message") or {}).get("content", []):
                if c.get("type") == "tool_use":
                    tools.append(json.dumps({"name": c.get("name"), "input": c.get("input")}, ensure_ascii=False))
    return reply, tools, rc, ctx


def generate(target, prompt, cwd, lastfile):
    """Returns (reply, tools, rc, ctx_tokens); ctx_tokens is None for CLIs that do not report usage here."""
    if target == "agy":
        return (*gen_agy(prompt, cwd), None)
    if target == "codex":
        return (*gen_codex(prompt, cwd, lastfile), None)
    if target == "claude":
        return gen_claude(prompt, cwd)
    raise ValueError(f"unknown target {target}")


def claude_skill_call(tools):
    return any(json.loads(t).get("name") == "Skill" and SKILL in t for t in tools) or skill_reads(tools)["skill_md"]


def gen_one(a):
    target, arm, spec, rep, work, out = a
    f = out / "gen" / f"{target}__{arm}__{spec['id']}__{rep}.json"
    if f.exists():
        return
    prompt = (PREFIX[target] if arm != "base" else "") + spec["prompt"]
    cwd = work / arm
    for attempt in range(2):
        try:
            reply, tools, rc, ctx = generate(target, prompt, cwd, f.with_suffix(".last.txt"))
        except subprocess.TimeoutExpired:
            reply, tools, rc, ctx = "", [], -1, None
        if reply.strip():
            break
    reads = skill_reads(tools)
    if target == "claude":  # the CLI expands the /skill prefix itself (headless docs); ctx_tokens lets a report audit it
        loaded = arm != "base" or claude_skill_call(tools)
    else:  # agy's /skill call can apply the skill without a logged file read, so False here may undercount
        loaded = reads["skill_md"]
    rec = dict(target=target, arm=arm, id=spec["id"], rep=rep, reply=reply, rc=rc, tools=tools,
               skill_read=loaded, refs_read=reads["refs"], ctx_tokens=ctx, dup=is_dup(reply),
               chars=len(reply.strip()), list_ratio=list_ratio(reply), mech=mech(reply, spec))
    f.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    print("gen", f.name, rec["chars"], flush=True)


def trig_one(a):
    target, arm, spec, work, out = a
    f = out / "trig" / f"{target}__{arm}__{spec['id']}.json"
    if f.exists():
        return
    try:  # no skill prefix: does the CLI load the skill on its own from the description?
        reply, tools, rc, _ = generate(target, spec["prompt"], work / arm, f.with_suffix(".last.txt"))
    except subprocess.TimeoutExpired:
        reply, tools, rc = "", [], -1
    loaded = claude_skill_call(tools) if target == "claude" else skill_reads(tools)["skill_md"]
    f.write_text(json.dumps(dict(target=target, arm=arm, id=spec["id"], expect=spec["expect"], loaded=loaded,
                                 rc=rc, tools=tools, chars=len(reply.strip())), ensure_ascii=False, indent=1), encoding="utf-8")
    print("trig", f.name, loaded, flush=True)


def trig_report(out, arms, targets):
    rows = [json.loads(f.read_text(encoding="utf-8")) for f in (out / "trig").glob("*.json")]
    L = ["| target | arm | 應觸發題載入率 | 不應觸發題載入率 | 失敗(rc≠0) |", "|---|---|---|---|---|"]
    for t in targets:
        for a in arms:
            r = [x for x in rows if x["target"] == t and x["arm"] == a]
            pos, neg = [x["loaded"] for x in r if x["expect"]], [x["loaded"] for x in r if not x["expect"]]
            L.append(f"| {t} | {a} | {sum(pos)}/{len(pos)} | {sum(neg)}/{len(neg)} | {sum(x['rc'] != 0 for x in r)} |")
    return "\n".join(L)


# ---------- judging ----------
def judge_prompt(spec, labeled):
    atoms = "\n".join(f"{i+1}. {a}" for i, a in enumerate(spec["atoms"]))
    n = len(labeled)
    reps = "\n\n".join(f"<reply label=\"{l}\">\n{r}\n</reply>" for l, r in labeled)
    return (f"你是繁體中文回覆品質的評審。下面是使用者提問與 {n} 個匿名回覆。\n\n<user_prompt>\n{spec['prompt']}\n</user_prompt>\n\n"
            f"<must_have_points>\n{atoms}\n</must_have_points>\n\n{reps}\n\n"
            "逐一評分每個回覆：\n"
            "- atoms_met：依 must_have_points 的順序，各點是否在回覆中被明確、正確地涵蓋（布林陣列，長度必須等於要點數）。\n"
            "- directness 1-5：第一句是否直接回應問題。\n"
            "- readability 1-5：結構（段落、條列、編號）是否與內容相稱，易於掃讀，沒有多餘標題、重複或贅述。\n"
            "- tone 1-5：自然、尊重、不說教，沒有空泛套語。\n"
            "- fabricated：回覆是否加入提問沒有提供、也無法由常識確定的事實、數值或步驟。\n"
            "不要因為長度或簡短本身加分或扣分。best 填整體最佳回覆的 label。"
            f"只輸出符合 JSON schema 的 JSON，replies 必須依序包含 {'、'.join(l for l, _ in labeled)} 共 {n} 個 label。")


JUDGE_INDEX = {"agy": 0, "codex": 1, "claude": 2}
AGY_JUDGE_NO_TOOLS = "\n\n不要使用任何工具，也不要執行指令或讀取檔案；只依上面提供的內容評分，直接輸出 JSON。"


def order_for(prompt_id, rep, judge, arms):
    """Cyclic Latin square: over consecutive prompts every arm takes every label position equally often,
    and each judge sees a different rotation of the same replies."""
    idx = int(re.sub(r"\D", "", prompt_id) or zlib.crc32(prompt_id.encode()))
    r = (idx + rep + JUDGE_INDEX.get(judge, 0)) % len(arms)
    return list(arms[r:]) + list(arms[:r])


def extract_json(s):
    # first complete object only: agy sometimes prints the same JSON twice, which a greedy {.*} turns into invalid JSON
    i = s.find("{")
    if i < 0:
        raise ValueError("no JSON object in judge output")
    return json.JSONDecoder().raw_decode(s[i:])[0]


def judge_one(a):
    judge, gen_target, spec, rep, arms, out, work = a
    f = out / "judge" / f"{judge}__{gen_target}__{spec['id']}__{rep}.json"
    if f.exists():
        return
    order = order_for(spec["id"], rep, judge, arms)
    reps = {}
    for arm in arms:
        reps[arm] = json.loads((out / "gen" / f"{gen_target}__{arm}__{spec['id']}__{rep}.json").read_text(encoding="utf-8"))["reply"]
    labels = list("ABCDEFG")[:len(arms)]
    mapping = dict(zip(labels, order))
    prompt = judge_prompt(spec, [(l, reps[mapping[l]]) for l in labels])
    schema = out / "judge_schema.json"
    cwd = work / "judge"
    parsed = None
    for attempt in range(2):
        try:
            if judge == "agy":
                # Gemini judges sometimes call a shell tool, which headless agy denies, and then return nothing.
                # The Claude judge runs with no tools and the Codex judge in an empty read-only dir; this line
                # puts agy on the same footing without changing the rubric.
                t = int(os.environ.get("AGY_JUDGE_TIMEOUT", "240"))
                o, e, rc = run(["agy", "-p", prompt + AGY_JUDGE_NO_TOOLS, "--model", AGY_MODEL, "--output-format", "json",
                                "--json-schema", str(schema), "--print-timeout", f"{t}s"], cwd, t + 60)
                txt = json.loads(o)["response"]
            elif judge == "claude":
                o, e, rc = run(CLAUDE_BASE + ["--model", CLAUDE_MODEL, "--tools", "", "--output-format", "json",
                                              "--json-schema", json.dumps(JUDGE_SCHEMA)], cwd, 300, CLAUDE_ENV, prompt)
                assert rc == 0, f"claude judge rc={rc}"
                r = json.loads(o)
                txt = json.dumps(r["structured_output"]) if r.get("structured_output") else r.get("result", "")
            else:
                lf = f.with_suffix(".last.txt")
                lf.unlink(missing_ok=True)  # a stale file from an earlier pass was read when codex failed (usage limit)
                _, _, rc = run(CODEX_BASE + ["--output-schema", str(schema), "-o", str(lf), prompt], cwd, 300)
                assert rc == 0, f"codex judge rc={rc}"
                txt = lf.read_text(encoding="utf-8")
            parsed = extract_json(txt)
            assert all(len(r["atoms_met"]) == len(spec["atoms"]) for r in parsed["replies"]), "atoms length"
            break
        except Exception as ex:  # noqa: BLE001 - retry once, then record the failure
            parsed = None
            err = repr(ex)
    rec = dict(judge=judge, gen_target=gen_target, id=spec["id"], rep=rep, mapping=mapping,
               result=parsed, error=None if parsed else err)
    f.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    print("judge", f.name, "ok" if parsed else "FAIL", flush=True)


# ---------- report ----------
def mean(xs):
    xs = list(xs)
    return round(sum(xs) / len(xs), 3) if xs else float("nan")


def boot_ci_raw(diffs, n=4000, seed=7):
    # percentile bootstrap; the indices are the ones every recorded CI used, so keep them for comparability
    if len(diffs) < 2:
        return (float("nan"), float("nan"))
    rnd = random.Random(seed)
    ms = sorted(sum(rnd.choice(diffs) for _ in diffs) / len(diffs) for _ in range(n))
    return (ms[int(0.025 * n)], ms[int(0.975 * n)])


def boot_ci(diffs, n=4000, seed=7):
    lo, hi = boot_ci_raw(diffs, n, seed)
    return (round(lo, 3), round(hi, 3))


def report(out, specs, arms, targets, judges, reps, skip=frozenset()):
    gens = {}
    for f in (out / "gen").glob("*.json"):
        r = json.loads(f.read_text(encoding="utf-8"))
        if (r["target"], r["id"]) in skip:
            continue
        spec = next(x for x in specs if x["id"] == r["id"])
        r["mech"] = mech(r["reply"], spec)  # recomputed with current regexes, same for every arm
        gens[(r["target"], r["arm"], r["id"], r["rep"])] = r
    scores = {}  # (judge, target, arm, id, rep) -> dict
    for f in (out / "judge").glob("*.json"):
        j = json.loads(f.read_text(encoding="utf-8"))
        if not j["result"] or (j["gen_target"], j["id"]) in skip:
            continue
        for rr in j["result"]["replies"]:
            arm = j["mapping"].get(rr["label"])
            if arm:
                natoms = len(rr["atoms_met"])
                scores[(j["judge"], j["gen_target"], arm, j["id"], j["rep"])] = dict(
                    atoms=sum(rr["atoms_met"]) / natoms, d=rr["directness"], r=rr["readability"],
                    t=rr["tone"], fab=rr["fabricated"], best=(rr["label"] == j["result"]["best"]))
    L = []

    def cell(target, arm, judge_filter=None):
        sc = [v for k, v in scores.items() if k[1] == target and k[2] == arm and (judge_filter is None or judge_filter(k[0], k[1]))]
        g = [v for k, v in gens.items() if k[0] == target and k[1] == arm]
        mp = [all(v["mech"].values()) for v in g if v["mech"]]
        mf = [sum(v["mech"].values()) / len(v["mech"]) for v in g if v["mech"]]
        return dict(n=len(g), atoms=mean(s["atoms"] for s in sc), d=mean(s["d"] for s in sc), r=mean(s["r"] for s in sc),
                    t=mean(s["t"] for s in sc), fab=mean(s["fab"] for s in sc), best=mean(s["best"] for s in sc),
                    mech=mean(mf), mech_all=mean(mp), chars=mean(v["chars"] for v in g),
                    lr=mean(v["list_ratio"] for v in g), skill=mean(v["skill_read"] for v in g),
                    ctx=mean(v["ctx_tokens"] for v in g if v.get("ctx_tokens")),
                    dup=mean(v.get("dup", is_dup(v["reply"])) for v in g))

    hdr = "| target | arm | n | atoms | direct | read | tone | fab | best | mech | mech全過 | 字數 | 條列比 | 讀 SKILL | 輸入 tokens 累計 | 整段重複 |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"
    for title, flt in (("兩位評審平均", None), ("僅交叉評審（評審不是生成者）", lambda j, t: j != t),
                       ("僅自評（評審就是生成者）", lambda j, t: j == t)):
        L += [f"### {title}", "", hdr]
        for t in targets:
            for a in arms:
                c = cell(t, a, flt)
                L.append(f"| {t} | {a} | {c['n']} | {c['atoms']} | {c['d']} | {c['r']} | {c['t']} | {c['fab']} | {c['best']} | {c['mech']} | {c['mech_all']} | {c['chars']} | {c['lr']} | {c['skill']} | {c['ctx']} | {c['dup']} |")
        L.append("")
    # paired differences on prompt level
    L += ["### 配對差（逐題，兩位評審平均；括號為 bootstrap 95% CI，只有 n 題可重抽，僅供量級參考）", "",
          "| target | 比較 | atoms | readability | directness | mech |", "|---|---|---|---|---|---|"]
    ids = [s["id"] for s in specs]

    def per_prompt(target, arm, key):
        d = {}
        for i in ids:
            vals = [v[key] for k, v in scores.items() if k[1] == target and k[2] == arm and k[3] == i]
            if vals:
                d[i] = sum(vals) / len(vals)
        return d

    def per_prompt_mech(target, arm):
        d = {}
        for i in ids:
            v = [sum(g["mech"].values()) / len(g["mech"]) for k, g in gens.items() if k[0] == target and k[1] == arm and k[2] == i and g["mech"]]
            if v:
                d[i] = sum(v) / len(v)
        return d

    for t in targets:
        for b, a in [(x, y) for x, y in itertools.permutations(arms, 2) if arms.index(x) < arms.index(y)]:
            row = []
            for key in ("atoms", "r", "d"):
                A, B = per_prompt(t, a, key), per_prompt(t, b, key)
                diffs = [A[i] - B[i] for i in A if i in B]
                row.append(f"{mean(diffs):+} {boot_ci(diffs)}")
            A, B = per_prompt_mech(t, a), per_prompt_mech(t, b)
            diffs = [A[i] - B[i] for i in A if i in B]
            row.append(f"{mean(diffs):+} {boot_ci(diffs)}")
            L.append(f"| {t} | {a} − {b} | " + " | ".join(row) + " |")
    L.append("")
    # per prompt atoms table
    L += ["### 逐題 atoms 滿足率（所有生成者與評審的分數平均）","", "| 題 | kind | " + " | ".join(arms) + " |", "|---|---|" + "---|" * len(arms)]
    for s in specs:
        cols = []
        for a in arms:
            vals = [v["atoms"] for k, v in scores.items() if k[2] == a and k[3] == s["id"]]
            cols.append(str(mean(vals)))
        L.append(f"| {s['id']} | {s['kind']} | " + " | ".join(cols) + " |")
    L.append("")
    # mechanical failures
    L += ["### 機械檢查失敗清單（非 LLM）", ""]
    for k, g in sorted(gens.items()):
        bad = [c for c, ok in g["mech"].items() if not ok]
        if bad:
            L.append(f"- {k[0]} / {k[1]} / {k[2]} / rep{k[3]}: {', '.join(bad)}")
    judge_fail = [f.name for f in (out / "judge").glob("*.json") if not json.loads(f.read_text(encoding="utf-8"))["result"]]
    L += ["", f"評審呼叫失敗：{len(judge_fail)} 次 {judge_fail[:6]}"]
    return "\n".join(L)


def selftest():
    assert list_ratio("a\n- b\n1. c\n\nd") == 0.5
    s = {"must_regex": ["百分點"], "first_line_regex": "^結論：", "last_line_regex": "^風險：", "max_chars": 20, "json_only": False}
    assert all(mech("結論：2 個百分點\n風險：低", s).values())
    assert not mech("x\n風險：低", s)["first_line"]
    assert mech('{"a": 1}', {"json_only": True})["json_only"] and not mech("```json\n{}\n```", {"json_only": True})["json_only"]
    arms = ["base", "lean", "new"]
    for j in ("codex", "claude"):  # every arm takes every position equally often over 24 prompts
        pos = [[order_for(f"g{i:02d}", 0, j, arms).index(a) for i in range(1, 25)] for a in arms]
        assert all(p.count(k) == 8 for p in pos for k in range(3)), pos
    assert order_for("g01", 0, "codex", arms) != order_for("g01", 0, "claude", arms)
    once = "暫存用來暫時保留工作中的內容，備份用來在原始資料遺失或損毀時還原資料。" * 3
    assert is_dup(once + "\n\n" + once) and not is_dup(once) and not is_dup("短答")
    assert skill_reads([r"Get-Content C:\w\.agents\skills\asd-ste100-zh-tw\SKILL.md"])["skill_md"]
    assert not skill_reads(['cat ~/.agents/skills/other-skill/SKILL.md'])["skill_md"]
    assert skill_reads(['{"file_path": ".claude/skills/asd-ste100-zh-tw/references/documents.md"}'])["refs"] == ["documents"]
    assert extract_json('x {"a": 1}\n{"a": 1}') == {"a": 1} and extract_json('{"a": {"b": 2}}') == {"a": {"b": 2}}
    # mean of 4 draws from {0,0,0,1}: count of 1s ~ Binomial(4, 1/4), CDF 0.316/0.738/0.949/0.996 -> 2.5% is 0, 97.5% is 3/4
    assert boot_ci([1 / 3] * 3) == (0.333, 0.333) and boot_ci_raw([0.0, 0.0, 0.0, 1.0]) == (0.0, 0.75)
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["setup", "gen", "judge", "report", "trigger", "trigreport", "selftest"])
    ap.add_argument("--work", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--arm", action="append", default=[], help="name=skill_dir, or name=none for base")
    ap.add_argument("--targets", default="agy,codex")
    ap.add_argument("--judges", default="agy,codex")
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--only", default="", help="comma-separated prompt ids")
    ap.add_argument("--skip", default="", help="report only: comma-separated target:prompt_id pairs to drop (e.g. failed generations)")
    ap.add_argument("--prompts", type=Path, default=HERE / "prompts.json")
    a = ap.parse_args()
    if a.stage == "selftest":
        return selftest()
    arms_def = [x.split("=", 1) for x in a.arm]
    arms = [n for n, _ in arms_def]
    specs = json.loads(a.prompts.read_text(encoding="utf-8"))
    if a.only:
        specs = [s for s in specs if s["id"] in a.only.split(",")]
    targets, judges = a.targets.split(","), a.judges.split(",")
    for p in (a.work, a.out):
        if p:
            outside_repo(p)
    if a.stage == "setup":
        snapshot = {}
        for n, src in arms_def:
            d = a.work / n
            shutil.rmtree(d, ignore_errors=True)
            d.mkdir(parents=True)
            if src != "none":
                shutil.copytree(src, d / ".agents" / "skills" / SKILL)  # agy and Codex
                shutil.copytree(src, d / ".claude" / "skills" / SKILL)  # Claude Code
                snapshot[n] = {str(f.relative_to(src)).replace("\\", "/"): hashlib.sha256(f.read_bytes()).hexdigest()
                               for f in sorted(Path(src).rglob("*")) if f.is_file()}
            else:
                snapshot[n] = None
        (a.work / "judge").mkdir(parents=True, exist_ok=True)
        (a.work / "arms.json").write_text(json.dumps(snapshot, indent=1), encoding="utf-8")  # sha256 of every file each arm saw
        return
    (a.out / "gen").mkdir(parents=True, exist_ok=True)
    (a.out / "judge").mkdir(parents=True, exist_ok=True)
    (a.out / "judge_schema.json").write_text(json.dumps(JUDGE_SCHEMA), encoding="utf-8")
    if a.stage == "gen":
        jobs = [(t, arm, s, r, a.work, a.out) for r in range(a.reps) for s in specs for arm in arms for t in targets]
        with ThreadPoolExecutor(a.jobs) as ex:
            list(ex.map(gen_one, jobs))
    elif a.stage == "trigger":
        (a.out / "trig").mkdir(exist_ok=True)
        tspecs = json.loads((HERE / "triggers.json").read_text(encoding="utf-8"))
        jobs = [(t, arm, s, a.work, a.out) for s in tspecs for arm in arms for t in targets if arm != "base"]
        with ThreadPoolExecutor(a.jobs) as ex:
            list(ex.map(trig_one, jobs))
    elif a.stage == "trigreport":
        print(trig_report(a.out, [x for x in arms if x != "base"], targets))
    elif a.stage == "judge":
        jobs = [(j, t, s, r, arms, a.out, a.work) for r in range(a.reps) for s in specs for t in targets for j in judges]
        with ThreadPoolExecutor(a.jobs) as ex:
            list(ex.map(judge_one, jobs))
    else:
        print(report(a.out, specs, arms, targets, judges, a.reps, frozenset(tuple(x.split(":")) for x in a.skip.split(",") if x)))


if __name__ == "__main__":
    sys.exit(main())
