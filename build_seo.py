#!/usr/bin/env python3
"""SEO static-site builder for ElectricTechs (GitHub Pages).
Reads articles.json and generates crawlable article pages + hub + sitemap.
Reusable for daily posts: add entry to articles.json, re-run, commit, push.
"""
import json, os, re, html
from datetime import datetime

BASE = "https://electricami055-web.github.io"
ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_NAME = "ElectricTechs"
SOCIAL_BAR = '<script src="https://pl29415251.profitablecpmratenetwork.com/bc/c9/c1/bcc9c1f2044fb1a300b55a62c069a50e.js"></script>'

SLUGS = {
    "E000": "building-diy-rc-car-transmitter-receiver-from-scratch",
    "E001": "house-wiring-101-complete-beginners-guide",
    "E002": "top-electrical-mistakes-to-avoid-at-home",
    "E003": "must-have-electrical-tools-for-diyer",
    "E004": "smart-home-wiring-plan-before-you-pull",
    "E005": "diy-led-strip-lighting-under-cabinets",
    "E006": "how-to-use-a-multimeter-without-frying-it",
}

CSS = """
:root{--bg:#0b0f14;--card:#121924;--txt:#e8edf3;--mut:#9aa7b8;--acc:#fbbf24;--line:#1f2a3a}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font-family:Inter,system-ui,-apple-system,sans-serif;line-height:1.75}
.wrap{max-width:760px;margin:0 auto;padding:0 20px}
header.site{border-bottom:1px solid var(--line);padding:14px 0;margin-bottom:28px}
header.site .wrap{display:flex;align-items:center;justify-content:space-between}
.logo{font-weight:800;font-size:20px;color:var(--txt);text-decoration:none}
.logo span{color:var(--acc)}
nav a{color:var(--mut);text-decoration:none;margin-left:18px;font-size:14px}
nav a:hover{color:var(--acc)}
.crumb{font-size:13px;color:var(--mut);margin-bottom:14px}
.crumb a{color:var(--mut);text-decoration:none}.crumb a:hover{color:var(--acc)}
.cat{display:inline-block;background:#1a2433;color:var(--acc);font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:4px 12px;border-radius:20px;margin-bottom:12px}
h1{font-size:clamp(26px,5vw,38px);line-height:1.25;font-weight:800;margin-bottom:10px}
.meta{color:var(--mut);font-size:14px;margin-bottom:20px}
.hero{width:100%;border-radius:12px;margin:6px 0 26px}
.lede{font-size:18px;color:#cdd6e2;border-left:3px solid var(--acc);padding-left:16px;margin-bottom:26px}
h2{font-size:23px;margin:34px 0 12px;font-weight:700}
p{margin-bottom:16px;color:#d5dce6}
ul,ol{margin:0 0 18px 22px;color:#d5dce6}li{margin-bottom:8px}
.disclaimer{background:#171208;border:1px solid #5a4413;border-radius:10px;padding:14px 18px;font-size:14px;color:#e8cf8f;margin:30px 0}
.author{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin:34px 0;display:flex;gap:14px;align-items:center}
.author .av{width:48px;height:48px;border-radius:50%;background:var(--acc);color:#111;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:20px}
.pn{display:flex;justify-content:space-between;gap:12px;margin:30px 0;flex-wrap:wrap}
.pn a{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 16px;color:var(--txt);text-decoration:none;font-size:14px;flex:1;min-width:200px}
.pn a:hover{border-color:var(--acc)}.pn small{display:block;color:var(--mut);font-size:12px}
.cards{display:grid;gap:16px;margin:20px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;text-decoration:none;color:var(--txt);display:block}
.card:hover{border-color:var(--acc)}.card img{width:100%;height:180px;object-fit:cover}
.card .b{padding:16px}.card h3{font-size:18px;margin:6px 0}.card p{font-size:14px;color:var(--mut);margin:0}
footer.site{border-top:1px solid var(--line);margin-top:44px;padding:26px 0 60px;color:var(--mut);font-size:14px}
footer.site a{color:var(--mut);text-decoration:none;margin-right:16px}footer.site a:hover{color:var(--acc)}
"""

def esc(t): return html.escape(t or "")
def paras(text):
    parts = [p.strip() for p in re.split(r'\n\s*\n', text.strip()) if p.strip()]
    return "\n".join(f"<p>{esc(p)}</p>" for p in parts)

def parse_date(d):
    try: return datetime.strptime(d, "%b %d, %Y").strftime("%Y-%m-%d")
    except Exception: return "2026-01-01"

def page_shell(title, desc, url, body_html, schema=None, og_image=None):
    og = f'\n<meta property="og:image" content="{og_image}"/>' if og_image else ""
    sch = f'\n<script type="application/ld+json">{json.dumps(schema)}</script>' if schema else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}"/>
<link rel="canonical" href="{url}"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="{esc(title)}"/>
<meta property="og:description" content="{esc(desc)}"/>
<meta property="og:url" content="{url}"/>{og}
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{esc(title)}"/>
<meta name="twitter:description" content="{esc(desc)}"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet"/>
<style>{CSS}</style>{sch}
</head>
<body>
<header class="site"><div class="wrap">
<a class="logo" href="{BASE}/">&#9889; <span>Electric</span>Techs</a>
<nav><a href="{BASE}/">Home</a><a href="{BASE}/articles/">Articles</a><a href="{BASE}/about/">About</a></nav>
</div></header>
<div class="wrap">
{body_html}
</div>
<footer class="site"><div class="wrap">
<a href="{BASE}/about/">About</a><a href="{BASE}/contact/">Contact</a><a href="{BASE}/privacy-policy/">Privacy Policy</a><a href="{BASE}/articles/">All Articles</a>
<p style="margin-top:12px">&copy; 2026 ElectricTechs. As an Amazon Associate we earn from qualifying purchases.</p>
</div></footer>
{SOCIAL_BAR}
</body>
</html>"""

def article_page(a, prev_a, next_a):
    slug = SLUGS[a["id"]]
    url = f"{BASE}/articles/{slug}/"
    img = a["image"] if a["image"].startswith("http") else f"{BASE}/assets/{a['image']}"
    desc = (a["subtitle"] or a["introduction"])[:155]
    d_iso = parse_date(a["date"])
    body = f"""<div class="crumb"><a href="{BASE}/">Home</a> &rsaquo; <a href="{BASE}/articles/">Articles</a> &rsaquo; {esc(a['category'])}</div>
<div class="cat">{esc(a['category'])}</div>
<h1>{esc(a['title'])}</h1>
<div class="meta">{esc(a['date'])} &middot; {esc(a['readTime'])} read &middot; By ElectricTechs Team</div>
<img class="hero" src="{img}" alt="{esc(a['title'])}" loading="eager"/>
<div class="lede">{esc(a['introduction'])}</div>
"""
    for s in a["sections"]:
        if s["heading"]:
            body += f"<h2>{esc(s['heading'])}</h2>\n"
        body += paras(s["body"]) + "\n"
    body += """<div class="disclaimer">&#9888;&#65039; <strong>Safety first:</strong> Electrical work can be dangerous. Always turn off power at the breaker, verify with a tester, and follow local codes. When in doubt, call a licensed electrician.</div>"""
    body += """<div class="author"><div class="av">E</div><div><strong>ElectricTechs Team</strong><br/><span style="color:#9aa7b8;font-size:14px">Hands-on electricians sharing practical, real-world tips.</span></div></div>"""
    body += '<div class="pn">'
    body += f'<a href="{BASE}/articles/{SLUGS[prev_a["id"]]}/"><small>&larr; Previous</small>{esc(prev_a["title"])}</a>' if prev_a else '<span></span>'
    body += f'<a href="{BASE}/articles/{SLUGS[next_a["id"]]}/" style="text-align:right"><small>Next &rarr;</small>{esc(next_a["title"])}</a>' if next_a else ''
    body += '</div>'
    schema = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": a["title"], "description": desc, "image": img,
        "datePublished": d_iso, "dateModified": d_iso,
        "author": {"@type": "Organization", "name": "ElectricTechs", "url": BASE},
        "publisher": {"@type": "Organization", "name": "ElectricTechs", "url": BASE},
        "mainEntityOfPage": url,
    }
    return page_shell(f"{a['title']} | ElectricTechs", desc, url, body, schema, img)

def hub_page(arts):
    cards = ""
    for a in arts:
        slug = SLUGS[a["id"]]
        img = a["image"] if a["image"].startswith("http") else f"{BASE}/assets/{a['image']}"
        cards += f"""<a class="card" href="{BASE}/articles/{slug}/"><img src="{img}" alt="{esc(a['title'])}" loading="lazy"/><div class="b"><div class="cat">{esc(a['category'])}</div><h3>{esc(a['title'])}</h3><p>{esc((a['subtitle'] or '')[:120])}</p></div></a>\n"""
    body = f"""<div class="crumb"><a href="{BASE}/">Home</a> &rsaquo; Articles</div>
<h1>All Articles</h1>
<p style="color:#9aa7b8">Wiring guides, DIY electronics, tool reviews and safety tips &mdash; explained simply.</p>
<div class="cards">{cards}</div>"""
    schema = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "ElectricTechs Articles", "url": f"{BASE}/articles/"}
    return page_shell("All Articles | ElectricTechs", "Browse all ElectricTechs guides: wiring, DIY electronics, tools, safety tips and smart home tech.", f"{BASE}/articles/", body, schema)

def simple_page(title, desc, url, h1, paragraphs):
    body = f"<h1>{esc(h1)}</h1>\n" + "\n".join(f"<p>{esc(p)}</p>" for p in paragraphs)
    return page_shell(title, desc, url, body)

def main():
    arts = json.load(open(os.path.join(ROOT, "articles.json")))
    # 1. article pages
    for idx, a in enumerate(arts):
        slug = SLUGS[a["id"]]
        d = os.path.join(ROOT, "articles", slug)
        os.makedirs(d, exist_ok=True)
        prev_a = arts[idx - 1] if idx > 0 else None
        next_a = arts[idx + 1] if idx < len(arts) - 1 else None
        open(os.path.join(d, "index.html"), "w").write(article_page(a, prev_a, next_a))
    # 2. hub
    os.makedirs(os.path.join(ROOT, "articles"), exist_ok=True)
    open(os.path.join(ROOT, "articles", "index.html"), "w").write(hub_page(arts))
    # 3. trust pages
    trust = {
        "about": ("About | ElectricTechs", "About ElectricTechs — hands-on electricians sharing practical DIY electrical guides.", "About ElectricTechs",
                  ["ElectricTechs is run by hands-on electricians and DIY electronics makers.",
                   "We publish practical guides on house wiring, electrical tools, DIY projects, safety and smart home tech — explained simply, so beginners can learn without getting overwhelmed.",
                   "Every guide focuses on real-world practice and safety. If a project is beyond your skill level, we always recommend calling a licensed electrician.",
                   "Follow our work on TikTok @electrictech09 and Instagram @electrictechsusa for daily short tips from the workbench."]),
        "contact": ("Contact | ElectricTechs", "Contact the ElectricTechs team.", "Contact Us",
                    ["Have a question about a guide, a topic suggestion, or a business inquiry?",
                     "Reach us on Instagram @electrictechsusa or TikTok @electrictech09 — we read every message.",
                     "We aim to reply within a few days."]),
        "privacy-policy": ("Privacy Policy | ElectricTechs", "Privacy Policy for ElectricTechs.", "Privacy Policy",
                    ["Last updated: September 2026.",
                     "ElectricTechs does not collect personal information directly. We use third-party advertising partners (such as Adsterra) that may use cookies to serve ads based on your visits to this and other sites.",
                     "You can disable cookies in your browser settings. Third-party vendors use cookies to serve ads; you may opt out of personalized advertising via your browser or device settings.",
                     "This site contains affiliate links (including Amazon). As an Amazon Associate we earn from qualifying purchases, at no extra cost to you.",
                     "If you have questions about this policy, contact us via the Contact page."]),
    }
    for slug, (t, dsc, h1, ps) in trust.items():
        dd = os.path.join(ROOT, slug)
        os.makedirs(dd, exist_ok=True)
        open(os.path.join(dd, "index.html"), "w").write(simple_page(t, dsc, f"{BASE}/{slug}/", h1, ps))
    # 4. sitemap
    urls = [("", "2026-09-29"), ("articles/", "2026-09-29"), ("about/", "2026-09-29"),
            ("contact/", "2026-09-29"), ("privacy-policy/", "2026-09-29")]
    for a in arts:
        urls.append((f"articles/{SLUGS[a['id']]}/", parse_date(a["date"])))
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for path, lm in urls:
        sm += f"  <url><loc>{BASE}/{path}</loc><lastmod>{lm}</lastmod><changefreq>weekly</changefreq></url>\n"
    sm += "</urlset>\n"
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(sm)
    # 5. robots.txt
    open(os.path.join(ROOT, "robots.txt"), "w").write(
        "User-agent: *\nAllow: /\n\nSitemap: https://electricami055-web.github.io/sitemap.xml\n")
    # 6. remove popunder from index.html (keep social bar)
    idx = os.path.join(ROOT, "index.html")
    h = open(idx).read()
    h2 = re.sub(r'\s*<!-- Adsterra Popunder Script -->\s*<script src="https://pl29415249\.profitablecpmratenetwork\.com/[^"]+"></script>', '', h)
    if h2 != h:
        open(idx, "w").write(h2)
        print("popunder removed from index.html")
    else:
        print("popunder pattern NOT found (check manually)")
    print(f"built {len(arts)} articles + hub + trust pages + sitemap")

if __name__ == "__main__":
    main()
