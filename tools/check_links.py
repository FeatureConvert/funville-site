#!/usr/bin/env python3
"""Checks the site before a push. Run from the repo root: python3 tools/check_links.py

1. Every local href, src, srcset and poster in every top-level .html file points at a file
   that exists, and every #anchor points at an id on that page.
2. Every page has a <title> and a <main id="main">.
3. Words the site must not use (house rules: no em dashes, never "kids"/"children" in our own
   words, no prices or percentages outside the press fact sheet, no Android, no awards).
   privacy.html and rules.html are legal text kept word for word, so they are only reported, not failed.

Prints "LINKS OK" and exits 0 when everything passes."""
import html.parser, pathlib, re, sys, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEGAL = {"privacy.html", "rules.html"}
WORDS = [("em dash", re.compile("—")), ("kids", re.compile(r"\bkids?\b", re.I)),
         ("children", re.compile(r"\bchildren\b", re.I)), ("percent", re.compile(r"%")),
         ("price", re.compile(r"\$\d")), ("Android", re.compile(r"Android")), ("award-winning", re.compile(r"award[- ]winning", re.I))]
PRICE_OK = {("press.html", "price")}   # the fact sheet's prices are the press kit's own facts


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.ids, self.text, self.title, self.main = [], set(), [], False, False
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "title":
            self.title = True
        if tag == "main" and a.get("id") == "main":
            self.main = True
        if tag in ("script", "style"):
            self._skip += 1
        for k in ("href", "src", "poster"):
            if a.get(k):
                self.refs.append(a[k])
        if a.get("srcset"):
            self.refs += [part.strip().split()[0] for part in a["srcset"].split(",") if part.strip()]
        if tag == "meta" and a.get("content"):
            self.text.append(a["content"])
        if a.get("alt"):
            self.text.append(a["alt"])

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.text.append(data)

    def handle_comment(self, data):
        pass


def parse(path):
    p = Page()
    p.feed(path.read_text(encoding="utf-8"))
    return p


def main():
    pages = sorted(ROOT.glob("*.html"))
    parsed = {p.name: parse(p) for p in pages}
    errors, notes, count = [], [], 0
    for name, p in parsed.items():
        if not p.title:
            errors.append(f"{name}: no <title>")
        if not p.main:
            errors.append(f'{name}: no <main id="main">')
        for ref in p.refs:
            u = urllib.parse.urlsplit(ref)
            if u.scheme in ("http", "https", "mailto", "tel", "data") or ref.startswith("//"):
                continue
            count += 1
            if ref.startswith("/"):
                errors.append(f"{name}: root-relative link {ref!r} (use a relative link)")
                continue
            target = name if not u.path else urllib.parse.unquote(u.path)
            tpath = (ROOT / target)
            if not tpath.is_file():
                errors.append(f"{name}: missing file {ref!r}")
                continue
            if u.fragment and target.endswith(".html"):
                tp = parsed.get(target) or parse(tpath)
                if u.fragment not in tp.ids:
                    errors.append(f"{name}: no id {u.fragment!r} in {target}")
        text = " ".join(p.text)
        for label, rx in WORDS:
            hits = rx.findall(text)
            if not hits:
                continue
            msg = f"{name}: {label} x{len(hits)}"
            if name in LEGAL or (name, label) in PRICE_OK:
                notes.append(msg + " (allowed: kept word for word)")
            else:
                errors.append(msg)
    for n in notes:
        print("note:", n)
    for e in errors:
        print("FAIL:", e)
    print(f"{len(pages)} pages, {count} local links checked")
    if errors:
        sys.exit(1)
    print("LINKS OK")


if __name__ == "__main__":
    main()
