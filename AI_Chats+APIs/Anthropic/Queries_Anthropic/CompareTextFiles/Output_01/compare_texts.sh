#!/usr/bin/env bash
# ------------------------------------------------------------------
# compare_texts.sh
#
# Compares two .txt files symbol by symbol and writes a report with a
# table of the differences.
#
#   Input : exactly two .txt files in  ~/Desktop/compare_files
#   Output: a .txt report in           ~/Desktop/comparison_made
#
# Report contents:
#   1. Summary (sizes, line/character counts, number of differences)
#   2. Table of differences, position by position (line, column,
#      symbol in file A, symbol in file B)
#   3. Alignment-aware line diff (standard `diff`), useful when text
#      was inserted or deleted and everything after it shifted
#
# Requires: bash, gawk (recommended, for UTF-8 aware character
# handling), diff, wc, cmp.  Install gawk with: sudo apt install gawk
#
# ======== To run:======================
# chmod +x compare_texts.sh &&
#./compare_texts.sh
# ------------------------------------------------------------------
set -euo pipefail

IN_DIR="$HOME/Desktop/compare_files"
OUT_DIR="$HOME/Desktop/comparison_made"
MAX_ROWS=5000        # cap on table rows, to keep the report readable

# Treat text as UTF-8 so accented letters etc. count as one symbol
export LC_ALL=C.UTF-8

mkdir -p "$IN_DIR" "$OUT_DIR"

# ---- locate the two input files ----------------------------------
mapfile -t FILES < <(find "$IN_DIR" -maxdepth 1 -type f -iname '*.txt' | sort)

if [ "${#FILES[@]}" -ne 2 ]; then
  echo "Error: expected exactly 2 .txt files in $IN_DIR, found ${#FILES[@]}." >&2
  exit 1
fi

FILE_A="${FILES[0]}"
FILE_B="${FILES[1]}"
NAME_A="$(basename "$FILE_A")"
NAME_B="$(basename "$FILE_B")"

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_FILE="$OUT_DIR/comparison_${NAME_A%.*}_vs_${NAME_B%.*}_${STAMP}.txt"

# ---- pick awk implementation -------------------------------------
BYTEMODE=0
if command -v gawk >/dev/null 2>&1; then
  AWK=gawk
else
  AWK=awk
  BYTEMODE=1   # plain awk (mawk) works on bytes, not characters
  echo "Warning: gawk not found; falling back to '$AWK' (byte mode)." >&2
  echo "         Non-ASCII symbols will be listed byte by byte as [0xHH]." >&2
  echo "         For true character comparison: sudo apt install gawk" >&2
fi

TABLE_TMP="$(mktemp)"
SUMMARY_TMP="$(mktemp)"
trap 'rm -f "$TABLE_TMP" "$SUMMARY_TMP"' EXIT

# ---- symbol-by-symbol comparison (awk) ---------------------------
# Lines are paired by line number; within each pair, symbols are
# compared by column. Rows are written to the table; totals to the
# summary file.
"$AWK" -v maxrows="$MAX_ROWS" -v summary="$SUMMARY_TMP" -v bytemode="$BYTEMODE" '
BEGIN {
  if (bytemode) for (k = 0; k < 256; k++) ORD[sprintf("%c", k)] = k
}
function vis(c) {
  if (c == "")   return "(none)"
  if (c == " ")  return "[SPACE]"
  if (c == "\t") return "[TAB]"
  if (c == "\r") return "[CR]"
  if (bytemode && (c in ORD) && (ORD[c] < 32 || ORD[c] > 126))
    return sprintf("[0x%02X]", ORD[c])
  return c
}
function row(line, col, a, b) {
  diffs++
  if (shown < maxrows) {
    printf "%-8s %-8s %-14s %-14s\n", line, col, a, b
    shown++
  }
}

FILENAME == ARGV[1] { A[FNR] = $0; nA = FNR; next }
                    { B[FNR] = $0; nB = FNR }

END {
  n = (nA > nB) ? nA : nB
  printf "%-8s %-8s %-14s %-14s\n", "LINE", "COL", "SYMBOL IN A", "SYMBOL IN B"
  printf "%-8s %-8s %-14s %-14s\n", "--------", "--------", "--------------", "--------------"

  for (i = 1; i <= n; i++) {
    if (i > nA) {                       # line exists only in B
      linesOnlyB++
      row(i, "all", "(no line)", "(" length(B[i]) " symbols)")
      totalSyms += length(B[i]); continue
    }
    if (i > nB) {                       # line exists only in A
      linesOnlyA++
      row(i, "all", "(" length(A[i]) " symbols)", "(no line)")
      totalSyms += length(A[i]); continue
    }
    la = length(A[i]); lb = length(B[i])
    m = (la > lb) ? la : lb
    totalSyms += m
    if (A[i] == B[i]) { sameLines++; continue }
    changedLines++
    for (j = 1; j <= m; j++) {
      ca = substr(A[i], j, 1); cb = substr(B[i], j, 1)
      if (ca != cb) row(i, j, vis(ca), vis(cb))
    }
  }

  if (diffs > shown)
    printf "\n... %d more differing rows not shown (limit %d)\n", diffs - shown, maxrows

  if (totalSyms > 0) sim = 100 * (totalSyms - diffs) / totalSyms; else sim = 100
  printf "Lines in A                 : %d\n", nA        > summary
  printf "Lines in B                 : %d\n", nB        > summary
  printf "Identical lines            : %d\n", sameLines + 0     > summary
  printf "Lines that differ          : %d\n", changedLines + 0  > summary
  printf "Lines only in A            : %d\n", linesOnlyA + 0    > summary
  printf "Lines only in B            : %d\n", linesOnlyB + 0    > summary
  printf "Differing symbol positions : %d\n", diffs + 0         > summary
  printf "Positional similarity      : %.2f %%\n", sim          > summary
}
' "$FILE_A" "$FILE_B" > "$TABLE_TMP"

# ---- assemble the report -----------------------------------------
{
  echo "TEXT COMPARISON REPORT"
  echo "Generated : $(date '+%Y-%m-%d %H:%M:%S')"
  echo "File A    : $NAME_A"
  echo "File B    : $NAME_B"
  echo
  echo "=== 1. SUMMARY ==="
  printf "Size of A (bytes / chars)  : %s / %s\n" "$(wc -c < "$FILE_A")" "$(wc -m < "$FILE_A")"
  printf "Size of B (bytes / chars)  : %s / %s\n" "$(wc -c < "$FILE_B")" "$(wc -m < "$FILE_B")"
  cat "$SUMMARY_TMP"
  echo
  if cmp -s "$FILE_A" "$FILE_B"; then
    echo "RESULT: the two files are IDENTICAL."
  else
    echo "RESULT: the two files DIFFER."
    echo
    echo "=== 2. TABLE OF DIFFERENCES (position by position) ==="
    echo "Lines are paired by number, symbols by column. After an insertion or"
    echo "deletion, later text shifts and shows up as many differences; see"
    echo "section 3 for an alignment-aware view."
    echo
    cat "$TABLE_TMP"
    echo
    echo "=== 3. LINE DIFF (alignment-aware) ==="
    echo "'<' = line only in A (or changed, A version), '>' = line only in B"
    echo
    diff "$FILE_A" "$FILE_B" || true
  fi
} > "$OUT_FILE"

echo "Comparison written to: $OUT_FILE"
