#!/usr/bin/env bash
# Download the Shorts listed in shorts/selection.txt into shorts/,
# best video + the ORIGINAL English audio track (not YouTube auto-dubs).
#
# Needs a residential IP (YouTube blocks most cloud IPs with
# "Sign in to confirm you're not a bot"), or pass a cookies file:
#   COOKIES=cookies.txt tools/download.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p shorts

extra=()
[[ -n "${COOKIES:-}" ]] && extra+=(--cookies "$COOKIES")

# Audio preference: track marked "original" -> any English track -> default.
FMT='bv*+ba[format_note*=original]/bv*+ba[language^=en]/bv*+ba/b'

grep -v '^#' shorts/selection.txt | while IFS=$'\t' read -r id name; do
  num=${name%% *}
  yt-dlp "${extra[@]}" \
    -f "$FMT" -S 'res,fps,vcodec:avc' \
    --extractor-args 'youtube:lang=en' \
    --merge-output-format mp4 \
    --write-info-json --no-playlist \
    -o "shorts/${num} %(title)s [%(id)s].%(ext)s" \
    "https://www.youtube.com/shorts/${id}"
done
