#!/usr/bin/env python3


"""
Created on Sat Oct 31 14:55:18 2026
Modified: 19 Nov 2026

@author: bruce-vdb, claude

---------------------------------
Calculate_LatLon_cell_areas_v1.3.py
---------------------------------
Calculates the area of the lat/lon "uncertainty cell" implied by each coordinate's precision.


Reads a file like LatLon.txt (columns: Lat, Lon, Dimension) where coordinates
are written as degrees [minutes [seconds]], e.g. "19 11 25.8" / "-100 05 18.2".
The last component given sets the cell size: 1 deg, 1 min, 1 sec, 0.1 sec...
(i.e. one unit of the last digit written). The cell extends from the stated
point away from zero in both latitude and longitude (north/west here).

Areas are computed on the WGS84 ellipsoid. If pyproj is installed it is used
(geodesic polygon area); otherwise an exact closed-form equal-area formula
is used, which gives the same answer.

v1.2: file access and reading are explicit and reported (path, size, a
      line-by-line ACCEPTED/SKIPPED report, summary, clear error messages).
v1.3: made for running in Spyder from a venv.
  - settings are constants in the SETTINGS block below (no command-line
    arguments needed: just press Run)
  - input files are looked for in INPUT_DIR (your Desktop), NOT in the
    current working directory or the script's folder; a full path still works
  - the output file defaults to <input name>_areas.txt in the same folder
  - errors are printed and the script stops cleanly (no SystemExit message
    in the IPython console)
  - the script refuses to write its output over the input file


<<< bash
    cd ~/spyder-6/envs && source ./ai-apis/bin/activate &&

    python3 -m pip install --upgrade pip &&
    pip install --upgrade pyproj &&
    pip list &&
    deactivate
>>>

<<< Spyder >>>
    Run the script as is (F5). Optional command-line options in
    Run > Configuration per file > "Command line options":
        [input.txt] [output.txt] [--quiet]
    A bare file name is looked for in INPUT_DIR.
>>>

<<< python
python3 Calculate_LatLon_cell_areas_v1.3.py [LatLon.txt] [output.txt] [--quiet]
>>>

"""

import math
import os
import re
import sys

# ---- SETTINGS (edit these) -------------------------------------------------
INPUT_DIR = "/home/bruce-vdb/Desktop"   # bare file names are looked for here
INPUT_FILE = "LatLon.txt"               # used when no file name is given
OUTPUT_FILE = None                      # None -> "<input name>_areas.txt" next to the input
                                        # (a bare name is placed in INPUT_DIR)
WRITE_OUTPUT = True                     # False -> only print the results
OVERWRITE_OUTPUT = True                 # replace the output file if it exists
                                        # (the input file is never overwritten)
VERBOSE = True                          # per-line report of what was read
# ----------------------------------------------------------------------------


class InputError(Exception):
    """A problem with the input file or its contents (reported, then stop)."""


# ---- area engine -----------------------------------------------------------
try:
    from pyproj import Geod

    _geod = Geod(ellps="WGS84")
    ENGINE = "pyproj"

    def cell_area(lat0, lat1, lon0, lon1):
        a, _ = _geod.polygon_area_perimeter(
            [lon0, lon1, lon1, lon0], [lat0, lat0, lat1, lat1]
        )
        return abs(a)


###### # an exact closed-form equal-area formula ####################
except ImportError:
    ENGINE = "closed-form WGS84 formula"
    _A = 6378137.0
    _F = 1 / 298.257223563
    _E2 = _F * (2 - _F)
    _E = math.sqrt(_E2)

    def _q(phi):
        s = math.sin(phi)
        return (1 - _E2) * (
            s / (1 - _E2 * s * s) - (1 / (2 * _E)) * math.log((1 - _E * s) / (1 + _E * s))
        )

    def cell_area(lat0, lat1, lon0, lon1):
        dq = _q(math.radians(lat1)) - _q(math.radians(lat0))
        return abs(_A * _A / 2 * dq * math.radians(lon1 - lon0))
########################################################################



# ---- parsing ---------------------------------------------------------------
def parse_dms(text):
    """'-100 05 18.2' -> (signed decimal degrees, step in degrees)."""
    parts = text.split()
    if not 1 <= len(parts) <= 3:
        raise ValueError(f"expected 1 to 3 parts (deg [min [sec]]), got {len(parts)}: {text!r}")
    sign = -1 if parts[0].startswith("-") else 1
    vals = [abs(float(p)) for p in parts]          # raises ValueError if not numeric
    divisors = [1, 60, 3600]
    deg = sum(v / d for v, d in zip(vals, divisors))

    # step = one unit of the last digit written in the last component
    last = parts[-1].lstrip("-")
    decimals = len(last.split(".")[1]) if "." in last else 0
    step = (10 ** -decimals) / divisors[len(vals) - 1]
    return sign * deg, step


# ---- file access -----------------------------------------------------------
def resolve_path(name):
    """Full paths (and ~/...) are used as given; a bare or relative name is
    looked for in INPUT_DIR. The current directory and the script's own
    folder are NOT used."""
    name = os.path.expanduser(name)
    if os.path.isabs(name):
        return os.path.normpath(name)
    return os.path.normpath(os.path.join(os.path.expanduser(INPUT_DIR), name))


def split_columns(line):
    """Columns are separated by tabs or by 2+ spaces (single spaces stay
    inside a value, e.g. '19 11 25.8')."""
    return [c.strip() for c in re.split(r"\t+|\s{2,}", line.strip()) if c.strip()]


def read_input_file(abs_path, verbose=True):
    """Open `abs_path`, read it line by line, and return a list of records:
         {"line_no", "raw", "lat_text", "lon_text"}
    for every line that looks like a coordinate row.

    Header, separator and blank lines are skipped. Every decision is
    reported when verbose=True so you can see exactly what was read.
    """
    print(f"Input file : {abs_path}")

    # --- check the path before opening -------------------------------------
    if not os.path.exists(abs_path):
        folder = os.path.dirname(abs_path)
        hint = ("the folder does not exist" if not os.path.isdir(folder)
                else "the folder exists but the file is not in it")
        raise InputError(f"file not found: {abs_path}\n"
                         f"       ({hint}; INPUT_DIR is {INPUT_DIR})")
    if not os.path.isfile(abs_path):
        raise InputError(f"not a regular file: {abs_path}")
    print(f"File size  : {os.path.getsize(abs_path)} bytes")

    # --- open and read (the only place the input file is opened) -----------
    # utf-8-sig also copes with a byte-order mark added by some editors
    try:
        with open(abs_path, "r", encoding="utf-8-sig") as fh:
            lines = fh.read().splitlines()
    except PermissionError:
        raise InputError(f"no permission to read: {abs_path}")
    except UnicodeDecodeError as exc:
        raise InputError(f"{abs_path} is not valid UTF-8 text ({exc})")
    print(f"Lines read : {len(lines)}\n")

    # --- classify each line -------------------------------------------------
    records, skipped = [], 0
    if verbose:
        print("Line  Status    Content")
        print("----  --------  -------")
    for line_no, raw in enumerate(lines, start=1):
        cols = split_columns(raw)
        if not raw.strip():
            status, note = "SKIPPED", "blank line"
        elif not re.match(r"^-?\d", cols[0]):
            status, note = "SKIPPED", "header/separator (does not start with a number)"
        elif len(cols) < 2:
            status, note = "SKIPPED", "only one column found, need Lat and Lon"
        else:
            status = "ACCEPTED"
            note = f"lat={cols[0]!r}  lon={cols[1]!r}"
            if len(cols) > 2:
                note += f"  (existing 3rd column {cols[2]!r} ignored)"
            records.append({"line_no": line_no, "raw": raw,
                            "lat_text": cols[0], "lon_text": cols[1]})
        if status == "SKIPPED":
            skipped += 1
        if verbose:
            print(f"{line_no:>4}  {status:<8}  {note}")

    print(f"\nSummary    : {len(lines)} lines read, "
          f"{len(records)} accepted, {skipped} skipped\n")
    return records


def default_output_path(abs_src):
    stem, _ = os.path.splitext(abs_src)
    return stem + "_areas.txt"


# ---- main ------------------------------------------------------------------
def run(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    unknown = flags - {"--quiet"}
    if unknown:
        raise InputError(f"unknown option(s): {', '.join(sorted(unknown))}  (only --quiet is known)")
    if len(args) > 2:
        raise InputError("too many arguments: expected [input.txt] [output.txt]")
    verbose = VERBOSE and "--quiet" not in flags

    src = resolve_path(args[0] if args else INPUT_FILE)
    if len(args) > 1:
        dst = resolve_path(args[1])
    elif OUTPUT_FILE:
        dst = resolve_path(OUTPUT_FILE)
    else:
        dst = default_output_path(src)

    records = read_input_file(src, verbose=verbose)
    if not records:
        raise InputError("no coordinate rows found, nothing to calculate.")

    out = ["Lat\t\t\t\tLon\t\t\t\tDimension (m2)", "---\t\t\t\t---\t\t\t\t----------"]
    for rec in records:
        try:
            lat, dlat = parse_dms(rec["lat_text"])
            lon, dlon = parse_dms(rec["lon_text"])
        except ValueError as exc:
            raise InputError(f"line {rec['line_no']} ({rec['raw']!r}): {exc}")
        lat_end = lat + math.copysign(dlat, lat)
        lon_end = lon + math.copysign(dlon, lon)
        area = cell_area(lat, lat_end, lon, lon_end)
        out.append(f"{rec['lat_text']}\t\t{rec['lon_text']}\t\t{area:.2f}")
    out.append(f"\n# engine: {ENGINE}; ellipsoid: WGS84")
    text = "\n".join(out) + "\n"

    print("Results")
    print("-------")
    print(text)

    if not WRITE_OUTPUT:
        print("Output file: not written (WRITE_OUTPUT is False)")
        return
    if os.path.abspath(dst) == os.path.abspath(src):
        raise InputError(f"output path is the same as the input file, refusing to overwrite it: {dst}")
    if os.path.exists(dst) and not OVERWRITE_OUTPUT:
        raise InputError(f"output file already exists: {dst}\n"
                         f"       Set OVERWRITE_OUTPUT = True to replace it.")
    existed = os.path.exists(dst)
    try:
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(text)
    except OSError as exc:
        raise InputError(f"could not write output file {dst}: {exc}")
    print(f"Output file: {dst} ({len(text)} characters written"
          f"{', replaced existing file' if existed else ''})")


def main(argv):
    try:
        run(argv)
    except InputError as exc:
        print(f"ERROR: {exc}")


if __name__ == "__main__":
    main(sys.argv)
