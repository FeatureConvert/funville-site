# Funville website

The website for Funville: Idle Adventure Park, served by GitHub Pages from `main` at
https://featureconvert.github.io/funville-site/. Keep the repo name lowercase: App Store Connect and the game link
these addresses.

Plain HTML pages, one stylesheet (`site.css`) and one tiny script (`site.js`, the phone menu button). No build step,
no frameworks, no outside fonts, scripts, trackers or cookies. The fonts are the game's own, in `fonts/`
(SIL Open Font License, text in `fonts/OFL.txt`).

## Pages

| Page | What it has |
|---|---|
| `index.html` | Home: the splash-style wordmark, key art, screenshots, what you do, the towns, "No ads, ever." |
| `game.html` | How it plays, tapping the park, putting, park life, towns, critters and collections, the Weekly Cup and events |
| `attractions.html` | The nine holes, Glow Putt's nine Glow Holes and all twenty-six blocks with their rides |
| `updates.html` | News: what's coming in 1.1 |
| `faq.html` | Questions and answers, from the in-game Help |
| `about.html` | The developer, how it was made, credits |
| `media.html` | Trailer and screenshots |
| `support.html`, `press.html` | Support and the press kit (linked from App Store Connect and the game) |
| `privacy.html`, `rules.html` | Privacy policy and park-name rules. Legal text: change the words only on purpose |
| `404.html` | GitHub Pages shows it for a missing address |

Never rename or remove `index.html`, `privacy.html`, `support.html`, `rules.html`, `press.html` or anything in
`press/` and `img/` that a page or the press kit links: outside links depend on them.

The pages share the same header and footer. When you change one, change it on every page.

## The App Store link

Funville is live (1.0, October 2026): https://apps.apple.com/app/funville-idle-adventure-park/id6816280683. The home page
links it twice (the hero and "Get Funville", a `store-soon`-styled "Download on the App Store" button), every footer
links it, and the press kit's fact sheet lists it. Apple's official badge is not in the repo yet (it has to be downloaded
from Apple's marketing site, with Robert's OK): save it as `img/app-store-badge.svg` and swap it into the two home-page
buttons.

## Check before pushing

```sh
python3 tools/check_links.py      # every local link, image and #anchor resolves; banned words; ends "LINKS OK"
python3 -m http.server 8000       # then open http://localhost:8000/
```

## Moving to a domain

The domain is **playfunville.com** (Robert, 2026-10-26): the `CNAME` file, the absolute addresses (step 4) and the
404 page's root links (step 6) are done on the branch that adds `CNAME`. Push it only after the domain's DNS records
resolve, or the old github.io links (App Store Connect, the game) would redirect to a domain that does not answer yet.

All links are relative, so the site works at any address.

1. Buy the domain, and in its DNS add the records GitHub lists under "Managing a custom domain for your GitHub
   Pages site" (four `A` records for the bare domain, or a `CNAME` record pointing `www` at `featureconvert.github.io`).
2. Add a file named `CNAME` at the repo root holding just the domain (for example `funville.example`), commit and push.
   (Or set it in the repo's Settings, Pages, Custom domain, which makes the same file.)
3. In Settings, Pages, tick "Enforce HTTPS" once the certificate is ready.
4. Update the few absolute addresses, which have to be absolute: the `og:url`, `og:image` and `twitter:image` tags
   at the top of every page (search for `featureconvert.github.io`), and the Website line in `press.html`.
5. Update the links in App Store Connect (privacy policy, support and marketing URLs) and in the game. The old
   github.io addresses redirect to the domain for as long as the `CNAME` file stays.
6. `404.html` uses relative links like every page, so it is fully styled for a missing page at the top level
   (for example `/oldpage.html`). On the domain you may change its links to start with `/` so it is styled at any depth.
