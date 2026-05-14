# Maison BU — Notion Marketing OS Builder
# Uitvoeren in PowerShell: .\notion_builder.ps1
# Geen installaties nodig — werkt op elke Windows laptop

$TOKEN = $env:NOTION_TOKEN
if (-not $TOKEN) {
    $TOKEN = Read-Host "Plak je Notion token (begint met ntn_...)"
}
$API   = "https://api.notion.com/v1"
$HDR   = @{
    "Authorization"  = "Bearer $TOKEN"
    "Notion-Version" = "2022-06-28"
    "Content-Type"   = "application/json"
}

function Notion($method, $path, $body) {
    try {
        $json = if ($body) { $body | ConvertTo-Json -Depth 20 -Compress } else { $null }
        $r = Invoke-RestMethod -Uri "$API/$path" -Method $method -Headers $HDR -Body $json -ErrorAction Stop
        Start-Sleep -Milliseconds 400
        return $r
    } catch {
        $msg = $_.Exception.Response
        Write-Host "  ⚠  Fout bij $path : $($_.Exception.Message)" -ForegroundColor Yellow
        return $null
    }
}

function MakePage($parentId, $title, $children, $workspace=$false, $dbParent=$false) {
    $par = if ($workspace)  { @{ type="workspace"; workspace=$true } }
           elseif ($dbParent) { @{ type="database_id"; database_id=$parentId } }
           else               { @{ type="page_id";     page_id=$parentId } }
    $body = @{
        parent     = $par
        properties = @{ title = @{ title = @(@{ text = @{ content = $title } }) } }
    }
    if ($children) { $body.children = $children[0..99] }
    $r = Notion "POST" "pages" $body
    if ($r) { Write-Host "  ✓  $title" -ForegroundColor Green }
    return $r
}

function MakeDatabase($parentId, $title, $props) {
    $body = @{
        parent     = @{ type="page_id"; page_id=$parentId }
        title      = @(@{ text = @{ content = $title } })
        properties = $props
    }
    $r = Notion "POST" "databases" $body
    if ($r) { Write-Host "  ✓  Database: $title" -ForegroundColor Green }
    return $r
}

function AddItem($dbId, $props) {
    $body = @{ parent = @{ database_id = $dbId }; properties = $props }
    return Notion "POST" "pages" $body
}

function AppendBlocks($pageId, $blocks) {
    $body = @{ children = $blocks[0..99] }
    return Notion "PATCH" "blocks/$pageId/children" $body
}

# Block helpers
function H2($t)     { @{ object="block"; type="heading_2";           heading_2          =@{ rich_text=@(@{type="text";text=@{content=$t}}) } } }
function H3($t)     { @{ object="block"; type="heading_3";           heading_3          =@{ rich_text=@(@{type="text";text=@{content=$t}}) } } }
function P($t)      { @{ object="block"; type="paragraph";           paragraph          =@{ rich_text=@(@{type="text";text=@{content=$t}}) } } }
function Div()      { @{ object="block"; type="divider";             divider            =@{} } }
function Todo($t)   { @{ object="block"; type="to_do";               to_do              =@{ rich_text=@(@{type="text";text=@{content=$t}}); checked=$false } } }
function Bullet($t) { @{ object="block"; type="bulleted_list_item";  bulleted_list_item =@{ rich_text=@(@{type="text";text=@{content=$t}}) } } }
function Quote($t)  { @{ object="block"; type="quote";               quote              =@{ rich_text=@(@{type="text";text=@{content=$t}}) } } }
function Callout($t,$icon="💡") {
    @{ object="block"; type="callout"; callout=@{ rich_text=@(@{type="text";text=@{content=$t}}); icon=@{type="emoji";emoji=$icon} } }
}
function Code($t) {
    @{ object="block"; type="code"; code=@{ rich_text=@(@{type="text";text=@{content=$t}}); language="plain text" } }
}

# Database schema
$DB_PROPS = @{
    Titel            = @{ title = @{} }
    Type             = @{ select = @{ options = @(
        @{name="Reel";       color="purple"}
        @{name="Feedpost";   color="blue"}
        @{name="Story Flow"; color="green"}
        @{name="Email";      color="yellow"} ) } }
    Week             = @{ select = @{ options = @(
        @{name="Week 1"; color="gray"}
        @{name="Week 2"; color="brown"}
        @{name="Week 3"; color="orange"}
        @{name="Week 4"; color="red"} ) } }
    Pillar           = @{ select = @{ options = @(
        @{name="De Maison";       color="default"}
        @{name="De Craft";        color="purple"}
        @{name="De Gast";         color="blue"}
        @{name="De Transformatie";color="green"}
        @{name="De Filosofie";    color="gray"}
        @{name="De Ceremonie";    color="pink"} ) } }
    Status           = @{ select = @{ options = @(
        @{name="Idee";                color="gray"}
        @{name="In Productie";        color="yellow"}
        @{name="Klaar";               color="blue"}
        @{name="Wacht op Goedkeuring";color="orange"}
        @{name="Gepubliceerd";        color="green"} ) } }
    Publicatiedatum  = @{ date = @{} }
    CTA              = @{ select = @{ options = @(
        @{name="Geen";         color="gray"}
        @{name="Fluistering";  color="blue"}
        @{name="Weloverwogen"; color="orange"}
        @{name="Uitnodiging";  color="red"} ) } }
    "Asset Link"     = @{ url = @{} }
    Notities         = @{ rich_text = @{} }
}

# 36 content items: type, title, week, pillar, date, cta, status
$ITEMS = @(
    # WEEK 1
    @("Reel",      "Reel 01 — Juni betreedt de maison",                    "Week 1","De Maison",       "2026-06-02","Geen",        "Klaar"),
    @("Reel",      "Reel 02 — Het golf van zomer",                         "Week 1","De Craft",        "2026-06-06","Geen",        "Klaar"),
    @("Feedpost",  "Post 01 — Juni betreedt de maison",                    "Week 1","De Maison",       "2026-06-02","Geen",        "Klaar"),
    @("Feedpost",  "Post 02 — Over vakmanschap in de zomer (Kristof)",     "Week 1","De Filosofie",    "2026-06-05","Geen",        "Klaar"),
    @("Feedpost",  "Post 03 — De signature cut, opnieuw gedacht",          "Week 1","De Craft",        "2026-06-04","Geen",        "Klaar"),
    @("Story Flow","SF 01 — Hoe juni eruitziet in de maison",             "Week 1","De Maison",       "2026-06-01","Geen",        "Klaar"),
    @("Story Flow","SF 02 — De maison in de vroege ochtend",              "Week 1","De Maison",       "2026-06-03","Geen",        "Klaar"),
    @("Story Flow","SF 03 — Vijf dingen die we nooit zullen doen",        "Week 1","De Filosofie",    "2026-06-06","Geen",        "Klaar"),
    @("Story Flow","SF 04 — Wat is een signature cut?",                   "Week 1","De Craft",        "2026-06-07","Geen",        "Klaar"),
    # WEEK 2
    @("Reel",      "Reel 03 — Een kleur die zichzelf niet aankondigt",    "Week 2","De Transformatie","2026-06-09","Fluistering", "Klaar"),
    @("Reel",      "Reel 04 — De gast die een dinsdag droeg",             "Week 2","De Gast",         "2026-06-13","Fluistering", "Klaar"),
    @("Feedpost",  "Post 04 — De golf die altijd bestond",                "Week 2","De Transformatie","2026-06-08","Fluistering", "Klaar"),
    @("Feedpost",  "Post 05 — Ze arriveerde met een dinsdag",             "Week 2","De Gast",         "2026-06-11","Fluistering", "Klaar"),
    @("Feedpost",  "Post 06 — Kleur die zichzelf niet aankondigt",        "Week 2","De Transformatie","2026-06-13","Fluistering", "Klaar"),
    @("Story Flow","SF 05 — Beachwaves voor jouw haar",                   "Week 2","De Craft",        "2026-06-10","Fluistering", "Klaar"),
    @("Story Flow","SF 06 — Wat onze gasten echt voelen",                 "Week 2","De Gast",         "2026-06-10","Fluistering", "Klaar"),
    @("Story Flow","SF 07 — De kleur van juni",                           "Week 2","De Transformatie","2026-06-14","Fluistering", "Klaar"),
    @("Story Flow","SF 08 — Kristof over zomer en terughoudendheid",      "Week 2","De Filosofie",    "2026-06-12","Fluistering", "Klaar"),
    # WEEK 3
    @("Reel",      "Reel 05 — Kristof over vakmanschap",                  "Week 3","De Filosofie",    "2026-06-16","Weloverwogen","Klaar"),
    @("Reel",      "Reel 06 — De ceremonieochtend",                       "Week 3","De Ceremonie",    "2026-06-20","Weloverwogen","Klaar"),
    @("Feedpost",  "Post 07 — Sommige dagen vragen alles (Huwelijk)",     "Week 3","De Ceremonie",    "2026-06-16","Weloverwogen","Klaar"),
    @("Feedpost",  "Post 08 — Over niet achter trends aanlopen (Kristof)","Week 3","De Filosofie",    "2026-06-19","Geen",        "Klaar"),
    @("Feedpost",  "Post 09 — De communieochtend",                        "Week 3","De Ceremonie",    "2026-06-20","Weloverwogen","Klaar"),
    @("Story Flow","SF 09 — De bruid de avond voor de ceremonie",         "Week 3","De Ceremonie",    "2026-06-15","Weloverwogen","Klaar"),
    @("Story Flow","SF 10 — De communieochtend",                          "Week 3","De Ceremonie",    "2026-06-17","Weloverwogen","Klaar"),
    @("Story Flow","SF 11 — Waarom we e-mail verkiezen boven een link",   "Week 3","De Filosofie",    "2026-06-18","Weloverwogen","Klaar"),
    @("Story Flow","SF 12 — De headspa in juni",                          "Week 3","De Craft",        "2026-06-21","Weloverwogen","Klaar"),
    # WEEK 4
    @("Reel",      "Reel 07 — De vlucht is over drie dagen",              "Week 4","De Gast",         "2026-06-23","Uitnodiging", "Klaar"),
    @("Reel",      "Reel 08 — Een opening heeft zich voorgedaan",         "Week 4","De Maison",       "2026-06-27","Uitnodiging", "Klaar"),
    @("Feedpost",  "Post 10 — Ze had het uitgesteld tot juni",            "Week 4","De Gast",         "2026-06-23","Uitnodiging", "Klaar"),
    @("Feedpost",  "Post 11 — De maison is klaar om u te ontvangen",      "Week 4","De Maison",       "2026-06-25","Uitnodiging", "Klaar"),
    @("Feedpost",  "Post 12 — Deze zomer besloot ze te stoppen met haasten","Week 4","De Gast",       "2026-06-28","Uitnodiging", "Klaar"),
    @("Story Flow","SF 13 — De vlucht is over drie dagen",                "Week 4","De Gast",         "2026-06-22","Uitnodiging", "Klaar"),
    @("Story Flow","SF 14 — Zij had het al sinds mei bedacht",            "Week 4","De Gast",         "2026-06-24","Uitnodiging", "Klaar"),
    @("Story Flow","SF 15 — Wat juli niet kan geven wat juni nog kan",    "Week 4","De Maison",       "2026-06-28","Uitnodiging", "Klaar"),
    @("Story Flow","SF 16 — Maison BU wenst u een mooie zomer",          "Week 4","De Maison",       "2026-06-30","Uitnodiging", "Klaar")
)

# Page content
function VandaagBlocks {
    @(
        Callout "Filter de Content Database op vandaag's datum om te zien wat er gepland staat." "🌅"
        Div; H2 "Dagelijkse checklist"; H3 "Voor het posten"
        Todo "Caption nagelezen als Kristof — klinkt het menselijk?"
        Todo "Geen verboden woorden (luxury, deal, boek nu, miss het niet)"
        Todo "Juiste CTA voor deze week"
        Todo "Asset klaar in correct formaat"
        Todo "Publicatietijd correct ingesteld in Later / Buffer / Instagram"
        Div; H3 "Na het posten"
        Todo "Status -> Gepubliceerd in Content Database"
        Todo "Datum bevestigd"
        Todo "Reacties bekeken na 1 uur"
        Div; H2 "Vaste publicatietijden"
        P "Maandag  18:30 — Feedpost of Story"
        P "Dinsdag  19:00 — Reel"
        P "Woensdag 18:00 — Story"
        P "Donderdag 19:00 — Feedpost"
        P "Vrijdag  08:00 — Kristof / Filosofie"
        P "Zaterdag 10:00 — Story of Reel"
        P "Zondag   11:00 — Slotweek (Week 4)"
    )
}

function WorkflowBlocks {
    @(
        Quote "Van idee tot gepubliceerd — stap voor stap."
        Div; H2 "Stap 1 — Idee"
        Bullet "Nieuw item aanmaken in Content Database"
        Bullet "Status: Idee — Type, Pillar en Week invullen"
        Div; H2 "Stap 2 — Aanmaken"
        Bullet "Template openen (Reel / Feedpost / Story)"
        Bullet "Caption schrijven + visueel beschrijven"
        Bullet "Status: In Productie"
        Div; H2 "Stap 3 — Asset maken"
        Bullet "Canva / Premiere / CapCut openen"
        Bullet "Feedpost: 1080x1350px JPG | Reel: 1080x1920px MP4 | Story: 1080x1920px"
        Bullet "Asset link toevoegen aan Content Database"
        Div; H2 "Stap 4 — Goedkeuring"
        Todo "Toon correct?"
        Todo "Geen verboden woorden?"
        Todo "'Atelier' nergens — altijd 'de maison'?"
        Todo "CTA past bij de week?"
        Div; H2 "Stap 5 — Klaar"
        Bullet "Status: Klaar — Publicatiedatum instellen in Later / Buffer"
        Div; H2 "Stap 6 — Gepubliceerd"
        Bullet "Status: Gepubliceerd — Engagement na 24u bekijken"
        Div
        Code "Idee  ->  In Productie  ->  Klaar  ->  Goedkeuring  ->  Gepubliceerd"
    )
}

function RichtlijnBlocks {
    @(
        Quote "De regels die nooit veranderen."
        Div; H2 "Kleuren"
        P "Diepzwart  #1A1A18 — Hoofdkleur, accenten, tekst"
        P "Warm wit   #F8F5F0 — Achtergronden"
        P "Creme      #EDE9E3 — Tussenliggende sfeer"
        P "Lichtgrijs #C9BFB4 — Scheidingslijnen"
        Div; H2 "Lettertypes"
        P "Headlines:    Cormorant Garamond Italic"
        P "Bodytekst:    Cormorant Garamond Regular"
        P "Labels / CTA: Arial of Helvetica Regular — klein, altijd"
        Div; H2 "Taal"
        P "Altijd Nederlands"
        P "Frans accent spaarzaam: maison, savoir-faire, l'invitation, signature"
        P "Nooit Engelse cliches als stijlkeuze"
        P "Nooit 'het atelier' — altijd 'de maison'"
        Div; H2 "Goede woorden"
        P "verfijning, vakmanschap, tijdloos, gast (nooit klant), de maison, gecreeerd voor jou, aanwezig, ritueel, stil, eerbiedig, savoir-faire"
        Div; H2 "VERBODEN woorden"
        P "luxury, premium, transformatie, glam, deal"
        P "aanbieding, boek nu, mis het niet, summer sale"
        P "hair goals, glow-up, before/after, new hair who dis"
        P "het atelier, the atelier, notre atelier"
        Div; H2 "CTA per week"
        P "Week 1: Geen CTA"
        P "Week 2: Fluistering — 'Reserveer jouw moment. Link in bio.'"
        P "Week 3: Weloverwogen — 'hello@maisonbu.be' (voor ceremonies)"
        P "Week 4: Uitnodiging — 'maisonbu.be/book'"
        Div; H2 "Visuele regels"
        P "Warm licht — gouden uur: 7-9u of 17-19u"
        P "Statische of trage camera (slider)"
        P "Close-ups van handen en haartextuur"
        P "Week 1: geen gezichten — mysterie bewaren"
        P "NOOIT: ring lights, viral audio, koude filters, voor/na zonder toestemming"
        Div
        Callout "De Soul Test: Zou Kristof dit gezegd hebben? Als nee — herschrijf." "✨"
        Div; H2 "Contact"
        P "hello@maisonbu.be | maisonbu.be | maisonbu.be/book"
    )
}

function ChecklistBlocks {
    @(
        H2 "Week 1 lancering"
        Todo "Strategie en kalender volledig ingevuld"
        Todo "Shootdag ingepland en voorbereid"
        Todo "Week 1 content aangemaakt (4 stuks)"
        Todo "Geen CTA's in Week 1 — gecontroleerd"
        Todo "Muziek geselecteerd per reel"
        Todo "Assets klaar in Google Drive / Canva"
        Div; H2 "Week 2 lancering"
        Todo "Week 2 content aangemaakt (4 stuks)"
        Todo "CTA aanwezig maar subtiel ('Link in bio')"
        Todo "Mailchimp campagne klaar en getest"
        Todo "E-mail verstuurd op dinsdag 09:15"
        Div; H2 "Week 3 lancering"
        Todo "Ceremonie content aangemaakt"
        Todo "CTA via e-mail (hello@maisonbu.be) voor huwelijk/communie"
        Todo "Kristof filosofie post ingepland"
        Div; H2 "Week 4 lancering"
        Todo "Sluitingsweek content aangemaakt"
        Todo "CTA op elk stuk (altijd als laatste regel)"
        Todo "Herboekings-e-mail verstuurd"
        Todo "Alle content gepubliceerd"
        Div; H2 "Dagelijkse checklist — voor posten"
        Todo "Caption nagelezen als Kristof"
        Todo "Geen verboden woorden"
        Todo "Juiste CTA voor deze week"
        Todo "Asset klaar in correct formaat"
        Todo "Publicatietijd correct ingesteld"
        Div; H2 "Dagelijkse checklist — na posten"
        Todo "Status -> Gepubliceerd in Content Database"
        Todo "Datum bevestigd"
        Todo "Reacties bekeken na 1 uur"
        Div; H2 "Shootdag checklist"
        Todo "Shot list volledig"
        Todo "Licht: gouden uur (7-9u of 17-19u)"
        Todo "Camera geladen, geheugenkaart leeg"
        Todo "Alle shots gemaakt"
        Todo "Bestanden overgezet naar Drive"
        Div; H2 "Mailchimp checklist"
        Todo "Hardop gelezen als Kristof"
        Todo "Onderwerpregel getest op mobiel"
        Todo "Boekingslink getest en actief"
        Todo "Uitschrijflink functioneel"
        Todo "Slechts een CTA — bevestigd"
        Todo "Geen verboden woorden"
        Todo "'Atelier' nergens — altijd 'de maison'"
    )
}

function AssetBlocks {
    @(
        Quote "Alles op de juiste plek, altijd terug te vinden."
        Div; H2 "Mappenstructuur"
        Code "Maison BU Assets\Juni 2026\Reels\`n                  \Feedposts\`n                  \Stories\`n                  \Shootdag 2026-06-04\Brand Assets (permanent)\Logo\Kleurpaletten\Lettertypes\Archief"
        Div; H2 "Exportformaten"
        P "Feedpost    -> 1080x1350px (4:5) JPG of PNG"
        P "Reel        -> 1080x1920px (9:16) MP4 H.264"
        P "Story       -> 1080x1920px (9:16) JPG of MP4"
        P "Email header-> 600x340px JPG"
        Div; H2 "Naamconventie"
        Code "[type]_[week]_[korte-titel]_[datum].[ext]`nreel_w1_juni-betreedt-maison_20260602.mp4`nfeedpost_w2_golf-bestond_20260609.jpg"
    )
}

function ShootBlocks {
    @(
        Callout "Shootdag juni 2026 — plan op 2 of 3 juni (Week 1)" "📸"
        Div; H2 "Shot list Week 1 (geen gezichten)"
        Todo "Maison in junilicht — architecturaal, vroege ochtend"
        Todo "Schaar, kam, spuitfles — close-up stilleven"
        Todo "Hand die gereedschap neerlegt"
        Todo "Betonvloer met lichtval"
        Todo "Spiegel die licht terugkaatst"
        Todo "Haar close-up — textuur in beweging (beachwaves)"
        Todo "Handen die golf vormen — slow motion 120fps"
        Todo "Lege stoel in junilicht"
        Div; H2 "Shot list Week 2 (transformatie)"
        Todo "Kleurpigment in kom — close-up"
        Todo "Borstel die kleur aanbrengt — bewust en traag"
        Todo "Haar dat gewassen wordt — fragmenten"
        Todo "Gast vertrekt — rug, licht, haar in beweging"
        Div; H2 "Shot list Week 3 (ceremonie)"
        Todo "Elegante opsteek — detail, geen gezicht"
        Todo "Handen die haarpins plaatsen"
        Todo "Communiestijl — close-up details"
        Div; H2 "Productie-afspraken"
        P "Gouden uur: 7-9u of 17-19u | Geen ring lights"
        P "Camera: statisch voor architectuur / langzame slide voor haar"
        P "Kleurgrading: warm en ingetogen — geen filters, geen presets"
        P "Elke cut minimaal 3 seconden — geen flits, geen snelheid"
    )
}

function TemplateBlocks {
    @(
        H2 "Reel Template"
        P "CONCEPT: [wat laat dit reel zien?]"
        P "WEEK: [1/2/3/4] | PILLAR: [pillar naam] | DUUR: [30/45/60 sec]"
        P "VISUELE STRUCTUUR:"
        P "[00:00] Opening — [beschrijving]"
        P "[00:xx] Kern — [beschrijving]"
        P "[00:xx] Slot — [beschrijving]"
        P "TEKST OP SCHERM: [tijdstempel] — '[tekst]' (klein, serif)"
        P "MUZIEK: [instrumentaal / referentie]"
        P "CAPTION: [opening] / [kern] / [CTA van de week] / [hashtags max 8]"
        Div; H2 "Feedpost Template"
        P "TITEL: [intern] | WEEK: [1/2/3/4] | PILLAR: [naam]"
        P "BEELD: [beschrijving visueel]"
        P "CAPTION:"
        P "[opening — directe sfeer]"
        P "[kern — diepte of emotie]"
        P "[afsluiting — stilte of CTA] / #MaisonBU #Hasselt"
        Div; H2 "Story Flow Template"
        P "TITEL: [intern] | WEEK: [1/2/3/4] | FRAMES: [3-7]"
        P "FRAME 1: [beeld + tekst]"
        P "FRAME 2: [beeld + tekst]"
        P "FRAME 3: [beeld + tekst + CTA]"
    )
}

# ── MAIN ──────────────────────────────────────────────────────────────────────

Write-Host "`n🌿 Maison BU — Notion Marketing OS Builder`n" -ForegroundColor Cyan

# 1. Root page
Write-Host "Aanmaken: Home pagina..." -ForegroundColor Cyan
$root = MakePage $null "🏠 Maison BU — Marketing OS" $null $true

if (-not $root) {
    Write-Host "`n⚠  Workspace aanmaken mislukt." -ForegroundColor Yellow
    Write-Host "   Maak een lege pagina in Notion, deel die met je integratie," -ForegroundColor Yellow
    Write-Host "   kopieer de pagina-ID uit de URL en herstart:" -ForegroundColor Yellow
    Write-Host "   .\notion_builder.ps1 <PAGE_ID>" -ForegroundColor Yellow
    if ($args[0]) {
        Write-Host "`n   Probeer met: $($args[0])" -ForegroundColor Cyan
        $root = MakePage $args[0] "🏠 Maison BU — Marketing OS"
    }
    if (-not $root) { Write-Host "❌ Gestopt." -ForegroundColor Red; exit 1 }
}

$rootId = $root.id
Write-Host "`n   Root URL: https://notion.so/$($rootId -replace '-','')`n" -ForegroundColor Cyan

# 2. Content Database
Write-Host "Aanmaken: Content Database..." -ForegroundColor Cyan
$db = MakeDatabase $rootId "📋 Content Database — Juni 2026" $DB_PROPS
if (-not $db) { Write-Host "❌ Database mislukt." -ForegroundColor Red; exit 1 }
$dbId = $db.id

# 3. Fill 36 items
Write-Host "`nInvullen: $($ITEMS.Count) content items..." -ForegroundColor Cyan
$i = 1
foreach ($item in $ITEMS) {
    $props = @{
        Titel           = @{ title = @(@{ text = @{ content = $item[1] } }) }
        Type            = @{ select = @{ name = $item[0] } }
        Week            = @{ select = @{ name = $item[2] } }
        Pillar          = @{ select = @{ name = $item[3] } }
        Status          = @{ select = @{ name = $item[6] } }
        Publicatiedatum = @{ date = @{ start = $item[4] } }
        CTA             = @{ select = @{ name = $item[5] } }
    }
    $r = AddItem $dbId $props
    $status = if ($r) { "✓" } else { "⚠" }
    $color  = if ($r) { "Green" } else { "Yellow" }
    Write-Host ("  {0} {1:D2}/36  {2}" -f $status, $i, $item[1].Substring(0, [Math]::Min(55,$item[1].Length))) -ForegroundColor $color
    $i++
}

# 4. Sub-pages
Write-Host "`nAanmaken: Sub-paginas..." -ForegroundColor Cyan
MakePage $rootId "🌅 Vandaag"           (VandaagBlocks)   | Out-Null
MakePage $rootId "📅 Deze Week"         @(Callout "Week 1 (1-7 juni): geen CTAs. Week 2 (8-14 juni): fluistering. Week 3 (15-21 juni): ceremonie. Week 4 (22-30 juni): uitnodiging." "📅") | Out-Null
MakePage $rootId "🔄 Posting Workflow"  (WorkflowBlocks)  | Out-Null
MakePage $rootId "🎨 Merkrichtlijnen"   (RichtlijnBlocks) | Out-Null
MakePage $rootId "✅ Checklists"        (ChecklistBlocks) | Out-Null
MakePage $rootId "📁 Asset Beheer"      (AssetBlocks)     | Out-Null
MakePage $rootId "📸 Shootdag Planner"  (ShootBlocks)     | Out-Null
MakePage $rootId "📝 Templates"         (TemplateBlocks)  | Out-Null

# 5. Home content
Write-Host "`nBijwerken: Home pagina..." -ForegroundColor Cyan
$homeBlocks = @(
    Callout "Maison BU | De Zoetheid van Juni 2026 | Marketing OS`nAlles op een plek. Strategie, content, checklists, workflow." "🌿"
    Div; H2 "Snelnavigatie"
    Bullet "Content Database — alle 36 juni-stukken"
    Bullet "Vandaag — wat staat er vandaag gepland?"
    Bullet "Deze Week — campagne-overzicht"
    Bullet "Checklists — voor, tijdens en na het posten"
    Bullet "Posting Workflow — 6-stappen proces"
    Bullet "Merkrichtlijnen — de regels die nooit veranderen"
    Bullet "Asset Beheer — mappenstructuur en naamconventie"
    Bullet "Shootdag Planner — shot lists per week"
    Bullet "Templates — Reel, Feedpost en Story Flow"
    Div; H2 "Campagne — De Zoetheid van Juni 2026"
    P "Week 1 | Wereldopbouw (1-7 juni) — geen CTAs, mysterie opbouwen"
    P "Week 2 | De Fluistering (8-14 juni) — zachte CTAs, zomerafspraken"
    P "Week 3 | De Weloverwogen Vraag (15-21 juni) — ceremonie en huwelijk"
    P "Week 4 | De Uitnodiging (22-30 juni) — directe uitnodiging, afsluiting"
    Div
    Quote "Zou Kristof dit gezegd hebben? Als nee — herschrijf."
)
AppendBlocks $rootId $homeBlocks | Out-Null

# Done
Write-Host "`n$("─" * 60)" -ForegroundColor Cyan
Write-Host "✅  Maison BU Marketing OS aangemaakt in Notion!" -ForegroundColor Green
Write-Host "`n   Ga naar: https://notion.so/$($rootId -replace '-','')" -ForegroundColor Cyan
Write-Host "`n   Aangemaakt:"
Write-Host "   · Content Database met alle 36 juni 2026 items"
Write-Host "   · Vandaag, Deze Week, Posting Workflow"
Write-Host "   · Merkrichtlijnen, Checklists, Asset Beheer"
Write-Host "   · Shootdag Planner, Templates"
Write-Host "$("─" * 60)`n" -ForegroundColor Cyan
