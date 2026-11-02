#!/usr/bin/env python3
"""
Build the website from the YAML data files and HTML templates.

    python3 tools/build.py

Reads   _data/site.yaml, _data/publications.yaml, _data/seminar.yaml
        _templates/*.html
Writes  index.html, research.html, publications.html, seminar.html, 404.html
        (in the repository root, where GitHub Pages serves them)

Requirements: Python 3.8+ with jinja2 and pyyaml
    pip install jinja2 pyyaml
"""
import datetime as dt
import hashlib
import html
import re
import sys
from pathlib import Path

try:
    import yaml
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    sys.exit("Missing packages. Run:  pip install jinja2 pyyaml")

ROOT = Path(__file__).resolve().parent.parent
ME = "T. M. Surowiec"          # bolded in author lists
PAGES = ["index.html", "research.html", "publications.html", "seminar.html", "404.html"]


def fingerprint(path):
    """Short hash of a file's contents, used as ?v=... so browsers fetch changed CSS/JS."""
    return hashlib.sha1((ROOT / path).read_bytes()).hexdigest()[:10]


def load(name):
    with open(ROOT / "_data" / name, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def prepare_pub(p):
    """Add derived fields used by the templates and check the entry."""
    for key in ("title", "authors", "year", "kind"):
        if key not in p:
            sys.exit(f"publications.yaml: entry is missing '{key}': {p}")
    for opt in ("venue", "details", "note", "award"):
        p.setdefault(opt, "")
    p.setdefault("topics", [])
    p.setdefault("links", {})
    p["authors_html"] = html.escape(p["authors"]).replace(ME, f"<strong>{ME}</strong>")

    links = []
    L = p["links"] or {}
    if L.get("doi"):
        links.append({"label": "DOI", "href": "https://doi.org/" + L["doi"], "external": True})
    if L.get("url"):
        links.append({"label": "Publisher", "href": L["url"], "external": True})
    if L.get("arxiv"):
        links.append({"label": "arXiv", "href": "https://arxiv.org/abs/" + str(L["arxiv"]), "external": True})
    if L.get("pdf"):
        links.append({"label": "PDF", "href": L["pdf"], "external": L["pdf"].startswith("http")})
    if L.get("code"):
        links.append({"label": "Code", "href": L["code"], "external": True})
    p["link_list"] = links
    p["keys"] = {str(L.get("doi", "")), str(L.get("arxiv", ""))} - {""}
    return p


def main():
    site = load("site.yaml")
    pubs = [prepare_pub(p) for p in load("publications.yaml")]
    talks = load("seminar.yaml")

    # --- publications: preprints first, then by year (newest first) ---
    order = {"preprint": 0}
    pubs.sort(key=lambda p: (order.get(p["kind"], 1), -int(p["year"])))
    groups = []
    for p in pubs:
        label = "Preprints" if p["kind"] == "preprint" else str(p["year"])
        if not groups or groups[-1][0] != label:
            groups.append((label, []))
        groups[-1][1].append(p)

    published = [p for p in pubs if p["kind"] != "preprint"]
    recent = [p for p in published if p["topics"] != ["interdisciplinary"]][:5]
    by_key = {k: p for p in pubs for k in p["keys"]}

    # --- research themes: resolve paper keys to entries ---
    for t in site["themes"]:
        resolved = []
        for k in t.get("papers", []):
            if str(k) not in by_key:
                sys.exit(f"site.yaml: theme '{t['id']}' lists unknown paper '{k}' (use a DOI or arXiv ID)")
            resolved.append(by_key[str(k)])
        t["papers"] = resolved

    # --- seminar: newest first, grouped by year ---
    for t in talks:
        d = dt.datetime.strptime(t["date"], "%B %d, %Y")
        t["_date"], t["short_date"] = d, f"{d.day} {d:%B}"
    talks.sort(key=lambda t: t["_date"], reverse=True)
    talk_groups = []
    for t in talks:
        y = t["_date"].year
        if not talk_groups or talk_groups[-1][0] != y:
            talk_groups.append((y, []))
        talk_groups[-1][1].append(t)

    today = dt.date.today()
    env = Environment(loader=FileSystemLoader(ROOT / "_templates"), autoescape=True,
                      trim_blocks=True, lstrip_blocks=True)
    ctx = dict(site=site, themes=site["themes"], topics=site["topics"], groups=groups,
               recent=recent, talks=talks, talk_groups=talk_groups,
               n_journal=len(published), year=today.year,
               updated=today.strftime("%B %Y"),
               css_v=fingerprint("assets/css/style.css"), js_v=fingerprint("assets/js/site.js"))

    for page in PAGES:
        out = env.get_template(page).render(page_file=page, **ctx)
        out = re.sub(r"\n\s*\n+", "\n", out)          # tidy blank lines
        (ROOT / page).write_text(out, encoding="utf-8")
        print(f"wrote {page}")


if __name__ == "__main__":
    main()
