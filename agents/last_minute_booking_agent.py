"""
Maison BU — Last Minute Booking Agent
Fills last-minute availability while preserving every ounce of luxury positioning.
"""
from datetime import datetime
from .base_agent import BaseAgent
from prompts.system_prompts import LAST_MINUTE_BOOKING_SYSTEM
from config.settings import STUDIO
from config.brand_voice import APPROVED_BOOKING_PHRASES, SALES_PHILOSOPHY


class LastMinuteBookingAgent(BaseAgent):
    def __init__(self):
        super().__init__("last_minute", use_fast_model=True)

    def generate_last_minute_post(
        self,
        available_slots: list[dict],
        service: str | None = None,
        therapist: str | None = None,
        special_context: str | None = None,
    ) -> str:
        """
        available_slots: list of {"date": "Thursday 15 May", "time": "14:00", "duration": "90 min"}
        """
        slots_str = "\n".join(
            f"  — {s['date']} at {s['time']} ({s.get('duration', 'TBD')})"
            for s in available_slots
        )
        service_str = service or "a signature treatment"
        therapist_str = f"with {therapist}" if therapist else "with one of our artisans"
        context_str = special_context or "a rare opening in the atelier"
        approved_str = "\n".join(f"  — {p}" for p in APPROVED_BOOKING_PHRASES)

        prompt = f"""
Generate all last-minute booking content for Maison BU.

AVAILABLE SLOTS:
{slots_str}

SERVICE: {service_str}
ARTISAN: {therapist_str}
CONTEXT: {context_str}
BOOKING URL: {STUDIO["booking_url"]}
INSTAGRAM: {STUDIO["instagram"]}

APPROVED BOOKING LANGUAGE (use these as anchors):
{approved_str}

NEVER USE: "last minute", "hurry", "don't wait", "act now", "cancellation available",
"still spots left", "book now before it's gone", countdown language, promotional energy.

Frame every slot as: a window has opened — and you are being personally invited.
Not as: we have a gap and need to fill it.

The guest receiving this should feel quietly chosen. Not mass-messaged.

DELIVERABLE FORMAT:

### 1. INSTAGRAM STORY TEXT
2–3 lines. Clean. No emojis. Quiet privilege. As if typed by hand.

### 2. INSTAGRAM FEED CAPTION
4–6 lines. Atmospheric, brief, elegant. Booking URL on the final line.

### 3. SMS / WHATSAPP MESSAGE
Max 160 characters including booking link. Warm, personal, direct.
Feels like it was sent by a person who thought of you specifically.

### 4. EMAIL
Subject line (max 45 chars) + 4-line body. Nothing more.
The reader should feel they are the only person receiving this.

### 5. STORY VISUAL DIRECTION
One sentence describing the exact image or video to pair with the Story.
Must feel cinematic and brand-aligned.
(e.g., "The empty treatment chair in warm late-afternoon light, slightly out of focus.")

Tone: a close friend who runs the most refined studio in Hasselt
just thought of you. That is the entirety of the energy.
"""
        result = self._call(LAST_MINUTE_BOOKING_SYSTEM, prompt)
        output = self._header(f"Last Minute — {service_str}") + result
        path = self._save(output, f"lastminute_{service_str.replace(' ', '_')[:30]}")
        print(f"  Saved → {path}")
        return output

    def generate_cancellation_fill(
        self,
        date: str,
        time: str,
        service: str,
        duration_minutes: int = 60,
    ) -> str:
        urgency_note = self._urgency_note(date)
        prompt = f"""
A cancellation has created an opening at Maison BU.

Opening: {date} at {time} ({duration_minutes} minutes)
Service available: {service}
Timing context: {urgency_note}
Booking URL: {STUDIO["booking_url"]}

This is time-sensitive but the tone must remain unhurried and elegant.
The guest who fills this slot should feel they received a gift, not a
desperate sales message.

Produce:
1. INSTAGRAM STORY (2 lines max, pure and clean)
2. SMS (under 140 characters)
3. EMAIL SUBJECT + 3-LINE BODY
4. WHATSAPP BROADCAST message (slightly more personal, max 200 characters)
"""
        result = self._call(LAST_MINUTE_BOOKING_SYSTEM, prompt)
        output = self._header(f"Cancellation Fill — {date} {time}") + result
        path = self._save(output, f"cancellation_{date.replace(' ', '_')}_{time.replace(':', '')}")
        print(f"  Saved → {path}")
        return output

    def generate_slow_period_campaign(
        self,
        period: str,
        available_services: list[str],
        duration_days: int = 7,
    ) -> str:
        services_str = ", ".join(available_services)
        prompt = f"""
Maison BU has a quieter period coming up and wants to gently invite bookings.

Period: {period} ({duration_days} days)
Available services: {services_str}
Booking URL: {STUDIO["booking_url"]}

This is NOT a sale. There are no discounts. This is simply an invitation
to those who have been meaning to visit — a reminder that the atelier
is ready to receive them.

Create a 3-part mini-campaign:

PART 1 — THE ANNOUNCEMENT (Day 1)
Story text + email subject + opening line.

PART 2 — THE REMINDER (Day 3–4)
A different angle. Sensory, specific, personal.

PART 3 — THE FINAL INVITATION (Day 6–7)
Gentle close. "A few moments remain."

For each part: Story text, SMS, email subject + body.
"""
        result = self._call(LAST_MINUTE_BOOKING_SYSTEM, prompt)
        output = self._header(f"Slow Period Campaign — {period}") + result
        path = self._save(output, f"slow_period_{period.replace(' ', '_')[:30]}")
        print(f"  Saved → {path}")
        return output

    @staticmethod
    def _urgency_note(date_str: str) -> str:
        """Return a plain-language urgency context string."""
        date_lower = date_str.lower()
        if "today" in date_lower or "tonight" in date_lower:
            return "Same day — act within hours"
        if "tomorrow" in date_lower:
            return "Next day — act within 24 hours"
        return "Short notice — within the next few days"
