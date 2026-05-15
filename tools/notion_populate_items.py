#!/usr/bin/env python3
"""
Maison BU — Content Database Populatie
Vult de 36 Content Database items met volledige creatieve brieven.
Maakt ook 3 nieuwe sub-pagina's aan voor strategie, e-mail en CTA.
"""

import os, re, sys, time, traceback
import requests

TOKEN = os.environ["NOTION_TOKEN"]
VER   = "2022-06-28"
BASE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FEEDS_FILE   = os.path.join(BASE, "outputs/captions/juni_2026_twaalf_feedposts.txt")
STORIES_FILE = os.path.join(BASE, "outputs/captions/juni_2026_zestien_story_flows.txt")
REELS_FILE   = os.path.join(BASE, "outputs/reel_scripts/juni_2026_acht_reels.txt")
STRAT_FILE   = os.path.join(BASE, "outputs/content_calendar/juni_2026_volledige_strategie.txt")
EMAIL_FILE   = os.path.join(BASE, "outputs/emails/juni_2026_mailchimp_campagne.txt")
CTA_FILE     = os.path.join(BASE, "outputs/last_minute/juni_2026_cta_filosofie_kristof_gast.txt")


# ── API ──────────────────────────────────────────────────────────────────────

def call(method, path, body=None):
    url = f"https://api.notion.com/v1/{path}"
    hdrs = {
        "Authorization": f"Bearer {TOKEN}",
        "Notion-Version": VER,
        "Content-Type": "application/json",
    }
    try:
        r = requests.request(method, url, headers=hdrs, json=body, timeout=30)
    except requests.RequestException as exc:
        print(f"  ⚠ Netwerkfout: {exc}")
        return None
    if not r.ok:
        print(f"  ⚠ {method} {path} → {r.status_code}: {r.text[:300]}")
        return None
    return r.json()


# ── Block helpers ─────────────────────────────────────────────────────────────

def _rt(text):
    return [{"type": "text", "text": {"content": str(text)[:2000]}}]

def h2(text):
    return {"object": "block", "type": "heading_2",
            "heading_2": {"rich_text": _rt(text)}}

def h3(text):
    return {"object": "block", "type": "heading_3",
            "heading_3": {"rich_text": _rt(text)}}

def p(text=""):
    if not str(text).strip():
        return {"object": "block", "type": "paragraph",
                "paragraph": {"rich_text": []}}
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": _rt(text)}}

def li(text):
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": _rt(text)}}

def divider():
    return {"object": "block", "type": "divider", "divider": {}}

def text_to_blocks(text, chunk=1900):
    if not text or not str(text).strip():
        return []
    blocks = []
    for para in str(text).split("\n\n"):
        para = para.strip()
        if not para:
            continue
        for i in range(0, len(para), chunk):
            blocks.append(p(para[i:i + chunk]))
    return blocks or [p(str(text)[:chunk])]

def add_blocks(page_id, blocks):
    for i in range(0, len(blocks), 90):
        call("PATCH", f"blocks/{page_id}/children", {"children": blocks[i:i + 90]})
        time.sleep(0.4)

def clear_page(page_id):
    res = call("GET", f"blocks/{page_id}/children?page_size=100")
    if not res:
        return
    for blk in res.get("results", []):
        call("DELETE", f"blocks/{blk['id']}")
        time.sleep(0.15)

def update_props(page_id, caption="", hashtags="", visueel=""):
    props = {}
    if caption:
        props["Caption"]  = {"rich_text": _rt(caption[:2000])}
    if hashtags:
        props["Hashtags"] = {"rich_text": _rt(hashtags[:2000])}
    if visueel:
        props["Visueel"]  = {"rich_text": _rt(visueel[:2000])}
    if props:
        call("PATCH", f"pages/{page_id}", {"properties": props})
        time.sleep(0.3)


# ── Parsers ───────────────────────────────────────────────────────────────────

def parse_feedposts(filepath):
    """Returns {nr: {context, beeld, caption, hashtags}}"""
    text = open(filepath, encoding="utf-8").read()
    posts = {}
    matches = list(re.finditer(r"^POST (\d+) — \"", text, re.MULTILINE))

    for idx, m in enumerate(matches):
        nr    = int(m.group(1))
        start = m.start()
        end   = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        lines = text[start:end].split("\n")

        context = lines[1].strip() if len(lines) > 1 else ""
        beeld   = lines[2][6:].strip() if len(lines) > 2 and lines[2].startswith("Beeld:") else ""

        # Body starts after the ━━━ separator that follows the 3-line header
        body_start = 3
        for j in range(3, min(8, len(lines))):
            if "━" * 10 in lines[j]:
                body_start = j + 1
                break

        hashtag_parts, caption_parts = [], []
        for line in lines[body_start:]:
            s = line.strip()
            if s.startswith("╔") or s.startswith("╚") or s.startswith("║") or "━" * 10 in s:
                continue
            if s.startswith("#"):
                hashtag_parts.append(s)
            else:
                caption_parts.append(line)

        posts[nr] = {
            "context":  context,
            "beeld":    beeld,
            "caption":  "\n".join(caption_parts).strip(),
            "hashtags": " ".join(hashtag_parts),
        }

    print(f"  → {len(posts)} feedposts geparsed")
    return posts


def parse_stories(filepath):
    """Returns {nr: {context, screens: [str]}}"""
    text    = open(filepath, encoding="utf-8").read()
    stories = {}
    flow_re   = re.compile(r"^STORY FLOW (\d+) — \"", re.MULTILINE)
    screen_re = re.compile(r"^SCHERM \d+ van \d+", re.MULTILINE)
    flow_matches = list(flow_re.finditer(text))

    for idx, m in enumerate(flow_matches):
        nr    = int(m.group(1))
        start = m.start()
        end   = flow_matches[idx + 1].start() if idx + 1 < len(flow_matches) else len(text)
        block = text[start:end]
        lines = block.split("\n")
        context = lines[1].strip() if len(lines) > 1 else ""

        screen_matches = list(screen_re.finditer(block))
        screens = []
        for si, sm in enumerate(screen_matches):
            sc_start = sm.start()
            sc_end   = screen_matches[si + 1].start() if si + 1 < len(screen_matches) else len(block)
            sc_lines = block[sc_start:sc_end].split("\n")
            content  = []
            for sl in sc_lines[1:]:  # skip the SCHERM X van Y header line
                s = sl.strip()
                if s and "━" * 10 not in s and not s.startswith("╔") \
                        and not s.startswith("╚") and not s.startswith("║"):
                    content.append(s)
            screens.append("\n".join(content))

        stories[nr] = {"context": context, "screens": screens}

    print(f"  → {len(stories)} story flows geparsed")
    return stories


def parse_reels(filepath):
    """Returns {nr: {concept, visuele_structuur, tekst_op_scherm, muziek,
                      caption_bij_posting, productiememo}}"""
    text    = open(filepath, encoding="utf-8").read()
    reels   = {}
    reel_re = re.compile(r"║\s+REEL (\d+) — \"", re.MULTILINE)
    matches = list(reel_re.finditer(text))

    SECTIONS = [
        "CONCEPT",
        "VISUELE STRUCTUUR",
        "TEKST OP SCHERM",
        "MUZIEK",
        "CAPTION BIJ POSTING",
        "PRODUCTIEMEMO",
    ]

    for idx, m in enumerate(matches):
        nr    = int(m.group(1))
        start = m.start()
        end   = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        block = text[start:end]

        buckets = {sec: [] for sec in SECTIONS}
        current = None

        for line in block.split("\n"):
            s = line.strip()
            found = next(
                (sec for sec in SECTIONS if s == sec or s.startswith(sec + " (")),
                None,
            )
            if found:
                current = found
            elif current:
                if not (s.startswith("║") or s.startswith("╔") or s.startswith("╚")):
                    buckets[current].append(line)

        reels[nr] = {
            sec.lower().replace(" ", "_"): "\n".join(lines).strip()
            for sec, lines in buckets.items()
        }

    print(f"  → {len(reels)} reels geparsed")
    return reels


# ── Block builders ────────────────────────────────────────────────────────────

def blocks_for_reel(data):
    blocks = []
    for key, label in [
        ("concept",             "Concept"),
        ("visuele_structuur",   "Visuele Structuur"),
        ("tekst_op_scherm",     "Tekst op Scherm"),
        ("muziek",              "Muziek"),
        ("caption_bij_posting", "Caption bij Posting"),
        ("productiememo",       "Productiememo"),
    ]:
        content = data.get(key, "").strip()
        if content:
            blocks.append(h2(label))
            blocks.extend(text_to_blocks(content))
    return blocks


def blocks_for_feedpost(data):
    blocks = []
    if data.get("context"):
        blocks.append(h2("Context"))
        blocks.append(p(data["context"]))
    if data.get("beeld"):
        blocks.append(h2("Visuele Richting"))
        blocks.append(p(data["beeld"]))
    if data.get("caption"):
        blocks.append(h2("Caption"))
        blocks.extend(text_to_blocks(data["caption"]))
    if data.get("hashtags"):
        blocks.append(h2("Hashtags"))
        blocks.append(p(data["hashtags"]))
    return blocks


def blocks_for_story(data):
    blocks = []
    if data.get("context"):
        blocks.append(h2("Context"))
        blocks.append(p(data["context"]))
    screens = data.get("screens", [])
    total   = len(screens)
    for i, content in enumerate(screens, 1):
        blocks.append(h2(f"Scherm {i} van {total}"))
        if content.strip():
            blocks.extend(text_to_blocks(content))
    return blocks


# ── Supporting pages ──────────────────────────────────────────────────────────

def file_to_blocks(filepath, intro, max_chars=10000):
    """Convert a box-formatted text file into Notion blocks."""
    raw   = open(filepath, encoding="utf-8").read()[:max_chars]
    blks  = [p(intro), divider()]
    buf   = []

    for line in raw.split("\n"):
        s = line.strip()
        # Box section headers → h2
        if s.startswith("║") and not s.startswith("║   ─"):
            clean = re.sub(r"^[║╔╚═\s]+", "", re.sub(r"[║╔╚═\s]+$", "", s)).strip()
            if clean and len(clean) > 2:
                if buf:
                    blks.extend(text_to_blocks("\n".join(buf)))
                    buf = []
                blks.append(h2(clean[:100]))
                continue
        if s.startswith("╔") or s.startswith("╚") or "━" * 10 in s:
            continue  # skip structural chars
        buf.append(line)

    if buf:
        blks.extend(text_to_blocks("\n".join(buf)))

    return blks[:200]  # stay within reasonable block limits


# ── Notion helpers ────────────────────────────────────────────────────────────

def find_db():
    res = call("POST", "search", {
        "query": "Content Database",
        "filter": {"property": "object", "value": "database"},
    })
    if res and res.get("results"):
        return res["results"][0]["id"]
    return None


def query_all_items(db_id):
    items, cursor = [], None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        res = call("POST", f"databases/{db_id}/query", body)
        if not res:
            break
        for page in res.get("results", []):
            title_parts = page["properties"].get("Titel", {}).get("title", [])
            title = "".join(t.get("plain_text", "") for t in title_parts)
            items.append((title, page["id"]))
        if not res.get("has_more"):
            break
        cursor = res.get("next_cursor")
    return items


def find_root():
    res = call("POST", "search", {
        "query": "Maison BU Marketing OS",
        "filter": {"property": "object", "value": "page"},
    })
    if res and res.get("results"):
        return res["results"][0]["id"]
    return None


def create_page(parent_id, title):
    res = call("POST", "pages", {
        "parent": {"page_id": parent_id},
        "properties": {"title": {"title": [{"text": {"content": title}}]}},
    })
    return res["id"] if res else None


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Maison BU — Content Database Populatie")
    print("=" * 50)

    # 1. Parse primary content files
    print("\n📂 Contentbestanden laden...")
    feedposts = parse_feedposts(FEEDS_FILE)
    stories   = parse_stories(STORIES_FILE)
    reels     = parse_reels(REELS_FILE)

    # 2. Find the Content Database
    print("\n🔍 Content Database zoeken...")
    db_id = find_db()
    if not db_id:
        print("❌ Content Database niet gevonden!")
        sys.exit(1)
    print(f"  ✓ {db_id}")

    # 3. Retrieve all 36 items
    print("\n📋 Items ophalen uit database...")
    items = query_all_items(db_id)
    print(f"  ✓ {len(items)} items gevonden")

    # 4. Fill each item with its creative brief
    print("\n✍️  Items vullen met creatieve brieven...")
    ok = skip = errors = 0

    for title, page_id in items:
        m = re.match(r"^(Reel|Post|SF) (\d+) —", title)
        if not m:
            print(f"  ⚠ Onbekend formaat: '{title}' — overgeslagen")
            skip += 1
            continue

        kind = m.group(1)
        nr   = int(m.group(2))

        try:
            if kind == "Reel":
                data = reels.get(nr)
                if not data:
                    print(f"  ⚠ REEL {nr:02d} niet gevonden in bestand")
                    skip += 1
                    continue
                update_props(page_id,
                             caption=data.get("caption_bij_posting", ""),
                             visueel=data.get("concept", ""))
                blocks = blocks_for_reel(data)

            elif kind == "Post":
                data = feedposts.get(nr)
                if not data:
                    print(f"  ⚠ POST {nr:02d} niet gevonden in bestand")
                    skip += 1
                    continue
                update_props(page_id,
                             caption=data.get("caption", ""),
                             hashtags=data.get("hashtags", ""),
                             visueel=data.get("beeld", ""))
                blocks = blocks_for_feedpost(data)

            elif kind == "SF":
                data = stories.get(nr)
                if not data:
                    print(f"  ⚠ STORY FLOW {nr:02d} niet gevonden in bestand")
                    skip += 1
                    continue
                screens = data.get("screens", [])
                update_props(page_id,
                             visueel=(f"{len(screens)} schermen · {data.get('context', '')}")[:2000])
                blocks = blocks_for_story(data)

            else:
                skip += 1
                continue

            clear_page(page_id)
            add_blocks(page_id, blocks)
            print(f"  ✓ {title}")
            ok += 1
            time.sleep(0.2)

        except Exception:
            print(f"  ❌ Fout bij '{title}':")
            traceback.print_exc()
            errors += 1

    print(f"\n✅ Items: {ok} gevuld · {skip} overgeslagen · {errors} fouten")

    # 5. Create supporting sub-pages from remaining 3 files
    print("\n📄 Ondersteunende pagina's aanmaken...")
    root_id = find_root()
    if not root_id:
        print("  ⚠ Root pagina niet gevonden — ondersteunende pagina's overgeslagen")
        return

    for title, source_file, intro in [
        (
            "📊 Campagnestrategie",
            STRAT_FILE,
            "Volledige campagnestrategie · De Zoetheid van Juni · Juni 2026",
        ),
        (
            "📧 E-mail Campagne",
            EMAIL_FILE,
            "Mailchimp e-mailcampagne · De Zoetheid van Juni · Juni 2026",
        ),
        (
            "🎯 CTA Filosofie & Kristof",
            CTA_FILE,
            "CTA-filosofie en Kristof content ideeën · Juni 2026",
        ),
    ]:
        try:
            print(f"  → {title} aanmaken...")
            pid = create_page(root_id, title)
            if pid:
                blks = file_to_blocks(source_file, intro)
                add_blocks(pid, blks)
                print(f"  ✓ {title} aangemaakt ({len(blks)} blokken)")
            time.sleep(0.5)
        except Exception:
            print(f"  ⚠ {title} mislukt:")
            traceback.print_exc()

    print("\n🎉 Alles klaar!")


if __name__ == "__main__":
    main()
