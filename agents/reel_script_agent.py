"""
Maison BU — Reel Script Agent
Creates cinematic video scripts for Instagram Reels and TikTok.
"""
from .base_agent import BaseAgent
from prompts.system_prompts import REEL_SCRIPT_SYSTEM


REEL_DURATIONS = {
    "short": "15 seconds",
    "medium": "30 seconds",
    "long": "60 seconds",
}

REEL_TYPES = {
    "ritual": "A slow, sensory walk-through of a treatment ritual.",
    "transformation": "A before/after reveal with emotional build.",
    "day_in_the_life": "A quiet, cinematic day inside the Maison BU atelier.",
    "technique": "An artistic close-up of a specific hair or beauty technique.",
    "seasonal": "A mood piece anchored to the current season.",
    "invitation": "A soft booking invitation disguised as an editorial film.",
    "team": "An intimate portrait of a team member and their craft.",
}


class ReelScriptAgent(BaseAgent):
    def __init__(self):
        super().__init__("reel_scripts")

    def write_reel_script(
        self,
        reel_type: str,
        subject: str,
        service: str | None = None,
        duration: str = "medium",
        season: str | None = None,
        special_notes: str | None = None,
    ) -> str:
        reel_desc = REEL_TYPES.get(reel_type, reel_type)
        duration_str = REEL_DURATIONS.get(duration, "30 seconds")

        prompt = f"""
Write a complete reel script for Maison BU.

REEL TYPE: {reel_type.upper()} — {reel_desc}
SUBJECT: {subject}
SERVICE FEATURED: {service or "Atmosphere / brand world"}
TARGET DURATION: {duration_str}
SEASON / MOOD: {season or "Timeless — no specific season"}
SPECIAL NOTES: {special_notes or "None"}

DELIVERABLE (in this exact order):

## REEL CONCEPT
One-paragraph description of the feeling this reel creates.

## SHOT LIST
List every shot with:
  [SHOT N] [DURATION] — [WHAT THE CAMERA SEES] — [CAMERA MOVEMENT]
Be specific: "Extreme close-up of balayage brush pulling through damp hair,
warm window light from the left, slow zoom out."

## ON-SCREEN TEXT
Any text overlays, their timing, and their typographic treatment.
(e.g. "00:08 — 'The ritual begins.' — white serif, fade in, lower third")

## VOICEOVER / AUDIO DIRECTION
If there is voiceover, write it in full.
Music direction: tempo, mood, reference artists or track names.
Sound design notes: any ambient sounds to layer in.

## CAPTION COPY
The Instagram caption to accompany this reel (follows brand caption rules).

## HASHTAG SET
8–10 curated hashtags.

## PRODUCTION NOTES
Any technical notes for the videographer: lens suggestions, colour grade
direction, must-capture moments, what to avoid.
"""
        result = self._call(REEL_SCRIPT_SYSTEM, prompt, max_tokens=2500)
        output = self._header(f"Reel Script — {subject}") + result
        path = self._save(output, f"reel_{reel_type}_{subject.replace(' ', '_')[:30]}")
        print(f"  Saved → {path}")
        return output

    def write_series(self, series_name: str, episodes: list[dict]) -> list[str]:
        """Write a multi-episode reel series (e.g. 'The Ritual Series')."""
        outputs = []
        print(f"\n  Writing reel series: '{series_name}' ({len(episodes)} episodes)")
        for i, ep in enumerate(episodes, 1):
            print(f"  Episode {i}: {ep.get('subject', 'Untitled')}")
            out = self.write_reel_script(**ep)
            outputs.append(out)
        return outputs

    def write_brand_anthem_reel(self) -> str:
        prompt = """
Write the ultimate brand anthem reel script for Maison BU.

This is the reel that defines the brand world. It plays on the profile,
it's pinned, it's shared. It is 45–60 seconds of pure brand storytelling.

No service. No price. No offer. Just the world of Maison BU.

Use the full script format: Concept, Shot List, On-Screen Text,
Audio Direction, Caption, Hashtags, Production Notes.

This should make someone in Hasselt — or anywhere in the world — feel
that Maison BU is the only place they want to be.
"""
        result = self._call(REEL_SCRIPT_SYSTEM, prompt, max_tokens=3000)
        output = self._header("Brand Anthem Reel") + result
        path = self._save(output, "brand_anthem_reel")
        print(f"  Saved → {path}")
        return output
