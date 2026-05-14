#!/usr/bin/env python3
"""
Maison BU — AI Marketing System
CLI entry point.

Usage:
  python main.py campaign       Run a full monthly campaign
  python main.py caption        Write a single caption
  python main.py reel           Write a reel script
  python main.py email          Write an email
  python main.py lastminute     Run the last-minute booking protocol
  python main.py onboarding     Generate client onboarding emails
  python main.py brandkit       Generate Brand World Kit
  python main.py demo           Run a demo of all agents
  python main.py pdf            Export campaign files to PDF
"""
import sys
import argparse
from pathlib import Path


BANNER = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║        M A I S O N   B U   ·   AI Marketing             ║
║        Hair & Beauty Lab · Hasselt, Belgium              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""


def run_campaign(args):
    from orchestrator import MaisonBUOrchestrator
    o = MaisonBUOrchestrator()
    o.run_monthly_campaign(
        month=args.month or _prompt("Month (e.g. June)"),
        year=int(args.year or _prompt("Year (e.g. 2025)")),
        campaign_theme=args.theme or _prompt("Campaign theme"),
        focus_services=_parse_list(args.services or _prompt("Focus services (comma-separated)")),
        email_objective=args.email_obj or _prompt("Email objective"),
    )


def run_caption(args):
    from agents import CaptionWritingAgent
    agent = CaptionWritingAgent()
    agent.write_caption(
        content_pillar=args.pillar or _prompt("Content pillar (The Ritual / The Transformation / The Maison / The Edit / L'Invitation)"),
        subject=args.subject or _prompt("Subject / moment to capture"),
        visual_description=args.visual or _prompt("Describe the visual in the post"),
        service=args.service or None,
        include_cta=not args.no_cta,
    )


def run_reel(args):
    from agents import ReelScriptAgent
    agent = ReelScriptAgent()
    reel_types = ["ritual", "transformation", "day_in_the_life", "technique", "seasonal", "invitation", "team"]
    agent.write_reel_script(
        reel_type=args.type or _prompt(f"Reel type ({' / '.join(reel_types)})"),
        subject=args.subject or _prompt("Subject of the reel"),
        service=args.service or None,
        duration=args.duration or "medium",
    )


def run_email(args):
    from agents import MailMarketingAgent
    agent = MailMarketingAgent()
    email_type = args.type or _prompt("Email type (campaign / newsletter / welcome / loyalty / reengagement)")
    if email_type == "welcome":
        agent.write_welcome_email()
    elif email_type == "newsletter":
        agent.write_newsletter(
            month=args.month or _prompt("Month"),
            year=int(args.year or _prompt("Year")),
            editorial_theme=args.theme or _prompt("Editorial theme"),
            featured_content=_parse_list(args.content or _prompt("Featured sections (comma-separated)")),
        )
    elif email_type == "loyalty":
        agent.write_loyalty_email(milestone=args.milestone or _prompt("Loyalty milestone"))
    elif email_type == "reengagement":
        agent.write_reengagement_email(months_since_visit=int(args.months or 3))
    else:
        agent.write_campaign_email(
            campaign_name=args.campaign or _prompt("Campaign name"),
            objective=args.objective or _prompt("Objective"),
            key_message=args.message or _prompt("Key message"),
        )


def run_last_minute(args):
    from orchestrator import MaisonBUOrchestrator
    o = MaisonBUOrchestrator()
    o.run_last_minute_protocol()


def run_onboarding(args):
    from orchestrator import MaisonBUOrchestrator
    o = MaisonBUOrchestrator()
    o.run_onboarding_sequence()


def run_brand_kit(args):
    from orchestrator import MaisonBUOrchestrator
    o = MaisonBUOrchestrator()
    o.run_brand_world_kit()


def run_pdf(args):
    from tools.pdf_export import MaisonBUPdfExporter
    exporter = MaisonBUPdfExporter()

    if args.file:
        p = Path(args.file)
        if not p.is_absolute():
            p = Path(__file__).parent / "outputs" / args.file
        out = exporter.export_file(p)
        print(f"  [OK] PDF aangemaakt: {out}")
    elif args.campaign:
        results = exporter.export_campaign(args.campaign)
        if results:
            for r in results:
                print(f"  [OK] {r.name}")
            print(f"\n  {len(results)} PDF('s) opgeslagen in: outputs/pdf/")
        else:
            print(f"  Geen bestanden gevonden voor campagne '{args.campaign}'.")
    else:
        results = exporter.export_all()
        if results:
            for r in results:
                print(f"  [OK] {r.name}")
            print(f"\n  {len(results)} PDF('s) opgeslagen in: outputs/pdf/")
        else:
            print("  Geen .txt bestanden gevonden in outputs/.")


def run_demo(args):
    """Quick demo — generates one output per agent without prompts."""
    from agents import (
        ContentStrategyAgent, CaptionWritingAgent,
        ReelScriptAgent, MailMarketingAgent, LastMinuteBookingAgent,
    )
    print(BANNER)
    print("  Running demo — generating sample outputs for all five agents.\n")

    print("─" * 60)
    print("  AGENT 1: Content Strategy")
    print("─" * 60)
    ContentStrategyAgent().generate_monthly_calendar(
        month="June", year=2025,
        focus_services=["Colour & Balayage", "Scalp Rituals"],
        campaign_theme="The Golden Hour Edit",
    )

    print("\n" + "─" * 60)
    print("  AGENT 2: Caption Writing")
    print("─" * 60)
    CaptionWritingAgent().write_caption(
        content_pillar="The Ritual",
        subject="A balayage session in the late afternoon light",
        visual_description="Close-up of a brush being drawn through golden hair, warm window light",
        service="Colour & Balayage",
    )

    print("\n" + "─" * 60)
    print("  AGENT 3: Reel Script")
    print("─" * 60)
    ReelScriptAgent().write_reel_script(
        reel_type="ritual",
        subject="A scalp ritual at golden hour",
        service="Scalp Ritual",
        duration="medium",
        season="summer",
    )

    print("\n" + "─" * 60)
    print("  AGENT 4: Mail Marketing")
    print("─" * 60)
    MailMarketingAgent().write_campaign_email(
        campaign_name="The Golden Hour Edit",
        objective="Drive bookings for summer colour and scalp treatments",
        key_message="Summer calls for your most luminous self.",
        service_or_offer="Colour & Balayage, Scalp Rituals",
        season="summer",
    )

    print("\n" + "─" * 60)
    print("  AGENT 5: Last Minute Booking")
    print("─" * 60)
    LastMinuteBookingAgent().generate_last_minute_post(
        available_slots=[
            {"date": "Tomorrow — Thursday 15 May", "time": "14:00", "duration": "90 min"},
            {"date": "Friday 16 May", "time": "10:30", "duration": "60 min"},
        ],
        service="Colour & Balayage",
        therapist="Sophie",
    )

    print(f"\n{'═'*60}")
    print("  Demo complete. All outputs saved to /outputs/")
    print(f"{'═'*60}\n")


def _prompt(label: str) -> str:
    return input(f"  {label}: ").strip()


def _parse_list(s: str) -> list[str]:
    return [item.strip() for item in s.split(",") if item.strip()]


def main():
    print(BANNER)

    parser = argparse.ArgumentParser(
        description="Maison BU AI Marketing System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    # campaign
    p_campaign = subparsers.add_parser("campaign", help="Run a full monthly campaign")
    p_campaign.add_argument("--month")
    p_campaign.add_argument("--year")
    p_campaign.add_argument("--theme")
    p_campaign.add_argument("--services")
    p_campaign.add_argument("--email-obj", dest="email_obj")

    # caption
    p_caption = subparsers.add_parser("caption", help="Write a single caption")
    p_caption.add_argument("--pillar")
    p_caption.add_argument("--subject")
    p_caption.add_argument("--visual")
    p_caption.add_argument("--service")
    p_caption.add_argument("--no-cta", action="store_true")

    # reel
    p_reel = subparsers.add_parser("reel", help="Write a reel script")
    p_reel.add_argument("--type")
    p_reel.add_argument("--subject")
    p_reel.add_argument("--service")
    p_reel.add_argument("--duration", choices=["short", "medium", "long"], default="medium")

    # email
    p_email = subparsers.add_parser("email", help="Write an email")
    p_email.add_argument("--type")
    p_email.add_argument("--month")
    p_email.add_argument("--year")
    p_email.add_argument("--theme")
    p_email.add_argument("--content")
    p_email.add_argument("--campaign")
    p_email.add_argument("--objective")
    p_email.add_argument("--message")
    p_email.add_argument("--milestone")
    p_email.add_argument("--months", type=int)

    # lastminute
    subparsers.add_parser("lastminute", help="Run last-minute booking protocol")

    # onboarding
    subparsers.add_parser("onboarding", help="Generate client onboarding emails")

    # brandkit
    subparsers.add_parser("brandkit", help="Generate Brand World Kit")

    # demo
    subparsers.add_parser("demo", help="Run a demo of all agents")

    # pdf
    p_pdf = subparsers.add_parser("pdf", help="Exporteer campagnebestanden naar PDF")
    p_pdf.add_argument(
        "--file",
        help="Specifiek bestand (bijv. reel_scripts/juni_2026_acht_reels.txt)",
    )
    p_pdf.add_argument(
        "--campaign",
        help="Filter op campagnenaam (bijv. juni_2026)",
    )

    args = parser.parse_args()

    commands = {
        "campaign": run_campaign,
        "caption": run_caption,
        "reel": run_reel,
        "email": run_email,
        "lastminute": run_last_minute,
        "onboarding": run_onboarding,
        "brandkit": run_brand_kit,
        "demo": run_demo,
        "pdf": run_pdf,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
