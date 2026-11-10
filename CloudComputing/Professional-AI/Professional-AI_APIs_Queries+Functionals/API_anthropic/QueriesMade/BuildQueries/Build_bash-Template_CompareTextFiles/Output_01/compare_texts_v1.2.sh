#!/usr/bin/env bash
# ------------------------------------------------------------------
# compare_texts_v2.sh
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
# Changes vs. v1 (which could appear to freeze):
#   - Both files are streamed line by line (no whole-file arrays).
#   - Each line is split into symbols once (linear time). v1 called
#     substr() once per symbol, which in gawk becomes extremely slow
#     on long lines that contain accented characters.
#   - Progress messages are printed, so the script never looks dead.
#   - `diff` has a time limit, and its output in the report is capped.
#
# Requires: bash, awk (gawk recommended), diff, wc, cmp, timeout.
#   Install gawk with: sudo apt install gawk
#
#
#
# ======== To run:======================
# chmod +x compare_texts_v2.sh &&
#./compare_texts_v2.sh
#
# ------------------------------------------------------------------
set -euo pipefail

IN_DIR="$HOME/Desktop/compare_files"
OUT_DIR="$HOME/Desktop/comparison_made"

MAX_ROWS=5000          # max rows in the difference table
MAX_DIFF_LINES=2000    # max lines of `diff` output kept in the report
MAX_DIFF_WIDTH=300     # long diff lines are cut to this many symbols
DIFF_TIMEOUT=120       # seconds allowed for the `diff` step

# Treat text as UTF-8 so accented letters count as one symbol
export LC_ALL=C.UTF-8

log() { echo "[$(date +%H:%M:%S)] $*" >&2; }

mkdir -p "$IN_DIR" "$OUT_DIR"

# ---- locate the two input files ----------------------------------
log "Looking for .txt files in $IN_DIR"
mapfile -t FILES < <(find "$IN_DIR" -maxdepth 1 -type f -iname '*.txt' | sort)

if [ "${#FILES[@]}" -ne 2 ]; then
  echo "Error: expected exactly 2 .txt files in $IN_DIR, found ${#FILES[@]}." >&2
  exit 1
fi

FILE_A="${FILES[0]}"
FILE_B="${FILES[1]}"
NAME_A="$(basename "$FILE_A")"
NAME_B="$(basename "$FILE_B")"
log "File A: $NAME_A ($(wc -c < "$FILE_A") bytes)"
log "File B: $NAME_B ($(wc -c < "$FILE_B") bytes)"

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_FILE="$OUT_DIR/comparison_${NAME_A%.*}_vs_${NAME_B%.*}_${STAMP}.txt"

# ---- pick awk implementation -------------------------------------
BYTEMODE=0
if command -v gawk >/dev/null 2>&1; then
  AWK=gawk
else
  AWK=awk
  BYTEMODE=1   # plain awk (mawk) works on bytes, not characters
  log "Warning: gawk not found; using '$AWK' in byte mode."
  log "         Non-ASCII symbols will be listed byte by byte as [0xHH]."
  log "         For true character comparison: sudo apt install gawk"
fi

TABLE_TMP="$(mktemp)"
SUMMARY_TMP="$(mktemp)"
DIFF_TMP="$(mktemp)"
trap 'rm -f "$TABLE_TMP" "$SUMMARY_TMP" "$DIFF_TMP"' EXIT

# ---- step 1: symbol-by-symbol comparison -------------------------
# Lines are paired by line number; within each pair, symbols are
# compared by column. Rows go to the table, totals to the summary.
log "Step 1/3: comparing symbols..."

export FILE_A FILE_B MAX_ROWS SUMMARY_TMP BYTEMODE

"$AWK" '
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

BEGIN {
  fa       = ENVIRON["FILE_A"]
  fb       = ENVIRON["FILE_B"]
  maxrows  = ENVIRON["MAX_ROWS"] + 0
  summary  = ENVIRON["SUMMARY_TMP"]
  bytemode = ENVIRON["BYTEMODE"] + 0
  if (bytemode) for (k = 0; k < 256; k++) ORD[sprintf("%c", k)] = k

  printf "%-8s %-8s %-14s %-14s\n", "LINE", "COL", "SYMBOL IN A", "SYMBOL IN B"
  printf "%-8s %-8s %-14s %-14s\n", "--------", "--------", "--------------", "--------------"

  # Read both files in lockstep, one line at a time
  while (1) {
    haveA = ((getline la < fa) > 0)
    haveB = ((getline lb < fb) > 0)
    if (!haveA && !haveB) break

    i++
    if (haveA) nA++
    if (haveB) nB++
    if (i % 100000 == 0) printf "    ... %d lines compared\n", i > "/dev/stderr"

    if (!haveA) {                         # line exists only in B
      linesOnlyB++
      row(i, "all", "(no line)", "(" length(lb) " symbols)")
      totalSyms += length(lb); continue
    }
    if (!haveB) {                         # line exists only in A
      linesOnlyA++
      row(i, "all", "(" length(la) " symbols)", "(no line)")
      totalSyms += length(la); continue
    }
    if (la == lb) {                       # identical pair
      sameLines++
      totalSyms += length(la); continue
    }

    changedLines++
    na = split(la, ca, "")                # one pass per line: linear time
    nb = split(lb, cb, "")
    m = (na > nb) ? na : nb
    totalSyms += m
    for (j = 1; j <= m; j++)
      if (ca[j] != cb[j]) row(i, j, vis(ca[j]), vis(cb[j]))
  }
  close(fa); close(fb)

  if (diffs > shown)
    printf "\n... %d more differing rows not shown (limit %d)\n", diffs - shown, maxrows

  if (totalSyms > 0) sim = 100 * (totalSyms - diffs) / totalSyms; else sim = 100
  printf "Lines in A                 : %d\n", nA + 0           > summary
  printf "Lines in B                 : %d\n", nB + 0           > summary
  printf "Identical lines            : %d\n", sameLines + 0    > summary
  printf "Lines that differ          : %d\n", changedLines + 0 > summary
  printf "Lines only in A            : %d\n", linesOnlyA + 0   > summary
  printf "Lines only in B            : %d\n", linesOnlyB + 0   > summary
  printf "Differing symbol positions : %d\n", diffs + 0        > summary
  printf "Positional similarity      : %.2f %%\n", sim         > summary
  close(summary)
}
' > "$TABLE_TMP"

# ---- step 2: alignment-aware line diff ---------------------------
log "Step 2/3: computing line diff (time limit ${DIFF_TIMEOUT}s)..."
DIFF_NOTE=""
DIFF_STATUS=0
timeout "$DIFF_TIMEOUT" diff --speed-large-files "$FILE_A" "$FILE_B" \
  > "$DIFF_TMP" 2>/dev/null || DIFF_STATUS=$?
if [ "$DIFF_STATUS" -eq 124 ]; then
  DIFF_NOTE="(diff stopped after ${DIFF_TIMEOUT}s; the files are probably very different)"
  : > "$DIFF_TMP"
fi

# ---- step 3: assemble the report ---------------------------------
log "Step 3/3: writing report..."
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
    if [ -n "$DIFF_NOTE" ]; then
      echo "$DIFF_NOTE"
    else
      head -n "$MAX_DIFF_LINES" "$DIFF_TMP" | "$AWK" -v w="$MAX_DIFF_WIDTH" '
        { if (length($0) > w) print substr($0, 1, w) " [...line cut]"; else print }'
      DIFF_TOTAL="$(wc -l < "$DIFF_TMP")"
      if [ "$DIFF_TOTAL" -gt "$MAX_DIFF_LINES" ]; then
        echo "... $((DIFF_TOTAL - MAX_DIFF_LINES)) more diff lines not shown (limit $MAX_DIFF_LINES)"
      fi
    fi
  fi
} > "$OUT_FILE"

log "Done."
echo "Comparison written to: $OUT_FILE"
