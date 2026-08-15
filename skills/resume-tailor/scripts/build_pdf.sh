#!/usr/bin/env bash
# Build a numbered resume PDF from a .tex file.
#
# Usage:
#   build_pdf.sh <path-to.tex> --out-dir <dir> [--base <name>] [--pages <n>]
#
#   --out-dir  where the numbered pair is written (required)
#   --base     filename stem, e.g. "Jane_Doe_Resume" (default: Resume)
#   --pages    expected page count; warn if the build differs (default: 1)
#
# Output: <out-dir>/<base>-N.{pdf,tex}  where N is the next free number.
#
# Docker is the primary engine (full TeX Live, so no missing-package chasing).
# A local pdflatex, if one exists, is used as a fallback.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SRC=""
OUT_DIR="${RESUME_OUT_DIR:-}"
BASE="${RESUME_BASE:-Resume}"
WANT_PAGES="1"
IMAGE="texlive/texlive:latest"
DOCKER="${DOCKER_BIN:-}"

usage() {
  echo "usage: build_pdf.sh <path-to.tex> --out-dir <dir> [--base <name>] [--pages <n>]" >&2
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out-dir) OUT_DIR="${2:-}"; shift 2 ;;
    --base)    BASE="${2:-}";    shift 2 ;;
    --pages)   WANT_PAGES="${2:-}"; shift 2 ;;
    -h|--help) usage ;;
    -*)        echo "unknown option: $1" >&2; usage ;;
    *)         [[ -n "$SRC" ]] && usage; SRC="$1"; shift ;;
  esac
done

[[ -n "$SRC" && -f "$SRC" ]] || usage
if [[ -z "$OUT_DIR" ]]; then
  echo "ERROR: --out-dir is required (or set RESUME_OUT_DIR)." >&2
  usage
fi

# Sanitize the stem so it can't escape the output directory.
BASE="$(basename "$BASE")"
[[ -n "$BASE" ]] || BASE="Resume"

if [[ -z "$DOCKER" ]]; then
  DOCKER="$(command -v docker || true)"
  [[ -z "$DOCKER" && -x /opt/homebrew/bin/docker ]] && DOCKER=/opt/homebrew/bin/docker
  [[ -z "$DOCKER" && -x /usr/local/bin/docker ]] && DOCKER=/usr/local/bin/docker
fi

# Pick an engine: docker (preferred) or a local pdflatex.
ENGINE=""
if [[ -n "$DOCKER" ]] && "$DOCKER" info >/dev/null 2>&1; then
  if "$DOCKER" image inspect "$IMAGE" >/dev/null 2>&1; then
    ENGINE="docker"
  else
    echo "NOTE: pulling $IMAGE (one time, several GB)..." >&2
    if "$DOCKER" pull "$IMAGE" >&2; then ENGINE="docker"; fi
  fi
fi

if [[ -z "$ENGINE" ]]; then
  PDFLATEX="$(command -v pdflatex || true)"
  for candidate in /Library/TeX/texbin/pdflatex /usr/local/texlive/*/bin/*/pdflatex; do
    [[ -n "$PDFLATEX" ]] && break
    [[ -x "$candidate" ]] && PDFLATEX="$candidate"
  done
  if [[ -n "$PDFLATEX" ]]; then
    ENGINE="local"
    export PATH="$(dirname "$PDFLATEX"):$PATH"
  else
    echo "ERROR: no LaTeX engine available." >&2
    if [[ -z "$DOCKER" ]]; then
      echo "  Docker is not installed, and no local pdflatex was found." >&2
    else
      echo "  Docker is installed but the daemon isn't running. Start Docker, then re-run." >&2
    fi
    echo "  See $SCRIPT_DIR/SETUP.md" >&2
    exit 3
  fi
fi

mkdir -p "$OUT_DIR" || exit 1

# Next free number
N=1
while [[ -e "$OUT_DIR/$BASE-$N.pdf" ]]; do N=$((N + 1)); done
NAME="$BASE-$N"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cp "$SRC" "$WORK/$NAME.tex"
LOG="$WORK/$NAME.log"

# Two passes: hyperref needs a second one to settle its outlines.
RUN="pdflatex -interaction=nonstopmode -halt-on-error $(printf '%q' "$NAME.tex")"
if [[ "$ENGINE" == "docker" ]]; then
  "$DOCKER" run --rm \
    -v "$WORK:/work" -w /work \
    --user "$(id -u):$(id -g)" \
    "$IMAGE" sh -c "$RUN; $RUN" >/dev/null 2>&1
else
  ( cd "$WORK" && eval "$RUN" >/dev/null 2>&1; eval "$RUN" >/dev/null 2>&1 )
fi

if [[ ! -f "$WORK/$NAME.pdf" ]]; then
  echo "BUILD FAILED (engine: $ENGINE)." >&2
  MISSING=$(grep -oE "File \`[a-zA-Z0-9._-]+\.(sty|cls)' not found" "$LOG" 2>/dev/null \
            | sed -E "s/File \`(.+)' not found/\1/" | sort -u | tr '\n' ' ')
  FONT=$(grep -oE "Font [a-zA-Z0-9]+ at [0-9]+ not found" "$LOG" 2>/dev/null | sort -u | tr '\n' ' ')
  [[ -n "$MISSING" ]] && echo "Missing file(s): $MISSING" >&2
  [[ -n "$FONT" ]] && echo "Missing font(s): $FONT" >&2
  if [[ -n "$MISSING$FONT" ]]; then
    if [[ "$ENGINE" == "docker" ]]; then
      echo "Unexpected in the full TeX Live image — the .tex may reference something nonstandard." >&2
    else
      echo "Install them with: sudo tlmgr install <name>   (or use the Docker engine, see SETUP.md)" >&2
    fi
  else
    echo "--- last 40 lines of pdflatex log ---" >&2
    tail -40 "$LOG" >&2
  fi
  exit 1
fi

# Always keep the source next to the PDF: it is what makes a past resume re-editable.
cp "$WORK/$NAME.pdf" "$OUT_DIR/$NAME.pdf"
cp "$WORK/$NAME.tex" "$OUT_DIR/$NAME.tex"

PAGES=$(grep -oE "Output written on .*\([0-9]+ page" "$LOG" | grep -oE "[0-9]+ page" | grep -oE "[0-9]+" | tail -1)
echo "BUILT: $OUT_DIR/$NAME.pdf"
echo "SOURCE: $OUT_DIR/$NAME.tex"
echo "ENGINE: $ENGINE"
echo "PAGES: ${PAGES:-unknown}"
if [[ -n "$PAGES" && "$PAGES" != "$WANT_PAGES" ]]; then
  echo "WARNING: resume is $PAGES pages — expected $WANT_PAGES."
fi
exit 0
