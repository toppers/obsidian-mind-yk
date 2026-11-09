#!/usr/bin/env python3
"""Batch ingest HTML files from tecs-docs into the my-topic wiki raw/articles/."""

import os
import re
import sys
from html.parser import HTMLParser
from datetime import date
from pathlib import Path

TODAY = date.today().isoformat()
WIKI_ROOT = Path(__file__).parent.parent
RAW_ARTICLES = WIKI_ROOT / "raw" / "articles"
LOG_FILE = WIKI_ROOT / "log.md"


class TECSHTMLParser(HTMLParser):
    """Extract title and main article body from Sphinx-generated HTML."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.in_main = False
        self.in_nav = False
        self.in_footer = False
        self.in_script = False
        self.depth_main = 0
        self.parts = []
        self.current_tag = ""
        self.current_attrs = {}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.current_tag = tag
        self.current_attrs = attrs_dict

        if tag == "title":
            self.in_title = True
            return
        if tag == "script":
            self.in_script = True
            return
        if tag == "nav":
            self.in_nav = True
            return
        if tag == "footer":
            self.in_footer = True
            return

        role = attrs_dict.get("role", "")
        cls = attrs_dict.get("class", "")

        if role == "main" or "document" in cls or "articleBody" in attrs_dict.get("itemprop", ""):
            self.in_main = True
            self.depth_main = 1
            return

        if self.in_main:
            self.depth_main += 1
            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                level = int(tag[1])
                self.parts.append("\n" + "#" * level + " ")
            elif tag == "p":
                self.parts.append("\n")
            elif tag == "li":
                self.parts.append("\n- ")
            elif tag == "pre":
                self.parts.append("\n```\n")
            elif tag == "code":
                self.parts.append("`")
            elif tag == "strong" or tag == "b":
                self.parts.append("**")
            elif tag == "em" or tag == "i":
                self.parts.append("*")
            elif tag == "a":
                pass  # just emit text
            elif tag == "table":
                self.parts.append("\n")
            elif tag == "tr":
                self.parts.append("\n| ")
            elif tag == "th" or tag == "td":
                pass

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
            return
        if tag == "script":
            self.in_script = False
            return
        if tag == "nav":
            self.in_nav = False
            return
        if tag == "footer":
            self.in_footer = False
            return

        if self.in_main:
            self.depth_main -= 1
            if self.depth_main <= 0:
                self.in_main = False
                return
            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                self.parts.append("\n")
            elif tag == "pre":
                self.parts.append("\n```\n")
            elif tag == "code":
                self.parts.append("`")
            elif tag == "strong" or tag == "b":
                self.parts.append("**")
            elif tag == "em" or tag == "i":
                self.parts.append("*")
            elif tag == "th" or tag == "td":
                self.parts.append(" | ")
            elif tag == "tr":
                pass
            elif tag == "p":
                self.parts.append("\n")

    def handle_data(self, data):
        if self.in_title:
            self.title += data
            return
        if self.in_script or self.in_nav or self.in_footer:
            return
        if self.in_main and data.strip():
            self.parts.append(data)

    def get_content(self):
        text = "".join(self.parts)
        # Clean up excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove permalink symbols
        text = re.sub(r"¶", "", text)
        return text.strip()

    def get_title(self):
        # Strip " — TECS ドキュメント" suffix
        t = self.title.strip()
        t = re.sub(r"\s*[—–-]\s*TECS\s*ドキュメント.*$", "", t)
        return t.strip()


def slugify(path: str) -> str:
    """Convert file path to a slug: dir__filename."""
    p = Path(path)
    parent = p.parent.name.replace("+", "-").replace(" ", "-").lower()
    stem = p.stem.lower().replace("+", "-").replace(" ", "-").replace("_", "-")
    return f"{parent}--{stem}"


def classify(html_path: str) -> str:
    return "article"


def ingest_file(html_path: Path) -> tuple[str, str]:
    """Parse HTML and return (slug, markdown_content)."""
    with open(html_path, encoding="utf-8", errors="replace") as f:
        raw = f.read()

    parser = TECSHTMLParser()
    parser.feed(raw)

    title = parser.get_title() or html_path.stem
    content = parser.get_content()
    slug = slugify(str(html_path))
    source_type = classify(str(html_path))

    md = f"""---
date: {TODAY}
source-type: {source_type}
source-url: {html_path}
title: {title}
compiled: false
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: {title[:100]}"
---

# {title}

{content}

---

Source: [[index]]
"""
    return slug, md, title


def main():
    base = Path("E:/Crepo/github-toppers/tecs-docs/docs/_build/html")
    dirs = [d for d in sorted(base.iterdir())
            if d.is_dir() and d.name[0].isalpha()]

    html_files = []
    for d in dirs:
        html_files.extend(sorted(d.glob("*.html")))

    print(f"Found {len(html_files)} HTML files")

    RAW_ARTICLES.mkdir(parents=True, exist_ok=True)
    log_entries = []
    saved = []

    for html_path in html_files:
        slug, md, title = ingest_file(html_path)
        out_name = f"{TODAY}-{slug}.md"
        out_path = RAW_ARTICLES / out_name

        if out_path.exists():
            print(f"  SKIP (exists): {out_name}")
            continue

        out_path.write_text(md, encoding="utf-8")
        print(f"  OK: {out_name}")

        log_entries.append(
            f"## [{TODAY}] ingest | {title}\n"
            f"Saved article from {html_path.name} to [[{TODAY}-{slug}]]."
        )
        saved.append(out_name)

    # Append to log.md
    if log_entries:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("\n" + "\n\n".join(log_entries) + "\n")
        print(f"\nAppended {len(log_entries)} entries to log.md")

    print(f"\nDone. {len(saved)} files saved.")


if __name__ == "__main__":
    main()
