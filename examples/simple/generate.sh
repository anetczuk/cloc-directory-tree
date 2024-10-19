#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


SRC_DIR="$SCRIPT_DIR/../../src"

RUN_DIR="$SCRIPT_DIR/src"

OUT_DIR="$SCRIPT_DIR/cloc_tree"


"$SRC_DIR"/clocdirtree/main.py --clocdir "$RUN_DIR" --outdir "$OUT_DIR"
