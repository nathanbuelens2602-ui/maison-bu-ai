"""
Maison BU — Mail Marketing Agent
Writes email campaigns that feel like personal letters from the atelier.
"""
from .base_agent import BaseAgent
from prompts.system_prompts import MAIL_MARKETING_SYSTEM
from config.brand_voice import EMAIL_SIGNATURE
from config.settings import STUDIO


class MailMarketingAgent(BaseAgent):
    def __init__(self):
        super().__init__("emails")

    def write_campaign_email(
        self,
        campaign_name: str,
        objective: str,
        key_message: str,
        service_or_offer: str | None = None,
        season: str | None = None,
        segment: str = "all clients",
        include_html: bool = True,
    ) -> str:
        prompt = f"""
Write a complete email campaign for Maison BU.

CAMPAIGN: {campaign_name}
OBJECTIVE: {objective}
KEY MESSAGE: {key_message}
SERVICE / OFFER FEATURED: {service_or_offer or "Brand storytelling — no specific offer"}
SEASON / CONTEXT: {season or "Evergreen"}
AUDIENCE SEGMENT: {segment}
BOOKING URL: {STUDIO["booking_url"]}

DELIVERABLES:

### SUBJECT LINE OPTIONS (3 variations)
Each max 50 characters. From most personal to most evocative.

### PREVIEW TEXT
Completes the subject line. Max 90 characters. 3 variations.

### EMAIL BODY
Write the full email in clean prose. Structure:
  — Salutation (personal, not "Dear subscriber")
  — Opening paragraph (sensory, emotional, draws them in)
  — Body (2 short paragraphs max — the story, the invitation)
  — Single CTA button text (5–7 words)
  — Sign-off

{"### HTML VERSION" if include_html else ""}
{"Provide a clean, minimal single-column HTML version with inline styles." if include_html else ""}

The email should feel like finding a handwritten note under your door from
the most beautiful studio in Hasselt.
"""
        result = self._call(MAIL_MARKETING_SYSTEM, prompt)
        output = self._header(f"Email Campaign — {campaign_name}") + result
        path = self._save(output, f"email_{campaign_name.replace(' ', '_')[:40]}")
        print(f"  Saved → {path}")
        return output

    def write_newsletter(
        self,
        month: str,
        year: int,
        editorial_theme: str,
        featured_content: list[str],
    ) -> str:
        featured_str = "\n".join(f"  — {item}" for item in featured_content)
        prompt = f"""
Write the monthly editorial newsletter for Maison BU.

Month: {month} {year}
Editorial theme: {editorial_theme}
Featured content sections:
{featured_str}
Booking URL: {STUDIO["booking_url"]}

This is not a promotional email. It is a curated moment — like a mini
magazine from the atelier. Clients should look forward to receiving it.

Structure:
1. EDITOR'S NOTE (2–3 sentences, personal, seasonal)
2. THE EDIT (each featured content section, 2–3 sentences each)
3. FROM THE ATELIER (a behind-the-scenes moment or team note)
4. THE INVITATION (one gentle booking prompt, last, never first)
5. SIGN-OFF

Subject line + preview text to accompany.
"""
        result = self._call(MAIL_MARKETING_SYSTEM, prompt)
        output = self._header(f"Newsletter — {month} {year}") + result
        path = self._save(output, f"newsletter_{month}_{year}")
        print(f"  Saved → {path}")
        return output

    def write_welcome_email(self) -> str:
        prompt = f"""
Write the welcome email for a new Maison BU client — someone who has just
booked their first appointment.

This email should make them feel they have just been welcomed into something rare.
Not a salon. An atelier. A world they are now part of.

Deliverables:
1. Subject line (warm, personal, curious)
2. Preview text
3. Full email body
4. HTML version (minimal, single-column, warm off-white background)

Booking URL: {STUDIO["booking_url"]}
Studio: {STUDIO["name"]}, {STUDIO["city"]}
"""
        result = self._call(MAIL_MARKETING_SYSTEM, prompt)
        output = self._header("Welcome Email — New Client") + result
        path = self._save(output, "welcome_email_new_client")
        print(f"  Saved → {path}")
        return output

    def write_loyalty_email(self, milestone: str, client_name_placeholder: str = "{{first_name}}") -> str:
        prompt = f"""
Write a client loyalty email for Maison BU.

Milestone: {milestone}
Client name variable: {client_name_placeholder}

This email celebrates the client's relationship with Maison BU. It is not
a discount email. It is an acknowledgement of a shared ritual — the kind
of loyalty that cannot be bought, only felt.

Deliverables:
1. Subject line (personal, never salesy)
2. Preview text
3. Full email body
4. Optional: a single, exclusive privilege to offer (not a discount — think
   priority booking, a complimentary ritual, a curated recommendation)
"""
        result = self._call(MAIL_MARKETING_SYSTEM, prompt)
        output = self._header(f"Loyalty Email — {milestone}") + result
        path = self._save(output, f"loyalty_{milestone.replace(' ', '_')[:30]}")
        print(f"  Saved → {path}")
        return output

    def write_reengagement_email(self, months_since_visit: int = 3) -> str:
        prompt = f"""
Write a re-engagement email for Maison BU clients who haven't visited
in approximately {months_since_visit} months.

The challenge: win them back without sounding desperate or transactional.
Remind them what they've been missing — not through guilt, but through beauty.

The email should feel like a gentle, warm invitation from a place they loved
and simply haven't returned to yet.

Deliverables:
1. Subject line (intriguing, personal — they should wonder who sent it)
2. Preview text
3. Full email body
4. CTA copy
5. Booking URL: {STUDIO["booking_url"]}
"""
        result = self._call(MAIL_MARKETING_SYSTEM, prompt)
        output = self._header(f"Re-engagement Email — {months_since_visit}mo lapse") + result
        path = self._save(output, f"reengagement_{months_since_visit}months")
        print(f"  Saved → {path}")
        return output
