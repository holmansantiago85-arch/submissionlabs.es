#!/bin/bash
# Change talk key or mic mode. See: ./talk_config.sh
HERE="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$HERE/tools/talk_config.py" "$@"
