#!/bin/bash
# usage: run_pass.sh OFFSET   -- reruns every Mũ-Logarit generator with the seeds shifted by OFFSET
SB="$(cd "$(dirname "$0")" && pwd)"
OFF="${1:-1}"
cd "$SB"
export SEED_OFFSET="$OFF"
export PYTHONPATH="$SB/patch"
export PYTHONIOENCODING=utf-8
export PYTHONHASHSEED="$OFF"
mkdir -p "data/questions/mu_logarit_extraction/bien_the"
LOG="$SB/log_pass_${OFF}.txt"
: > "$LOG"
for s in 11_generate_D01 12_generate_D12 13_generate_D18 14_generate_D53 15_generate_identities_A 16_generate_identities_B \
         17_generate_basic_eq 18_generate_counting 19_generate_identities_C 23_generate_round2 24_generate_round3 \
         25_generate_round4 26_generate_round5 27_generate_round6 28_generate_round7 29_generate_round8 30_generate_round9 \
         32_generate_round10_shortfalls; do
  t0=$(date +%s)
  echo "=== $s start" >> "$LOG"
  python "scripts/generate_questions/$s.py" >> "$LOG" 2>&1
  echo "=== $s exit=$? seconds=$(( $(date +%s) - t0 ))" >> "$LOG"
done
echo "=== ALL DONE" >> "$LOG"
mkdir -p "$SB/passes/offset_${OFF}"
cp "$SB"/data/questions/mu_logarit_extraction/bien_the/*.json "$SB/passes/offset_${OFF}/" 2>/dev/null
echo "=== COPIED" >> "$LOG"
