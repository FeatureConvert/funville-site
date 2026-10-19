#!/usr/bin/env python3
"""Local checker for the Funville site (stdlib only). Usage: tools/check_site.py [site_dir]

Checks every *.html: title, description, viewport, canonical, og/twitter tags, icon,
relative links and #anchors resolve, <img> alt, no http:// or third-party hosts
(fonts, analytics, scripts, styles), mailto equals the contact constant, absolute
site URLs use the lowercase base, files under 100 MB (warns over 50). Exit 1 on any problem.
"""
import os, re, sys
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

CONTACT = "mailto:Nexrax@icloud.com"
BASE = "https://featureconvert.github.io/funville-site/"
# Links to other sites that are fine as plain <a href> (not loaded by the page).
ALLOWED_LINK_HOSTS = {"featureconvert.github.io", "www.cloudflare.com", "www.apple.com",
                      "reportaproblem.apple.com", "apps.apple.com"}
REQUIRED_META = [("name", "description"), ("name", "viewport"), ("property", "og:title"),
                 ("property", "og:description"), ("property", "og:image"), ("property", "og:url"),
                 ("property", "og:type"), ("name", "twitter:card")]

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.metas = []; s.links = []; s.ids = set(); s.hrefs = []; s.srcs = []
        s.imgs = []; s.title = False; s.title_text = ""; s.scripts = []; s.lang = None; s.css_text = ""
    def handle_starttag(s, t, a):
        a = dict(a)
        if "id" in a: s.ids.add(a["id"])
        if t == "html": s.lang = a.get("lang")
        if t == "title": s.title = True
        if t == "meta": s.metas.append(a)
        if t == "link": s.links.append(a)
        if t == "a" and "href" in a: s.hrefs.append(a["href"])
        if t == "img": s.imgs.append(a)
        if t in ("img", "video", "source", "script", "iframe") and "src" in a: s.srcs.append((t, a["src"]))
        if t == "video" and "poster" in a: s.srcs.append(("poster", a["poster"]))
        if t == "script": s.scripts.append(a)
    def handle_endtag(s, t):
        if t == "title": s.title = False
    def handle_data(s, d):
        if s.title: s.title_text += d

def main(root):
    root = os.path.abspath(root); errs = []
    def err(f, m): errs.append(f"{f}: {m}")
    pages = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in (".git", "tools")]
        for f in fn:
            path = os.path.join(dp, f)
            sz = os.path.getsize(path)
            if sz > 100 * 1024 * 1024: err(os.path.relpath(path, root), "file over 100 MB (GitHub limit)")
            elif sz > 50 * 1024 * 1024: print("WARN", os.path.relpath(path, root), "over 50 MB (GitHub warns)")
            if f.endswith(".html"):
                p = P(); p.feed(open(path, encoding="utf-8").read()); pages[os.path.relpath(path, root)] = p
    if not pages: err(root, "no html pages")
    for name, p in sorted(pages.items()):
        if not p.title_text.strip(): err(name, "missing <title>")
        if not p.lang: err(name, "missing html lang")
        for k, v in REQUIRED_META:
            m = [x for x in p.metas if x.get(k) == v and x.get("content", "").strip()]
            if not m: err(name, f"missing meta {v}")
        rels = {l.get("rel"): l for l in p.links}
        if "canonical" not in rels: err(name, "missing canonical")
        elif not rels["canonical"]["href"].startswith(BASE): err(name, "canonical not on lowercase base")
        if "icon" not in rels: err(name, "missing favicon link")
        if "apple-touch-icon" not in rels: err(name, "missing apple-touch-icon")
        for s in p.scripts:
            if "src" in s: err(name, "external script " + s["src"])
        for l in p.links:
            h = l.get("href", "")
            if urlparse(h).netloc and urlparse(h).netloc != "featureconvert.github.io" and l.get("rel") != "canonical":
                err(name, f"third-party <link> {h}")
        for i in p.imgs:
            if "alt" not in i: err(name, f"<img> without alt: {i.get('src')}")
        for t, s in p.srcs:
            if s.startswith("http://") or (urlparse(s).netloc and urlparse(s).netloc != "featureconvert.github.io"):
                err(name, f"third-party or insecure {t} {s}")
        for m in p.metas:
            c = m.get("content", "")
            if m.get("property") in ("og:image", "og:url") or m.get("name") == "twitter:image":
                if not c.startswith(BASE): err(name, f"{m.get('property') or m.get('name')} not an absolute lowercase URL")
        refs = [("href", h) for h in p.hrefs] + [("href", l["href"]) for l in p.links if "href" in l] + [("src", s) for _, s in p.srcs]
        for _, h in refs:
            if h.startswith("mailto:"):
                if h != CONTACT: err(name, f"mailto {h} is not the contact")
                continue
            if h.startswith("http://"): err(name, f"http:// link {h}"); continue
            u = urlparse(h)
            if u.netloc:
                if u.netloc not in ALLOWED_LINK_HOSTS: err(name, f"link to unlisted host {u.netloc}")
                if "funville-site" in h.lower() and not h.startswith(BASE): err(name, f"wrong-case site URL {h}")
                if h.startswith(BASE) and u.path != "/funville-site/":
                    tgt = os.path.join(root, unquote(u.path[len("/funville-site/"):]))
                    if not os.path.exists(tgt): err(name, f"absolute site link does not resolve: {h}")
                continue
            if u.scheme: err(name, f"unknown scheme {h}"); continue
            tp = name if not u.path else os.path.normpath(os.path.join(os.path.dirname(name), unquote(u.path)))
            if not os.path.exists(os.path.join(root, tp)): err(name, f"broken link {h}"); continue
            if u.fragment and tp in pages and u.fragment not in pages[tp].ids: err(name, f"missing anchor {h}")
    css = os.path.join(root, "site.css")
    if os.path.exists(css):
        c = open(css).read()
        if re.search(r"url\(\s*['\"]?https?:|@import", c): err("site.css", "remote url/@import")
        for u in re.findall(r"url\(['\"]?([^)'\"]+)", c):
            if not os.path.exists(os.path.join(root, u)): err("site.css", f"missing file {u}")
    for e in errs: print("FAIL", e)
    print(f"{len(pages)} pages checked, {len(errs)} problems")
    return 1 if errs else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
