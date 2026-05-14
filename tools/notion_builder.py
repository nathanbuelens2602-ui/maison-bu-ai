#!/usr/bin/env python3
"""
Maison BU — Notion Marketing OS Builder
Uitvoeren op je laptop: python tools/notion_builder.py
Vereist: pip install requests python-dotenv
"""

import os
import sys
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("NOTION_TOKEN")
if not TOKEN:
    print("❌  NOTION_TOKEN niet gevonden. Voeg toe aan .env")
    sys.exit(1)

API = "https://api.notion.com/v1"
H = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}

# ─── helpers ────────────────────────────────────────────────────────────────

def call(method, path, body=None):
    r = requests.request(method, f"{API}/{path}", headers=H, json=body)
    time.sleep(0.4)
    if r.status_code not in (200, 201):
        print(f"    ⚠  {r.status_code}: {r.text[:300]}")
        return None
    return r.json()


def page(parent_id, title, children=None, db_parent=False, workspace=False):
    if workspace:
        par = {"type": "workspace", "workspace": True}
    elif db_parent:
        par = {"type": "database_id", "database_id": parent_id}
    else:
        par = {"type": "page_id", "page_id": parent_id}
    body = {
        "parent": par,
        "properties": {"title": {"title": [{"text": {"content": title}}]}},
    }
    if children:
        body["children"] = children[:100]
    res = call("POST", "pages", body)
    if res:
        print(f"  ✓  {title}")
    return res


def database(parent_id, title, props):
    body = {
        "parent": {"type": "page_id", "page_id": parent_id},
        "title": [{"text": {"content": title}}],
        "properties": props,
    }
    res = call("POST", "databases", body)
    if res:
        print(f"  ✓  Database: {title}")
    return res


def search_any_page():
    res = call("POST", "search", {"filter": {"property": "object", "value": "page"}, "page_size": 1})
    if res and res.get("results"):
        return res["results"][0]["id"]
    return None


# ─── block helpers ───────────────────────────────────────────────────────────

def h1(t):
    return {"object": "block", "type": "heading_1",
            "heading_1": {"rich_text": [{"type": "text", "text": {"content": t}}]}}

def h2(t):
    return {"object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": t}}]}}

def h3(t):
    return {"object": "block", "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": t}}]}}

def p(t):
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": t}}]}}

def div():
    return {"object": "block", "type": "divider", "divider": {}}

def todo(t, done=False):
    return {"object": "block", "type": "to_do",
            "to_do": {"rich_text": [{"type": "text", "text": {"content": t}}], "checked": done}}

def bullet(t):
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": t}}]}}

def callout(t, icon="💡"):
    return {"object": "block", "type": "callout",
            "callout": {"rich_text": [{"type": "text", "text": {"content": t}}],
                        "icon": {"type": "emoji", "emoji": icon}}}

def quote(t):
    return {"object": "block", "type": "quote",
            "quote": {"rich_text": [{"type": "text", "text": {"content": t}}]}}

def code(t, lang="plain text"):
    return {"object": "block", "type": "code",
            "code": {"rich_text": [{"type": "text", "text": {"content": t}}], "language": lang}}


# ─── content database schema ────────────────────────────────────────────────

DB_PROPS = {
    "Titel": {"title": {}},
    "Type": {"select": {"options": [
        {"name": "Reel", "color": "purple"},
        {"name": "Feedpost", "color": "blue"},
        {"name": "Story Flow", "color": "green"},
        {"name": "Email", "color": "yellow"},
    ]}},
    "Week": {"select": {"options": [
        {"name": "Week 1", "color": "gray"},
        {"name": "Week 2", "color": "brown"},
        {"name": "Week 3", "color": "orange"},
        {"name": "Week 4", "color": "red"},
    ]}},
    "Pillar": {"select": {"options": [
        {"name": "De Maison", "color": "default"},
        {"name": "De Craft", "color": "purple"},
        {"name": "De Gast", "color": "blue"},
        {"name": "De Transformatie", "color": "green"},
        {"name": "De Filosofie", "color": "gray"},
        {"name": "De Ceremonie", "color": "pink"},
    ]}},
    "Status": {"select": {"options": [
        {"name": "Idee", "color": "gray"},
        {"name": "In Productie", "color": "yellow"},
        {"name": "Klaar", "color": "blue"},
        {"name": "Wacht op Goedkeuring", "color": "orange"},
        {"name": "Gepubliceerd", "color": "green"},
    ]}},
    "Publicatiedatum": {"date": {}},
    "CTA": {"select": {"options": [
        {"name": "Geen", "color": "gray"},
        {"name": "Fluistering", "color": "blue"},
        {"name": "Weloverwogen", "color": "orange"},
        {"name": "Uitnodiging", "color": "red"},
    ]}},
    "Asset Link": {"url": {}},
    "Notities": {"rich_text": {}},
}

# ─── all 36 june 2026 content items ──────────────────────────────────────────
# (type, title, week, pillar, date YYYY-MM-DD, cta, status)

ITEMS = [
    # WEEK 1 — Wereldopbouw
    ("Reel",       "Reel 01 — Juni betreedt de maison",                    "Week 1", "De Maison",       "2026-06-02", "Geen",         "Klaar"),
    ("Reel",       "Reel 02 — Het golf van zomer",                         "Week 1", "De Craft",        "2026-06-06", "Geen",         "Klaar"),
    ("Feedpost",   "Post 01 — Juni betreedt de maison",                    "Week 1", "De Maison",       "2026-06-02", "Geen",         "Klaar"),
    ("Feedpost",   "Post 02 — Over vakmanschap in de zomer (Kristof)",     "Week 1", "De Filosofie",    "2026-06-05", "Geen",         "Klaar"),
    ("Feedpost",   "Post 03 — De signature cut, opnieuw gedacht",          "Week 1", "De Craft",        "2026-06-04", "Geen",         "Klaar"),
    ("Story Flow", "SF 01 — Hoe juni eruitziet in de maison",             "Week 1", "De Maison",       "2026-06-01", "Geen",         "Klaar"),
    ("Story Flow", "SF 02 — De maison in de vroege ochtend",              "Week 1", "De Maison",       "2026-06-03", "Geen",         "Klaar"),
    ("Story Flow", "SF 03 — Vijf dingen die we nooit zullen doen",        "Week 1", "De Filosofie",    "2026-06-06", "Geen",         "Klaar"),
    ("Story Flow", "SF 04 — Wat is een signature cut?",                   "Week 1", "De Craft",        "2026-06-07", "Geen",         "Klaar"),
    # WEEK 2 — De Fluistering
    ("Reel",       "Reel 03 — Een kleur die zichzelf niet aankondigt",    "Week 2", "De Transformatie","2026-06-09", "Fluistering",  "Klaar"),
    ("Reel",       "Reel 04 — De gast die een dinsdag droeg",             "Week 2", "De Gast",         "2026-06-13", "Fluistering",  "Klaar"),
    ("Feedpost",   "Post 04 — De golf die altijd bestond",                "Week 2", "De Transformatie","2026-06-08", "Fluistering",  "Klaar"),
    ("Feedpost",   "Post 05 — Ze arriveerde met een dinsdag",             "Week 2", "De Gast",         "2026-06-11", "Fluistering",  "Klaar"),
    ("Feedpost",   "Post 06 — Kleur die zichzelf niet aankondigt",        "Week 2", "De Transformatie","2026-06-13", "Fluistering",  "Klaar"),
    ("Story Flow", "SF 05 — Beachwaves voor jouw haar",                   "Week 2", "De Craft",        "2026-06-10", "Fluistering",  "Klaar"),
    ("Story Flow", "SF 06 — Wat onze gasten echt voelen",                 "Week 2", "De Gast",         "2026-06-10", "Fluistering",  "Klaar"),
    ("Story Flow", "SF 07 — De kleur van juni",                           "Week 2", "De Transformatie","2026-06-14", "Fluistering",  "Klaar"),
    ("Story Flow", "SF 08 — Kristof over zomer en terughoudendheid",      "Week 2", "De Filosofie",    "2026-06-12", "Fluistering",  "Klaar"),
    # WEEK 3 — De Weloverwogen Vraag
    ("Reel",       "Reel 05 — Kristof over vakmanschap",                  "Week 3", "De Filosofie",    "2026-06-16", "Weloverwogen", "Klaar"),
    ("Reel",       "Reel 06 — De ceremonieochtend",                       "Week 3", "De Ceremonie",    "2026-06-20", "Weloverwogen", "Klaar"),
    ("Feedpost",   "Post 07 — Sommige dagen vragen alles (Huwelijk)",     "Week 3", "De Ceremonie",    "2026-06-16", "Weloverwogen", "Klaar"),
    ("Feedpost",   "Post 08 — Over niet achter trends aanlopen (Kristof)","Week 3", "De Filosofie",    "2026-06-19", "Geen",         "Klaar"),
    ("Feedpost",   "Post 09 — De communieochtend",                        "Week 3", "De Ceremonie",    "2026-06-20", "Weloverwogen", "Klaar"),
    ("Story Flow", "SF 09 — De bruid de avond voor de ceremonie",         "Week 3", "De Ceremonie",    "2026-06-15", "Weloverwogen", "Klaar"),
    ("Story Flow", "SF 10 — De communieochtend",                          "Week 3", "De Ceremonie",    "2026-06-17", "Weloverwogen", "Klaar"),
    ("Story Flow", "SF 11 — Waarom we e-mail verkiezen boven een link",   "Week 3", "De Filosofie",    "2026-06-18", "Weloverwogen", "Klaar"),
    ("Story Flow", "SF 12 — De headspa in juni",                          "Week 3", "De Craft",        "2026-06-21", "Weloverwogen", "Klaar"),
    # WEEK 4 — De Uitnodiging
    ("Reel",       "Reel 07 — De vlucht is over drie dagen",              "Week 4", "De Gast",         "2026-06-23", "Uitnodiging",  "Klaar"),
    ("Reel",       "Reel 08 — Een opening heeft zich voorgedaan",         "Week 4", "De Maison",       "2026-06-27", "Uitnodiging",  "Klaar"),
    ("Feedpost",   "Post 10 — Ze had het uitgesteld tot juni",            "Week 4", "De Gast",         "2026-06-23", "Uitnodiging",  "Klaar"),
    ("Feedpost",   "Post 11 — De maison is klaar om u te ontvangen",      "Week 4", "De Maison",       "2026-06-25", "Uitnodiging",  "Klaar"),
    ("Feedpost",   "Post 12 — Deze zomer besloot ze te stoppen met haasten","Week 4","De Gast",        "2026-06-28", "Uitnodiging",  "Klaar"),
    ("Story Flow", "SF 13 — De vlucht is over drie dagen",                "Week 4", "De Gast",         "2026-06-22", "Uitnodiging",  "Klaar"),
    ("Story Flow", "SF 14 — Zij had het al sinds mei bedacht",            "Week 4", "De Gast",         "2026-06-24", "Uitnodiging",  "Klaar"),
    ("Story Flow", "SF 15 — Wat juli niet kan geven wat juni nog kan",    "Week 4", "De Maison",       "2026-06-28", "Uitnodiging",  "Klaar"),
    ("Story Flow", "SF 16 — Maison BU wenst u een mooie zomer",          "Week 4", "De Maison",       "2026-06-30", "Uitnodiging",  "Klaar"),
]


def db_item_props(typ, title, week, pillar, date_str, cta, status):
    return {
        "Titel":          {"title": [{"text": {"content": title}}]},
        "Type":           {"select": {"name": typ}},
        "Week":           {"select": {"name": week}},
        "Pillar":         {"select": {"name": pillar}},
        "Status":         {"select": {"name": status}},
        "Publicatiedatum":{"date": {"start": date_str}},
        "CTA":            {"select": {"name": cta}},
    }


# ─── page content builders ───────────────────────────────────────────────────

def home_blocks(db_page_id, kalender_id, vandaag_id, workflow_id, richtlijn_id, asset_id):
    return [
        callout(
            "Maison BU · De Zoetheid van Juni 2026 · Marketing OS\n"
            "Alles op één plek. Strategie, content, checklists, workflow.",
            "🌿"
        ),
        div(),
        h2("📌 Snelnavigatie"),
        bullet("📋 Content Database → alle 36 juni-stukken"),
        bullet("🌅 Vandaag → wat staat er vandaag gepland?"),
        bullet("📅 Deze Week → weekoverzicht"),
        bullet("✅ Checklists → voor, tijdens en na het posten"),
        bullet("🔄 Posting Workflow → 6-stappen proces"),
        bullet("🎨 Merkrichtlijnen → de regels die nooit veranderen"),
        bullet("📁 Asset Beheer → mappenstructuur en naamconventie"),
        bullet("📸 Shootdag Planner → shot list en voorbereiding"),
        div(),
        h2("🗓 Campagne — De Zoetheid van Juni"),
        p("Week 1 · Wereldopbouw (1–7 juni) — geen CTA's, mysterie opbouwen"),
        p("Week 2 · De Fluistering (8–14 juni) — zachte CTAs, zomerafspraken"),
        p("Week 3 · De Weloverwogen Vraag (15–21 juni) — ceremonie & huwelijk"),
        p("Week 4 · De Uitnodiging (22–30 juni) — directe uitnodiging, afsluiting"),
        div(),
        quote("Zou Kristof dit gezegd hebben? Als nee → herschrijf."),
    ]


def vandaag_blocks():
    return [
        callout("Filter de Content Database op vandaag's datum om te zien wat er gepland staat.", "🌅"),
        div(),
        h2("Dagelijkse checklist"),
        h3("Voor het posten"),
        todo("Caption nagelezen als Kristof — klinkt het menselijk?"),
        todo("Geen verboden woorden (luxury, deal, boek nu, miss het niet, enz.)"),
        todo("Juiste CTA voor deze week"),
        todo("Asset klaar in correct formaat"),
        todo("Publicatietijd correct ingesteld in Later / Buffer / Instagram"),
        div(),
        h3("Na het posten"),
        todo("Status → Gepubliceerd in Content Database"),
        todo("Datum bevestigd"),
        todo("Reacties bekeken na 1 uur"),
        div(),
        h2("Vaste publicatietijden"),
        p("Maandag  18:30 — Feedpost of Story"),
        p("Dinsdag  19:00 — Reel"),
        p("Woensdag 18:00 — Story"),
        p("Donderdag 19:00 — Feedpost"),
        p("Vrijdag  08:00 — Kristof / Filosofie"),
        p("Zaterdag 10:00 — Story of Reel"),
        p("Zondag   11:00 — Slotweek (Week 4)"),
    ]


def week_blocks():
    return [
        callout("Filter de Content Database op 'Deze Week' om het weekoverzicht te zien.", "📅"),
        div(),
        h2("Week 1 — Wereldopbouw"),
        p("Doel: mysterie opbouwen. Geen CTA's. Geen gezichten."),
        p("4 posts klaar · 2 reels · 4 story flows"),
        div(),
        h2("Week 2 — De Fluistering"),
        p("Doel: eerste zachte uitnodiging. CTA: 'Reserveer jouw ritueel. Link in bio.'"),
        p("4 posts klaar · 2 reels · 4 story flows · 1 email"),
        div(),
        h2("Week 3 — De Weloverwogen Vraag"),
        p("Doel: ceremonie & huwelijk. CTA via e-mail: hello@maisonbu.be"),
        p("3 posts · 2 reels · 4 story flows"),
        div(),
        h2("Week 4 — De Uitnodiging"),
        p("Doel: directe uitnodiging. CTA: maisonbu.be/book"),
        p("3 posts · 2 reels · 4 story flows · herboeking email"),
    ]


def workflow_blocks():
    return [
        quote("Van idee tot gepubliceerd — stap voor stap."),
        div(),
        h2("De 6 stappen"),
        h3("Stap 1 — Idee 💡"),
        bullet("Nieuw item aanmaken in Content Database"),
        bullet("Status: Idee"),
        bullet("Type, Pillar en Week invullen"),
        bullet("Kort concept noteren"),
        div(),
        h3("Stap 2 — Aanmaken ✏️"),
        bullet("Template openen (Reel / Feedpost / Story)"),
        bullet("Caption schrijven"),
        bullet("Visueel beschrijven"),
        bullet("Status: In Productie"),
        div(),
        h3("Stap 3 — Asset maken 🎨"),
        bullet("Canva / Premiere / CapCut openen"),
        bullet("Ontwerp of video afwerken"),
        bullet("Exporteren: Feedpost 1080×1350px JPG · Reel 1080×1920px MP4 · Story 1080×1920px"),
        bullet("Asset link toevoegen aan Content Database"),
        div(),
        h3("Stap 4 — Goedkeuring 👀"),
        todo("Toon correct?"),
        todo("Geen verboden woorden?"),
        todo("'Atelier' nergens — altijd 'de maison'?"),
        todo("CTA past bij de week?"),
        div(),
        h3("Stap 5 — Klaar ✅"),
        bullet("Status: Klaar"),
        bullet("Publicatiedatum en tijd instellen in Later / Buffer / Instagram"),
        div(),
        h3("Stap 6 — Gepubliceerd 📣"),
        bullet("Status: Gepubliceerd"),
        bullet("Datum bevestigd in database"),
        bullet("Engagement na 24u bekijken"),
        div(),
        h2("Status flow"),
        code("💡 Idee  →  ✏️ In Productie  →  ✅ Klaar  →  👀 Goedkeuring  →  📣 Gepubliceerd"),
    ]


def merkrichtlijnen_blocks():
    return [
        quote("De regels die nooit veranderen."),
        div(),
        h2("Kleuren"),
        p("Diepzwart  #1A1A18 — Hoofdkleur, accenten, tekst"),
        p("Warm wit   #F8F5F0 — Achtergronden, lichte schermen"),
        p("Crème      #EDE9E3 — Tussenliggende sfeer"),
        p("Lichtgrijs #C9BFB4 — Scheidingslijnen"),
        p("Tekst grijs #999999 — Labels, meta-informatie"),
        div(),
        h2("Lettertypes"),
        p("Headlines:   Cormorant Garamond Italic"),
        p("Bodytekst:   Cormorant Garamond Regular"),
        p("Labels / CTA: Arial of Helvetica Regular"),
        p("Grootte: Klein. Altijd. Maison BU fluistert."),
        div(),
        h2("Taal"),
        p("✅ Altijd Nederlands"),
        p("✅ Frans accent spaarzaam: maison · savoir-faire · l'invitation · signature"),
        p("❌ Nooit Engelse clichés als stijlkeuze"),
        p("❌ Nooit 'het atelier' → altijd 'de maison'"),
        div(),
        h2("Goede woorden"),
        p("verfijning · vakmanschap · tijdloos · gast (nooit klant) · de maison · gecreëerd voor jou · aanwezig · ritueel · stil · eerbiedig · savoir-faire"),
        div(),
        h2("VERBODEN woorden"),
        p("❌ luxury · premium · transformatie · glam · deal"),
        p("❌ aanbieding · boek nu · mis het niet · summer sale"),
        p("❌ hair goals · glow-up · before/after · new hair who dis"),
        p("❌ het atelier · the atelier · notre atelier"),
        div(),
        h2("CTA regels per week"),
        p("Week 1: Geen CTA"),
        p("Week 2: Fluistering — 'Reserveer jouw moment. Link in bio.'"),
        p("Week 3: Weloverwogen — 'hello@maisonbu.be' (voor ceremonies)"),
        p("Week 4: Uitnodiging — 'maisonbu.be/book'"),
        div(),
        h2("Visuele regels"),
        p("✅ Warm licht — gouden uur: 7–9u of 17–19u"),
        p("✅ Statische of trage camera (slider)"),
        p("✅ Close-ups van handen en haartextuur"),
        p("✅ Week 1: geen gezichten — mysterie bewaren"),
        p("❌ Geen ring lights"),
        p("❌ Geen viral audio of trending sounds"),
        p("❌ Geen koude kleurfilters"),
        p("❌ Geen voor/na vergelijkingen zonder toestemming"),
        div(),
        h2("De Soul Test"),
        callout("Vraag jezelf vóór publicatie:\n\"Zou Kristof dit gezegd hebben?\"\n\nAls nee → herschrijf.\nAls ja → goedgekeurd.", "✨"),
        div(),
        h2("Contactgegevens"),
        p("Maison BU · Hasselt, België"),
        p("hello@maisonbu.be"),
        p("maisonbu.be · maisonbu.be/book"),
    ]


def checklists_blocks():
    return [
        div(),
        h2("Maandelijkse lancering — Week 1"),
        todo("Strategie en kalender volledig ingevuld in Content Database"),
        todo("Shootdag ingepland en voorbereid"),
        todo("Week 1 content aangemaakt (4 stuks)"),
        todo("Geen CTA's in Week 1 content — gecontroleerd"),
        todo("Muziek geselecteerd per reel"),
        todo("Assets klaar in Google Drive / Canva"),
        div(),
        h2("Maandelijkse lancering — Week 2"),
        todo("Week 2 content aangemaakt (4 stuks)"),
        todo("CTA aanwezig maar subtiel ('Link in bio')"),
        todo("Mailchimp campagne klaar en getest"),
        todo("E-mail verstuurd op dinsdag 09:15"),
        div(),
        h2("Maandelijkse lancering — Week 3"),
        todo("Ceremonie content aangemaakt"),
        todo("CTA via e-mail (hello@maisonbu.be) voor huwelijk/communie"),
        todo("Kristof filosofie post ingepland"),
        div(),
        h2("Maandelijkse lancering — Week 4"),
        todo("Sluitingsweek content aangemaakt"),
        todo("CTA op elk stuk (altijd als laatste regel)"),
        todo("Herboekings-e-mail verstuurd"),
        todo("Alle content gepubliceerd"),
        div(),
        h2("Dagelijkse posting checklist"),
        h3("Voor het posten"),
        todo("Caption nagelezen als Kristof — klinkt het menselijk?"),
        todo("Geen verboden woorden"),
        todo("Juiste CTA voor deze week"),
        todo("Asset klaar in correct formaat"),
        todo("Publicatietijd correct ingesteld"),
        h3("Na het posten"),
        todo("Status → Gepubliceerd in Content Database"),
        todo("Datum bevestigd"),
        todo("Reacties bekeken na 1 uur"),
        div(),
        h2("Shootdag checklist"),
        todo("Shot list volledig"),
        todo("Licht: gouden uur (7–9u of 17–19u)"),
        todo("Camera geladen, geheugenkaart leeg"),
        todo("Alle shots gemaakt"),
        todo("Bestanden overgezet naar Drive"),
        todo("Asset links in Content Database bijgewerkt"),
        div(),
        h2("Mailchimp checklist"),
        todo("Hardop gelezen als Kristof — klinkt het menselijk?"),
        todo("Onderwerpregel getest op mobiel (volledig zichtbaar)"),
        todo("Boekingslink getest en actief"),
        todo("Uitschrijflink functioneel"),
        todo("Slechts één CTA — bevestigd"),
        todo("Geen verboden woorden"),
        todo("Taal: Nederlands — geen Engelse clichés"),
        todo("'Atelier' nergens — altijd 'de maison'"),
    ]


def asset_blocks():
    return [
        quote("Alles op de juiste plek, altijd terug te vinden."),
        div(),
        h2("Mappenstructuur"),
        code(
            "📁 Maison BU — Assets\n"
            "├── 📁 Juni 2026\n"
            "│   ├── 📁 Reels (ruwe bestanden + exports)\n"
            "│   ├── 📁 Feedposts (afbeeldingen)\n"
            "│   ├── 📁 Stories (frames)\n"
            "│   ├── 📁 Shootdag 2026-06-04\n"
            "│   └── 📁 E-mail (header afbeelding)\n"
            "├── 📁 Brand Assets (permanent)\n"
            "│   ├── Logo (alle varianten)\n"
            "│   ├── Kleurpaletten\n"
            "│   ├── Lettertypes\n"
            "│   └── Handtekening Kristof\n"
            "└── 📁 Archief\n"
            "    └── [vorige maanden]"
        ),
        div(),
        h2("Exportformaten"),
        p("Feedpost   → 1080 × 1350px (4:5) · JPG of PNG · Hoog"),
        p("Reel       → 1080 × 1920px (9:16) · MP4 (H.264) · Hoog"),
        p("Story      → 1080 × 1920px (9:16) · JPG of MP4 · Hoog"),
        p("E-mail header → 600 × 340px · JPG · Gemiddeld"),
        div(),
        h2("Naamconventie bestanden"),
        code(
            "[type]_[week]_[korte-titel]_[datum].[extensie]\n\n"
            "reel_w1_juni-betreedt-maison_20260602.mp4\n"
            "feedpost_w2_golf-bestond_20260609.jpg\n"
            "story_w3_bruid-dag-erna_20260616.mp4"
        ),
    ]


def shootdag_blocks():
    return [
        callout("Shootdag voor juni 2026 — plan dit op 2 of 3 juni (Week 1)", "📸"),
        div(),
        h2("Shot list — Week 1 (geen gezichten)"),
        todo("Maison in junilicht — architecturale opname vroege ochtend"),
        todo("Schaar, kam, spuitfles — close-up stilleven"),
        todo("Hand die gereedschap neerlegt"),
        todo("Betonvloer met lichtval"),
        todo("Spiegel die licht terugkaatst"),
        todo("Haar close-up — textuur in beweging (beachwaves)"),
        todo("Handen die golf vormen — slow motion 120fps"),
        todo("Lege stoel in junilicht"),
        div(),
        h2("Shot list — Week 2 (transformatie)"),
        todo("Kleurpigment in kom — close-up"),
        todo("Borstel die kleur aanbrengt — bewust en traag"),
        todo("Haar dat gewassen wordt — fragmenten"),
        todo("Gast vertrekt — rug, licht, haar in beweging — straat buiten"),
        div(),
        h2("Shot list — Week 3 (ceremonie)"),
        todo("Elegante opsteek — detail, geen gezicht"),
        todo("Handen die haarpins plaatsen"),
        todo("Communiestijl — close-up details"),
        todo("Moeder-kind sfeer — warmte zonder gezichten"),
        div(),
        h2("Productie-afspraken"),
        p("Gouden uur: 7–9u of 17–19u"),
        p("Geen ring lights"),
        p("Camera: statisch voor architectuur / langzame slide voor haar"),
        p("Kleurgrading: warm en ingetogen — geen filters, geen presets"),
        p("Elke cut minimaal 3 seconden — geen flits, geen snelheid"),
        div(),
        h2("Na de shoot"),
        todo("Bestanden overgezet naar Google Drive"),
        todo("Reel-exports: MP4 H.264 1080×1920"),
        todo("Feedpost-exports: JPG 1080×1350"),
        todo("Asset links bijgewerkt in Content Database"),
    ]


def templates_blocks():
    return [
        div(),
        h2("🎬 Reel Template"),
        p("CONCEPT: [wat laat dit reel zien?]"),
        p("WEEK: [1 / 2 / 3 / 4]"),
        p("PILLAR: [De Maison / De Craft / De Gast / De Transformatie / De Filosofie / De Ceremonie]"),
        p("DUUR: [30 / 45 / 60 sec]"),
        div(),
        p("VISUELE STRUCTUUR"),
        p("[00:00–00:xx] Opening — [beschrijving]"),
        p("[00:xx–00:xx] Kern — [beschrijving]"),
        p("[00:xx–00:xx] Slot — [beschrijving]"),
        div(),
        p("TEKST OP SCHERM"),
        p("[tijdstempel] — '[tekst]' (klein, serif, gecentreerd)"),
        div(),
        p("MUZIEK: [instrumentaal / referentie]"),
        div(),
        p("CAPTION"),
        p("[opening zonder introductie]"),
        p("[kern — diepte of emotie]"),
        p("[afsluiting — stilte of CTA van de week]"),
        p("[hashtags — max 8]"),
        div(),
        div(),
        h2("📸 Feedpost Template"),
        p("TITEL: [intern werktitel]"),
        p("WEEK: [1 / 2 / 3 / 4]"),
        p("PILLAR: [pillar naam]"),
        p("BEELD: [beschrijving van het visuele]"),
        div(),
        p("CAPTION"),
        p("[opening — directe sfeer]"),
        p(""),
        p("[kern — diepte, eerlijkheid, vakmanschap of emotie]"),
        p(""),
        p("[afsluiting — stilte of CTA van de week]"),
        p(""),
        p("#MaisonBU #[relevante tag] #[relevante tag] #Hasselt"),
        div(),
        div(),
        h2("📖 Story Flow Template"),
        p("TITEL: [intern werktitel]"),
        p("WEEK: [1 / 2 / 3 / 4]"),
        p("AANTAL FRAMES: [3–7]"),
        div(),
        p("FRAME 1: [beeld + tekst]"),
        p("FRAME 2: [beeld + tekst]"),
        p("FRAME 3: [beeld + tekst — afsluiting of CTA]"),
    ]


# ─── main builder ────────────────────────────────────────────────────────────

def build():
    print("\n🌿 Maison BU — Notion Marketing OS Builder\n")

    # 1. Root page — probeer workspace, dan bestaande pagina als terugval
    print("Aanmaken: Home pagina...")
    root = page(None, "🏠 Maison BU — Marketing OS", workspace=True)
    if not root:
        print("  ↳ Workspace-level mislukt, zoek bestaande pagina als parent...")
        parent_id = sys.argv[1] if len(sys.argv) > 1 else search_any_page()
        if parent_id:
            print(f"  ↳ Gevonden parent: {parent_id}")
            root = page(parent_id, "🏠 Maison BU — Marketing OS")
        if not root:
            print("\n❌ Kon geen pagina aanmaken.")
            print("   Zorg dat de Notion-integratie toegang heeft tot minstens één pagina:")
            print("   Open een pagina in Notion → ··· → Connections → voeg de integratie toe.")
            sys.exit(1)

    root_id = root["id"]
    print(f"\n   Root pagina ID: {root_id}")
    print(f"   Root URL: https://notion.so/{root_id.replace('-', '')}\n")

    # 2. Content Database
    print("Aanmaken: Content Database...")
    db = database(root_id, "📋 Content Database — Juni 2026", DB_PROPS)
    if not db:
        print("❌ Content Database kon niet aangemaakt worden.")
        sys.exit(1)
    db_id = db["id"]

    # 3. Add all 36 items
    print(f"\nInvullen: {len(ITEMS)} content items...")
    for i, (typ, title, week, pillar, date_str, cta, status) in enumerate(ITEMS, 1):
        props = db_item_props(typ, title, week, pillar, date_str, cta, status)
        result = add_to_database(db_id, props)
        if result:
            print(f"  {i:02d}/36  {title[:55]}")
        else:
            print(f"  {i:02d}/36  ⚠ mislukt: {title[:55]}")

    # 4. Sub-pages
    print("\nAanmaken: Sub-pagina's...")

    vandaag = page(root_id, "🌅 Vandaag", vandaag_blocks())
    week_pg = page(root_id, "📅 Deze Week", week_blocks())
    workflow_pg = page(root_id, "🔄 Posting Workflow", workflow_blocks())
    richtlijn_pg = page(root_id, "🎨 Merkrichtlijnen", merkrichtlijnen_blocks())
    checklist_pg = page(root_id, "✅ Checklists", checklists_blocks())
    asset_pg = page(root_id, "📁 Asset Beheer", asset_blocks())
    shoot_pg = page(root_id, "📸 Shootdag Planner", shootdag_blocks())
    template_pg = page(root_id, "📝 Templates", templates_blocks())

    # 5. Update home page with navigation (append blocks)
    print("\nBijwerken: Home pagina...")
    nav = [
        callout(
            "Maison BU · De Zoetheid van Juni 2026 · Marketing OS\n"
            "Alles op één plek. Strategie, content, checklists, workflow.",
            "🌿"
        ),
        div(),
        h2("📌 Snelnavigatie"),
        bullet("📋 Content Database → alle 36 juni-stukken"),
        bullet("🌅 Vandaag → wat staat er vandaag gepland?"),
        bullet("📅 Deze Week → weekoverzicht"),
        bullet("✅ Checklists → voor, tijdens en na het posten"),
        bullet("🔄 Posting Workflow → 6-stappen proces"),
        bullet("🎨 Merkrichtlijnen → de regels die nooit veranderen"),
        bullet("📁 Asset Beheer → mappenstructuur en naamconventie"),
        bullet("📸 Shootdag Planner → shot list en voorbereiding"),
        bullet("📝 Templates → Reel, Feedpost en Story Flow"),
        div(),
        h2("🗓 Campagne — De Zoetheid van Juni 2026"),
        p("Week 1 · Wereldopbouw (1–7 juni) — geen CTA's, mysterie opbouwen"),
        p("Week 2 · De Fluistering (8–14 juni) — zachte CTAs, zomerafspraken"),
        p("Week 3 · De Weloverwogen Vraag (15–21 juni) — ceremonie & huwelijk"),
        p("Week 4 · De Uitnodiging (22–30 juni) — directe uitnodiging, afsluiting"),
        div(),
        quote("Zou Kristof dit gezegd hebben? Als nee → herschrijf."),
    ]
    call("PATCH", f"blocks/{root_id}/children", {"children": nav})

    # 6. Summary
    print("\n" + "─" * 60)
    print("✅  Maison BU Marketing OS succesvol aangemaakt in Notion!")
    print(f"\n   🔗  Ga naar: https://notion.so/{root_id.replace('-', '')}")
    print("\n   Wat er aangemaakt is:")
    print("   · 📋 Content Database met alle 36 juni 2026 items")
    print("   · 🌅 Vandaag (met dagelijkse checklist)")
    print("   · 📅 Deze Week (campagne-overzicht)")
    print("   · 🔄 Posting Workflow (6 stappen)")
    print("   · 🎨 Merkrichtlijnen (kleuren, fonts, taal, soul test)")
    print("   · ✅ Checklists (maandelijks, dagelijks, shootdag, Mailchimp)")
    print("   · 📁 Asset Beheer (mappenstructuur + naamconventie)")
    print("   · 📸 Shootdag Planner (shot lists per week)")
    print("   · 📝 Templates (Reel / Feedpost / Story Flow)")
    print("\n   💡 Tip: Maak in Notion database-views aan:")
    print("      · Kalenderweergave (gefilterd op publicatiedatum)")
    print("      · Gefilterd op 'Status = Klaar' → klaar om te posten")
    print("      · Gefilterd op 'Week' → per week bekijken")
    print("─" * 60)


if __name__ == "__main__":
    build()
