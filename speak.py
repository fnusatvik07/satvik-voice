"""Speak a script in Satvik's cloned voice. Free, fully local (Chatterbox on Apple MPS).

Script format: one paragraph per line, optionally prefixed with a style tag.
  [teach] So here's the thing about the Drake Passage...
  [energetic] And then, out of the fog, the first iceberg!
Styles: calm, teach, energetic, narrate (default: teach). Blank lines add a longer pause.

Usage: .venv/bin/python -I speak.py script.txt out.wav [--play]
Writes out.wav plus out.json with each line's start/end time (for captions and scene sync).
"""
import json
import re
import subprocess
import sys
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
from chatterbox.tts import ChatterboxTTS, Conditionals

# delivery settings per style, calibrated so pitch variation matches the real recording (f0 std ~30 Hz)
STYLE = {
    "calm": dict(exaggeration=0.25, cfg_weight=0.5, temperature=0.7),
    "teach": dict(exaggeration=0.3, cfg_weight=0.5, temperature=0.7),
    "narrate": dict(exaggeration=0.3, cfg_weight=0.5, temperature=0.7),
    "energetic": dict(exaggeration=0.4, cfg_weight=0.5, temperature=0.75),
}
GAP_SENTENCE, GAP_LINE, GAP_BLANK = 0.12, 0.35, 0.8


def chunks(text, limit=220):
    """Group sentences into chunks short enough for one stable generation."""
    out, cur = [], ""
    for s in re.split(r"(?<=[.!?])\s+", text.strip()):
        if cur and len(cur) + len(s) > limit:
            out.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    return out + [cur] if cur else out


def trim(wav, sr, db=-42):
    """Trim leading/trailing near-silence so gaps are controlled by us, not the model."""
    env = np.convolve(np.abs(wav), np.ones(256) / 256, mode="same")
    idx = np.where(env > 10 ** (db / 20))[0]
    if not len(idx):
        return wav
    return wav[max(idx[0] - int(0.02 * sr), 0):idx[-1] + int(0.06 * sr)]


PROFILE_DIR = Path(__file__).resolve().parent / "voice-profile"


def main(script_path, out_path, play=False):
    model = ChatterboxTTS.from_pretrained(device="mps")
    sr = model.sr
    conds = {s: Conditionals.load(PROFILE_DIR / f"{s}.pt").to("mps") for s in STYLE}

    pieces, timeline, t = [], [], 0.0
    for line in open(script_path).read().splitlines():
        if not line.strip():
            pieces.append(np.zeros(int(GAP_BLANK * sr)))
            t += GAP_BLANK
            continue
        m = re.match(r"\s*\[(\w+)\]\s*(.*)", line)
        style, text = (m.group(1), m.group(2)) if m else ("teach", line)
        model.conds = conds[style]
        start = t
        for c in chunks(text):
            torch.manual_seed(len(pieces))
            wav = trim(model.generate(c, **STYLE[style]).squeeze(0).numpy(), sr)
            pieces += [wav, np.zeros(int(GAP_SENTENCE * sr))]
            t += len(wav) / sr + GAP_SENTENCE
            print(f"[{style}] {t:6.1f}s  {c[:70]}", flush=True)
        timeline.append(dict(style=style, text=text, start=round(start, 3), end=round(t, 3)))
        pieces.append(np.zeros(int(GAP_LINE * sr)))
        t += GAP_LINE

    audio = np.concatenate(pieces)
    audio = audio / max(np.abs(audio).max(), 1e-6) * 0.89
    sf.write(out_path, audio, sr)
    json.dump(timeline, open(out_path.rsplit(".", 1)[0] + ".json", "w"), indent=1)
    print(f"wrote {out_path} ({len(audio) / sr:.1f}s)")
    if play:
        subprocess.run(["afplay", out_path])


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--play"]
    main(*args, play="--play" in sys.argv)
