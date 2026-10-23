# satvik-voice

Satvik's cloned voice for YouTube and HyperFrames narration. It's free and runs locally with
[Chatterbox](https://github.com/resemble-ai/chatterbox) (MIT license) on Apple Silicon.

A Claude Code skill (`skill/SKILL.md`, linked into `~/.claude/skills/satvik-voice`) teaches any
Claude session to use it. Just say "narrate this in my voice".

## Quick start

```bash
./setup.sh                                   # once: Python env + Chatterbox (~3 GB of weights on first run)
echo "[teach] So let me ask you something, right?" > /tmp/hi.txt
.venv/bin/python -I speak.py /tmp/hi.txt /tmp/hi.wav --play
```

Script format: one paragraph per line, each tagged `[teach]`, `[narrate]`, `[calm]` or `[energetic]`.
The output is a wav plus a JSON file with each line's start and end time.

## What's here

| Path | What it is |
|---|---|
| `voice-profile/*.pt` | **The voice.** Chatterbox conditionals per style: a speaker embedding averaged over 40 clean class clips, plus that style's prompt. |
| `refs/*.wav` | The ~12 s reference clips each style was built from (Zoom class recording, 2026-10-23). |
| `samples/` | What it should sound like: a short test and the full 2-minute Antarctica narration with its script. |
| `speak.py` | Script → narration. Style settings are calibrated to Satvik's real pitch range; keep exaggeration at 0.4 or below. |
| `tools/build_voice.py`, `tools/good.json` | Rebuild the profiles. This needs the source recording's audio at `audio/full_24k.wav` (not committed). |
| `skill/SKILL.md` | The Claude Code skill. |

## On a new machine

```bash
git clone <this repo> ~/satvik-voice && ~/satvik-voice/setup.sh
ln -sfn ~/satvik-voice/skill ~/.claude/skills/satvik-voice
```

## Making it better

Cleaner references help more than anything else. Record 2–3 minutes of natural teaching in a quiet room,
cut 10–15 s clips into `refs/`, and rebuild. Measured quality now: speaker similarity 0.957 against
real speech (real voice compared to itself scores 0.972).

## Responsible use

Outputs carry Resemble's inaudible Perth watermark. Disclose AI narration on YouTube.
This voice belongs to Satvik. Do not use it to impersonate them or to say things they have not approved.
