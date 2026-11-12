#!/usr/bin/env bash
set -u
# E4/arms/{old,descA,descB}: the commit 2881cf4 skill folder with SKILL.md line 4 set to the description in
# heldout3-protocol.md (sha256 listed there). Usage: E4=<scratch> CODEX_BIN=<codex.exe> bash run_trig.sh
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
C=(--work "$E4/twork" --out "$E4/tout" --arm "old=$E4/arms/old" --arm "descA=$E4/arms/descA" --arm "descB=$E4/arms/descB"
   --triggers "$W/tests/eval/triggers2.json")
[ -f "$E4/twork/arms.json" ] || "${PY[@]}" setup "${C[@]}" || { echo "SETUP FAILED"; exit 1; }
for pass in 1 2; do
  echo "== trigger pass $pass $(date +%T)"
  [ -d "$E4/tout/trig" ] && clean "$E4/tout" trig
  ( "${PY[@]}" trigger "${C[@]}" --targets agy --jobs 3 ) &
  ( "${PY[@]}" trigger "${C[@]}" --targets codex --jobs 2 ) &
  ( "${PY[@]}" trigger "${C[@]}" --targets claude --jobs 3 ) &
  wait
done
echo "trig records: $(ls "$E4/tout/trig"/*.json | wc -l) (expect 216)"
"${PY[@]}" trigreport "${C[@]}" --targets agy,codex,claude > "$E4/trig_report.md"
echo "done $(date +%T)"
