"""
Maison BU — Runtime Settings
"""
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Primary model for high-quality creative output
PRIMARY_MODEL = "claude-opus-4-7"

# Faster model for drafts and last-minute content
FAST_MODEL = "claude-sonnet-4-6"

# Token budgets
MAX_TOKENS = {
    "content_strategy": 4096,
    "caption": 1024,
    "reel_script": 2048,
    "email": 2048,
    "last_minute": 1024,
}

# Output paths
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
OUTPUTS = {
    "content_calendar": os.path.join(OUTPUT_DIR, "content_calendar"),
    "captions": os.path.join(OUTPUT_DIR, "captions"),
    "reel_scripts": os.path.join(OUTPUT_DIR, "reel_scripts"),
    "emails": os.path.join(OUTPUT_DIR, "emails"),
    "last_minute": os.path.join(OUTPUT_DIR, "last_minute"),
}

# Studio info used across agents
STUDIO = {
    "name": "Maison BU",
    "city": "Hasselt",
    "country": "Belgium",
    "instagram": "@maisonbu",
    "booking_url": "https://maisonbu.be/book",
    "phone": "+32 ...",
    "email": "hello@maisonbu.be",
}
