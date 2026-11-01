#!/usr/bin/env bash
# Install the video toolchain on a fresh machine or cloud session:
# HyperFrames, Remotion and GSAP (npm), yt-dlp (pip, in .venv), whisper.cpp's whisper-cli,
# and the headless Chrome both renderers use. ffmpeg comes from the OS package manager.
# Safe to run again: each step skips what is already installed.
set -euo pipefail
cd "$(dirname "$0")/.."

WHISPER_REF=482279b # whisper.cpp commit, v1.9.5
BIN=/usr/local/bin
[ -w "$BIN" ] || { BIN="$HOME/.local/bin"; mkdir -p "$BIN"; }

command -v ffmpeg >/dev/null || { echo "ffmpeg missing: install it with your package manager (apt install ffmpeg / brew install ffmpeg)"; exit 1; }

echo "== npm packages"
npm install --no-audit --no-fund

echo "== yt-dlp"
[ -x .venv/bin/python ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
ln -sf "$PWD/.venv/bin/yt-dlp" "$BIN/yt-dlp"

echo "== whisper.cpp"
if ! command -v whisper-cli >/dev/null; then
  src="$(mktemp -d)"
  git clone -q --filter=blob:none https://github.com/ggml-org/whisper.cpp "$src"
  git -C "$src" checkout -q "$WHISPER_REF"
  cmake -S "$src" -B "$src/build" -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF -DWHISPER_BUILD_TESTS=OFF >/dev/null
  cmake --build "$src/build" -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)" --target whisper-cli >/dev/null
  install -m755 "$src/build/bin/whisper-cli" "$BIN/whisper-cli"
  rm -rf "$src"
fi

echo "== render browsers"
npx hyperframes browser ensure
# Remotion's own download host is blocked in cloud sessions; remotion.config.js then
# falls back to the Chrome above, so a failure here is not fatal.
npx remotion browser ensure || echo "Remotion will use the local headless Chrome (see remotion.config.js)"

echo "== versions"
ffmpeg -version | head -1
echo "yt-dlp $(yt-dlp --version)"
echo "whisper-cli $(command -v whisper-cli)"
echo "hyperframes $(npx hyperframes --version)"
echo "remotion $(node -p 'require("remotion/package.json").version')"
