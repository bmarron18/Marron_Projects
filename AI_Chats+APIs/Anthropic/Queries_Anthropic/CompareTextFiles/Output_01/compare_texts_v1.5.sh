#!/usr/bin/env bash
# ------------------------------------------------------------------
# compare_texts_v4.sh   (built for comparing two translations)
#
#   Input : exactly two .txt files in  ~/Desktop/compare_files
#   Output: in ~/Desktop/comparison_made, three files sharing one name:
#             comparison_<A>_vs_<B>_<time>.txt              the report
#             comparison_<A>_vs_<B>_<time>_differences.tsv  the difference
#                 table for a spreadsheet (with empty CATEGORY / NOTES
#                 columns to fill in)
#             comparison_<A>_vs_<B>_<time>_marked.txt       the text with
#                 differences marked inline: [-old-]{+new+}
#
# Report sections:
#   1. Summary
#   2. Word and phrase differences (aligned word by word), with
#      paragraph.sentence locations, risk flags (numbers / names) and
#      the words around each difference
#   3. Line diff (standard `diff`)
#   4. Style statistics
#   5. Vocabulary comparison
#
# Options (top of the script, or on the command line, for example
#   IGNORE_CASE=1 IGNORE_PUNCT=1 ./compare_texts_v4.sh ):
#   NORMALIZE=1        clean typography before comparing: Unicode NFC,
#                      curly/straight quotes and guillemets, dashes,
#                      ellipsis, non-breaking spaces, ligatures, line
#                      endings. Set 0 to compare the raw text.
#   FIX_HYPHENATION=0  set 1 to rejoin words split across lines with a
#                      hyphen ("trans-\nlation"), typical of PDF text
#   IGNORE_CASE=0      set 1 to treat "Fox" and "fox" as the same word
#   IGNORE_PUNCT=0     set 1 to ignore punctuation around words
#   PARA_MODE=auto     how paragraphs are found: "blank" (separated by
#                      blank lines), "line" (every line is a paragraph)
#                      or "auto" (blank if the file has blank lines
#                      between text, otherwise line)
#   CONTEXT_WORDS=6    words of context shown around each difference
#   VOCAB_TOP=30       length of the vocabulary lists
#
# Requires: bash, awk (gawk recommended), sed, tr, diff, cmp, iconv,
#   timeout, sort. perl is needed only for NORMALIZE=1.
#   Install gawk with: sudo apt install gawk
#
# ======== To run:======================
# chmod +x compare_texts_v5.sh && ./compare_texts_v5.sh
#
# ------------------------------------------------------------------
set -euo pipefail

IN_DIR="$HOME/Desktop/compare_files"
OUT_DIR="$HOME/Desktop/comparison_made"

NORMALIZE="${NORMALIZE:-1}"
FIX_HYPHENATION="${FIX_HYPHENATION:-0}"
IGNORE_CASE="${IGNORE_CASE:-0}"
IGNORE_PUNCT="${IGNORE_PUNCT:-0}"
PARA_MODE="${PARA_MODE:-auto}"
CONTEXT_WORDS="${CONTEXT_WORDS:-6}"
VOCAB_TOP="${VOCAB_TOP:-30}"

MAX_ROWS=5000          # max rows in the word/phrase table of the report
MAX_PHRASE_WIDTH=50    # phrases in that table are cut to this many symbols
TSV_MAX_TEXT=2000      # phrases in the TSV are cut to this many symbols
MARK_WIDTH=100         # line width of the marked-up text
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
BASE="$OUT_DIR/comparison_${NAME_A%.*}_vs_${NAME_B%.*}_${STAMP}"
OUT_FILE="$BASE.txt"
TSV_FILE="${BASE}_differences.tsv"
MARK_FILE="${BASE}_marked.txt"

# ---- pick awk implementation -------------------------------------
BYTEMODE=0
if command -v gawk >/dev/null 2>&1; then
  AWK=gawk
else
  AWK=awk
  BYTEMODE=1   # plain awk (mawk) works on bytes, not characters
  log "Warning: gawk not found; using '$AWK' in byte mode."
  log "         Accented letters still work inside words, but capital"
  log "         accented letters, case-folding and punctuation rules only"
  log "         apply to plain ASCII characters."
  log "         For full character support: sudo apt install gawk"
fi

# ---- temporary files ---------------------------------------------
NORM_A="$(mktemp)"; NORM_B="$(mktemp)"       # normalized copies
MAP_A="$(mktemp)";  MAP_B="$(mktemp)"        # line/para/sent/first/word
KEYS_A="$(mktemp)"; KEYS_B="$(mktemp)"       # words as compared
WDIFF_TMP="$(mktemp)"
TABLE_TMP="$(mktemp)"
SUMMARY_TMP="$(mktemp)"
DIFF_TMP="$(mktemp)"
STYLE_TMP="$(mktemp)"
VOC_ONLY_A="$(mktemp)"; VOC_ONLY_B="$(mktemp)"; VOC_SHIFT="$(mktemp)"
trap 'rm -f "$NORM_A" "$NORM_B" "$NORM_A.tmp" "$NORM_B.tmp" "$MAP_A" "$MAP_B" "$KEYS_A" "$KEYS_B" "$WDIFF_TMP" "$TABLE_TMP" "$SUMMARY_TMP" "$DIFF_TMP" "$STYLE_TMP" "$VOC_ONLY_A" "$VOC_ONLY_B" "$VOC_SHIFT"' EXIT

# ---- step 1: normalize typography --------------------------------
# Translators and word processors disagree on invisible details that are
# not wording: é as one character or e + accent, curly vs straight
# quotes, guillemets, dashes, non-breaking spaces. These would show up
# as false differences, so both texts are cleaned the same way.
NORM_PL='
  $_ = NFC($_);
  s/\r//g;
  s/^\x{FEFF}//;
  s/\x{00AB}[ \x{00A0}\x{202F}]*/"/g;            # << text >>  ->  "text"
  s/[ \x{00A0}\x{202F}]*\x{00BB}/"/g;
  tr/\x{2018}\x{2019}\x{201A}\x{201B}\x{2032}/\x27/;   # single quotes
  tr/\x{201C}\x{201D}\x{201E}\x{201F}\x{2033}\x{2039}\x{203A}/"/;  # double quotes
  s/[\x{2014}\x{2015}]/ - /g;                    # em dash
  s/\x{2013}/-/g;                                # en dash
  s/\x{2026}/.../g;                              # ellipsis
  tr/\x{00A0}\x{202F}\x{2000}-\x{200A}\x{3000}/ /;     # odd spaces
  s/[\x{200B}-\x{200D}\x{2060}\x{00AD}]//g;      # invisible characters
  s/\x{FB00}/ff/g; s/\x{FB01}/fi/g; s/\x{FB02}/fl/g;
  s/\x{FB03}/ffi/g; s/\x{FB04}/ffl/g;            # ligatures
'

PERL_OK=0
if [ "$NORMALIZE" = 1 ]; then
  if command -v perl >/dev/null 2>&1 && perl -MUnicode::Normalize -e1 2>/dev/null; then
    PERL_OK=1
  else
    log "Warning: perl with Unicode::Normalize not found; comparing raw text."
    NORMALIZE=0
  fi
fi

normalize_file() {   # $1 = input file, $2 = output file
  if [ "$NORMALIZE" != 1 ]; then cp "$1" "$2"; return; fi
  if ! iconv -f UTF-8 -t UTF-8 "$1" >/dev/null 2>&1; then
    log "Warning: $(basename "$1") is not valid UTF-8; normalization skipped for it."
    cp "$1" "$2"; return
  fi
  perl -CSD -MUnicode::Normalize -pe "$NORM_PL" "$1" > "$2"
  if [ "$FIX_HYPHENATION" = 1 ]; then
    perl -CSD -0777 -pe 's/(\w)-\n([[:lower:]])/$1$2/g' "$2" > "$2.tmp"
    mv "$2.tmp" "$2"
  fi
}

log "Step 1/7: normalizing typography (NORMALIZE=$NORMALIZE)..."
normalize_file "$FILE_A" "$NORM_A"
normalize_file "$FILE_B" "$NORM_B"

# ---- step 2: split both texts into words -------------------------
# Every source line gets an end-of-line marker (ASCII 0x1E), then all
# whitespace becomes a newline, so the words come out one per line.
# awk numbers lines, paragraphs and sentences and writes two parallel
# files:
#   map  : line, paragraph, sentence, first-in-sentence flag, word
#          (the word exactly as written)
#   keys : the word as it is compared (case/punctuation options applied)
detect_para_mode() {   # $1 = file -> prints "blank" or "line"
  if [ "$PARA_MODE" != auto ]; then echo "$PARA_MODE"; return; fi
  "$AWK" '
    /[^ \t\r]/ { if (gap) { found = 1; exit } ; seen = 1; next }
    seen       { gap = 1 }
    END        { print (found ? "blank" : "line") }' "$1"
}

tokenize() {   # $1 = input file, $2 = map file, $3 = keys file, $4 = para mode
  sed 's/$/ \x1e/' "$1" | tr -s ' \t\r' '\n' |
  IGN_CASE="$IGNORE_CASE" IGN_PUNCT="$IGNORE_PUNCT" MAPF="$2" KEYF="$3" \
  PMODE="$4" BYTEMODE="$BYTEMODE" \
  "$AWK" '
    BEGIN {
      mapf = ENVIRON["MAPF"]; keyf = ENVIRON["KEYF"]
      ic = ENVIRON["IGN_CASE"] + 0; ip = ENVIRON["IGN_PUNCT"] + 0
      pmode = ENVIRON["PMODE"]; bytemode = ENVIRON["BYTEMODE"] + 0
      ln = 1; para = 1; sent = 1; ptok = 0; ltok = 0; pendPara = 0; pendSent = 0
      n = split("mr mrs ms dr prof sr sra srta dra lic ing st jr", ab, " ")
      for (i = 1; i <= n; i++) ABBR[ab[i]] = 1
    }
    $0 == "\036" {                       # end of a source line
      if (ltok == 0) { if (pmode == "blank" && ptok > 0) pendPara = 1 }
      else if (pmode == "line") pendPara = 1
      ln++; ltok = 0
      next
    }
    $0 == "" { next }
    {
      tok = $0
      key = tok
      if (ip) {
        gsub(/^[[:punct:]]+|[[:punct:]]+$/, "", key)
        if (key == "") next
      }
      if (ic) key = tolower(key)

      # --- paragraph / sentence bookkeeping ---
      sfirst = 0
      if (pendPara) {
        pendPara = 0
        if (ptok > 0) { para++; sent = 1; sfirst = 1; ptok = 0; pendSent = 0 }
      }
      if (!sfirst) {
        if (pendSent) {
          u = tok; sub(/^[[:punct:]]+/, "", u)
          if (tok ~ /^[[:punct:]]*(¿|¡)/ || u ~ /^[[:upper:][:digit:]]/ ||
              (bytemode && u != "" && u !~ /^[ -~]/)) { sent++; sfirst = 1; pendSent = 0 }
          else if (u != "") pendSent = 0     # a lowercase word: same sentence
          # a stand-alone dash or quote: decide on the next word
        } else if (ptok == 0) sfirst = 1
      }
      print ln "\t" para "\t" sent "\t" sfirst "\t" tok > mapf
      print key > keyf
      ptok++; ltok++

      # --- does this word end a sentence? ---
      if (tok ~ /[.!?]+[])"\047]*$/) {
        b = tok; sub(/[].!?)"\047]+$/, "", b)
        lb = tolower(b); sub(/^[[:punct:]]+/, "", lb)
        if (tok ~ /[?!][])"\047]*$/) pendSent = 1
        else if (!(lb in ABBR) && lb !~ /^[a-z]$/ && b !~ /\./) pendSent = 1
      }
    }
    END { close(mapf); close(keyf) }
  '
}

PMODE_A="$(detect_para_mode "$NORM_A")"
PMODE_B="$(detect_para_mode "$NORM_B")"
log "Step 2/7: splitting texts into words (paragraphs: A=$PMODE_A, B=$PMODE_B)..."
: > "$MAP_A"; : > "$KEYS_A"; : > "$MAP_B"; : > "$KEYS_B"
tokenize "$NORM_A" "$MAP_A" "$KEYS_A" "$PMODE_A"
tokenize "$NORM_B" "$MAP_B" "$KEYS_B" "$PMODE_B"
WORDS_A="$(wc -l < "$KEYS_A")"
WORDS_B="$(wc -l < "$KEYS_B")"
log "         $WORDS_A words in A, $WORDS_B words in B"

# ---- step 3: align the two word lists ----------------------------
log "Step 3/7: comparing words (time limit ${DIFF_TIMEOUT}s)..."
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

# ---- step 4: table, TSV and marked-up text -----------------------
# Each diff block becomes a table row, a TSV row and an inline mark.
# Blocks arrive in file order, so the word maps are read forward; a
# small sliding cache provides the surrounding words.
log "Step 4/7: building difference table, TSV and marked-up text..."

printf '\xef\xbb\xbf' > "$TSV_FILE"     # BOM, so Excel reads accents correctly
printf '#\tTYPE\tFLAGS\tLOC_A\tLOC_B\tLINES_A\tLINES_B\tWORDS_A\tWORDS_B\tTEXT_A\tTEXT_B\tCONTEXT_BEFORE\tCONTEXT_AFTER\tCATEGORY\tNOTES\n' >> "$TSV_FILE"

export MAP_A MAP_B MAX_ROWS MAX_PHRASE_WIDTH CONTEXT_WORDS TSV_MAX_TEXT MARK_WIDTH
export MARK_FILE TSV_FILE SUMMARY_TMP BYTEMODE WORDS_A WORDS_B NAME_A NAME_B

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
# ---- sliding cache over the word maps ----
function rd(w,    r, s, f) {               # read the next map line of file w
  f = mapf[w]
  r = (getline s < f)
  if (r <= 0) return 0
  pos[w]++
  C[w, pos[w]] = s
  delete C[w, pos[w] - win]
  return 1
}
function get(w, idx) {                     # map line of word number idx
  if (idx < 1) return ""
  while (pos[w] < idx) if (!rd(w)) return ""
  return C[w, idx]
}
function parse(s,    n, f) {
  n = split(s, f, "\t")
  gL = f[1] + 0; gP = f[2] + 0; gS = f[3] + 0; gF = f[4] + 0; gT = f[5]
}
function isName(t,    u) {
  u = t; sub(/^[^[:alnum:]]+/, "", u)
  return (u ~ /^[[:upper:]]/)
}
function ctxWords(w, from, to,    i, s, str) {
  str = ""
  if (from < 1) from = 1
  for (i = from; i <= to; i++) {
    s = get(w, i); if (s == "") break
    parse(s)
    str = (str == "") ? gT : str " " gT
  }
  return str
}
function rng(a, b)  { return (a == b) ? a "" : a "-" b }
function near(s)    { return (s == "") ? "start" : "~" s }
# ---- marked-up text ----
function note(w, s) {                      # track paragraph changes per file
  if (s == "") return
  parse(s)
  if (lastP[w] != 0 && gP != lastP[w]) brk = 1
  lastP[w] = gP
}
function emit(s,    l) {
  if (brk) { if (started) { printf "\n\n" > markf; col = 0 }; brk = 0 }
  l = length(s)
  if (col > 0 && col + 1 + l > markw) { printf "\n" > markf; col = 0 }
  if (col > 0) { printf " " > markf; col++ }
  printf "%s", s > markf
  col += l; started = 1
}
function common(fromA, toA, fromB,    k, sa, sb) {   # words present in both
  for (k = 0; k <= toA - fromA; k++) {
    sa = get("A", fromA + k); sb = get("B", fromB + k)
    note("B", sb); note("A", sa)
    parse(sa)
    emit(gT)
  }
}

BEGIN {
  mapf["A"] = ENVIRON["MAP_A"]; mapf["B"] = ENVIRON["MAP_B"]
  maxrows  = ENVIRON["MAX_ROWS"] + 0
  pw       = ENVIRON["MAX_PHRASE_WIDTH"] + 0
  ctxn     = ENVIRON["CONTEXT_WORDS"] + 0
  tsvw     = ENVIRON["TSV_MAX_TEXT"] + 0
  markw    = ENVIRON["MARK_WIDTH"] + 0
  markf    = ENVIRON["MARK_FILE"];  tsvf = ENVIRON["TSV_FILE"]
  summary  = ENVIRON["SUMMARY_TMP"]
  bytemode = ENVIRON["BYTEMODE"] + 0
  totA     = ENVIRON["WORDS_A"] + 0; totB = ENVIRON["WORDS_B"] + 0
  win      = 3 * ctxn + 50
  if (bytemode) for (k = 0; k < 256; k++) ORD[sprintf("%c", k)] = k

  rowfmt = "%-6s %-10s %-9s %-11s %-11s %-7s %-" pw "s %s\n"
  printf rowfmt, "#", "TYPE", "FLAGS", "LOC A", "LOC B", "WORDS", "TEXT IN A", "TEXT IN B"
  dash = ""; for (k = 0; k < pw; k++) dash = dash "-"
  printf rowfmt, "------", "----------", "---------", "-----------", "-----------", "-------", dash, dash

  printf "MARKED-UP COMPARISON\n" > markf
  printf "A = %s    B = %s\n", ENVIRON["NAME_A"], ENVIRON["NAME_B"] > markf
  printf "[-text only in A-]   {+text only in B+}   [-A wording-]{+B wording+}\n" > markf
  printf "Paragraph breaks come from either text. Text is shown as normalized.\n\n" > markf
}

# Header lines of `diff` normal format:  3c3   5,7d4   9a10,12
/^[0-9]/ {
  p  = match($0, /[acd]/)
  op = substr($0, p, 1)
  n  = split(substr($0, 1, p - 1), L, ",");  a1 = L[1] + 0;  a2 = (n > 1) ? L[2] + 0 : a1
  n  = split(substr($0, p + 1),    R, ",");  b1 = R[1] + 0;  b2 = (n > 1) ? R[2] + 0 : b1

  if (op == "a")      { na = 0;           nb = b2 - b1 + 1; type = "ONLY IN B"; onlyB++ }
  else if (op == "d") { na = a2 - a1 + 1; nb = 0;           type = "ONLY IN A"; onlyA++ }
  else                { na = a2 - a1 + 1; nb = b2 - b1 + 1; type = "CHANGED";   changed++ }
  blocks++
  dA += na; dB += nb

  # words shared with the previous block, then the words before this one
  endCA = (op == "a") ? a1 : a1 - 1
  if (endCA > prevA) common(prevA + 1, endCA, prevB + 1)
  bEnd = (na > 0) ? a1 - 1 : a1
  cb = ctxWords("A", bEnd - ctxn + 1, bEnd)
  if (bEnd < 1) cb = "(start)"

  hasNum = 0; hasName = 0
  sa = ""; slA = 0; sb = ""; slB = 0; held = ""

  # ---- words of this block in A ----
  for (i = a1; na > 0 && i <= a2; i++) {
    s = get("A", i); note("A", s)
    if (i == a1) { fpA = gP "." gS; flA = gL }
    lpA = gP "." gS; llA = gL
    if (gT ~ /[0-9]/) hasNum = 1
    if (!gF && isName(gT)) hasName = 1
    if (slA <= tsvw) { sa = (sa == "") ? gT : sa " " gT; slA += length(gT) + 1 }
    t = gT
    if (i == a1) t = "[-" t
    if (i == a2) { if (nb > 0) held = t; else t = t "-]" }
    if (!(i == a2 && nb > 0)) emit(t)
  }
  # ---- words of this block in B ----
  for (j = b1; nb > 0 && j <= b2; j++) {
    s = get("B", j); note("B", s)
    if (j == b1) { fpB = gP "." gS; flB = gL }
    lpB = gP "." gS; llB = gL
    if (gT ~ /[0-9]/) hasNum = 1
    if (!gF && isName(gT)) hasName = 1
    if (slB <= tsvw) { sb = (sb == "") ? gT : sb " " gT; slB += length(gT) + 1 }
    t = gT
    if (j == b1) t = (na > 0) ? held "-]{+" t : "{+" t
    if (j == b2) t = t "+}"
    emit(t)
  }

  # ---- locations for blocks that exist in one text only ----
  if (na == 0) {                           # insertion point in A
    s = get("A", a1)
    if (s == "") { locA = "start"; linA = "start" }
    else { parse(s); locA = near(gP "." gS); linA = near(gL) }
  } else { locA = rng(fpA, lpA); linA = rng(flA, llA) }
  if (nb == 0) {
    s = get("B", b1)
    if (s == "") { locB = "start"; linB = "start" }
    else { parse(s); locB = near(gP "." gS); linB = near(gL) }
  } else { locB = rng(fpB, lpB); linB = rng(flB, llB) }

  # ---- context after the block (read from A) ----
  aStart = (na > 0) ? a2 + 1 : a1 + 1
  ca = ctxWords("A", aStart, aStart + ctxn - 1)
  if (ca == "") ca = "(end)"

  prevA = (na > 0) ? a2 : a1
  prevB = (nb > 0) ? b2 : b1

  flags = ""
  if (hasNum)  { flags = "NUM"; nNum++ }
  if (hasName) { flags = flags (flags == "" ? "" : ",") "NAME"; nName++ }
  if (flags == "") flags = "-"

  if (shown < maxrows) {
    ta = (na > 0) ? trunc(sa, pw) : "-"
    tb = (nb > 0) ? trunc(sb, pw) : "-"
    printf rowfmt, blocks, type, flags, locA, locB, na "/" nb, ta, tb
    printf "       in context: %s | %s\n", trunc(cb, 60), trunc(ca, 60)
    shown++
  }
  fl2 = (flags == "-") ? "" : flags
  tsA = (slA > tsvw) ? sa " ..." : sa
  tsB = (slB > tsvw) ? sb " ..." : sb
  printf "%d\t%s\t%s\t%s\t%s\t%s\t%s\t%d\t%d\t%s\t%s\t%s\t%s\t\t\n", blocks, type, fl2, locA, locB, linA, linB, na, nb, tsA, tsB, cb, ca >> tsvf
}

END {
  if (totA > prevA) common(prevA + 1, totA, prevB + 1)
  printf "\n" > markf
  close(markf); close(tsvf); close(mapf["A"]); close(mapf["B"])

  if (blocks > shown)
    printf "\n... %d more difference blocks not shown here (limit %d); all of them are in the TSV file\n", blocks - shown, maxrows

  common_words = totA - dA
  if (totA + totB > 0) sim = 200 * common_words / (totA + totB); else sim = 100
  printf "Words in A                 : %d\n", totA          > summary
  printf "Words in B                 : %d\n", totB          > summary
  printf "Difference blocks          : %d\n", blocks + 0    > summary
  printf "  changed (word/phrase)    : %d\n", changed + 0   > summary
  printf "  only in A (removed)      : %d\n", onlyA + 0     > summary
  printf "  only in B (added)        : %d\n", onlyB + 0     > summary
  printf "  flagged NUM (digits)     : %d\n", nNum + 0      > summary
  printf "  flagged NAME (capitals)  : %d\n", nName + 0     > summary
  printf "Words affected in A / in B : %d / %d\n", dA + 0, dB + 0 > summary
  printf "Word-level similarity      : %.2f %%\n", sim      > summary
  close(summary)
}
' "$WDIFF_TMP" > "$TABLE_TMP"

# ---- step 5: style statistics and vocabulary ---------------------
log "Step 5/7: computing style statistics and vocabulary..."

export VOC_ONLY_A VOC_ONLY_B VOC_SHIFT
"$AWK" '
function closeSent(w) {
  if (slen > 0) { sents[w]++; if (slen > maxs[w]) maxs[w] = slen; slen = 0 }
}
function scan(w, f,    s, n, fld, tok, key, tmp) {
  slen = 0
  while ((getline s < f) > 0) {
    n = split(s, fld, "\t")
    tok = fld[5]
    if (fld[2] + 0 > paras[w]) paras[w] = fld[2] + 0
    if (fld[4] + 0) closeSent(w)
    key = tok
    gsub(/^[[:punct:]]+|[[:punct:]]+$/, "", key)
    if (key == "") continue
    key = tolower(key)
    tot[w]++; slen++
    chars[w] += length(key)
    if (cnt[w, key]++ == 0) { uniq[w]++; voc[key] = 1 }
    tmp = tok; commas[w] += gsub(/,/, "", tmp)
  }
  closeSent(w)
  close(f)
}
function pct(a, b) { return (a > 0) ? sprintf("%+.1f%%", 100 * (b - a) / a) : "n/a" }
function srow(label, fmt, a, b) {
  printf "%-36s %14s %14s %10s\n", label, sprintf(fmt, a), sprintf(fmt, b), pct(a, b)
}
function ratio(a, b) { return (b > 0) ? a / b : 0 }

BEGIN {
  scan("A", ENVIRON["MAP_A"]); scan("B", ENVIRON["MAP_B"])
  onlyA = ENVIRON["VOC_ONLY_A"]; onlyB = ENVIRON["VOC_ONLY_B"]; shiftf = ENVIRON["VOC_SHIFT"]

  for (k in voc) {
    ca = (("A", k) in cnt) ? cnt["A", k] : 0
    cb = (("B", k) in cnt) ? cnt["B", k] : 0
    if (ca == 1) hap["A"]++
    if (cb == 1) hap["B"]++
    if (cb == 0)      printf "%s\t%d\n", k, ca > onlyA
    else if (ca == 0) printf "%s\t%d\n", k, cb > onlyB
    else if (ca + cb >= 6) {
      # count in B compared with what B would have if it used the word
      # at the same rate as A (corrects for one text being longer)
      expc = ca * tot["B"] / tot["A"]
      d = cb - expc
      ad = (d < 0) ? -d : d
      printf "%.2f\t%s\t%d\t%d\t%.1f\n", ad, k, ca, cb, expc > shiftf
    }
  }
  close(onlyA); close(onlyB); close(shiftf)

  printf "%-36s %14s %14s %10s\n", "", "TEXT A", "TEXT B", "B vs A"
  printf "%-36s %14s %14s %10s\n", "", "--------------", "--------------", "----------"
  srow("Words",                          "%d",   tot["A"], tot["B"])
  srow("Paragraphs",                     "%d",   paras["A"], paras["B"])
  srow("Sentences",                      "%d",   sents["A"], sents["B"])
  srow("Words per paragraph",            "%.1f", ratio(tot["A"], paras["A"]), ratio(tot["B"], paras["B"]))
  srow("Words per sentence (average)",   "%.1f", ratio(tot["A"], sents["A"]), ratio(tot["B"], sents["B"]))
  srow("Longest sentence (words)",       "%d",   maxs["A"], maxs["B"])
  srow("Word length (average, symbols)", "%.2f", ratio(chars["A"], tot["A"]), ratio(chars["B"], tot["B"]))
  srow("Different words used",           "%d",   uniq["A"], uniq["B"])
  srow("Different / total words (%)",    "%.1f", 100 * ratio(uniq["A"], tot["A"]), 100 * ratio(uniq["B"], tot["B"]))
  srow("Words used only once (% of diff.)", "%.1f", 100 * ratio(hap["A"], uniq["A"]), 100 * ratio(hap["B"], uniq["B"]))
  srow("Commas per 100 words",           "%.2f", 100 * ratio(commas["A"], tot["A"]), 100 * ratio(commas["B"], tot["B"]))
}
' > "$STYLE_TMP"

# ---- step 6: line diff -------------------------------------------
log "Step 6/7: computing line diff (time limit ${DIFF_TIMEOUT}s)..."
DIFF_NOTE=""
DIFF_STATUS=0
timeout "$DIFF_TIMEOUT" diff --speed-large-files "$NORM_A" "$NORM_B" \
  > "$DIFF_TMP" 2>/dev/null || DIFF_STATUS=$?
if [ "$DIFF_STATUS" -eq 124 ]; then
  DIFF_NOTE="(diff stopped after ${DIFF_TIMEOUT}s; the files are probably very different)"
  : > "$DIFF_TMP"
fi

# ---- step 7: assemble the report ---------------------------------
log "Step 7/7: writing report..."
FIRST_DIFF="$(cmp "$NORM_A" "$NORM_B" 2>/dev/null | sed 's/^.* differ: //' || true)"
FIRST_DIFF="${FIRST_DIFF:-one file ends where the other continues}"

TAB="$(printf '\t')"
side_by_side() {   # $1 = "only A" file, $2 = "only B" file (word<TAB>count)
  local a b
  a="$(mktemp)"; b="$(mktemp)"
  sort -t "$TAB" -k2,2nr -k1,1 "$1" | head -n "$VOCAB_TOP" > "$a"
  sort -t "$TAB" -k2,2nr -k1,1 "$2" | head -n "$VOCAB_TOP" > "$b"
  printf '%-28s %6s     %-28s %6s\n' "ONLY IN A" "COUNT" "ONLY IN B" "COUNT"
  printf '%-28s %6s     %-28s %6s\n' "----------------------------" "------" "----------------------------" "------"
  "$AWK" -F "$TAB" '
    NR == FNR { wa[FNR] = $1; ca[FNR] = $2; na = FNR; next }
              { wb[FNR] = $1; cb[FNR] = $2; nb = FNR }
    END {
      n = (na > nb) ? na : nb
      for (i = 1; i <= n; i++)
        printf "%-28s %6s     %-28s %6s\n", wa[i], ca[i], wb[i], cb[i]
    }' "$a" "$b"
  rm -f "$a" "$b"
}

{
  echo "TEXT COMPARISON REPORT"
  echo "Generated : $(date '+%Y-%m-%d %H:%M:%S')"
  echo "File A    : $NAME_A"
  echo "File B    : $NAME_B"
  echo "Options   : normalize = $NORMALIZE, fix hyphenation = $FIX_HYPHENATION, ignore case = $IGNORE_CASE, ignore punctuation = $IGNORE_PUNCT"
  echo "Also written (same folder):"
  echo "  $(basename "$TSV_FILE")   all differences, for a spreadsheet"
  echo "  $(basename "$MARK_FILE")   text with inline marks [-old-]{+new+}"
  echo
  echo "=== 1. SUMMARY ==="
  printf "Size of A (bytes / chars)  : %s / %s\n" "$(wc -c < "$FILE_A")" "$(wc -m < "$FILE_A")"
  printf "Size of B (bytes / chars)  : %s / %s\n" "$(wc -c < "$FILE_B")" "$(wc -m < "$FILE_B")"
  printf "Lines in A / in B          : %s / %s\n" "$(wc -l < "$FILE_A")" "$(wc -l < "$FILE_B")"
  cat "$SUMMARY_TMP"
  echo
  if cmp -s "$NORM_A" "$NORM_B"; then
    if cmp -s "$FILE_A" "$FILE_B"; then
      echo "RESULT: the two files are IDENTICAL."
    else
      echo "RESULT: the two files are IDENTICAL after normalization (they differ only in"
      echo "        typography, invisible characters or line endings)."
    fi
  else
    echo "RESULT: the two files DIFFER (first differing symbol: $FIRST_DIFF)."
    echo
    echo "=== 2. WORD AND PHRASE DIFFERENCES ==="
    echo "Words from both texts are aligned, so an inserted or deleted phrase is"
    echo "listed once. Each row is one block of consecutive differing words."
    echo "  TYPE   CHANGED = wording differs; ONLY IN A = removed in B; ONLY IN B = added in B"
    echo "  FLAGS  NUM = the block contains digits (numbers, dates);"
    echo "         NAME = it contains a capitalized word inside a sentence (likely a name)."
    echo "         Check these first: they are the likeliest real mistranslations."
    echo "  LOC    paragraph.sentence in each text (3.2 = paragraph 3, sentence 2);"
    echo "         ~3.2 = the spot near there where the other text has no words"
    echo "  WORDS  number of words in the block in A / in B"
    echo "  in context: the words just before | and after the block"
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
  echo
  echo "=== 4. STYLE STATISTICS ==="
  echo "Words here exclude stand-alone punctuation marks. Sentences are detected by"
  echo "punctuation, so treat sentence figures as estimates."
  echo "Different/total words depends on text length, so compare it only for texts"
  echo "of similar length."
  echo
  cat "$STYLE_TMP"
  echo
  echo "=== 5. VOCABULARY COMPARISON ==="
  echo "Words are compared in lower case without surrounding punctuation. Each"
  echo "inflected form counts as a separate word (walk / walked / walking)."
  echo
  echo "--- Words used by only one translation (top $VOCAB_TOP by frequency) ---"
  side_by_side "$VOC_ONLY_A" "$VOC_ONLY_B"
  echo
  echo "--- Shared words used noticeably more in one text (top $VOCAB_TOP) ---"
  echo "EXPECTED = how often B would use the word if it used it at A's rate,"
  echo "given the length of the two texts. Words appearing 6+ times in total only."
  echo
  printf '%-28s %8s %8s %10s %10s\n' "WORD" "COUNT A" "COUNT B" "EXPECTED B" "B - EXP."
  printf '%-28s %8s %8s %10s %10s\n' "----------------------------" "--------" "--------" "----------" "----------"
  sort -t "$TAB" -k1,1gr "$VOC_SHIFT" | head -n "$VOCAB_TOP" | "$AWK" -F "$TAB" '
    { printf "%-28s %8d %8d %10.1f %+10.1f\n", $2, $3, $4, $5, $4 - $5 }'
} > "$OUT_FILE"

log "Done."
echo "Report      : $OUT_FILE"
echo "TSV         : $TSV_FILE"
echo "Marked text : $MARK_FILE"
