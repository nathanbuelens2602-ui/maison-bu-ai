#!/usr/bin/env python3
"""
Vult alle Maison BU Marketing OS sub-pagina's met de volledige geplande inhoud.
Cross-references worden als klikbare Notion-mentions toegevoegd.
Wist eerst bestaande blokken zodat duplicaten worden opgelost.
"""
import os, time, requests

TOKEN = os.getenv("NOTION_TOKEN")
API = "https://api.notion.com/v1"
H = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

def call(method, path, body=None):
    r = requests.request(method, f"{API}/{path}", headers=H, json=body)
    time.sleep(0.35)
    if r.status_code not in (200, 201, 204):
        print(f"  ⚠  {r.status_code}: {r.text[:200]}")
        return None
    if r.status_code == 204:
        return {}
    return r.json()

def find_pages(title):
    res = call("POST", "search", {"query": title, "filter": {"property": "object", "value": "page"}})
    if not res:
        return []
    ids = []
    for pg in res.get("results", []):
        props = pg.get("properties", {})
        t = props.get("title", {}).get("title", [])
        name = t[0]["plain_text"] if t else ""
        if title.lower() in name.lower():
            ids.append(pg["id"])
    return ids

def find_db(title):
    res = call("POST", "search", {"query": title, "filter": {"property": "object", "value": "database"}})
    if not res:
        return None
    for item in res.get("results", []):
        t = item.get("title", [])
        name = t[0]["plain_text"] if t else ""
        if title.lower() in name.lower():
            return item["id"]
    return None

def clear_page(page_id):
    res = call("GET", f"blocks/{page_id}/children?page_size=100")
    if not res:
        return
    for block in res.get("results", []):
        call("DELETE", f"blocks/{block['id']}")
        time.sleep(0.2)

def add_blocks(page_id, blocks):
    for i in range(0, len(blocks), 95):
        call("PATCH", f"blocks/{page_id}/children", {"children": blocks[i:i+95]})

def create_child_page(parent_id, title):
    res = call("POST", "pages", {
        "parent": {"page_id": parent_id},
        "properties": {"title": {"title": [{"text": {"content": title}}]}}
    })
    return res["id"] if res else None

# ── Block helpers ─────────────────────────────────────────────────────────────

def _rt(text):
    return {"type": "text", "text": {"content": text}}

def _mention(page_id):
    return {"type": "mention", "mention": {"type": "page", "page": {"id": page_id}}}

def p(*parts):
    """Paragraaf. Parts: strings of page_id-dicts van mention()."""
    rich = [_mention(x["id"]) if isinstance(x, dict) else _rt(x) for x in parts]
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rich}}

def mention(page_id):
    return {"id": page_id}  # wordt herkend door p()

def quote(t):
    return {"object": "block", "type": "quote",
            "quote": {"rich_text": [_rt(t)]}}

def h2(t):
    return {"object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [_rt(t)]}}

def h3(t):
    return {"object": "block", "type": "heading_3",
            "heading_3": {"rich_text": [_rt(t)]}}

def li(*parts):
    rich = [_mention(x["id"]) if isinstance(x, dict) else _rt(x) for x in parts]
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": rich}}

def todo(t):
    return {"object": "block", "type": "to_do",
            "to_do": {"rich_text": [_rt(t)], "checked": False}}

def div():
    return {"object": "block", "type": "divider", "divider": {}}

def code(content, language="plain text"):
    return {"object": "block", "type": "code",
            "code": {"rich_text": [_rt(content)], "language": language}}

def table(headers, rows, has_header=True):
    all_rows = [headers] + rows
    row_blocks = [
        {"object": "block", "type": "table_row",
         "table_row": {"cells": [[_rt(c)] for c in r]}}
        for r in all_rows
    ]
    return {
        "object": "block", "type": "table",
        "table": {
            "table_width": len(headers),
            "has_column_header": has_header,
            "has_row_header": False,
            "children": row_blocks,
        }
    }

# ── Pagina-inhoud (met cross-references) ──────────────────────────────────────

def build_pages(refs):
    """
    Bouwt alle pagina-inhoud met klikbare mentions naar andere pagina's.
    refs = dict met paginanamen → Notion page/db ID
    """
    db  = refs.get("Content Database")
    wf  = refs.get("Posting Workflow")
    mb  = refs.get("Merkrichtlijnen")
    ab  = refs.get("Asset Beheer")
    sp  = refs.get("Shootdag Planner")
    tpl = refs.get("Templates")

    return {

        "Vandaag": [
            quote("Alleen zien wat je vandaag moet doen. Niets meer."),
            div(),
            h2("📌 Eenmalige instelling — Linked View (doe dit één keer in Notion)"),
            p("Stap 1 — Klik op een lege regel hieronder en typ:  /linked view  → druk Enter"),
            p("Stap 2 — Kies 'Content Database' uit de lijst"),
            p("Stap 3 — Klik op 'Filter' → '+ Add filter' → kies 'Publicatiedatum' → 'is' → selecteer 'Today'"),
            p("Stap 4 — Voeg tweede filter toe → 'Status' → 'is not' → 'Gepubliceerd'"),
            p("Stap 5 — Klik rechtsboven op de viewnaam → hernoem naar 'Vandaag'"),
            p("→ Vanaf nu zie je hier automatisch alle content die vandaag gepubliceerd moet worden."),
            div(),
            h2("📌 Tweede view — Goedkeuren (optioneel)"),
            p("Stap 1 — Klik weer op een lege regel → typ /linked view → Enter"),
            p("Stap 2 — Kies opnieuw 'Content Database'"),
            p("Stap 3 — Filter: 'Status' → 'is' → 'Wacht op goedkeuring'"),
            p("Stap 4 — Hernoem naar 'Goedkeuren'"),
            div(),
            h2("📌 Derde view — Afwerken (optioneel)"),
            p("Stap 1 — Linked view → Content Database"),
            p("Stap 2 — Filter: 'Status' → 'is' → 'In productie'"),
            p("Stap 3 — Hernoem naar 'Afwerken'"),
            div(),
            h2("✅ Dagelijkse posting checklist"),
            todo("Caption nagelezen als Kristof — klinkt het menselijk?"),
            todo("Geen verboden woorden"),
            todo("Juiste CTA voor deze week"),
            todo("Asset klaar in correct formaat"),
            todo("Publicatietijd correct ingesteld"),
            todo("Na posting: Status → Gepubliceerd in Content Database"),
        ],

        "Deze Week": [
            quote("Overzicht van 7 dagen. Wat is klaar, wat nog niet."),
            div(),
            h2("📌 Eenmalige instelling — Linked Views (doe dit één keer in Notion)"),
            p("── View 1: Week-overzicht ──"),
            p("Stap 1 — Klik op een lege regel hieronder → typ /linked view → Enter"),
            p("Stap 2 — Kies 'Content Database'"),
            p("Stap 3 — Filter: 'Publicatiedatum' → 'is within' → 'The next week'"),
            p("Stap 4 — Klik op 'Group' → kies 'Publicatiedatum' → selecteer 'Day'"),
            p("Stap 5 — Hernoem de view naar 'Deze Week'"),
            p("── View 2: Board per Status ──"),
            p("Stap 1 — Nog een /linked view → Content Database"),
            p("Stap 2 — Klik op 'Layout' → kies 'Board'"),
            p("Stap 3 — Group by: 'Status'"),
            p("Stap 4 — Hernoem naar 'Status Board'"),
            p("── View 3: Kalender ──"),
            p("Stap 1 — Nog een /linked view → Content Database"),
            p("Stap 2 — Klik op 'Layout' → kies 'Calendar'"),
            p("Stap 3 — Calendar by: 'Publicatiedatum'"),
            p("Stap 4 — Hernoem naar 'Kalender'"),
            div(),
            h2("Schema deze week"),
            table(
                ["Dag", "Tijd", "Type", "Status"],
                [
                    ["Maandag",   "18:30", "Feedpost of Story",            "—"],
                    ["Dinsdag",   "19:00", "Reel",                         "—"],
                    ["Woensdag",  "18:00", "Story",                        "—"],
                    ["Donderdag", "19:00", "Feedpost",                     "—"],
                    ["Vrijdag",   "08:00", "Kristof / Filosofie",          "—"],
                    ["Zaterdag",  "10:00", "Story of Reel",                "—"],
                    ["Zondag",    "11:00", "Campagne afsluiting (Week 4)", "—"],
                ]
            ),
            div(),
            h2("Notities deze week"),
            p("(Voeg hier opmerkingen of wijzigingen toe)"),
        ],

        "Posting Workflow": [
            quote("Van idee tot gepubliceerd — stap voor stap."),
            div(),
            h2("De 6 stappen"),
            h3("Stap 1 — Idee 💡"),
            li("Nieuw item aanmaken in ", mention(db) if db else "Content Database") if db
                else li("Nieuw item aanmaken in Content Database"),
            li("Status: Idee"),
            li("Type, Pillar en Week invullen"),
            li("Kort concept noteren"),
            h3("Stap 2 — Aanmaken ✏️"),
            li("Template openen (", mention(tpl) if tpl else "Templates", ")") if tpl
                else li("Template openen (Reel / Feedpost / Story)"),
            li("Caption schrijven"),
            li("Visueel beschrijven"),
            li("Status: In productie"),
            h3("Stap 3 — Asset maken 🎨"),
            li("Canva / Premiere / CapCut openen"),
            li("Ontwerp of video afwerken"),
            li("Exporteren in juist formaat:"),
            table(
                ["Type", "Formaat", "Bestandstype"],
                [
                    ["Feedpost", "1080 × 1350px (4:5)",  "JPG of PNG"],
                    ["Reel",     "1080 × 1920px (9:16)", "MP4 (H.264)"],
                    ["Story",    "1080 × 1920px (9:16)", "JPG of MP4"],
                ]
            ),
            li("Asset link toevoegen aan ", mention(db) if db else "Content Database") if db
                else li("Asset link toevoegen aan Content Database"),
            h3("Stap 4 — Goedkeuring 👀"),
            li("Status: Wacht op goedkeuring"),
            li("Kristof of teamlid controleert:"),
            todo("Toon correct?"),
            todo("Geen verboden woorden?"),
            todo("\"Atelier\" nergens?"),
            todo("CTA past bij de week?"),
            h3("Stap 5 — Klaar ✅"),
            li("Status: Klaar"),
            li("Publicatiedatum en tijd instellen in Later / Buffer / Instagram"),
            li("Checklist afvinken"),
            h3("Stap 6 — Gepubliceerd 📣"),
            li("Status: Gepubliceerd"),
            li("Datum bevestigd in ", mention(db) if db else "Content Database") if db
                else li("Datum bevestigd in Content Database"),
            li("Engagement na 24u bekijken"),
            div(),
            h2("Status flow"),
            p("💡 Idee  →  ✏️ In productie  →  ✅ Klaar  →  👀 Wacht op goedkeuring  →  📣 Gepubliceerd"),
            div(),
            h2("Vaste publicatietijden"),
            table(
                ["Dag", "Tijd", "Type"],
                [
                    ["Maandag",   "18:30", "Feedpost of Story"],
                    ["Dinsdag",   "19:00", "Reel"],
                    ["Woensdag",  "18:00", "Story"],
                    ["Donderdag", "19:00", "Feedpost"],
                    ["Vrijdag",   "08:00", "Kristof / Filosofie"],
                    ["Zaterdag",  "10:00", "Story of Reel"],
                    ["Zondag",    "11:00", "Slotweek (Week 4)"],
                ]
            ),
        ],

        "Merkrichtlijnen": [
            quote("De regels die nooit veranderen."),
            div(),
            h2("Kleuren"),
            table(
                ["Naam", "HEX", "Gebruik"],
                [
                    ["Diepzwart",   "#1A1A18", "Hoofdkleur, accenten, tekst"],
                    ["Warm wit",    "#F8F5F0", "Achtergronden, lichte schermen"],
                    ["Crème",       "#EDE9E3", "Tussenliggende sfeer"],
                    ["Lichtgrijs",  "#C9BFB4", "Scheidingslijnen"],
                    ["Tekst grijs", "#999999", "Labels, meta-informatie"],
                ]
            ),
            div(),
            h2("Lettertypes"),
            table(
                ["Gebruik", "Font", "Stijl"],
                [
                    ["Headlines",    "Cormorant Garamond", "Italic"],
                    ["Bodytekst",    "Cormorant Garamond", "Regular"],
                    ["Labels / CTA", "Arial of Helvetica", "Regular — klein, altijd"],
                ]
            ),
            p("Maison BU fluistert. Nooit schreeuwen."),
            div(),
            h2("Taal"),
            li("✅ Altijd Nederlands"),
            li("✅ Frans accent spaarzaam: maison · savoir-faire · l'invitation · signature"),
            li("❌ Nooit Engelse clichés als stijlkeuze"),
            li("❌ Nooit \"het atelier\" → altijd \"de maison\""),
            div(),
            h2("Woorden die we gebruiken"),
            p("verfijning · vakmanschap · tijdloos · gast (nooit klant) · de maison · gecreëerd voor jou · aanwezig · ritueel · stil · eerbiedig · savoir-faire"),
            div(),
            h2("Woorden die we NOOIT gebruiken"),
            li("❌ luxury · premium · transformatie · glam · deal"),
            li("❌ aanbieding · boek nu · mis het niet · summer sale"),
            li("❌ hair goals · glow-up · before/after · new hair who dis"),
            li("❌ het atelier · the atelier · notre atelier"),
            div(),
            h2("CTA regels per week"),
            table(
                ["Week", "CTA type", "Voorbeeldtekst"],
                [
                    ["Week 1", "Geen",         "—"],
                    ["Week 2", "Fluistering",  "Reserveer jouw moment. Link in bio."],
                    ["Week 3", "Weloverwogen", "hello@maisonbu.be (voor ceremonies)"],
                    ["Week 4", "Uitnodiging",  "maisonbu.be/book"],
                ]
            ),
            div(),
            h2("Visuele regels"),
            li("✅ Warm licht — gouden uur: 7–9u of 17–19u"),
            li("✅ Statische of trage camera (slider)"),
            li("✅ Close-ups van handen en haartextuur"),
            li("✅ Week 1: geen gezichten — mysterie bewaren"),
            li("❌ Geen ring lights"),
            li("❌ Geen viral audio of trending sounds"),
            li("❌ Geen koude kleurfilters"),
            li("❌ Geen voor/na vergelijkingen zonder toestemming"),
            div(),
            h2("De Soul Test"),
            quote("Vraag jezelf vóór publicatie:\n\"Zou Kristof dit gezegd hebben?\"\n\nAls nee → herschrijf. Als ja → goedgekeurd."),
            div(),
            h2("Snelle links"),
            li(mention(wf) if wf else "Posting Workflow")  if wf else li("→ Posting Workflow"),
            li(mention(ab) if ab else "Asset Beheer")      if ab else li("→ Asset Beheer"),
            li(mention(sp) if sp else "Shootdag Planner")  if sp else li("→ Shootdag Planner"),
            li(mention(tpl) if tpl else "Templates")       if tpl else li("→ Templates"),
            div(),
            h2("Contactgegevens"),
            table(
                ["", ""],
                [
                    ["E-mail",  "hello@maisonbu.be"],
                    ["Website", "maisonbu.be"],
                    ["Booking", "maisonbu.be/book"],
                ],
                has_header=False
            ),
        ],

        "Checklists": [
            h2("Maandelijkse lancering"),
            h3("Week 1 — Wereldopbouw"),
            todo("Strategie en kalender volledig ingevuld in Content Database"),
            todo("Shootdag ingepland — zie "),
            todo("Week 1 content aangemaakt (4 stuks)"),
            todo("Geen CTA's in Week 1 content — gecontroleerd"),
            todo("Muziek geselecteerd per reel"),
            todo("Assets klaar in Google Drive / Canva"),
            h3("Week 2 — De Fluistering"),
            todo("Week 2 content aangemaakt (4 stuks)"),
            todo("CTA aanwezig maar subtiel (\"Link in bio\")"),
            todo("Mailchimp campagne klaar en getest"),
            todo("E-mail verstuurd op dinsdag 09:15"),
            h3("Week 3 — De Weloverwogen Vraag"),
            todo("Ceremonie content aangemaakt"),
            todo("CTA via e-mail (hello@maisonbu.be) voor huwelijk/communie"),
            todo("Kristof filosofie post ingepland"),
            h3("Week 4 — De Uitnodiging"),
            todo("Sluitingsweek content aangemaakt"),
            todo("CTA op elk stuk (altijd als laatste regel)"),
            todo("Herboekings-e-mail verstuurd"),
            todo("Alle content gepubliceerd ✓"),
            div(),
            h2("Dagelijkse posting checklist"),
            h3("Voor het posten"),
            todo("Caption nagelezen als Kristof — klinkt het menselijk?"),
            todo("Geen verboden woorden (luxury, deal, boek nu, mis het niet, enz.)"),
            todo("Juiste CTA voor deze week"),
            todo("Asset klaar in correct formaat"),
            todo("Publicatietijd correct ingesteld in Later / Buffer / Instagram"),
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
            todo("\"Atelier\" nergens — altijd \"de maison\""),
        ],

        "Asset Beheer": [
            quote("Alles op de juiste plek, altijd terug te vinden."),
            div(),
            h2("Mappenstructuur (Google Drive of Canva)"),
            code(
                "📁 Maison BU — Assets\n"
                "├── 📁 Juni 2026\n"
                "│   ├── 📁 Reels (ruwe bestanden + exports)\n"
                "│   ├── 📁 Feedposts (afbeeldingen)\n"
                "│   ├── 📁 Stories (frames)\n"
                "│   ├── 📁 Shootdag 2026-06-04\n"
                "│   └── 📁 E-mail (header afbeelding)\n"
                "│\n"
                "├── 📁 Brand Assets (permanent)\n"
                "│   ├── Logo (alle varianten)\n"
                "│   ├── Kleurpaletten\n"
                "│   ├── Lettertypes\n"
                "│   └── Handtekening Kristof\n"
                "│\n"
                "└── 📁 Archief\n"
                "    └── [vorige maanden]"
            ),
            div(),
            h2("Exportformaten"),
            table(
                ["Type", "Formaat", "Bestandstype", "Kwaliteit"],
                [
                    ["Feedpost",      "1080 × 1350px (4:5)",  "JPG of PNG",  "Hoog"],
                    ["Reel",          "1080 × 1920px (9:16)", "MP4 (H.264)", "Hoog"],
                    ["Story",         "1080 × 1920px (9:16)", "JPG of MP4",  "Hoog"],
                    ["E-mail header", "600 × 340px",          "JPG",         "Gemiddeld"],
                ]
            ),
            div(),
            h2("Asset status tracker"),
            table(
                ["Stuk", "Type", "Asset gemaakt", "Link"],
                [
                    ["Juni betreedt de maison",      "Reel",     "☐", ""],
                    ["De golf die altijd bestond",    "Feedpost", "☐", ""],
                    ["Ze arriveerde met een dinsdag", "Feedpost", "☐", ""],
                    ["Sommige dagen vragen alles",    "Feedpost", "☐", ""],
                    ["De maison staat klaar",         "Reel",     "☐", ""],
                ]
            ),
            p("(Voeg rijen toe voor elke geplande content — zie ook ", mention(db) if db else "Content Database", ")")
              if db else p("(Voeg rijen toe voor elke geplande content)"),
            div(),
            h2("Naamconventie bestanden"),
            code(
                "[type]_[week]_[korte-titel]_[datum].[extensie]\n\n"
                "Voorbeelden:\n"
                "reel_w1_juni-betreedt-maison_20260602.mp4\n"
                "feedpost_w2_golf-bestond_20260609.jpg\n"
                "story_w3_bruid-dag-erna_20260616.mp4"
            ),
            div(),
            h2("Workflow"),
            li("Uploaden → ", mention(wf) if wf else "Posting Workflow") if wf
                else li("Uploaden → zie Posting Workflow"),
            li("Merkregels → ", mention(mb) if mb else "Merkrichtlijnen") if mb
                else li("Merkregels → zie Merkrichtlijnen"),
        ],

        "Shootdag Planner": [
            quote("Alles op één plek voor de dag dat je gaat filmen of fotograferen."),
            div(),
            h2("Voorbereiding"),
            todo("Shot list volledig ingevuld (zie hieronder)"),
            todo("Props klaargelegd"),
            todo("Ruimte voorbereid — licht gecontroleerd"),
            todo("Outfits / styling klaar"),
            todo("Camera geladen + geheugenkaart leeg"),
            todo("Juiste tijdstip ingepland (7–9u of 17–19u voor optimaal junilicht)"),
            div(),
            h2("Shot list"),
            table(
                ["#", "Beschrijving shot", "Voor welk content stuk", "Gedaan"],
                [
                    ["1", "", "", "☐"],
                    ["2", "", "", "☐"],
                    ["3", "", "", "☐"],
                    ["4", "", "", "☐"],
                    ["5", "", "", "☐"],
                    ["6", "", "", "☐"],
                ]
            ),
            div(),
            h2("Technische instellingen"),
            table(
                ["Instelling", "Waarde"],
                [
                    ["Camera",       "A7S III of equivalent"],
                    ["Lens",         "50mm of 85mm"],
                    ["Lichtmoment",  "7–9u ochtend of 17–19u gouden uur"],
                    ["Stabilisatie", "Statisch of zachte slider"],
                    ["Kleurgrading", "Warm, ingetogen — geen filters of presets"],
                ],
                has_header=False
            ),
            div(),
            h2("Na de shoot"),
            todo("Bestanden overgezet naar Google Drive / Canva"),
            todo("Beste shots geselecteerd"),
            todo("Asset links toegevoegd aan ", mention(db) if db else "Content Database") if db
                else todo("Asset links toegevoegd aan Content Database"),
            todo("Status content bijgewerkt naar In productie"),
            div(),
            h2("Notities"),
            p("(Voeg hier shootdag-specifieke opmerkingen toe)"),
        ],

        "Templates": [
            quote("Kopieer de juiste template voor elk nieuw content stuk."),
            p("Kies hieronder de juiste template en kopieer de pagina."),
            div(),
            h2("Hoe gebruik je een template?"),
            li("Open de template die past bij het type content"),
            li("Klik rechtsboven op ··· → Duplicate"),
            li("Hernoem de kopie naar de titel van je content stuk"),
            li("Vul alle velden in"),
            li("Voeg het item toe aan ", mention(db) if db else "Content Database") if db
                else li("Voeg het item toe aan de Content Database"),
            div(),
            h2("Beschikbare templates"),
            li("🎬 Reel Template — voor alle reels (30–60 sec)"),
            li("💬 Story Template — voor story flows (3–6 schermen)"),
            li("📷 Feedpost Template — voor feedposts (4:5 formaat)"),
            div(),
            p("Workflow: ", mention(wf) if wf else "Posting Workflow",
              "  |  Regels: ", mention(mb) if mb else "Merkrichtlijnen")
              if wf and mb else p("Zie ook: Posting Workflow en Merkrichtlijnen"),
        ],
    }


def build_reel_template(refs):
    db  = refs.get("Content Database")
    return [
        quote("Kopieer deze pagina voor elke nieuwe reel."),
        div(),
        h2("Basisinfo"),
        table(
            ["Veld", "Waarde"],
            [
                ["Week",            "Week 1 / 2 / 3 / 4"],
                ["Duur",            "45 / 60 seconden"],
                ["Publicatiedatum", ""],
                ["Platform",        "Instagram Reel"],
                ["Pillar",          "De Maison · De Craft · De Gast · Kristof · Ceremonie"],
                ["Status",          "💡 Idee"],
            ],
            has_header=False
        ),
        div(),
        h2("Concept"),
        p("(Beschrijf in 2–3 zinnen wat de kijker VOELT na het bekijken — niet wat er te zien is)"),
        div(),
        h2("Shot per shot structuur"),
        table(
            ["Tijdstip", "Wat zie je"],
            [
                ["00:00 – 00:08", ""],
                ["00:08 – 00:20", ""],
                ["00:20 – 00:36", ""],
                ["00:36 – 00:50", ""],
                ["00:50 – 00:60", ""],
            ]
        ),
        div(),
        h2("Tekst op scherm"),
        table(["Tijdstip", "Tekst"], [["", ""], ["", ""]]),
        div(),
        h2("Muziek"),
        table(["", ""], [["Sfeer", ""], ["Tempo", "BPM"], ["Referentie", ""]], has_header=False),
        div(),
        h2("Caption"),
        p("(Volledige caption — begin met sfeer, eindig met CTA indien van toepassing)"),
        div(),
        h2("CTA type"),
        todo("Geen (Week 1)"),
        todo("Fluistering — \"Reserveer jouw moment. Link in bio.\""),
        todo("Weloverwogen — \"hello@maisonbu.be\""),
        todo("Uitnodiging — \"maisonbu.be/book\""),
        div(),
        h2("Asset"),
        p("Link: (Canva / Drive link)"),
        div(),
        h2("✅ Checklist voor publicatie"),
        todo("Caption nagelezen als Kristof — klinkt het menselijk?"),
        todo("Geen verboden woorden (luxury, deal, boek nu, enz.)"),
        todo("\"Atelier\" nergens → altijd \"de maison\""),
        todo("Muziek gelicentieerd"),
        todo("Ondertitels toegevoegd"),
        todo("Status bijgewerkt in ", mention(db) if db else "Content Database") if db
            else todo("Status bijgewerkt in Content Database"),
        todo("Gepubliceerd op juiste tijdstip"),
    ]


def build_story_template(refs):
    db = refs.get("Content Database")
    return [
        quote("Kopieer deze pagina voor elke nieuwe story flow."),
        div(),
        h2("Basisinfo"),
        table(
            ["Veld", "Waarde"],
            [
                ["Aantal schermen", "3 / 4 / 5 / 6"],
                ["Week",            "Week 1 / 2 / 3 / 4"],
                ["Publicatiedatum", ""],
                ["Status",          "💡 Idee"],
                ["Formaat",         "1080×1920px (9:16)"],
            ],
            has_header=False
        ),
        div(),
        h2("Scherm 1"),
        p("Achtergrond: (foto / video / kleur #hex)"),
        p("Tekst:"),
        p("Lettertype: Cormorant Garamond Italic"),
        p("Positie: Boven / Midden / Onder"),
        div(),
        h2("Scherm 2"),
        p("Achtergrond:"),
        p("Tekst:"),
        div(),
        h2("Scherm 3"),
        p("Achtergrond:"),
        p("Tekst:"),
        div(),
        h2("Scherm 4 (indien van toepassing)"),
        p("Achtergrond:"),
        p("Tekst:"),
        div(),
        h2("Scherm 5 (indien van toepassing)"),
        p("Achtergrond:"),
        p("Tekst:"),
        div(),
        h2("CTA op laatste scherm"),
        todo("Geen"),
        todo("Link sticker"),
        todo("\"hello@maisonbu.be\""),
        todo("Swipe up / link in bio"),
        div(),
        h2("✅ Checklist voor publicatie"),
        todo("Elk scherm minimaal 7 seconden"),
        todo("Overgang: zachte fade"),
        todo("Muziek aanwezig (50–60% volume)"),
        todo("\"Atelier\" nergens gebruikt"),
        todo("Status bijgewerkt in ", mention(db) if db else "Content Database") if db
            else todo("Status bijgewerkt in Content Database"),
        todo("Gepubliceerd op juiste tijdstip"),
    ]


def build_feedpost_template(refs):
    db = refs.get("Content Database")
    return [
        quote("Kopieer deze pagina voor elke nieuwe feedpost."),
        div(),
        h2("Basisinfo"),
        table(
            ["Veld", "Waarde"],
            [
                ["Pillar",          "De Maison · De Craft · De Gast · Kristof · Ceremonie"],
                ["Week",            "Week 1 / 2 / 3 / 4"],
                ["Publicatiedatum", ""],
                ["Status",          "💡 Idee"],
                ["Aspect ratio",    "4:5 (1080×1350px)"],
            ],
            has_header=False
        ),
        div(),
        h2("Visueel"),
        p("Beschrijving: (Wat is er te zien op het beeld?)"),
        p("Asset link: (Canva / Drive)"),
        div(),
        h2("Caption"),
        p("(Begin met sfeer — minimaal 3 zinnen voor de CTA. Geen intro. Geen \"Hé!\". Gewoon beginnen.)"),
        div(),
        h2("Hashtags"),
        p("#MaisonBU  #Hasselt  (voeg 4–6 relevante hashtags toe)"),
        div(),
        h2("CTA type"),
        todo("Geen (Week 1)"),
        todo("\"Reserveer jouw moment. Link in bio.\" (Week 2)"),
        todo("\"hello@maisonbu.be\" (Week 3 ceremonie)"),
        todo("\"maisonbu.be/book\" (Week 4)"),
        div(),
        h2("✅ Checklist voor publicatie"),
        todo("Caption gelezen zonder beeld — voelt het nog iets?"),
        todo("Geen verboden woorden (luxury, premium, boek nu, sale, enz.)"),
        todo("\"Atelier\" nergens → altijd \"de maison\""),
        todo("Asset klaar: 1080×1350px, JPG of PNG"),
        todo("Status bijgewerkt in ", mention(db) if db else "Content Database") if db
            else todo("Status bijgewerkt in Content Database"),
        todo("Gepubliceerd op juiste tijdstip"),
    ]


# ── Hoofdprogramma ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🌿 Maison BU Marketing OS — inhoud toevoegen\n")

    # Verzamel alle page IDs voor cross-references
    print("  Pagina ID's ophalen...")
    page_names = ["Vandaag", "Deze Week", "Posting Workflow", "Merkrichtlijnen",
                  "Checklists", "Asset Beheer", "Shootdag Planner", "Templates"]
    refs = {}
    for name in page_names:
        ids = find_pages(name)
        if ids:
            refs[name] = ids[0]
    db_id = find_db("Content Database")
    if db_id:
        refs["Content Database"] = db_id
        print(f"  ✓ Content Database gevonden")
    for name, pid in refs.items():
        print(f"  ✓ {name}: {pid[:8]}...")

    # Bouw pagina-inhoud met juiste cross-references
    PAGES = build_pages(refs)

    # Vul alle sub-pagina's in
    print("\n  Inhoud toevoegen...\n")
    ok = 0
    for title, blocks in PAGES.items():
        page_ids = find_pages(title)
        if not page_ids:
            print(f"  ⚠  Niet gevonden: {title}")
            continue
        label = f"({len(page_ids)}×)" if len(page_ids) > 1 else ""
        for pid in page_ids:
            clear_page(pid)
            add_blocks(pid, blocks)
        print(f"  ✓  {title} {label}")
        ok += 1

    print(f"\n  Standaard pagina's: {ok}/{len(PAGES)} bijgewerkt")

    # Template sub-pagina's aanmaken
    print("\n📝 Template sub-pagina's aanmaken...\n")
    template_ids = find_pages("Templates")
    if template_ids:
        t_parent = template_ids[0]
        for title, fn in [
            ("🎬 Reel Template",     build_reel_template),
            ("💬 Story Template",    build_story_template),
            ("📷 Feedpost Template", build_feedpost_template),
        ]:
            child_id = create_child_page(t_parent, title)
            if child_id:
                add_blocks(child_id, fn(refs))
                print(f"  ✓  {title}")
            else:
                print(f"  ⚠  Kon niet aanmaken: {title}")
    else:
        print("  ⚠  'Templates' pagina niet gevonden")

    print("\n✅ Klaar. Alle pagina's zijn volledig ingevuld en onderling gelinkt.\n")
