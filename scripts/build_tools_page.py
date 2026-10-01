"""Renders bearnoby-tools/index.html from bearnoby-tools/content.yaml.

All copy for the Bearnoby Tools page lives in content.yaml. Values are treated
as trusted HTML so links and entities can be written inline.
"""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "bearnoby-tools"
CONTENT_FILE = TOOLS_DIR / "content.yaml"

SITE_URL = "https://bearnoby.com/bearnoby-tools/"
# 1200x630 card: the app screenshot letterboxed on the app's dark background.
OG_IMAGE = SITE_URL + "img/og-card.png"
OG_ALT = "Bearnoby Tools app showing the Features screen, with the Bearnoby bear mascot in front"


def attr(value: str) -> str:
    return str(value).replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def plain(value: str) -> str:
    """Strip tags/entities enough for use inside an attribute (alt text, titles)."""
    import html
    import re

    return attr(html.unescape(re.sub(r"<[^>]+>", "", str(value))))


def links(items: list) -> str:
    return "".join(
        f'<a class="btn sm" href="{attr(l["url"])}">{l["text"]}</a>' for l in items
    )


def shot(feature: dict) -> str:
    if not feature.get("image"):
        return f'<div class="shot soon">{feature["title"]}<br>Screenshot coming soon</div>'
    return (
        f'<button type="button" class="shot" data-lightbox="{attr(feature["image"])}" '
        f'data-title="{plain(feature["title"])}" data-text="{plain(feature["text"])}" '
        f'aria-label="Enlarge {plain(feature["title"])}">'
        f'<img src="{attr(feature["image"])}" alt="{plain(feature["title"])}" loading="lazy">'
        f"</button>"
    )


def render_feature_groups(c: dict) -> str:
    out = []
    for group in c["feature_groups"]:
        rows = [f for f in c["features"] if f["group"] == group["id"]]
        if not rows:
            continue
        cards = "".join(
            f'<article class="tile">{shot(f)}<div><h3>{f["title"]}</h3><p>{f["text"]}</p></div></article>'
            for f in rows
        )
        out.append(
            f'<section id="{group["id"]}"><h2 class="outline-title h-section">'
            f'{group["name"].upper()}</h2><div class="tile-grid">{cards}</div></section>'
        )
    if c.get("features_footer"):
        out.append(f'<div class="card feature-more"><p>{c["features_footer"]}</p></div>')
    return "".join(out)


def render_addon(a: dict) -> str:
    bullets = "".join(f"<li>{b}</li>" for b in a.get("bullets", []))
    shots = "".join(
        f'<button type="button" class="shot" data-lightbox="{attr(s["image"])}" '
        f'data-title="{plain(s.get("alt", a["name"]))}" data-text="" aria-label="Enlarge screenshot">'
        f'<img src="{attr(s["image"])}" alt="{plain(s.get("alt", a["name"]))}" loading="lazy"></button>'
        for s in a.get("screenshots", [])
    )
    soon = a.get("status") == "coming-soon"
    price_note = f' &middot; {a["price_note"]}' if a.get("price_note") else ""
    price = "" if soon else f'<span class="price">{a.get("price", "")}{price_note}</span>'
    badge_text = a.get("badge") or ("" if soon else "NOW AVAILABLE")
    badge = f'<span class="badge now">{badge_text}</span>' if badge_text else ""
    see_btn = (
        f'<a href="{attr(a["page_url"])}" class="btn big yellow">See {a.get("short_name", a["name"])}</a>'
        if a.get("page_url") else ""
    )
    buy_btn = (
        '<span class="btn big disabled" aria-disabled="true">Coming Soon</span>'
        if soon
        else f'<a href="{attr(a["buy_url"])}" class="btn big">Buy on Itch.io</a>'
    )
    return f"""
      <div class="card lav addon">
        <div class="addon-art"><div class="pet-art"><img src="{attr(a["art"])}" alt="{plain(a.get("art_alt", a["name"]))}"></div></div>
        <div class="addon-body">
          <div class="addon-head">{badge}{price}</div>
          <h3>{a["name"]}</h3>
          <p class="pitch">{a["pitch"]}</p>
          <ul class="addon-list">{bullets}</ul>
          <div class="btn-row">{see_btn}{buy_btn}</div>
        </div>
      </div>
      {f'<div class="addon-shots">{shots}</div>' if shots else ''}"""


def render_premium(c: dict) -> str:
    p = c["premium"]
    addons = "".join(
        f'<div class="addon-wrap" id="{a["id"]}">{render_addon(a)}</div>' for a in p["addons"]
    )
    soon = f'<div class="coming-soon">{p["coming_soon"]}</div>' if p.get("coming_soon") else ""
    return (
        f'<section id="premium"><h2 class="outline-title h-section">{p["heading"].upper()}</h2>'
        f'<div class="premium">{addons}{soon}</div></section>'
    )


def render_nav(c: dict) -> str:
    groups = "".join(
        f'<a href="#{g["id"]}">{g["name"]}</a>'
        for g in c["feature_groups"]
        if any(f["group"] == g["id"] for f in c["features"])
    )
    addons = "".join(
        f'<a href="#{a["id"]}">{a.get("short_name", a["name"])}'
        f'{"<span class=new>NEW</span>" if a.get("status") != "coming-soon" else ""}</a>'
        for a in c["premium"]["addons"]
    )
    return (
        '<div class="logo"><img src="../static/img/bear_model.png" alt="">Bearnoby Tools</div>'
        '<h4>Start</h4><a href="#overview">Overview</a>'
        f"<h4>Free features</h4>{groups}"
        f"<h4>Premium</h4>{addons}"
        '<h4>Help</h4><a href="#about">About</a><a href="#faq">FAQ</a>'
    )


def render_pill(c: dict) -> str:
    ann = c.get("announcement", {})
    if not ann.get("enabled"):
        return ""
    addon = next((a for a in c["premium"]["addons"] if a["id"] == ann["addon"]), None)
    if not addon:
        raise ValueError(f"announcement.addon {ann['addon']!r} not found in premium.addons")
    pill = f'<b>{ann["pill"]}</b> ' if ann.get("pill") else ""
    return (
        f'<a class="newpill" href="#{addon["id"]}">'
        f'<span>{pill}{ann.get("text", "")}</span>'
        f'<span class="go">&rarr;</span></a>'
    )


def render_faq(c: dict) -> str:
    return "".join(
        f'<details class="faq-item"><summary>{q["q"]}</summary><div class="faq-body">'
        + "".join(f"<p>{p}</p>" for p in q["a"])
        + "</div></details>"
        for q in c["faq"]
    )


def render_about(c: dict) -> str:
    a = c["about"]
    points = "".join(f"<li>{p}</li>" for p in a["philosophy_points"])
    return (
        f'<div class="card white philosophy"><h3>{a["philosophy_heading"]}</h3>'
        f'<p>{a["philosophy_intro"]}</p><ol>{points}</ol></div>'
    )


def render_page(c: dict) -> str:
    page, ov = c["page"], c["overview"]
    badges = "".join(f'<span class="badge {b["style"]}">{b["text"]}</span>' for b in page["badges"])
    dl = ov["download"]
    desc = attr(page["description"])
    title = plain(page["title"])
    return f"""<!DOCTYPE html>
<html lang="en">

<head>
    <!-- GENERATED from bearnoby-tools/content.yaml by scripts/build_tools_page.py. Edit the YAML, not this file. -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">

    <link rel="canonical" href="{SITE_URL}">

    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Bearnoby">
    <meta property="og:url" content="{SITE_URL}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:image" content="{OG_IMAGE}">
    <meta property="og:image:type" content="image/png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="{OG_ALT}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{desc}">
    <meta name="twitter:image" content="{OG_IMAGE}">
    <meta name="twitter:image:alt" content="{OG_ALT}">

    <link rel="stylesheet" href="../static/css/style.css">
    <link rel="stylesheet" href="tools.css">
    <link rel="icon" type="image/png" href="../static/img/bear_model.png">
</head>

<body>
    <div class="page">
        <a href="/" class="back-link">&#8592; bearnoby.com</a>
        <div class="title-row">
            <h1 class="outline-title h-page">{page["title"].upper()}</h1>
            {badges}
            {render_pill(c)}
        </div>

        <div class="layout">
            <nav class="side-nav" id="side-nav" aria-label="Page sections">{render_nav(c)}</nav>

            <div class="main">
                <section id="overview">
                    <div class="overview">
                        <div class="shot hero-shot"><img src="{attr(ov["hero_image"])}" width="630" height="500" alt="{plain(ov["hero_alt"])}"></div>
                        <div class="card"><p>{ov["intro"]}</p></div>
                        <div class="card red download">
                            <h3>{dl["heading"]}</h3>
                            <a href="{attr(dl["button"]["url"])}" class="btn big">{dl["button"]["text"]}</a>
                            <p>{dl["support_text"]}</p>
                            <div class="btn-row">{links(dl["links"])}</div>
                        </div>
                    </div>
                </section>

                {render_feature_groups(c)}

                {render_premium(c)}

                <section id="about"><h2 class="outline-title h-section">ABOUT</h2>{render_about(c)}</section>

                <section id="faq"><h2 class="outline-title h-section">FAQ</h2><div class="faq-list">{render_faq(c)}</div></section>
            </div>
        </div>
    </div>

    <footer>
        <p>{c["footer"]}</p>
    </footer>

    <div class="lightbox" id="lightbox" hidden role="dialog" aria-modal="true" aria-label="Screenshot">
        <div class="lightbox-card">
            <div class="lightbox-top"><div><h3 id="lightbox-title"></h3><p id="lightbox-text"></p></div><button type="button" class="btn sm" id="lightbox-close">Close</button></div>
            <img id="lightbox-img" src="" alt="">
        </div>
    </div>

    <script src="tools.js"></script>
</body>

</html>
"""


def build_tools_page(out_dir: Path) -> None:
    content = yaml.safe_load(CONTENT_FILE.read_text(encoding="utf-8"))
    dest = out_dir / "bearnoby-tools"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "index.html").write_text(render_page(content), encoding="utf-8")
