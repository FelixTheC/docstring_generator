#!/usr/bin/env bash
set -e
CMD="gendocs_new $INPUT_PATH --check --style $INPUT_STYLE --threshold $INPUT_THRESHOLD"
[ "$INPUT_STRICT" = "true" ] && CMD="$CMD --strict"
[ -n "$INPUT_EXCLUDE_FILE" ] && for f in ${INPUT_EXCLUDE_FILE//,/ }; do CMD="$CMD --exclude-file $f"; done
[ -n "$INPUT_EXCLUDE_DIR" ]  && for d in ${INPUT_EXCLUDE_DIR//,/ };  do CMD="$CMD --exclude-dir $d";  done
[ "$INPUT_IGNORE_MAGIC" = "true" ] && CMD="$CMD --ignore-magic"
eval $CMD
