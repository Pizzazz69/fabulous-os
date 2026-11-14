#!/bin/bash
# Build llama.cpp's server inside Debian 13 at the commit fixed in llama.lock.
# Usage (inside a debian:trixie container): build-llama.sh llama.lock OUT_DIR
# One program for every PC: the processor-specific parts are built in all
# variants (plain SSE4.2 for the Beelink's N5105, AVX2 and newer for faster PCs)
# and the right one is chosen when Gemma starts.
set -euo pipefail
. "$1"; out=$2
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends build-essential cmake git ca-certificates
src=$(mktemp -d)
git init -q "$src"
git -C "$src" fetch -q --depth 1 "$LLAMA_REPO" "$LLAMA_COMMIT"
git -C "$src" checkout -q FETCH_HEAD
[ "$(git -C "$src" rev-parse HEAD)" = "$LLAMA_COMMIT" ] || { echo "llama.cpp: wrong commit" >&2; exit 1; }
# No web page, no HTTPS, no downloading: the server can only read a local file.
cmake -S "$src" -B "$src/build" -DCMAKE_BUILD_TYPE=Release \
    -DGGML_NATIVE=OFF -DBUILD_SHARED_LIBS=ON -DGGML_BACKEND_DL=ON -DGGML_CPU_ALL_VARIANTS=ON \
    -DLLAMA_OPENSSL=OFF -DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF \
    -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF -DLLAMA_BUILD_APP=OFF
cmake --build "$src/build" --target llama-server -j"$(nproc)"
rm -rf "$out"; mkdir -p "$out/bin" "$out/doc"
cp -a "$src"/build/bin/llama-server "$src"/build/bin/*.so* "$out/bin/"
strip --strip-unneeded "$out"/bin/llama-server "$out"/bin/*.so.*.* "$out"/bin/libggml-cpu-*.so "$out"/bin/libllama-server-impl.so
cp "$src/LICENSE" "$out/doc/llama.cpp-LICENSE-MIT"
[ -d "$src/licenses" ] && cp -r "$src/licenses" "$out/doc/llama.cpp-third-party-licenses"
printf 'llama.cpp %s (commit %s)\nfrom %s\n' "$LLAMA_TAG" "$LLAMA_COMMIT" "$LLAMA_REPO" > "$out/doc/llama.cpp-VERSION"
LD_LIBRARY_PATH="$out/bin" "$out/bin/llama-server" --version
ls -l "$out/bin"
