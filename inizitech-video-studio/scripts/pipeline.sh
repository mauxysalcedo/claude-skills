#!/usr/bin/env bash
# Uso: INIZI_OUT=/ruta/trabajo ./pipeline.sh <nombre_video> [solo_stills]
# Requiere: python3 + skia-python + numpy, ffmpeg.
# Antes: dejar en $INIZI_OUT/<nombre>/raw.json el mapa  {"<nombre>_1": "/ruta/voz1.wav", ...}
# (una clave por escena, tal como las usa V(..., 'clave') en la definicion del video).
set -euo pipefail
NAME="$1"; MODE="${2:-todo}"
HERE="$(cd "$(dirname "$0")" && pwd)"
export INIZI_OUT="${INIZI_OUT:-/tmp/inizi_out}"
D="$INIZI_OUT/$NAME"
mkdir -p "$D"
PY="python3 -I"
$PY "$HERE/motor_muneco.py" "$NAME" prep
$PY "$HERE/motor_muneco.py" "$NAME" stills
[ "$MODE" = "solo_stills" ] && { echo "Stills en $D/stills (revisalos antes de renderizar)"; exit 0; }
$PY "$HERE/motor_muneco.py" "$NAME" render
N=$(ls "$D"/scene*.mp4 | wc -l)
: > "$D/vlist.txt"
for i in $(seq 1 "$N"); do echo "file 'scene$i.mp4'" >> "$D/vlist.txt"; done
ffmpeg -y -loglevel error -f concat -safe 0 -i "$D/vlist.txt" -c copy "$D/video.mp4"
ffmpeg -y -loglevel error -i "$D/voz_total.wav" -i "$D/sfx.wav" \
  -filter_complex "[0][1]amix=inputs=2:weights=1 0.45:normalize=0,alimiter=limit=0.89" -ar 44100 "$D/audio.wav"
ffmpeg -y -loglevel error -i "$D/video.mp4" -i "$D/audio.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest "$D/final.mp4"
echo "OK -> $D/final.mp4"
ffmpeg -hide_banner -i "$D/final.mp4" -af volumedetect -vn -f null - 2>&1 | grep -E "max_volume|mean_volume" || true
