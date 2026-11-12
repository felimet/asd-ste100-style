#!/usr/bin/env bash
set -u
# E4/arms/{ship,len}: built by `python build_ab_arms.py $E4 <part A choice>`. Usage: E4=<scratch> CODEX_BIN=<codex.exe> bash run_ab.sh
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
C=(--work "$E4/abwork" --out "$E4/about" --arm "ship=$E4/arms/ship" --arm "len=$E4/arms/len"
   --prompts "$W/tests/eval/heldout3-prompts.json" --reps 3)
for a in ship len; do [ -f "$E4/arms/$a/SKILL.md" ] || { echo "arm $a missing: run build_ab_arms.py first"; exit 1; }; done
[ -f "$E4/abwork/arms.json" ] || "${PY[@]}" setup "${C[@]}" || { echo "SETUP FAILED"; exit 1; }
for pass in 1 2; do  # a rerun retries rc != 0 and empty replies in both passes
  echo "== gen pass $pass $(date +%T)"
  [ -d "$E4/about/gen" ] && clean "$E4/about" gen
  ( "${PY[@]}" gen "${C[@]}" --targets agy --jobs 3 ) &
  ( "${PY[@]}" gen "${C[@]}" --targets codex --jobs 2 ) &
  ( "${PY[@]}" gen "${C[@]}" --targets claude --jobs 3 ) &
  wait
done
stat=$(python -I -X utf8 -c "
import json,glob,sys
g=[json.load(open(f,encoding='utf-8')) for f in glob.glob(sys.argv[1]+'/gen/*.json')]
print(len(g), sum(x['rc']!=0 for x in g), sum(x['rc']==0 and not x['reply'].strip() for x in g))" "$E4/about")
read ngen nrc nempty <<< "$stat"
echo "gen records: $ngen, rc!=0: $nrc, empty kept for judging: $nempty"
if [ "$nrc" != 0 ] || [ "$ngen" != 324 ]; then echo "GEN INCOMPLETE: rerun later"; exit 3; fi
for pass in 1 2; do
  echo "== judge pass $pass $(date +%T)"
  [ -d "$E4/about/judge" ] && clean "$E4/about" judge
  ( "${PY[@]}" judge "${C[@]}" --targets agy --judges codex --jobs 2
    "${PY[@]}" judge "${C[@]}" --targets claude --judges codex --jobs 2 ) &
  ( "${PY[@]}" judge "${C[@]}" --targets claude --judges agy --jobs 3
    "${PY[@]}" judge "${C[@]}" --targets codex --judges agy --jobs 3 ) &
  ( "${PY[@]}" judge "${C[@]}" --targets agy --judges claude --jobs 3
    "${PY[@]}" judge "${C[@]}" --targets codex --judges claude --jobs 3 ) &
  wait
done
python -I -X utf8 -c "
import json,glob,sys
j=[json.load(open(f,encoding='utf-8')) for f in glob.glob(sys.argv[1]+'/judge/*.json')]
print('judge records:', len(j), '(expect 324), failed:', sum(not x['result'] for x in j))" "$E4/about"
"${PY[@]}" report "${C[@]}" --targets agy,codex,claude --judges agy,codex,claude > "$E4/ab_report.md"
echo "done $(date +%T)"
