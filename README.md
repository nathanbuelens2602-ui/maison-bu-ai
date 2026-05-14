# Maison BU — AI Marketing System

> *Where artistry meets ritual.*

A complete AI-powered marketing system for **Maison BU**, a high-end Hair & Beauty Lab in Hasselt, Belgium. Five specialised agents, one unified brand voice — inspired by Yves Saint Laurent, Jacquemus, and Four Seasons.

---

## System Architecture

```
maison-bu-ai/
├── main.py                          ← CLI entry point
├── orchestrator.py                  ← Coordinates all agents
├── config/
│   ├── brand_voice.py               ← Brand identity, tone, vocabulary
│   └── settings.py                  ← API keys, models, paths
├── agents/
│   ├── base_agent.py                ← Shared agent logic
│   ├── content_strategy_agent.py    ← Content calendars & campaigns
│   ├── caption_writing_agent.py     ← Instagram & social captions
│   ├── reel_script_agent.py         ← Cinematic video reel scripts
│   ├── mail_marketing_agent.py      ← Email campaigns & newsletters
│   └── last_minute_booking_agent.py ← Last-minute availability content
├── prompts/
│   └── system_prompts.py            ← All agent system prompts
├── tools/
│   └── booking_tools.py             ← Booking system integration stubs
└── outputs/                         ← All generated content saved here
    ├── content_calendar/
    ├── captions/
    ├── reel_scripts/
    ├── emails/
    └── last_minute/
```

---

## The Five Agents

### 1. Content Strategy Agent
Generates monthly content calendars, campaign briefs, and content pillar frameworks. Balances The Ritual, The Transformation, The Maison, The Edit, and L'Invitation across all weeks.

### 2. Caption Writing Agent
Crafts Instagram captions with cinematic precision. Each caption follows a sensory hook → intimate scene → quiet CTA architecture. Never sounds like an ad.

### 3. Reel Script Agent
Produces full production-ready reel scripts: shot lists, on-screen text, audio direction, music references, and caption copy. Inspired by the visual language of Loewe, Aesop, and Jacquemus.

### 4. Mail Marketing Agent
Writes email campaigns that feel like personal letters from the atelier — not newsletters, not promotional blasts. Handles campaigns, newsletters, welcome sequences, loyalty emails, and re-engagement.

### 5. Last Minute Booking Agent
Fills last-minute availability without ever sounding desperate. Frames every opening as a rare privilege. Produces Story copy, SMS, email, and WhatsApp content simultaneously.

---

## Setup

```bash
# 1. Clone and install
pip install -r requirements.txt

# 2. Configure your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Run
python main.py demo
```

---

## CLI Usage

```bash
# Full monthly campaign (calendar + caption + reel + email)
python main.py campaign --month June --year 2025 \
  --theme "The Golden Hour Edit" \
  --services "Colour & Balayage, Scalp Rituals" \
  --email-obj "Drive summer bookings"

# Single caption
python main.py caption \
  --pillar "The Ritual" \
  --subject "A balayage session at golden hour" \
  --visual "Close-up of brush through golden hair, warm window light"

# Reel script
python main.py reel \
  --type ritual \
  --subject "Scalp ritual ceremony" \
  --duration medium

# Email campaign
python main.py email --type campaign \
  --campaign "The Golden Hour Edit" \
  --objective "Drive summer bookings" \
  --message "Summer calls for your most luminous self."

# Email: welcome / newsletter / loyalty / reengagement
python main.py email --type welcome
python main.py email --type newsletter --month June --year 2025 \
  --theme "Light & Ritual" --content "Summer colour guide, Scalp care edit"
python main.py email --type loyalty --milestone "1 year anniversary"
python main.py email --type reengagement --months 4

# Last-minute booking protocol (auto-checks cancellations + availability)
python main.py lastminute

# New client onboarding sequence
python main.py onboarding

# Brand World Kit (pillars brief + brand anthem reel)
python main.py brandkit

# Demo all agents
python main.py demo
```

---

## Brand Voice Reference

| Pillar | Emotion | Example vocabulary |
|---|---|---|
| The Ritual | Reverence, curiosity | atelier, savoir-faire, sculpted |
| The Transformation | Wonder, desire | luminous, silhouette, radiant |
| The Maison | Intimacy, belonging | maison, devoted, considered |
| The Edit | Trust, authority | curated, refined, timeless |
| L'Invitation | Desire, exclusivity | bespoke, signature, intentional |

**References:** Yves Saint Laurent · Jacquemus · Four Seasons

---

## Connecting Your Booking System

Edit `tools/booking_tools.py` to replace the stubs with calls to your live booking platform (Fresha, Planity, Booksy, or a custom API). The `LastMinuteBookingAgent` will automatically use real slot data once connected.

---

*Maison BU · Hasselt, Belgium*
