"""Contract for founder-led vacancy reels; deliberately independent of article reels."""
from __future__ import annotations

import re

# Total clip length includes the silent visual hook, breathing room and end beat.
# The limit is spoken words, not words-per-video-second.
# This is a production ceiling, not a target to undershoot.  For a talking
# founder scene, 10 seconds should normally carry 16–20 words so the clip does
# not turn into a silent hold at either boundary.
REEL_DURATION_CAPACITY = (
    (8, 16),
    (10, 20),
    (15, 30),
    (20, 40),
    (30, 60),
)
FOUNDER_REEL_VOICE = "Charon"

def spoken_word_count(text: str) -> int:
    return len(re.findall(r"[\w’'-]+", str(text or ""), flags=re.UNICODE))

def duration_for_words(words: int) -> int:
    """Smallest natural Reel duration which leaves room for hook, pause and end beat."""
    words = max(0, int(words))
    for seconds, capacity in REEL_DURATION_CAPACITY:
        if words <= capacity:
            return seconds
    raise ValueError("A Reel may contain at most 60 spoken words; split at a completed thought.")

def split_finished_thoughts(script: str) -> list[str]:
    """Split only between completed sentences; never truncate to meet a duration."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", str(script or "")) if s.strip()]
    reels, current = [], []
    for sentence in sentences:
        candidate = " ".join([*current, sentence])
        if current and spoken_word_count(candidate) > 60:
            reels.append(" ".join(current)); current = [sentence]
        else:
            current.append(sentence)
    if current:
        reels.append(" ".join(current))
    if any(spoken_word_count(item) > 60 for item in reels):
        raise ValueError("One sentence exceeds the 60-word founder-reel limit; rewrite it, do not cut it.")
    return reels

VACANCY_FOUNDER_REEL_PROMPT_RULES = """
Create a founder-led vacancy Reel plan.

The founder is the primary on-screen person. Every scene with the founder uses the approved founder image reference to generate boundary frames; preserve the same face, glasses, hairstyle, beard and apparent age. The portrait reference fixes identity only: choose the location, interior, wardrobe, action, lighting and camera treatment that make the individual story beat clear. Do not force the same background or outfit across scenes, but ensure adjacent frames feel like a credible deliberate edit. Do not replace the founder with stock people. Omni receives only the generated first and final frames for each clip, never the original founder portrait. In the final boundary-frame generation, also pass the real YAS logo as a separate reference image and require one unchanged final YAS mark only; do not pass either the source portrait or the raw logo directly to Omni.

First write the complete spoken explanation. Then split it only at completed thoughts. A Reel may contain at most 60 spoken words. Select the shortest natural duration using exactly this capacity table: 8 seconds = 16 words, 10 = 20, 15 = 30, 20 = 40, 30 = 60. These are ceilings, not truncation rules: never cut a word or sentence to fit. A 10-second founder scene should normally contain 16–20 words, with speech beginning near 0.3s and ending close to 9.5s; do not manufacture long pauses at either boundary. Never infer duration from overall runtime alone.

For every Reel return: exact spoken text; exact wordCount; durationSeconds; a timed scene list; a startFramePrompt and endFramePrompt with the founder visible; and explicit insertPrompts. Use the fixed preset voice named Charon for every founder Reel; never leave voice selection to the model or switch it between scenes. The narrative placement is mandatory: opening = a strong hook only, with no logos, CTA or engagement request; middle = explain the vacancy/problem and show exactly one context-selected engagement action, but no YAS logo, website or final CTA; ending = show the custom solution, then the final CTA and exactly one YAS logo with yas.ooo. Select the middle engagement action intelligently from the actual viewer value: use FOLLOW when the Reel establishes a recurring useful series; use COMMENT only when the problem invites a specific experience, decision or answer; use SHARE only when the video identifies a concrete role, team or colleague who would benefit from it. Never use more than one, never use a generic action by default, and phrase it as a natural continuation of the specific case. A company logo may appear only where it helps identify the vacancy in the middle; do not repeat it in the ending. Every hook, logo, caption, photo-like evidence card, infographic, CTA and transition must be generated natively by Omni inside the video — never composited afterwards. Each key on-screen text or explanatory graphic must enter cleanly, remain fully visible and readable for at least 3.5 seconds, and leave only after the viewer has time to understand it. Never flash important text or replace a graphic before its meaning can be read; make one visual idea per beat rather than stacking multiple fast inserts. No arbitrary B-roll, stock people or dashboard fiction.
""".strip()
