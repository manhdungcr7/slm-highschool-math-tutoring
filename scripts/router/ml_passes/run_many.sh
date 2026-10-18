#!/bin/bash
SB="$(cd "$(dirname "$0")" && pwd)"
for o in "$@"; do
  rm -f "$SB"/data/questions/mu_logarit_extraction/bien_the/*.json
  bash "$SB/run_pass.sh" "$o"
done
echo ALL_OFFSETS_DONE > "$SB/many_done.txt"
