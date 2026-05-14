"""
Maison BU — Caption Writing Agent
Crafts Instagram and social media captions for every content type.
"""
from .base_agent import BaseAgent
from prompts.system_prompts import CAPTION_WRITING_SYSTEM
from config.brand_voice import CONTENT_PILLARS


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

        prompt = f"""
Write an Instagram caption for Maison BU.

CONTENT PILLAR: {content_pillar}
SUBJECT / MOMENT: {subject}
VISUAL IN THE POST: {visual_description}
SERVICE FEATURED: {service or "No specific service — brand moment"}
CALL TO ACTION: {cta or "None required"}

Deliver:
1. MAIN CAPTION (max 150 words, follows the brand caption architecture)
2. ALTERNATIVE HOOK (just the first line, a different angle)
3. HASHTAG SET (8 tags, curated and relevant)

Do not number these sections in your output — present them cleanly separated
by a line break. The caption should feel handwritten, not generated.
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
        feeling = client_feeling or "a quiet, radiant confidence"
        prompt = f"""
Write a before/after transformation caption for Maison BU.

Service performed: {service}
Before state: {before_description}
After state: {after_description}
How the client felt leaving: {feeling}

The caption should NOT describe the visual (the image speaks). Instead, it should
capture the emotional journey — the decision to transform, the ritual itself,
the feeling of leaving. Never use the word "transformation" or "makeover."

Deliver:
1. MAIN CAPTION (max 120 words)
2. STORY VERSION (shorter, 2–3 lines for Stories)
3. HASHTAG SET (6 tags)
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
