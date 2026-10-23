"""Build a reusable voice profile: one Chatterbox conditionals file per delivery style.

Timbre comes from a speaker embedding averaged over many clean clips of the class
recording (more robust than any single clip); rhythm and delivery come from each
style's own reference clip.
"""
import json
from pathlib import Path
import librosa
import numpy as np
import soundfile as sf
import torch
from chatterbox.tts import ChatterboxTTS, Conditionals
from chatterbox.models.t3.modules.cond_enc import T3Cond
from chatterbox.models.s3tokenizer import S3_SR

STYLES = ["calm", "teach", "energetic", "narrate"]
REPO = Path(__file__).resolve().parent.parent

model = ChatterboxTTS.from_pretrained(device="mps")

audio, sr = sf.read(REPO / "audio/full_24k.wav")  # mono 24 kHz audio of the source recording
good = sorted(json.load(open(REPO / "tools/good.json")), key=lambda x: -x["spk"])[:40]
clips = [librosa.resample(audio[int(g["start"] * sr):int(g["end"] * sr)].astype(np.float32),
                          orig_sr=sr, target_sr=S3_SR) for g in good]
avg_emb = torch.from_numpy(model.ve.embeds_from_wavs(clips, sample_rate=S3_SR)).mean(0, keepdim=True)
print("averaged speaker embedding over", len(clips), "clips")

for style in STYLES:
    model.prepare_conditionals(str(REPO / f"refs/{style}.wav"), exaggeration=0.5)
    c = model.conds
    single = c.t3.speaker_emb
    blended = (avg_emb.to(single.device) * single.norm() / avg_emb.norm()).to(single.dtype)
    c.t3 = T3Cond(speaker_emb=blended, cond_prompt_speech_tokens=c.t3.cond_prompt_speech_tokens,
                  emotion_adv=c.t3.emotion_adv).to(device="mps")
    c.save(REPO / f"voice-profile/{style}.pt")
    print("saved", style)
