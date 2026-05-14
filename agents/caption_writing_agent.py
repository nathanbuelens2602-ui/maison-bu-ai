"""
Maison BU — Caption Writing Agent
Crafts Instagram and social media captions for every content type.
"""
from .base_agent import BaseAgent
from prompts.system_prompts import CAPTION_WRITING_SYSTEM
from config.brand_voice import CONTENT_PILLARS, GUEST_JOURNEY, APPROVED_BOOKING_PHRASES


class CaptionWritingAgent(BaseAgent):
    def __init__(self):
        super().__init__("captions")

    def write_caption(
        self,
        content_pillar: str,
        subject: str,
        visual_description: str,
        service: str | None = None,
        include_cta: bool = True,
        cta_type: str = "booking",
    ) -> str:
        cta_map = {
            "booking": "Link in bio to reserve your moment.",
            "story": "Send us a message — we'd love to hear yours.",
            "save": "Save this for your next visit.",
            "none": "",
        }
        cta = cta_map.get(cta_type, cta_map["booking"]) if include_cta else ""

        approved_phrases = "\n".join(f"  — {p}" for p in APPROVED_BOOKING_PHRASES[:4])
        prompt = f"""
Write an Instagram caption for Maison BU.

CONTENT PILLAR: {content_pillar}
SUBJECT / MOMENT: {subject}
VISUAL IN THE POST: {visual_description}
SERVICE FEATURED: {service or "No specific service — brand moment"}
CALL TO ACTION: {cta or "None required — close with reflection or atmosphere"}

APPROVED BOOKING PHRASES (if CTA needed):
{approved_phrases}

CAPTION ARCHITECTURE:
Line 1: A sensory or emotional hook. Pure feeling. Not context, not information.
Lines 2–4: The scene unfolds. Intimate, specific, inside the moment.
Line 5: A quiet close — reflection, truth or gentle invitation.

DELIVER:
MAIN CAPTION (max 150 words — follow the architecture above)

ALTERNATIVE HOOK
A different opening line — different angle, same world.

HASHTAG SET
8 curated tags. Niche and specific first. No generic beauty spam.

Present cleanly with no section labels or numbering.
Separated only by a single line break.

The caption must feel written by a person who genuinely cares — not generated.
If it could belong to any other salon in the world, rewrite it.
"""
        result = self._call(CAPTION_WRITING_SYSTEM, prompt)
        output = self._header(f"Caption — {subject}") + result
        path = self._save(output, f"caption_{subject.replace(' ', '_')[:40]}")
        print(f"  Saved → {path}")
        return output

    def write_caption_batch(self, briefs: list[dict]) -> list[str]:
        """Generate multiple captions from a list of brief dicts."""
        outputs = []
        for i, brief in enumerate(briefs, 1):
            print(f"  Writing caption {i}/{len(briefs)}: {brief.get('subject', 'Untitled')}")
            out = self.write_caption(**brief)
            outputs.append(out)
        return outputs

    def write_transformation_caption(
        self,
        service: str,
        before_description: str,
        after_description: str,
        client_feeling: str | None = None,
    ) -> str:
        feeling = client_feeling or "a quiet, radiant confidence — more herself than when she arrived"
        prompt = f"""
Write a transformation caption for Maison BU.

Service performed: {service}
Before state: {before_description}
After state: {after_description}
How the guest felt leaving: {feeling}

CRITICAL RULES FOR THIS CAPTION:
— Do NOT describe what the image shows — the visual speaks; the words feel
— Do NOT use the words "transformation," "makeover," "glow up" or "new you"
— Write about the emotional journey: the decision, the ritual, the feeling of leaving
— The result should sound effortless and deeply personal — never triumphant
— The guest "carries a feeling" when they leave, not just a look
— Beauty = refinement of identity. Bringing someone closer to who they truly are.

MAIN CAPTION (max 120 words)
The emotional arc — before, during and after — told through feeling, not description.

STORY VERSION
2–3 lines only. For Instagram Stories. Intimate, immediate.

HASHTAG SET
6 curated, specific tags.

Separated cleanly — no labels or numbering.
"""
        result = self._call(CAPTION_WRITING_SYSTEM, prompt)
        output = self._header(f"Transformation Caption — {service}") + result
        path = self._save(output, f"transformation_{service.replace(' ', '_')}")
        print(f"  Saved → {path}")
        return output

    def write_product_caption(self, product_name: str, benefit: str, sensory_detail: str) -> str:
        prompt = f"""
Write a product/treatment caption for Maison BU.

Product or treatment: {product_name}
Primary benefit: {benefit}
Sensory detail (how it smells, feels, sounds, looks): {sensory_detail}

Make the reader feel the product before they've ever touched it.
Do not list features. Evoke experience.

Deliver:
1. MAIN CAPTION (max 100 words)
2. HASHTAG SET (6 tags)
"""
        result = self._call(CAPTION_WRITING_SYSTEM, prompt)
        output = self._header(f"Product Caption — {product_name}") + result
        path = self._save(output, f"product_{product_name.replace(' ', '_')[:30]}")
        print(f"  Saved → {path}")
        return output
