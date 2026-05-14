"""
Maison BU — Marketing Orchestrator
Coordinates all agents for complete campaign generation.
"""
from agents import (
    ContentStrategyAgent,
    CaptionWritingAgent,
    ReelScriptAgent,
    MailMarketingAgent,
    LastMinuteBookingAgent,
)
from tools.booking_tools import get_available_slots, get_todays_cancellations, format_slots_for_display


class MaisonBUOrchestrator:
    """
    High-level interface for running full marketing campaigns across all agents.
    """

    def __init__(self):
        print("\n  Initialising Maison BU Marketing System...")
        self.strategy = ContentStrategyAgent()
        self.captions = CaptionWritingAgent()
        self.reels = ReelScriptAgent()
        self.email = MailMarketingAgent()
        self.booking = LastMinuteBookingAgent()
        print("  All agents ready.\n")

    def run_monthly_campaign(
        self,
        month: str,
        year: int,
        campaign_theme: str,
        focus_services: list[str],
        email_objective: str,
    ) -> dict:
        """
        Generates a complete monthly campaign package:
        — Content calendar
        — Featured caption
        — Hero reel script
        — Campaign email
        """
        print(f"\n{'═'*60}")
        print(f"  MAISON BU — {month.upper()} {year} CAMPAIGN")
        print(f"  Theme: {campaign_theme}")
        print(f"{'═'*60}\n")

        results = {}

        print("[ 1/4 ] Generating content calendar...")
        results["calendar"] = self.strategy.generate_monthly_calendar(
            month=month,
            year=year,
            focus_services=focus_services,
            campaign_theme=campaign_theme,
        )

        print("[ 2/4 ] Writing hero caption...")
        results["caption"] = self.captions.write_caption(
            content_pillar="L'Invitation",
            subject=campaign_theme,
            visual_description=f"Editorial imagery for {campaign_theme} campaign",
            service=focus_services[0] if focus_services else None,
            include_cta=True,
            cta_type="booking",
        )

        print("[ 3/4 ] Writing hero reel script...")
        results["reel"] = self.reels.write_reel_script(
            reel_type="seasonal",
            subject=campaign_theme,
            service=focus_services[0] if focus_services else None,
            duration="medium",
        )

        print("[ 4/4 ] Writing campaign email...")
        results["email"] = self.email.write_campaign_email(
            campaign_name=campaign_theme,
            objective=email_objective,
            key_message=campaign_theme,
            service_or_offer=", ".join(focus_services),
        )

        print(f"\n  Campaign complete. All files saved to /outputs/\n")
        return results

    def run_last_minute_protocol(self, check_cancellations: bool = True) -> dict:
        """
        Checks availability and generates last-minute booking content automatically.
        """
        print("\n  Running Last Minute Protocol...")

        results = {}

        if check_cancellations:
            cancellations = get_todays_cancellations()
            if cancellations:
                print(f"  Found {len(cancellations)} cancellation(s) today:")
                for c in cancellations:
                    print(f"    — {c['date']} {c['time']} · {c['service']}")
                    results[f"cancellation_{c['time']}"] = self.booking.generate_cancellation_fill(
                        date=c["date"],
                        time=c["time"],
                        service=c["service"],
                        duration_minutes=int(c.get("duration", "60 min").split()[0]),
                    )
            else:
                print("  No cancellations today.")

        slots = get_available_slots(lookahead_days=3)
        if slots:
            print(f"  Found {len(slots)} available slot(s):")
            print(format_slots_for_display(slots))
            results["available_slots"] = self.booking.generate_last_minute_post(
                available_slots=slots,
                service=slots[0].get("service"),
            )

        return results

    def run_onboarding_sequence(self) -> dict:
        """
        Generates the full new client onboarding email sequence.
        """
        print("\n  Generating onboarding email sequence...")
        return {
            "welcome": self.email.write_welcome_email(),
            "first_loyalty": self.email.write_loyalty_email("first visit"),
        }

    def run_brand_world_kit(self) -> dict:
        """
        Generates foundational brand content: pillars brief + brand anthem reel.
        """
        print("\n  Generating Brand World Kit...")
        return {
            "pillars_brief": self.strategy.generate_content_pillars_brief(),
            "brand_anthem": self.reels.write_brand_anthem_reel(),
        }
