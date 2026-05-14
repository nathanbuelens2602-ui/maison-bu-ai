"""
Maison BU — Content Strategy Agent
Generates monthly content calendars, campaign themes, and pillar breakdowns.
"""
from .base_agent import BaseAgent
from prompts.system_prompts import CONTENT_STRATEGY_SYSTEM
from config.brand_voice import CONTENT_PILLARS, SEASONAL_THEMES, SERVICES


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
        seasonal_note = SEASONAL_THEMES.get(season, "")

        pillars_str = "\n".join(
            f"  • {p['name']}: {p['description']}" for p in CONTENT_PILLARS
        )

        prompt = f"""
Create a complete content calendar for Maison BU for {month} {year}.

BRIEF:
— Season: {season.title()} — "{seasonal_note}"
— Campaign theme: {theme_str}
— Focus services this month: {services_str}
— Posting frequency: {posts_per_week} posts per week (across feed + reels)
— Platforms: Instagram (primary), TikTok (secondary)

CONTENT PILLARS TO ROTATE THROUGH:
{pillars_str}

DELIVERABLE FORMAT:
For each week, provide:
  WEEK [N] — [Theme Title]
  Day | Content Pillar | Format | Visual Direction | Copy Direction | CTA

Then provide:
  MONTHLY THEME OVERVIEW (2–3 sentences on the overarching narrative arc)
  KEY DATES & MOMENTS to leverage this month
  3 × CAPTION HOOKS (opening lines ready to develop)
  HASHTAG BANK (15–20 tags, ranked by priority)

Make every entry specific, actionable, and unmistakably Maison BU.
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
— Pillar definition (what it is, why it matters to the brand)
— Visual language guide (lighting, subject, composition, colour palette)
— Copy voice for this pillar (how the tone shifts subtly within the brand voice)
— 5 content ideas with format suggestions
— What this pillar builds in the audience (trust / desire / loyalty / urgency)

End with a recommended monthly posting ratio across all five pillars.
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
