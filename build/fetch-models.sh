#!/bin/bash
# Fetch the Gemma files named in models.lock and check them. Usage:
#   build/fetch-models.sh models.lock CACHE_DIR DEST_DIR
# Stops with an error if a file is not from Google's repository or its checksum
# or size differs from models.lock.
set -euo pipefail
lock=$1; cache=$2; dest=$3
mkdir -p "$cache" "$dest"
grep -v -e '^#' -e '^[[:space:]]*$' "$lock" | while read -r sha bytes file url; do
    case "$url" in
        https://huggingface.co/google/*/resolve/*) ;;
        *) echo "REFUSED: $file is not from Google's repository: $url" >&2; exit 1 ;;
    esac
    if ! echo "$sha  $cache/$file" | sha256sum -c --status 2>/dev/null; then
        rm -f "$cache/$file"
        curl -fL --retry 3 -o "$cache/$file" "$url"
    fi
    size=$(stat -c %s "$cache/$file")
    [ "$size" = "$bytes" ] || { echo "WRONG SIZE: $file is $size bytes, expected $bytes" >&2; exit 1; }
    echo "$sha  $cache/$file" | sha256sum -c || { echo "WRONG CHECKSUM: $file" >&2; exit 1; }
    ln -f "$cache/$file" "$dest/$file" 2>/dev/null || cp "$cache/$file" "$dest/$file"
    echo "verified: $file ($bytes bytes, sha256 $sha)"
done
