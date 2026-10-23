---
name: satvik-voice
description: Narrate anything in Satvik's own cloned voice, free and fully local (Chatterbox on this Mac). Use whenever Satvik asks for a voiceover, narration, "my voice", "in my voice", audio for a YouTube video, or a HyperFrames/video project that needs a narrator. Use this instead of HeyGen voices, Kokoro, or any paid TTS unless Satvik asks for another voice.
---

# Satvik's voice

The voice lives in `~/satvik-voice`: a Chatterbox clone (MIT license) built from Satvik's class recordings. It runs on the Mac's GPU, with no API and no cost.

## First, check it is ready

```bash
ls ~/satvik-voice/.venv/bin/python || ~/satvik-voice/setup.sh
```

To hear what it should sound like: `afplay ~/satvik-voice/samples/short-teach-energetic.wav`.

## Generate narration

1. Write the script to a file, one paragraph per line, each line tagged with a style:

   ```
   [teach] So let me ask you something. Where do you actually start?
   [narrate] You start here, in Ushuaia, Argentina.
   [calm] Then one morning, you wake up, and the first iceberg is floating past your window.
   [energetic] And then, penguins! Thousands of them!
   ```

   | Style | When to use it |
   |---|---|
   | `teach` (default) | explaining, asking the viewer questions |
   | `narrate` | describing scenes, the story moving forward |
   | `calm` | reflective, slow, endings |
   | `energetic` | the one or two big moments; use sparingly |

2. Run it (it takes about real time, or longer if another session is using the GPU, so run long scripts in the background):

   ```bash
   cd ~/satvik-voice && .venv/bin/python -I -u speak.py /path/script.txt /path/out.wav
   ```

   It writes `out.wav` (24 kHz) and `out.json` (each line's `start`/`end` in seconds). Use the JSON to time scenes; for word-level caption timing, transcribe `out.wav`.

3. **Before a long narration, play Satvik a 10–20 s sample** (`--play` plays it when done) and get a yes. It has to sound like Satvik.

## Write like Satvik talks

From Satvik's real classes:
- Pace is about 3 words a second, so a 2-minute video is about 330–370 words.
- Satvik is conversational and direct: asks the viewer questions ("So what do you do?"), tags points with "right?", and says "So see," and "honestly".
- Keep sentences short and spoken: plain words, no lists read aloud, and numbers written as words ("ten to twelve days").

## Delivery rules (from Satvik's feedback)

- **Never over-exaggerate.** Satvik's feedback on the first version was "exaggerating too much, which I didn't do." The settings in `speak.py` (`STYLE`, exaggeration 0.25–0.4) are calibrated against Satvik's real pitch range (about 175 Hz ± 30 Hz). Don't raise them; if a line sounds flat, rewrite the line instead.
- If a word comes out mispronounced, check that line on its own with a strong transcriber. Whisper sometimes mishears the audio when the voice is fine. If the word really is wrong, regenerate with a rephrased line.

## In a HyperFrames video

Put the wav in the project's `assets/audio/` and add it as `<audio id="vo" class="clip" src="assets/audio/voiceover.wav" data-start="0" data-duration="<length>" data-volume="1">`. Make the voice the clock, so each scene starts at its line's `start` from the JSON. Normalize the final render to about -14 LUFS for YouTube.

## Publishing

- Every file carries Resemble's inaudible Perth watermark.
- Tell Satvik to switch on YouTube's "altered or synthetic content" disclosure.
- Never use this voice for anyone but Satvik, or to say things Satvik hasn't approved.

## Improving or rebuilding the voice

See `~/satvik-voice/README.md`. In short: a few minutes of clean, quiet-room audio in `refs/`, then rerun `tools/build_voice.py`.
