#!/usr/bin/env python3
"""
Voegt inhoud toe aan de bestaande Maison BU Marketing OS sub-pagina's.
Uitvoeren via GitHub Actions nadat de pagina's aangemaakt zijn.
"""
import os, sys, time, requests

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
    if r.status_code not in (200, 201):
        print(f"  ⚠  {r.status_code}: {r.text[:200]}")
        return None
    return r.json()

def find_page(title):
    res = call("POST", "search", {
        "query": title,
        "filter": {"property": "object", "value": "page"}
    })
    if not res:
        return None
    for p in res.get("results", []):
        props = p.get("properties", {})
        t = props.get("title", {}).get("title", [])
        name = t[0]["plain_text"] if t else ""
        if title.lower() in name.lower():
            return p["id"]
    return None

def add_blocks(page_id, blocks):
    for i in range(0, len(blocks), 95):
        call("PATCH", f"blocks/{page_id}/children", {"children": blocks[i:i+95]})

def p(t):
    return {"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":t}}]}}

def h2(t):
    return {"object":"block","type":"heading_2","heading_2":{"rich_text":[{"type":"text","text":{"content":t}}]}}

def h3(t):
    return {"object":"block","type":"heading_3","heading_3":{"rich_text":[{"type":"text","text":{"content":t}}]}}

def li(t):
    return {"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":[{"type":"text","text":{"content":t}}]}}

def todo(t):
    return {"object":"block","type":"to_do","to_do":{"rich_text":[{"type":"text","text":{"content":t}}],"checked":False}}

def div():
    return {"object":"block","type":"divider","divider":{}}

# ── Pagina-inhoud ────────────────────────────────────────────────────────────

PAGES = {
    "Vandaag": [
        p("Filter de Content Database op de datum van vandaag om te zien wat er gepland staat."),
        div(),
        h2("✅ Dagelijkse checklist — voor het posten"),
        todo("Caption nagelezen als Kristof — klinkt het menselijk?"),
        todo("Geen verboden woorden (luxury, deal, boek nu, miss het niet)"),
        todo("Juiste CTA voor deze week"),
        todo("Asset klaar in correct formaat"),
        todo("Publicatietijd correct ingesteld in Later / Buffer / Instagram"),
        div(),
        h2("✅ Dagelijkse checklist — na het posten"),
        todo("Status → Gepubliceerd in Content Database"),
        todo("Datum bevestigd"),
        todo("Reacties bekeken na 1 uur"),
        div(),
        h2("🕐 Vaste publicatietijden"),
        li("Maandag  18:30 — Feedpost of Story"),
        li("Dinsdag  19:00 — Reel"),
        li("Woensdag 18:00 — Story"),
        li("Donderdag 19:00 — Feedpost"),
        li("Vrijdag  08:00 — Kristof / Filosofie"),
        li("Zaterdag 10:00 — Story of Reel"),
        li("Zondag   11:00 — Slotweek (Week 4)"),
    ],

    "Deze Week": [
        p("Week 1 · Wereldopbouw (1–7 juni) — geen CTAs, mysterie opbouwen"),
        p("Week 2 · De Fluistering (8–14 juni) — zachte CTAs, zomerafspraken"),
        p("Week 3 · De Weloverwogen Vraag (15–21 juni) — ceremonie & huwelijk"),
        p("Week 4 · De Uitnodiging (22–30 juni) — directe uitnodiging, afsluiting"),
        div(),
        h2("Week 1 — Wereldopbouw"),
        li("Doel: mysterie opbouwen. Geen CTAs. Geen gezichten."),
        li("2 Reels · 3 Feedposts · 4 Story Flows"),
        li("CTA: geen"),
        div(),
        h2("Week 2 — De Fluistering"),
        li("Doel: eerste zachte uitnodiging."),
        li("2 Reels · 3 Feedposts · 4 Story Flows · 1 Email"),
        li("CTA: 'Reserveer jouw moment. Link in bio.'"),
        div(),
        h2("Week 3 — De Weloverwogen Vraag"),
        li("Doel: ceremonie & huwelijk."),
        li("2 Reels · 3 Feedposts · 4 Story Flows"),
        li("CTA: 'hello@maisonbu.be'"),
        div(),
        h2("Week 4 — De Uitnodiging"),
        li("Doel: directe uitnodiging."),
        li("2 Reels · 3 Feedposts · 4 Story Flows"),
        li("CTA: 'maisonbu.be/book'"),
    ],

    "Posting Workflow": [
        p("Van idee tot gepubliceerd — stap voor stap."),
        div(),
        h2("Stap 1 — Idee 💡"),
        li("Nieuw item aanmaken in Content Database"),
        li("Status: Idee — Type, Pillar en Week invullen"),
        div(),
        h2("Stap 2 — Aanmaken ✏️"),
        li("Template openen (Reel / Feedpost / Story)"),
        li("Caption schrijven + visueel beschrijven"),
        li("Status: In Productie"),
        div(),
        h2("Stap 3 — Asset maken 🎨"),
        li("Canva / Premiere / CapCut openen"),
        li("Feedpost: 1080x1350px JPG  |  Reel: 1080x1920px MP4  |  Story: 1080x1920px"),
        li("Asset link toevoegen aan Content Database"),
        div(),
        h2("Stap 4 — Goedkeuring 👀"),
        todo("Toon correct?"),
        todo("Geen verboden woorden?"),
        todo("'Atelier' nergens — altijd 'de maison'?"),
        todo("CTA past bij de week?"),
        div(),
        h2("Stap 5 — Klaar ✅"),
        li("Status: Klaar"),
        li("Publicatiedatum en tijd instellen in Later / Buffer / Instagram"),
        div(),
        h2("Stap 6 — Gepubliceerd 📣"),
        li("Status: Gepubliceerd"),
        li("Datum bevestigd in database"),
        li("Engagement na 24u bekijken"),
    ],

    "Merkrichtlijnen": [
        p("De regels die nooit veranderen."),
        div(),
        h2("🎨 Kleuren"),
        li("Diepzwart  #1A1A18 — Hoofdkleur, accenten, tekst"),
        li("Warm wit   #F8F5F0 — Achtergronden, lichte schermen"),
        li("Crème      #EDE9E3 — Tussenliggende sfeer"),
        li("Lichtgrijs #C9BFB4 — Scheidingslijnen"),
        li("Tekst grijs #999999 — Labels, meta-informatie"),
        div(),
        h2("🔤 Lettertypes"),
        li("Headlines:    Cormorant Garamond Italic"),
        li("Bodytekst:    Cormorant Garamond Regular"),
        li("Labels / CTA: Arial of Helvetica Regular — klein, altijd"),
        div(),
        h2("🗣 Taal"),
        li("✅ Altijd Nederlands"),
        li("✅ Frans accent spaarzaam: maison · savoir-faire · l'invitation · signature"),
        li("❌ Nooit Engelse clichés als stijlkeuze"),
        li("❌ Nooit 'het atelier' — altijd 'de maison'"),
        div(),
        h2("✅ Goede woorden"),
        p("verfijning · vakmanschap · tijdloos · gast (nooit klant) · de maison · gecreëerd voor jou · aanwezig · ritueel · stil · eerbiedig · savoir-faire"),
        div(),
        h2("❌ Verboden woorden"),
        li("luxury · premium · transformatie · glam · deal"),
        li("aanbieding · boek nu · mis het niet · summer sale"),
        li("hair goals · glow-up · before/after · new hair who dis"),
        li("het atelier · the atelier · notre atelier"),
        div(),
        h2("📣 CTA per week"),
        li("Week 1: Geen CTA"),
        li("Week 2: Fluistering — 'Reserveer jouw moment. Link in bio.'"),
        li("Week 3: Weloverwogen — 'hello@maisonbu.be'"),
        li("Week 4: Uitnodiging — 'maisonbu.be/book'"),
        div(),
        h2("📸 Visuele regels"),
        li("✅ Warm licht — gouden uur: 7-9u of 17-19u"),
        li("✅ Statische of trage camera (slider)"),
        li("✅ Close-ups van handen en haartextuur"),
        li("✅ Week 1: geen gezichten — mysterie bewaren"),
        li("❌ Geen ring lights · geen viral audio · geen koude filters"),
        div(),
        h2("✨ De Soul Test"),
        p("Vraag jezelf vóór publicatie: 'Zou Kristof dit gezegd hebben?'"),
        p("Als nee → herschrijf. Als ja → goedgekeurd."),
        div(),
        h2("📬 Contact"),
        li("hello@maisonbu.be"),
        li("maisonbu.be"),
        li("maisonbu.be/book"),
    ],

    "Checklists": [
        h2("📅 Maandelijkse lancering — Week 1"),
        todo("Strategie en kalender volledig ingevuld in Content Database"),
        todo("Shootdag ingepland en voorbereid"),
        todo("Week 1 content aangemaakt (4 stuks)"),
        todo("Geen CTAs in Week 1 content — gecontroleerd"),
        todo("Muziek geselecteerd per reel"),
        todo("Assets klaar in Google Drive / Canva"),
        div(),
        h2("📅 Maandelijkse lancering — Week 2"),
        todo("Week 2 content aangemaakt (4 stuks)"),
        todo("CTA aanwezig maar subtiel ('Link in bio')"),
        todo("Mailchimp campagne klaar en getest"),
        todo("E-mail verstuurd op dinsdag 09:15"),
        div(),
        h2("📅 Maandelijkse lancering — Week 3"),
        todo("Ceremonie content aangemaakt"),
        todo("CTA via e-mail (hello@maisonbu.be) voor huwelijk/communie"),
        todo("Kristof filosofie post ingepland"),
        div(),
        h2("📅 Maandelijkse lancering — Week 4"),
        todo("Sluitingsweek content aangemaakt"),
        todo("CTA op elk stuk (altijd als laatste regel)"),
        todo("Herboekings-e-mail verstuurd"),
        todo("Alle content gepubliceerd"),
        div(),
        h2("📸 Shootdag checklist"),
        todo("Shot list volledig"),
        todo("Licht: gouden uur (7-9u of 17-19u)"),
        todo("Camera geladen, geheugenkaart leeg"),
        todo("Alle shots gemaakt"),
        todo("Bestanden overgezet naar Drive"),
        todo("Asset links bijgewerkt in Content Database"),
        div(),
        h2("📧 Mailchimp checklist"),
        todo("Hardop gelezen als Kristof — klinkt het menselijk?"),
        todo("Onderwerpregel getest op mobiel (volledig zichtbaar)"),
        todo("Boekingslink getest en actief"),
        todo("Uitschrijflink functioneel"),
        todo("Slechts één CTA — bevestigd"),
        todo("Geen verboden woorden"),
        todo("'Atelier' nergens — altijd 'de maison'"),
    ],

    "Asset Beheer": [
        p("Alles op de juiste plek, altijd terug te vinden."),
        div(),
        h2("📁 Mappenstructuur"),
        li("Maison BU Assets/"),
        li("  Juni 2026/ → Reels / Feedposts / Stories / Shootdag / Email"),
        li("  Brand Assets/ → Logo / Kleurpaletten / Lettertypes / Handtekening Kristof"),
        li("  Archief/ → vorige maanden"),
        div(),
        h2("📐 Exportformaten"),
        li("Feedpost    → 1080x1350px (4:5) · JPG of PNG"),
        li("Reel        → 1080x1920px (9:16) · MP4 H.264"),
        li("Story       → 1080x1920px (9:16) · JPG of MP4"),
        li("Email header → 600x340px · JPG"),
        div(),
        h2("🏷 Naamconventie"),
        p("[type]_[week]_[korte-titel]_[datum].[ext]"),
        li("reel_w1_juni-betreedt-maison_20260602.mp4"),
        li("feedpost_w2_golf-bestond_20260609.jpg"),
        li("story_w3_bruid-dag-erna_20260616.mp4"),
    ],

    "Shootdag Planner": [
        p("Shootdag juni 2026 — plan op 2 of 3 juni (Week 1)"),
        div(),
        h2("🎬 Shot list — Week 1 (geen gezichten)"),
        todo("Maison in junilicht — architecturaal, vroege ochtend"),
        todo("Schaar, kam, spuitfles — close-up stilleven"),
        todo("Hand die gereedschap neerlegt"),
        todo("Betonvloer met lichtval"),
        todo("Spiegel die licht terugkaatst"),
        todo("Haar close-up — textuur in beweging (beachwaves)"),
        todo("Handen die golf vormen — slow motion 120fps"),
        todo("Lege stoel in junilicht"),
        div(),
        h2("🎬 Shot list — Week 2 (transformatie)"),
        todo("Kleurpigment in kom — close-up"),
        todo("Borstel die kleur aanbrengt — bewust en traag"),
        todo("Haar dat gewassen wordt — fragmenten"),
        todo("Gast vertrekt — rug, haar in beweging"),
        div(),
        h2("🎬 Shot list — Week 3 (ceremonie)"),
        todo("Elegante opsteek — detail, geen gezicht"),
        todo("Handen die haarpins plaatsen"),
        todo("Communiestijl — close-up details"),
        div(),
        h2("⚙️ Productie-afspraken"),
        li("Gouden uur: 7-9u of 17-19u"),
        li("Geen ring lights"),
        li("Camera: statisch voor architectuur / langzame slide voor haar"),
        li("Kleurgrading: warm en ingetogen — geen filters, geen presets"),
        li("Elke cut minimaal 3 seconden"),
        div(),
        h2("✅ Na de shoot"),
        todo("Bestanden overgezet naar Google Drive"),
        todo("Reel-exports: MP4 H.264 1080x1920"),
        todo("Feedpost-exports: JPG 1080x1350"),
        todo("Asset links bijgewerkt in Content Database"),
    ],

    "Templates": [
        h2("🎬 Reel Template"),
        p("CONCEPT: [wat laat dit reel zien?]"),
        p("WEEK: [1/2/3/4]  |  PILLAR: [naam]  |  DUUR: [30/45/60 sec]"),
        div(),
        h3("Visuele structuur"),
        p("[00:00] Opening — [beschrijving]"),
        p("[00:xx] Kern — [beschrijving]"),
        p("[00:xx] Slot — [beschrijving]"),
        div(),
        h3("Tekst op scherm"),
        p("[tijdstempel] — '[tekst]' (klein, serif, gecentreerd)"),
        div(),
        h3("Muziek"),
        p("[instrumentaal / referentie]"),
        div(),
        h3("Caption"),
        p("[opening zonder introductie]"),
        p("[kern — diepte of emotie]"),
        p("[afsluiting — stilte of CTA van de week]"),
        p("[hashtags — max 8]"),
        div(),
        h2("📸 Feedpost Template"),
        p("TITEL: [intern]  |  WEEK: [1/2/3/4]  |  PILLAR: [naam]"),
        p("BEELD: [beschrijving visueel]"),
        div(),
        h3("Caption"),
        p("[opening — directe sfeer]"),
        p("[kern — diepte of emotie]"),
        p("[afsluiting — stilte of CTA]"),
        p("#MaisonBU #[tag] #Hasselt"),
        div(),
        h2("📖 Story Flow Template"),
        p("TITEL: [intern]  |  WEEK: [1/2/3/4]  |  FRAMES: [3-7]"),
        div(),
        p("FRAME 1: [beeld + tekst]"),
        p("FRAME 2: [beeld + tekst]"),
        p("FRAME 3: [beeld + tekst + CTA van de week]"),
    ],
}

# ── Hoofdprogramma ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🌿 Inhoud toevoegen aan Maison BU Marketing OS pagina's\n")
    ok = 0
    for title, blocks in PAGES.items():
        page_id = find_page(title)
        if page_id:
            add_blocks(page_id, blocks)
            print(f"  ✓  {title}")
            ok += 1
        else:
            print(f"  ⚠  Niet gevonden: {title}")

    print(f"\n✅ {ok}/{len(PAGES)} pagina's bijgewerkt.")
