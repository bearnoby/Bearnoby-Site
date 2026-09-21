#!/usr/bin/env python3
"""Builds the static site into an output directory (default: _site).

Reads blog/live.json to find which post folders belong on the public
/blog/ feed vs. the unlisted /blog-preview/ sandbox, renders each
post's post.md (YAML frontmatter + markdown body) into themed HTML,
copies post assets, and emits an RSS 2.0 feed for the public blog.
"""
import argparse
import html
import json
import re
import shutil
import sys
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape

import markdown
import yaml
from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTagInlineProcessor

STRIKETHROUGH_RE = r"(~~)(.+?)~~"


class StrikethroughExtension(Extension):
    """Adds ~~text~~ -> <del>text</del> support (not in core python-markdown)."""

    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            SimpleTagInlineProcessor(STRIKETHROUGH_RE, "del"), "strikethrough", 75
        )

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "blog" / "posts"
LIVE_JSON = ROOT / "blog" / "live.json"
SITE_URL = "https://bearnoby.com"

REQUIRED_FIELDS = ["date", "title", "permalink", "description", "tags"]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n?(.*)$", re.DOTALL)


class PostError(Exception):
    pass


def parse_post(folder: str) -> dict:
    post_dir = POSTS_DIR / folder
    post_file = post_dir / "post.md"
    if not post_file.exists():
        raise PostError(f"{folder}: missing post.md")

    raw = post_file.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(raw)
    if not match:
        raise PostError(f"{folder}: post.md must start with a '---' frontmatter block")

    frontmatter_raw, body_raw = match.groups()
    try:
        meta = yaml.safe_load(frontmatter_raw) or {}
    except yaml.YAMLError as exc:
        raise PostError(f"{folder}: invalid frontmatter YAML ({exc})") from exc

    missing = [f for f in REQUIRED_FIELDS if not meta.get(f)]
    if missing:
        raise PostError(f"{folder}: missing required field(s): {', '.join(missing)}")

    tags = meta["tags"]
    if not isinstance(tags, list) or len(tags) == 0:
        raise PostError(f"{folder}: 'tags' must be a non-empty list")

    date_raw = meta["date"]
    if isinstance(date_raw, datetime):
        date = date_raw
    else:
        try:
            date = datetime.strptime(str(date_raw), "%Y-%m-%dT%H:%M")
        except ValueError as exc:
            raise PostError(
                f"{folder}: 'date' must be yyyy-MM-ddTHH:mm (got {date_raw!r})"
            ) from exc

    permalink = str(meta["permalink"]).strip()
    if not re.match(r"^[a-zA-Z0-9\-_]+$", permalink):
        raise PostError(
            f"{folder}: 'permalink' must contain only letters, numbers, '-' and '_' "
            f"(got {permalink!r})"
        )

    body_html = markdown.markdown(
        body_raw, extensions=["fenced_code", "tables", StrikethroughExtension()]
    )

    return {
        "folder": folder,
        "date": date,
        "title": str(meta["title"]),
        "permalink": permalink,
        "description": str(meta["description"]),
        "tags": [str(t) for t in tags],
        "body_html": body_html,
    }


def rewrite_asset_paths(body_html: str, section: str, folder: str) -> str:
    base = f"/{section}/posts/{quote(folder)}/"

    def repl(m: re.Match) -> str:
        attr, path = m.group("attr"), m.group("path")
        if re.match(r"^([a-z]+:)?//|^https?:|^mailto:|^#|^/", path):
            return m.group(0)
        return f'{attr}="{base}{quote(path)}"'

    return re.sub(r'(?P<attr>src|href)="(?P<path>[^"]+)"', repl, body_html)


def copy_assets(folder: str, section: str, out_dir: Path) -> None:
    post_dir = POSTS_DIR / folder
    dest = out_dir / section / "posts" / folder
    for item in post_dir.iterdir():
        if item.name == "post.md":
            continue
        dest.mkdir(parents=True, exist_ok=True)
        if item.is_file():
            shutil.copy2(item, dest / item.name)
        elif item.is_dir():
            shutil.copytree(item, dest / item.name, dirs_exist_ok=True)


def load_posts(folders: list, section: str, out_dir: Path) -> list:
    posts = []
    for folder in folders:
        post = parse_post(folder)
        post["body_html"] = rewrite_asset_paths(post["body_html"], section, folder)
        copy_assets(folder, section, out_dir)
        posts.append(post)
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def render_post_article(post: dict, section: str) -> str:
    tag_chips = "\n".join(
        f'<button class="tag-chip" data-tag="{html.escape(t)}">#{html.escape(t)}</button>'
        for t in post["tags"]
    )
    tags_attr = ",".join(html.escape(t) for t in post["tags"])
    date_str = post["date"].strftime("%B %-d, %Y") if sys.platform != "win32" else post["date"].strftime("%B %#d, %Y")
    return f"""
    <article class="post-card" id="{html.escape(post['permalink'])}" data-tags="{tags_attr}">
        <div class="post-meta">
            <time datetime="{post['date'].isoformat()}">{date_str}</time>
        </div>
        <h2 class="post-title"><a href="#{html.escape(post['permalink'])}">{html.escape(post['title'])}</a></h2>
        <div class="post-body">
            {post['body_html']}
        </div>
        <div class="post-footer">
            <div class="post-tags">{tag_chips}</div>
            <button class="share-btn" data-permalink="{html.escape(post['permalink'])}">Share</button>
        </div>
    </article>"""


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    {robots}
    <link rel="alternate" type="application/rss+xml" title="Bearnoby Blog" href="{rss_link}">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <link rel="stylesheet" href="/static/css/style.css">
    <link rel="stylesheet" href="/static/css/blog.css">
    <link rel="icon" type="image/png" href="/static/img/bear_model.png">
</head>

<body class="blog-body">
    <header class="blog-header">
        <div class="header-title">
            <a href="/" class="back-link">&larr; bearnoby.com</a>
            <h1 class="blog-title">{heading}</h1>
        </div>
        <div class="header-actions">
            <a href="{rss_link}" class="btn rss-btn-header" title="Subscribe via RSS">RSS Feed</a>
        </div>
    </header>

    {banner}

    <div class="blog-container">
        <main class="blog-feed" id="blog-feed">
{articles}
        </main>

        <aside class="blog-sidebar">
            <div class="sidebar-card">
                <h3 class="sidebar-card-title">Filter Tags</h3>
                <div class="tag-filter-bar" id="tag-filter-bar">
                    <button class="tag-chip active" data-tag="">All Tags</button>
{all_tag_chips}
                </div>
            </div>

            <div class="sidebar-card">
                <h3 class="sidebar-card-title">Posts</h3>
                <ul class="sidebar-posts-list">
{posts_list_items}
                </ul>
            </div>
        </aside>
    </div>

    <footer>
        <p>&copy; 2026 Bearnoby | For business inquiries, contact via socials.</p>
    </footer>

    <script src="/static/js/blog.js"></script>
</body>

</html>
"""

PREVIEW_BANNER = """<div class="preview-banner">
        This is an unlisted preview/sandbox page &mdash; posts here are not on the public blog.
    </div>"""


def build_page(posts: list, section: str, out_dir: Path) -> None:
    all_tags = sorted({t for p in posts for t in p["tags"]}, key=str.lower)
    all_tag_chips = "\n".join(
        f'                    <button class="tag-chip" data-tag="{html.escape(t)}">#{html.escape(t)}</button>'
        for t in all_tags
    )
    articles = "\n".join(render_post_article(p, section) for p in posts)

    posts_list_items = "\n".join(
        f'                    <li class="sidebar-post-item">'
        f'<a href="#{html.escape(p["permalink"])}">'
        f'<span class="sidebar-post-title">{html.escape(p["title"])}</span>'
        f'<span class="sidebar-post-date">{(p["date"].strftime("%B %-d, %Y") if sys.platform != "win32" else p["date"].strftime("%B %#d, %Y"))}</span>'
        f'</a></li>'
        for p in posts
    )

    is_preview = section == "blog-preview"
    page = PAGE_TEMPLATE.format(
        title="Bearnoby Blog (Preview)" if is_preview else "Bearnoby Blog",
        description="Unlisted preview of upcoming Bearnoby blog posts."
        if is_preview
        else "Updates, travel, and info-dumps from Bearnoby.",
        robots='<meta name="robots" content="noindex, nofollow">' if is_preview else "",
        rss_link="/blog/rss.xml",
        heading="BLOG PREVIEW" if is_preview else "BLOG",
        banner=PREVIEW_BANNER if is_preview else "",
        all_tag_chips=all_tag_chips,
        posts_list_items=posts_list_items if posts_list_items else '<li><span class="sidebar-post-title">No posts</span></li>',
        articles=articles if articles else '<p class="empty-feed">No posts yet.</p>',
    )

    section_dir = out_dir / section
    section_dir.mkdir(parents=True, exist_ok=True)
    (section_dir / "index.html").write_text(page, encoding="utf-8")


def build_rss(posts: list, out_dir: Path) -> None:
    items = []
    for p in posts:
        link = f"{SITE_URL}/blog/#{p['permalink']}"
        items.append(f"""    <item>
      <title>{xml_escape(p['title'])}</title>
      <link>{xml_escape(link)}</link>
      <guid isPermaLink="true">{xml_escape(link)}</guid>
      <pubDate>{format_datetime(p['date'])}</pubDate>
      <description>{xml_escape(p['description'])}</description>
      <content:encoded><![CDATA[{p['body_html']}]]></content:encoded>
    </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>Bearnoby Blog</title>
    <link>{SITE_URL}/blog/</link>
    <description>Updates, travel, and info-dumps from Bearnoby.</description>
    <language>en-us</language>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (out_dir / "blog" / "rss.xml").write_text(rss, encoding="utf-8")


def copy_static_site(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "index.html", out_dir / "index.html")
    shutil.copy2(ROOT / "CNAME", out_dir / "CNAME")
    shutil.copytree(ROOT / "static", out_dir / "static", dirs_exist_ok=True)
    shutil.copytree(ROOT / "bearnoby-tools", out_dir / "bearnoby-tools", dirs_exist_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="_site")
    args = parser.parse_args()

    out_dir = (ROOT / args.out).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    copy_static_site(out_dir)

    live = json.loads(LIVE_JSON.read_text(encoding="utf-8"))

    try:
        blog_posts = load_posts(live.get("blog", []), "blog", out_dir)
        preview_posts = load_posts(live.get("blog-preview", []), "blog-preview", out_dir)
    except PostError as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        sys.exit(1)

    build_page(blog_posts, "blog", out_dir)
    build_page(preview_posts, "blog-preview", out_dir)
    build_rss(blog_posts, out_dir)

    print(f"Built {len(blog_posts)} blog post(s) and {len(preview_posts)} preview post(s) into {out_dir}")


if __name__ == "__main__":
    main()
