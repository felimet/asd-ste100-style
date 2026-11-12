"""Build the ship and len arms from the part A arm that won. Usage: build_ab_arms.py <ev4> <old|descA|descB>"""
import sys, shutil, hashlib
from pathlib import Path
ev, choice = Path(sys.argv[1]), sys.argv[2]
OLD = "使用者限定篇幅（例如「一句話」「簡單說」）時，只交付符合限制的答案；補充說明與免責聲明只在會改變答案時才附。"
NEW = ("使用者限定篇幅（例如「一句話」「簡單說」「50 字內」）時，整則回覆都要符合限制，附註、免責說明與「此處省略……」之類的句子也算在內。"
       "放不下的補充就刪除。少了它答案會變成錯的限定，壓縮主答案後放進限制內；使用者限定句數時，併入既有句子，不另起一句。"
       "「省略了什麼」「未檢查什麼」不算這類限定。")
for name in ("ship", "len"):
    d = ev / "arms" / name
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(ev / "arms" / choice, d)
p = ev / "arms" / "len" / "SKILL.md"
t = p.read_bytes().decode("utf-8")
assert t.count(OLD) == 1
p.write_bytes(t.replace(OLD, NEW).encode("utf-8"))
for name in ("ship", "len"):
    print(name, hashlib.sha256((ev / "arms" / name / "SKILL.md").read_bytes()).hexdigest())
