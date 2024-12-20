#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


if [[ $* == *--venv* ]]; then
	## run under venv
	VENV_DIR="$SCRIPT_DIR/../../venv"
	"$VENV_DIR"/activatevenv.sh "$0; exit"
	exit 0
fi


SRC_DIR="$SCRIPT_DIR/../../src"
RUN_DIR="$SCRIPT_DIR/../.."
OUT_DIR="$SCRIPT_DIR/cloc_tree"


"$SRC_DIR"/clocdirtree/main.py --clocdir "$RUN_DIR" --outdir "$OUT_DIR" \
							   --exclude "*/venv*" "*/.git*" "*/tmp*" "$SCRIPT_DIR/*"


BROKEN_LINKS=0
result=$(checklink -r -q "$OUT_DIR/index.html" 2> /dev/null) || BROKEN_LINKS=1
if [[ "$result" != "" || $BROKEN_LINKS -ne 0 ]]; then
	echo "broken links found:"
	echo "$result"
	exit 1
fi
# else: # empty string - no errors
echo "no broken links found"


## generate image from html
echo -e "\ntaking screenshots"

PAGE_PATH="$OUT_DIR/graphs/index.html"
if [ -f "$PAGE_PATH" ]; then
	OUT_IMG_PATH="$OUT_DIR/main-page.png"
    cutycapt --url=file://"$PAGE_PATH" --out="$OUT_IMG_PATH"
    convert "$OUT_IMG_PATH" -trim "$OUT_IMG_PATH"
    convert -bordercolor \#BBBBBB -border 20 "$OUT_IMG_PATH" "$OUT_IMG_PATH"
    convert "$OUT_IMG_PATH" -strip "$OUT_IMG_PATH"
	exiftool -overwrite_original -all= "$OUT_IMG_PATH"
else
	echo "unable to find $PAGE_PATH"
	exit 1
fi


## generate small images
"$SCRIPT_DIR"/../generate_small.sh
