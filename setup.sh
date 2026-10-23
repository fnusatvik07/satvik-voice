#!/usr/bin/env bash
# One-time setup: Python 3.11 env with Chatterbox. Model weights (~3 GB) download on first run.
set -euo pipefail
cd "$(dirname "$0")"
command -v uv >/dev/null || { echo "Install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
[ -d .venv ] || uv venv -p 3.11 .venv
uv pip install -p .venv/bin/python chatterbox-tts "setuptools<81" librosa soundfile
.venv/bin/python -c "import torch; print('MPS available:', torch.backends.mps.is_available())"
