"""
Maison BU — Content Strategy Agent
Generates monthly content calendars, campaign themes, and pillar breakdowns.
"""
from .base_agent import BaseAgent
from prompts.system_prompts import CONTENT_STRATEGY_SYSTEM
from config.brand_voice import CONTENT_PILLARS, SEASONAL_THEMES, SERVICES, GUEST_PROFILE, CORE_MANTRAS, BRAND_MANIFESTO


class ContentStrategyAgent(BaseAgent):
    def __init__(self):
        super().__init__("content_calendar")

    def generate_monthly_calendar(
        self,
        month: str,
        year: int,
        focus_services: list[str] | None = None,
        campaign_theme: str | None = None,
        posts_per_week: int = 4,
    ) -> str:
        services_str = ", ".join(focus_services) if focus_services else "general brand storytelling"
        theme_str = campaign_theme or "no specific campaign — brand world building"

        season = self._get_season(month)
        seasonal_data = SEASONAL_THEMES.get(season, {})
        seasonal_emotion = seasonal_data.get("emotion", "")
        seasonal_services = ", ".join(seasonal_data.get("hero_services", []))
        seasonal_moments = ", ".join(seasonal_data.get("cultural_moments", []))
        seasonal_theme = seasonal_data.get("content_theme", "")
        seasonal_palette = seasonal_data.get("visual_palette", "")

        pillars_str = "\n".join(
            f"  • {p['name']} ({p['posting_weight']}): {p['description']}\n"
            f"    Emotion: {p['emotion']} | Copy: {p['copy_tone']}"
            for p in CONTENT_PILLARS
        )

        prompt = f"""
Create a complete content calendar for Maison BU for {month} {year}.

BRIEF:
— Season: {season.title()}
— Seasonal emotion: "{seasonal_emotion}"
— Seasonal content theme: "{seasonal_theme}"
— Visual palette this season: {seasonal_palette}
— Campaign theme: {theme_str}
— Focus services this month: {services_str}
— Season's hero services: {seasonal_services}
— Cultural moments to consider: {seasonal_moments}
— Posting frequency: {posts_per_week} posts per week (feed posts + reels)
— Platforms: Instagram (primary), TikTok (secondary)

THE GUEST THIS CONTENT SERVES:
Someone who moves through a fast, demanding world. They are tired of transactional
experiences. They want to feel seen, slowed down, elevated. They buy peace,
confidence, attention, discretion. Beauty = refinement of identity.

CONTENT PILLARS TO ROTATE THROUGH:
{pillars_str}

DELIVERABLE FORMAT:

## MONTHLY NARRATIVE ARC
2–3 sentences. The emotional story the month tells across all content.
A guest who follows for the whole month should feel a complete emotional journey.

## KEY DATES & CULTURAL MOMENTS
What to leverage and how — aligned with Maison BU's world, not generic holidays.

## WEEK-BY-WEEK CALENDAR
For each week:
  WEEK [N] — [Week Theme]
  [Day] | [Pillar] | [Format: Feed / Reel / Story / Carousel] | [Visual Direction] | [Copy Direction] | [CTA if any]

Visual Direction should be specific: lighting, subject, framing, texture.
Copy Direction should include the opening line or emotional anchor.

## 3 × CAPTION HOOKS
Opening lines — one per key piece. Sensory, emotional, unmistakably Maison BU.

## HASHTAG BANK
15–20 curated tags, ranked: niche and owned first, broader second.

Every entry must be specific and actionable. Generic = failure.
{self._soul_test_reminder()}
"""

        result = self._call(CONTENT_STRATEGY_SYSTEM, prompt)
        output = self._header(f"Content Calendar — {month} {year}") + result
        path = self._save(output, f"calendar_{month}_{year}")
        print(f"  Saved → {path}")
        return output

    def generate_content_pillars_brief(self) -> str:
        prompt = """
Write a definitive Content Pillars Brief for Maison BU's social media presence.

For each of the five pillars (The Ritual, The Transformation, The Maison,
The Edit, L'Invitation), provide:
— Pillar definition (what it is, why it matters to the Maison BU world)
— The guest this pillar speaks to and what it gives them emotionally
— Visual language guide: lighting, subject, composition, texture, camera approach
— Copy voice: how the tone shifts subtly within the brand voice for this pillar
— 5 specific content ideas with format suggestions and opening line
— What this pillar builds over time: trust / desire / belonging / anticipation

End with:
— Recommended monthly posting ratio across all five pillars
— A note on how the pillars work together as an emotional system —
  not isolated posts but chapters in an ongoing story

This brief is the creative bible for the Maison BU content team.
Every entry must be specific enough to hand to a photographer or copywriter
and have them immediately understand the world they are working within.
"""
        result = self._call(CONTENT_STRATEGY_SYSTEM, prompt)
        output = self._header("Content Pillars Brief") + result
        path = self._save(output, "content_pillars_brief")
        print(f"  Saved → {path}")
        return output

    def generate_campaign_brief(self, campaign_name: str, objective: str, duration: str) -> str:
        prompt = f"""
Write a full campaign brief for Maison BU.

Campaign name: {campaign_name}
Primary objective: {objective}
Duration: {duration}

Deliverable:
1. CAMPAIGN NARRATIVE — The story we're telling (1 paragraph, cinematic tone)
2. KEY MESSAGE — One sentence. The distilled truth of this campaign.
3. VISUAL WORLD — Mood board description, colour palette, lighting direction
4. CONTENT BREAKDOWN — By week, across all formats
5. COPY THEMES — 3 headline directions to test
6. EMAIL TIE-IN — How email supports the social campaign
7. SUCCESS METRICS — What does a beautiful result look like?
"""
        result = self._call(CONTENT_STRATEGY_SYSTEM, prompt)
        output = self._header(f"Campaign Brief — {campaign_name}") + result
        path = self._save(output, f"campaign_{campaign_name.replace(' ', '_')}")
        print(f"  Saved → {path}")
        return output

    @staticmethod
    def _get_season(month: str) -> str:
        month_lower = month.lower()[:3]
        seasons = {
            "dec": "winter", "jan": "winter", "feb": "winter",
            "mar": "spring", "apr": "spring", "may": "spring",
            "jun": "summer", "jul": "summer", "aug": "summer",
            "sep": "autumn", "oct": "autumn", "nov": "autumn",
        }
        return seasons.get(month_lower, "spring")
