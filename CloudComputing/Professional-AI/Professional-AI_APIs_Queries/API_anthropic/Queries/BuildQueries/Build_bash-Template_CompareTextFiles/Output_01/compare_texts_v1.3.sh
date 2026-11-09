#!/usr/bin/env bash
# ------------------------------------------------------------------
# compare_texts_v3.sh
#
# Compares two .txt files and writes a report of how their wording
# differs.
#
#   Input : exactly two .txt files in  ~/Desktop/compare_files
#   Output: a .txt report in           ~/Desktop/comparison_made
#
# Report contents:
#   1. Summary (sizes, word counts, number of differences, similarity,
#      position of the first differing symbol)
#   2. Table of WORD and PHRASE differences. Both texts are split into
#      words and aligned with `diff`, so an inserted or deleted phrase
#      is reported once instead of shifting everything after it.
#   3. Alignment-aware LINE diff (standard `diff`)
#
# Options (set at the top, or on the command line, e.g.
#   IGNORE_CASE=1 IGNORE_PUNCT=1 ./compare_texts_v3.sh ):
#   IGNORE_CASE=1   treat "Fox" and "fox" as the same word
#   IGNORE_PUNCT=1  ignore punctuation at the start/end of words
#                   ("fox." = "fox"; standalone punctuation is skipped)
#
# Requires: bash, awk (gawk recommended), sed, tr, diff, wc, cmp,
#   timeout.  Install gawk with: sudo apt install gawk
#
# ======== To run:======================
# chmod +x compare_texts_v3.sh &&
#./compare_texts_v3.sh
# ------------------------------------------------------------------
set -euo pipefail

IN_DIR="$HOME/Desktop/compare_files"
OUT_DIR="$HOME/Desktop/comparison_made"

IGNORE_CASE="${IGNORE_CASE:-0}"
IGNORE_PUNCT="${IGNORE_PUNCT:-0}"

MAX_ROWS=5000          # max rows in the word/phrase table
MAX_PHRASE_WIDTH=60    # phrases in the table are cut to this many symbols
MAX_DIFF_LINES=2000    # max lines of line-diff output kept in the report
MAX_DIFF_WIDTH=300     # long line-diff lines are cut to this many symbols
DIFF_TIMEOUT=120       # seconds allowed for each `diff` step

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
  log "         Accented letters still work inside words, but case-folding"
  log "         and punctuation rules only apply to plain ASCII characters."
  log "         For full character support: sudo apt install gawk"
fi

MAP_A="$(mktemp)";  MAP_B="$(mktemp)"      # line-number<TAB>word
KEYS_A="$(mktemp)"; KEYS_B="$(mktemp)"     # normalized word, one per line
WDIFF_TMP="$(mktemp)"
TABLE_TMP="$(mktemp)"
SUMMARY_TMP="$(mktemp)"
DIFF_TMP="$(mktemp)"
trap 'rm -f "$MAP_A" "$MAP_B" "$KEYS_A" "$KEYS_B" "$WDIFF_TMP" "$TABLE_TMP" "$SUMMARY_TMP" "$DIFF_TMP"' EXIT

# ---- step 1: split both texts into words -------------------------
# Every source line gets an end-of-line marker (ASCII 0x1E), then all
# whitespace becomes a newline, so the words come out one per line.
# awk numbers the source lines and writes two parallel files:
#   map  : source line number + the word exactly as written
#   keys : the word as it is compared (case/punctuation options applied)
tokenize() {   # $1 = input file, $2 = map file, $3 = keys file
  sed 's/$/ \x1e/' "$1" | tr -s ' \t\r' '\n' |
  IGN_CASE="$IGNORE_CASE" IGN_PUNCT="$IGNORE_PUNCT" MAPF="$2" KEYF="$3" \
  "$AWK" '
    BEGIN {
      mapf = ENVIRON["MAPF"]; keyf = ENVIRON["KEYF"]
      ic = ENVIRON["IGN_CASE"] + 0; ip = ENVIRON["IGN_PUNCT"] + 0
      ln = 1
    }
    $0 == "\036" { ln++; next }        # end-of-line marker
    $0 == ""     { next }
    {
      key = $0
      if (ip) {
        gsub(/^[[:punct:]]+|[[:punct:]]+$/, "", key)
        if (key == "") next
      }
      if (ic) key = tolower(key)
      print ln "\t" $0 > mapf
      print key       > keyf
    }
    END { close(mapf); close(keyf) }
  '
}

log "Step 1/4: splitting texts into words..."
: > "$MAP_A"; : > "$KEYS_A"; : > "$MAP_B"; : > "$KEYS_B"
tokenize "$FILE_A" "$MAP_A" "$KEYS_A"
tokenize "$FILE_B" "$MAP_B" "$KEYS_B"
WORDS_A="$(wc -l < "$KEYS_A")"
WORDS_B="$(wc -l < "$KEYS_B")"
log "         $WORDS_A words in A, $WORDS_B words in B"

# ---- step 2: align the two word lists ----------------------------
log "Step 2/4: comparing words (time limit ${DIFF_TIMEOUT}s)..."
WDIFF_NOTE=""
WDIFF_STATUS=0
timeout "$DIFF_TIMEOUT" diff --speed-large-files "$KEYS_A" "$KEYS_B" \
  > "$WDIFF_TMP" 2>/dev/null || WDIFF_STATUS=$?
if [ "$WDIFF_STATUS" -eq 124 ]; then
  WDIFF_NOTE="(word comparison stopped after ${DIFF_TIMEOUT}s; the texts are probably very different)"
  : > "$WDIFF_TMP"
elif [ "$WDIFF_STATUS" -gt 1 ]; then
  WDIFF_NOTE="(word comparison failed with diff exit status $WDIFF_STATUS)"
  : > "$WDIFF_TMP"
fi

# Turn each diff block into a table row. Blocks arrive in file order,
# so the word maps are simply read forward (constant memory).
export MAP_A MAP_B MAX_ROWS MAX_PHRASE_WIDTH SUMMARY_TMP BYTEMODE WORDS_A WORDS_B

"$AWK" '
function trunc(s, w,    n, c) {
  if (length(s) <= w) return s
  n = w - 3
  if (bytemode)      # do not cut in the middle of a UTF-8 character
    while (n > 0) {
      c = substr(s, n + 1, 1)
      if ((c in ORD) && ORD[c] >= 128 && ORD[c] < 192) n--; else break
    }
  return substr(s, 1, n) "..."
}
function rd(w,    r, s, t, f) {          # read next word of file w (A or B)
  f = mapf[w]
  r = (getline s < f)
  if (r <= 0) return 0
  pos[w]++
  t = index(s, "\t")
  ln[w] = substr(s, 1, t - 1) + 0
  tk[w] = substr(s, t + 1)
  return 1
}
function skipTo(w, idx) {                # advance until pos[w] == idx
  while (pos[w] < idx) if (!rd(w)) break
}
function anchorLine(w, idx) {            # line of word number idx
  if (idx <= 0) return 0
  skipTo(w, idx)
  return ln[w]
}
function collect(w, from, to,    p, str, full) {   # words from..to as a phrase
  skipTo(w, from - 1)
  str = ""; full = 0; gfirst = 0; glast = 0
  for (p = from; p <= to; p++) {
    if (!rd(w)) break
    if (p == from) gfirst = ln[w]
    glast = ln[w]
    if (!full) {
      str = (str == "") ? tk[w] : str " " tk[w]
      if (length(str) > phrasew) full = 1
    }
  }
  gstr = trunc(str, phrasew)
}
function fmtLines(a, b) { return (a == b) ? a "" : a "-" b }
function near(n)        { return (n > 0) ? "~" n : "start" }

BEGIN {
  mapf["A"]  = ENVIRON["MAP_A"]
  mapf["B"]  = ENVIRON["MAP_B"]
  maxrows    = ENVIRON["MAX_ROWS"] + 0
  phrasew    = ENVIRON["MAX_PHRASE_WIDTH"] + 0
  summary    = ENVIRON["SUMMARY_TMP"]
  bytemode   = ENVIRON["BYTEMODE"] + 0
  totA       = ENVIRON["WORDS_A"] + 0
  totB       = ENVIRON["WORDS_B"] + 0
  if (bytemode) for (k = 0; k < 256; k++) ORD[sprintf("%c", k)] = k

  rowfmt = "%-6s %-10s %-9s %-9s %-7s %-" phrasew "s %s\n"
  printf rowfmt, "#", "TYPE", "LINE A", "LINE B", "WORDS", "TEXT IN A", "TEXT IN B"
  dash = ""
  for (k = 0; k < phrasew; k++) dash = dash "-"
  printf rowfmt, "------", "----------", "---------", "---------", "-------", dash, dash
}

# Header lines of `diff` normal format:  3c3   5,7d4   9a10,12
/^[0-9]/ {
  p  = match($0, /[acd]/)
  op = substr($0, p, 1)
  n  = split(substr($0, 1, p - 1), L, ",");  a1 = L[1] + 0;  a2 = (n > 1) ? L[2] + 0 : a1
  n  = split(substr($0, p + 1),    R, ",");  b1 = R[1] + 0;  b2 = (n > 1) ? R[2] + 0 : b1

  if (op == "a") { na = 0;            nb = b2 - b1 + 1; type = "ONLY IN B"; onlyB++ }
  else if (op == "d") { na = a2 - a1 + 1; nb = 0;       type = "ONLY IN A"; onlyA++ }
  else           { na = a2 - a1 + 1; nb = b2 - b1 + 1; type = "CHANGED";   changed++ }

  blocks++
  dA += na; dB += nb

  if (shown < maxrows) {
    if (na > 0) { collect("A", a1, a2); ta = gstr; la = fmtLines(gfirst, glast) }
    else        { ta = "-"; la = near(anchorLine("A", a1)) }
    if (nb > 0) { collect("B", b1, b2); tb = gstr; lb = fmtLines(gfirst, glast) }
    else        { tb = "-"; lb = near(anchorLine("B", b1)) }
    printf rowfmt, blocks, type, la, lb, na "/" nb, ta, tb
    shown++
  }
}

END {
  if (blocks > shown)
    printf "\n... %d more difference blocks not shown (limit %d)\n", blocks - shown, maxrows

  common = totA - dA
  if (totA + totB > 0) sim = 200 * common / (totA + totB); else sim = 100
  printf "Words in A                 : %d\n", totA          > summary
  printf "Words in B                 : %d\n", totB          > summary
  printf "Difference blocks          : %d\n", blocks + 0    > summary
  printf "  changed (word/phrase)    : %d\n", changed + 0   > summary
  printf "  only in A (removed)      : %d\n", onlyA + 0     > summary
  printf "  only in B (added)        : %d\n", onlyB + 0     > summary
  printf "Words affected in A / in B : %d / %d\n", dA + 0, dB + 0 > summary
  printf "Word-level similarity      : %.2f %%\n", sim      > summary
  close(summary)
}
' "$WDIFF_TMP" > "$TABLE_TMP"

# ---- step 3: alignment-aware line diff ---------------------------
log "Step 3/4: computing line diff (time limit ${DIFF_TIMEOUT}s)..."
DIFF_NOTE=""
DIFF_STATUS=0
timeout "$DIFF_TIMEOUT" diff --speed-large-files "$FILE_A" "$FILE_B" \
  > "$DIFF_TMP" 2>/dev/null || DIFF_STATUS=$?
if [ "$DIFF_STATUS" -eq 124 ]; then
  DIFF_NOTE="(diff stopped after ${DIFF_TIMEOUT}s; the files are probably very different)"
  : > "$DIFF_TMP"
fi

# ---- step 4: assemble the report ---------------------------------
log "Step 4/4: writing report..."
FIRST_DIFF="$(cmp "$FILE_A" "$FILE_B" 2>/dev/null | sed 's/^.* differ: //' || true)"
FIRST_DIFF="${FIRST_DIFF:-one file ends where the other continues}"

{
  echo "TEXT COMPARISON REPORT"
  echo "Generated : $(date '+%Y-%m-%d %H:%M:%S')"
  echo "File A    : $NAME_A"
  echo "File B    : $NAME_B"
  echo "Options   : ignore case = $IGNORE_CASE, ignore punctuation = $IGNORE_PUNCT"
  echo
  echo "=== 1. SUMMARY ==="
  printf "Size of A (bytes / chars)  : %s / %s\n" "$(wc -c < "$FILE_A")" "$(wc -m < "$FILE_A")"
  printf "Size of B (bytes / chars)  : %s / %s\n" "$(wc -c < "$FILE_B")" "$(wc -m < "$FILE_B")"
  printf "Lines in A / in B          : %s / %s\n" "$(wc -l < "$FILE_A")" "$(wc -l < "$FILE_B")"
  cat "$SUMMARY_TMP"
  echo
  if cmp -s "$FILE_A" "$FILE_B"; then
    echo "RESULT: the two files are IDENTICAL."
  else
    echo "RESULT: the two files DIFFER (first differing symbol: $FIRST_DIFF)."
    echo
    echo "=== 2. WORD AND PHRASE DIFFERENCES ==="
    echo "Words from both texts are aligned, so an inserted or deleted phrase is"
    echo "listed once. Each row is one block of consecutive differing words."
    echo "  TYPE   CHANGED = wording differs; ONLY IN A = removed in B; ONLY IN B = added in B"
    echo "  LINE   line(s) of the text; ~N = the spot near line N where the other"
    echo "         text has no words"
    echo "  WORDS  number of words in the block in A / in B"
    echo
    if [ -n "$WDIFF_NOTE" ]; then
      echo "$WDIFF_NOTE"
    elif [ ! -s "$WDIFF_TMP" ]; then
      echo "No word-level differences found with the current options."
      echo "(The files differ only in spacing, line breaks, case or punctuation.)"
    else
      cat "$TABLE_TMP"
    fi
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
