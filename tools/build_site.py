"""Build the H2O Engineering Group website from tools/content.json.

content.json holds the text, links and image order extracted (verbatim) from the original
Google Site; tools/google_site_backup/ keeps the original HTML. Images are in assets/img/.

Usage (from the repository root):  python tools/build_site.py
Regenerating overwrites manual edits made to the HTML pages.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = json.loads((ROOT / "tools" / "content.json").read_text(encoding="utf-8"))
# spelling and grammar corrections to the old Google Site text (Nov 2026)
TYPO_FIXES = [
    ("We am actively engaged", "We are actively engaged"),
    ("Analytical modelling is something we very enthusiastic about and its application.",
     "We are also very enthusiastic about analytical modelling and its applications."),
    ("projects we have been working or previouly worked on", "projects we are working on or have previously worked on"),
    ("navigate to project specific webpage", "navigate to the project-specific webpages"),
    ("Grat Barrier Reef", "Great Barrier Reef"),
    ("is a widely research topic", "is a widely researched topic"),
    ("the knowledge on erosion", "knowledge of erosion"),
    ("renewable energies have been alternate solutions for energy production",
     "renewable energy has become an alternative solution for energy production"),
    ("these experiments were focused to measure", "these experiments focused on measuring"),
    ("one of the reasons of sedimentation", "one of the causes of sedimentation"),
    ("However, all the previous research focused", "However, previous research has focused"),
    ("Tsunami propagation and inundation is a serious problem for communities built-up",
     "Tsunami propagation and inundation are serious problems for communities built"),
    ("I studies variation", "I studied the variation"),
    ("these phenomenon", "these phenomena"),
    ("To this, runup and overtopping are the two important parameters characterized, to estimate",
     "To this end, runup and overtopping are the two important parameters characterized to estimate"),
    ("retained for longer years", "retained for longer"),
    ("for most part of my schooling", "for most of my schooling"),
    ("my Bachelors in", "my Bachelor's in"),
    ("a Masters degree", "a Master's degree"),
    ("January, 2018", "January 2018"), ("July, 2018", "July 2018"), ("November, 2019", "November 2019"),
    ("September, 2016", "September 2016"), ("May, 2017", "May 2017"),
    ("his PhD.\xa0 He", "his PhD. He"),
    ("As a researcher, we believe engaging with internal, external collaborators and communicating science is a crucial aspect to achieve",
     "As researchers, we believe that engaging with internal and external collaborators and communicating science are crucial to achieving"),
    ("we participate in delivering guest lectures, organizing workshops for early career researchers and conference activities",
     "we deliver guest lectures, organize workshops for early career researchers and take part in conference activities"),
    ('Last week, Faculty members and students from the<a href="https://www.linkedin.com/company/ocean-engineering-iit-bombay/"> Ocean Engineering IIT Bombay</a>, participated',
     'Last week, faculty members and students from<a href="https://www.linkedin.com/company/ocean-engineering-iit-bombay/"> Ocean Engineering, IIT Bombay</a> participated'),
    ("established its chapter, and showcased", "established its chapter and showcased"),
    ("opportunities for collaboration further to strengthen", "opportunities for collaboration to further strengthen"),
    ("present it in our class soon on their findings", "present their findings in our class soon"),
    ("scientisits", "scientists"),
    ("entusiastic", "enthusiastic"),
    ("came forward in organizing", "came forward to organize"),
    ("His career journey ranging from developing the buoyant jet model to training scientists, contributing to CRZ clearances has",
     "His career journey, ranging from developing the buoyant jet model to training scientists and contributing to CRZ clearances, has"),
    ('<a href="https://www.linkedin.com/company/ocean-engineering-iit-bombay/">Ocean Engineering IIT Bombay</a> group at IIT Bombay was invited to attend Maharastra Maritime Summit',
     'The <a href="https://www.linkedin.com/company/ocean-engineering-iit-bombay/">Ocean Engineering</a> group at IIT Bombay was invited to attend the Maharashtra Maritime Summit'),
    ("V K Srineash</a> and myself are keen", "V K Srineash</a> and I are keen"),
    ('will be hosted at<a href="https://www.linkedin.com/company/indian-institute-of-technology-bombay/"> Indian Institute of Technology, Bombay</a>',
     'will be hosted at the<a href="https://www.linkedin.com/company/indian-institute-of-technology-bombay/"> Indian Institute of Technology Bombay</a>.'),
    ("we had a chance to have interaction and detailed discussions", "we had the chance to interact and hold detailed discussions"),
    ("I invite all active researchers in this field for collaboration with us and help us in contributing to a great good for the nation and scientific community elsewhere.",
     "I invite all active researchers in this field to collaborate with us and help us contribute to the greater good of the nation and the wider scientific community."),
    ("I attended Advances in Water Resources", "I attended the Advances in Water Resources"),
    ("Fieldtrip with", "Field trip with"),
    ("UQ-India Flood resilience challenge", "UQ-India Flood Resilience Challenge"),
    ("Technology, Bombay", "Technology Bombay"),
    ("Technology, Madras", "Technology Madras"),
    ("nature based solutions", "nature-based solutions"),
]
_unused = []
for _old, _new in TYPO_FIXES:
    _hit = False
    for _page in CONTENT.values():
        for _b in (_page.get("blocks", []) if isinstance(_page, dict) else []):
            if "html" in _b and _old in _b["html"]:
                _b["html"] = _b["html"].replace(_old, _new)
                _hit = True
    if not _hit:
        _unused.append(_old)
if _unused:
    print("typo fixes not applied (text not found):", _unused)

# the group is called "H2O Engineering Group" (the old Google Site said "Lab")
for _b in CONTENT["home"]["blocks"]:
    if "html" in _b:
        _b["html"] = (_b["html"].replace("H2O Engineering Lab", "H2O Engineering Group")
                      .replace("Ocean Engineering Lab", "Ocean Engineering Group"))
IMG_DIR = ROOT / "assets" / "img"
SITE = "H2O Engineering Group"
FULL = "Hydro Hazards and Ocean Engineering Group"
PI_NAME = "Ananth Wuppukondur"

PAGES = [
    ("home", "index.html", "Home"),
    ("about-ananth", "about-ananth/index.html", "About Ananth"),
    ("about-ananth__bio", "about-ananth/bio/index.html", "Bio"),
    ("about-ananth__education", "about-ananth/education/index.html", "Education"),
    ("about-ananth__experience", "about-ananth/experience/index.html", "Experience"),
    ("current-members", "current-members/index.html", "Current Members"),
    ("research", "research/index.html", "Research"),
    ("research__research-overview", "research/research-overview/index.html", "Research overview"),
    ("research__great-barrier-reef-restoration", "research/great-barrier-reef-restoration/index.html", "Great Barrier Reef restoration"),
    ("research__tsunami-impacts-in-coastal-rivers", "research/tsunami-impacts-in-coastal-rivers/index.html", "Tsunami impacts in coastal rivers"),
    ("research__tsunami-runupovertopping", "research/tsunami-runupovertopping/index.html", "Tsunami runup/overtopping"),
    ("research__scour-around-bridge-piers", "research/scour-around-bridge-piers/index.html", "Scour around bridge piers"),
    ("research__scour-around-wave-energy-converter-device", "research/scour-around-wave-energy-converter-device/index.html", "Scour around wave energy converter device"),
    ("research__scour-around-artificial-reefs", "research/scour-around-artificial-reefs/index.html", "Scour around artificial reefs"),
    ("research__sediment-entry-control-into-intake-canals", "research/sediment-entry-control-into-intake-canals/index.html", "Sediment entry control into intake canals"),
    ("research__sediment-transport-at-river-confluences", "research/sediment-transport-at-river-confluences/index.html", "Sediment transport at river confluences"),
    ("research__miscellaneous", "research/miscellaneous/index.html", "Miscellaneous"),
    ("publications", "publications/index.html", "Publications"),
    ("projects", "projects/index.html", "Projects"),
    ("news-and-updates", "news-and-updates/index.html", "News and Updates"),
    ("contact", "contact/index.html", "Contact"),
]
PATH = {k: p for k, p, _ in PAGES}
LABEL = {k: l for k, _, l in PAGES}
PROJECTS = [k for k, _, _ in PAGES if k.startswith("research__") and k not in ("research__research-overview", "research__miscellaneous")]
NAV = [
    ("home", []),
    ("about-ananth", ["about-ananth__education", "about-ananth__experience"]),
    ("current-members", []),
    ("research", PROJECTS + ["research__miscellaneous"]),
    ("publications", []),
    ("projects", []),
    ("news-and-updates", []),
    ("contact", []),
]
EMAILS = ["a.wuppukondur@civil.iitb.ac.in", "a.wuppukondur@gmail.com"]
PHONE = "+91-22-2576-5323"
SOCIAL = [
    ("Twitter", "https://twitter.com/ananth_w", "x"),
    ("LinkedIn", "https://www.linkedin.com/in/awuppukondur/", "in"),
    ("ResearchGate", "https://www.researchgate.net/profile/Ananth-Wuppukondur-2", "rg"),
]
RECRUIT = "We are actively seeking to recruit interns, Masters/PhD students and Postdocs."

# ------------------------------------------------------------------ icons
ICONS = {
    "arrow": "M5 12h14M13 6l6 6-6 6",
    "left": "M15 6l-6 6 6 6",
    "right": "M9 6l6 6-6 6",
    "down": "M7 10l5 5 5-5",
    "cal": "M7 3v3M17 3v3M4 9h16M5 5h14a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z",
    "mail": "M4 6h16v12H4zM4 7l8 6 8-6",
    "phone": "M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2",
    "form": "M8 4h8M6 4h12a1 1 0 0 1 1 1v15a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1zM9 10h6M9 14h6M9 18h3",
    "menu": "M4 7h16M4 12h16M4 17h16",
    "tsunami": "M2 18c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5M3 13c1-5 5-8 10-8 3 0 5 1.5 5 4-2-1.5-5-1-6 1.5-.8 2 .5 3.5 2 3.5",
    "cyclone": "M12 12m-2 0a2 2 0 1 0 4 0a2 2 0 1 0-4 0M20 7c-2-3-6-4-9-3M4 17c2 3 6 4 9 3M7 4C4 6 3 10 4 13M17 20c3-2 4-6 3-9",
    "dam": "M3 20h18M5 20V8l4-3v15M9 9h3M9 13h5M9 17h7M14 20v-6M18 20v-4",
    "river": "M4 4c4 2 0 6 4 8s8-2 12 2M4 10c4 2 0 6 4 8s6-1 8 1",
    "leaf": "M5 19c0-8 5-14 15-14 0 10-6 15-14 15M5 19c3-4 6-7 10-9",
    "user": "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0",
    "cap": "M2 9l10-5 10 5-10 5zM6 11v5c3 2 9 2 12 0v-5M22 9v6",
    "brief": "M4 8h16v11H4zM9 8V5h6v3M4 13h16",
    "book": "M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2zM4 19V5M8 7h7",
    "flask": "M9 3h6M10 3v6L4 19a1 1 0 0 0 1 2h14a1 1 0 0 0 1-2l-6-10V3M7 15h10",
    "play": "M8 5v14l11-7z",
    "x": "M4 4l16 16M20 4L4 20",
    "in": "M6 9v9M6 6v.01M10 18v-5a3 3 0 0 1 6 0v5M10 9v9",
    "rg": "M7 18V6h5a3 3 0 0 1 0 6H7M12 12l5 6",
}


def icon(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{ICONS[name]}"/></svg>')


WAVES = ('<svg class="waves" viewBox="0 24 150 28" preserveAspectRatio="none" aria-hidden="true">'
         '<defs><path id="wv" d="M-160 44c30 0 58-18 88-18s58 18 88 18 58-18 88-18 58 18 88 18v44h-352z"/></defs>'
         '<g><use href="#wv" x="48" y="0"/><use href="#wv" x="48" y="3"/><use href="#wv" x="48" y="5"/>'
         '<use href="#wv" x="48" y="7"/></g></svg>')

# ------------------------------------------------------------------ image map
# Reproduces the order in which images were downloaded (assets/img/<page>-<n>.<ext>).
IMG = {}


def build_image_map():
    gcache = {}
    for key, path, _ in PAGES:
        slug = path.replace("/index.html", "").replace("index.html", "home").replace("/", "-")
        seen, n = set(), 0
        for i, b in enumerate(CONTENT[key]["blocks"]):
            if b["t"] not in ("img", "banner"):
                continue
            base = re.sub(r"=w\d+$", "", b["src"])
            if base in seen:
                continue
            seen.add(base)
            n += 1
            if base in gcache:
                IMG[(key, i)] = gcache[base]
                continue
            found = sorted(IMG_DIR.glob(f"{slug}-{n}.*"))
            if not found:
                raise SystemExit(f"missing image assets/img/{slug}-{n}.*")
            gcache[base] = IMG[(key, i)] = "assets/img/" + found[0].name


# ------------------------------------------------------------------ helpers
def esc(s):
    return html.escape(s, quote=True)


def plain(h):
    return html.unescape(re.sub(r"<[^>]+>", "", h)).strip()


def page_title(key):
    t = CONTENT[key]["title"].strip()
    return t.split(" - ", 1)[1].strip() if " - " in t else t


def fix(h, pre):
    """Clean Google Sites markup: relative internal links, external links in new tab."""
    def repl(m):
        href = html.unescape(m.group(1))
        s = re.match(r"/view/h2o-engineering-lab/?(.*)$", href)
        if s:
            key = s.group(1).strip("/").replace("/", "__") or "home"
            return f'<a href="{pre}{PATH.get(key, "index.html")}">'
        if href.startswith("http"):
            return f'<a href="{esc(href)}" target="_blank" rel="noopener">'
        return f'<a href="{esc(href)}">'
    h = re.sub(r'<a href="([^"]*)">', repl, h)
    h = h.replace("</strong><strong>", "")
    h = re.sub(r"^(\s|<strong>\s*</strong>)+", "", h)
    return h.strip()


def sections(key):
    out, cur = [], []
    for i, b in enumerate(CONTENT[key]["blocks"]):
        if b["t"] == "section":
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append((i, b))
    if cur:
        out.append(cur)
    return out


def banner(key):
    for i, b in enumerate(CONTENT[key]["blocks"]):
        if b["t"] == "banner":
            return IMG[(key, i)]
    return None


def images(key, items=None, carousel=False):
    items = items if items is not None else list(enumerate(CONTENT[key]["blocks"]))
    out = []
    for i, b in items:
        if b["t"] == "img" and (b.get("alt") == "Carousel image") == carousel and (key, i) in IMG:
            if IMG[(key, i)] not in out:
                out.append(IMG[(key, i)])
    return out


def is_bold_heading(b):
    h = b["html"].replace("</strong><strong>", "").strip()
    return bool(re.fullmatch(r"<strong>[^<]{1,80}</strong>", h))


def yt_id(src):
    m = re.search(r"youtube\.com/embed/([\w-]+)", src)
    return m.group(1) if m else None


def video(src, title):
    vid = yt_id(src)
    t = esc(re.sub(r"^YouTube Video,\s*", "", title or "Video"))
    return (f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{vid}" title="{t}" loading="lazy" '
            f'referrerpolicy="strict-origin-when-cross-origin" allow="accelerometer; encrypted-media; gyroscope; '
            f'picture-in-picture; fullscreen" allowfullscreen></iframe></div><p class="video-cap">{t}</p>')


def zoom(pre, src, alt, group, extra=""):
    return (f'<button type="button" data-lb="{group}" aria-label="Enlarge image"{extra}>'
            f'<img src="{pre}{src}" alt="{esc(alt)}" loading="lazy"></button>')


def date_text(s):
    m = re.fullmatch(r"(\d{2})/(?:(\d{2})/)?(\d{4})", s.strip())
    if not m:
        return None
    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    d, mo, y = m.group(1), m.group(2), m.group(3)
    if mo is None:  # MM/YYYY
        return f"{months[int(d) - 1]} {y}"
    return f"{int(d)} {months[int(mo) - 1]} {y}"


def reveal(i=0):
    return f' class="reveal" style="--d:{i * 0.08:.2f}s"'


# ------------------------------------------------------------------ data models
def project(key):
    blocks = list(enumerate(CONTENT[key]["blocks"]))
    heading, paras, links, vids, skip = None, [], [], [], set()
    for n, (i, b) in enumerate(blocks):
        if i in skip:
            continue
        t = b["t"]
        if t == "a":
            label = "Read more"
            if n + 1 < len(blocks) and blocks[n + 1][1]["t"] == "p":
                label = plain(blocks[n + 1][1]["html"])
                skip.add(blocks[n + 1][0])
            links.append((label, b["href"]))
        elif t == "iframe" and yt_id(b["src"]):
            vids.append((b["src"], b.get("title", "")))
        elif t in ("p", "h1", "h2"):
            if heading is None and (is_bold_heading(b) if t == "p" else len(plain(b["html"])) < 90):
                heading = plain(b["html"])
            else:
                paras.append(b["html"])
    return {"heading": heading or page_title(key), "paras": paras, "links": links,
            "images": images(key), "videos": vids}


def research_intro(key):
    texts = [b for _, b in enumerate(CONTENT[key]["blocks"]) if b["t"] == "p"]
    heading = plain(texts[0]["html"])
    return heading, texts[1]["html"], images(key)


def experience():
    entries, teach, photo, teach_img, mode = [], [], None, None, None
    for i, b in enumerate(CONTENT["about-ananth__experience"]["blocks"]):
        t = b["t"]
        if t == "h1":
            mode = "teach" if "Teaching" in plain(b["html"]) else "prof"
        elif t == "img":
            if mode == "teach":
                teach_img = IMG[("about-ananth__experience", i)]
            elif photo is None:
                photo = IMG[("about-ananth__experience", i)]
        elif t == "p" and mode == "prof":
            s = plain(b["html"])
            when, rest = s.split(":", 1)
            rest = rest.strip()
            role, _, org = rest.partition(", ")
            entries.append((when.strip(), role.strip(), org.strip()))
        elif t == "p" and mode == "teach":
            teach.append(b["html"])
    return entries, teach, photo, teach_img


def members():
    out = []
    for sec in sections("current-members"):
        name, paras, photo = None, [], None
        for i, b in sec:
            if b["t"] == "img" and photo is None:
                photo = IMG[("current-members", i)]
            elif b["t"] in ("h1", "h2") and name is None:
                name = plain(b["html"])
            elif b["t"] == "p":
                paras.append(b["html"])
        if name:
            text = plain(" ".join(paras))
            role = "Postdoctoral Fellow" if "Postdoctoral Fellow" in text else ("PhD Scholar" if "PhD" in text else "Member")
            out.append({"name": name, "paras": paras, "photo": photo, "role": role})
    return out + EXTRA_MEMBERS


# members added after the move from Google Sites
EXTRA_MEMBERS = [
    {"name": "Owais", "role": "PhD Scholar", "photo": "assets/img/member-owais.jpg", "paras": [
        "Owais is currently pursuing a PhD, following his M.Tech in Hydraulic Structures from Aligarh Muslim "
        "University and B.Tech in Civil Engineering from Jamia Millia Islamia. His research interests include "
        "coastal hydrodynamics, wave&ndash;surge interactions, compound flood modeling, and mangrove-based coastal "
        "resilience.",
        "He specializes in hydrological&ndash;hydraulic modeling (HEC-HMS, HEC-RAS), coupled coastal modeling "
        "(Delft3D&ndash;SWAN&ndash;XBeach), field-based wave and surge attenuation analysis, dam break and "
        "uncertainty analysis, and GIS-driven socioeconomic coastal risk mapping."]},
    {"name": "Ashok", "role": "M.Tech Student", "photo": "assets/img/member-ashok.jpg", "paras": [
        "Ashok is currently pursuing an M.Tech in Ocean Engineering at IIT Bombay and holds a Bachelor&rsquo;s "
        "degree in Petroleum Engineering. He has a strong interest in coastal and ocean engineering, particularly "
        "coastal processes, hydrodynamic modelling and numerical simulation.",
        "His current research focuses on coral reef morphology and on predicting cyclone-induced coral damage "
        "using coupled ADCIRC&ndash;SWAN modelling. He is passionate about computational modelling and simulation, "
        "and is keen to apply numerical methods to understand coastal dynamics and assess the impacts of extreme "
        "marine events."]},
]


def news():
    key = "news-and-updates"
    secs = sections(key)
    intro = [b["html"] for _, b in secs[0] if b["t"] == "p" and not is_bold_heading(b)]
    posts, carousel, pending = [], [], None
    for sec in secs[1:]:
        car = images(key, sec, carousel=True)
        if car:
            carousel = car
            continue
        imgs = images(key, sec)
        texts = [b for _, b in sec if b["t"] in ("p", "h1", "h2")]
        vids = [(b["src"], b.get("title", "")) for _, b in sec if b["t"] == "iframe" and yt_id(b["src"])]
        if texts and not imgs and not vids:
            if pending:
                posts.append({"texts": pending, "imgs": [], "vids": []})
            pending = texts
            continue
        if pending and not texts:
            texts, pending = pending, None
        elif pending:
            posts.append({"texts": pending, "imgs": [], "vids": []})
            pending = None
        posts.append({"texts": texts, "imgs": imgs, "vids": vids})
    if pending:
        posts.append({"texts": pending, "imgs": [], "vids": []})
    for p in posts:
        p["date"], p["title"], body = None, None, []
        for b in p["texts"]:
            s = plain(b["html"])
            d = date_text(s)
            if d:
                p["date"] = d
            elif p["title"] is None and not body and len(s) < 125:
                p["title"] = s
            else:
                body.append(b["html"])
        p["body"] = body
    return intro, carousel, posts


# ------------------------------------------------------------------ layout
def nav_html(active, pre):
    items, ac = [], ' aria-current="page"'
    for key, children in NAV:
        cur = active == key or active in children
        a = f'<a href="{pre}{PATH[key]}"{ac if active == key else ""}>{LABEL[key]}</a>'
        if children:
            sub = "".join(f'<li><a href="{pre}{PATH[c]}"{ac if active == c else ""}>{LABEL[c]}</a></li>' for c in children)
            items.append(f'<li class="has-sub{" current" if cur else ""}">{a}'
                         f'<button class="sub-toggle" aria-expanded="false" aria-label="Show {LABEL[key]} pages">{icon("down")}</button>'
                         f'<ul class="sub">{sub}</ul></li>')
        else:
            items.append(f'<li class="current">{a}</li>' if cur else f"<li>{a}</li>")
    return '<ul class="menu">' + "".join(items) + "</ul>"


def page_hero(key, pre, title, sub="", img=None, crumbs=None):
    img = img if img is not None else banner(key)
    bg = f'<div class="page-hero-bg" style="background-image:url(\'{pre}{img}\')"></div>' if img else ""
    cr = ""
    if crumbs:
        parts = [f'<a href="{pre}index.html">Home</a>']
        for k in crumbs:
            parts.append(f'<a href="{pre}{PATH[k]}">{LABEL[k]}</a>')
        cr = '<nav class="crumbs" aria-label="Breadcrumb">' + '<span aria-hidden="true">/</span>'.join(parts) + "</nav>"
    s = f'<p class="sub-title reveal" style="--d:.15s">{sub}</p>' if sub else ""
    return (f'<section class="page-hero{"" if img else " no-img"}">{bg}<div class="wrap">{cr}'
            f'<h1 class="reveal">{esc(title)}</h1>{s}</div>{WAVES}</section>')


def cta(pre):
    return f"""<section class="cta"><div class="wrap">
<div class="reveal"><span class="eyebrow">Join the group</span><h2>{RECRUIT}</h2>
<p>We welcome enquiries from potential students and collaborators for research opportunities.</p></div>
<div class="btn-row reveal" style="--d:.15s"><a class="btn btn-primary" href="{pre}{PATH['contact']}">Contact us {icon('arrow')}</a>
<a class="btn btn-ghost" href="mailto:{EMAILS[0]}">{icon('mail')} Email</a></div>
</div></section>"""


def redirect(key, pre, target):
    """Old Google-Site URL whose content duplicated another page: forward to that page."""
    url = pre + PATH[target]
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{esc(LABEL[target])} | {SITE}</title>
<meta http-equiv="refresh" content="0; url={url}"><link rel="canonical" href="{url}"></head>
<body><p>This page has moved: <a href="{url}">{esc(LABEL[target])}</a>.</p></body></html>
"""


def footer(pre, logo):
    soc = "".join(f'<a href="{u}" target="_blank" rel="noopener" aria-label="{n}">{icon(i)}</a>' for n, u, i in SOCIAL)
    return f"""<footer class="site-footer"><div class="wrap">
<div class="foot-grid">
<div><div class="foot-brand"><img src="{pre}{logo}" alt=""><b>{SITE}</b></div>
<p>{FULL}<br>Department of Civil Engineering<br>IIT Bombay, India</p></div>
<div><h4>Contact</h4><ul><li><a href="mailto:{EMAILS[0]}">{EMAILS[0]}</a></li><li><a href="mailto:{EMAILS[1]}">{EMAILS[1]}</a></li>
<li><a href="tel:{PHONE.replace('-', '')}">{PHONE}</a></li><li><a href="{pre}{PATH['contact']}">Contact form</a></li></ul>
<div class="socials">{soc}</div></div>
</div>
<div class="foot-bottom"><span>&copy; <span data-year>2026</span> {SITE}, IIT Bombay</span></div>
</div></footer>"""


def layout(key, pre, logo, body, desc=None, home=False):
    title = SITE + " | IIT Bombay" if home else f"{LABEL[key]} | {SITE}"
    desc = desc or f"{FULL} (H2O Group), Department of Civil Engineering, IIT Bombay."
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta name="theme-color" content="#061b2e">
<link rel="icon" href="{pre}{logo}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Sora:wght@500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{pre}assets/css/style.css">
<script>document.documentElement.classList.add('js')</script>
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<header class="site-header scrolled" data-solid><div class="wrap">
<a class="brand" href="{pre}index.html"><span class="brand-logo" aria-hidden="true">{animated_logo("hdr")}</span><span><b>{SITE}</b><small>IIT Bombay</small></span></a>
<nav id="site-nav" aria-label="Main">{nav_html(key, pre)}</nav>
<a class="btn btn-primary nav-cta" href="{pre}{PATH['contact']}">Contact us</a>
<button class="menu-toggle" aria-expanded="false" aria-controls="site-nav" aria-label="Menu">{icon('menu')}</button>
</div></header>
<main id="main">
{body}
</main>
{footer(pre, logo)}
<script src="{pre}assets/js/site.js"></script>
</body>
</html>
"""


# ------------------------------------------------------------------ pages
def proj_card(key, pre, n, wide=False):
    p = project(key)
    img = p["images"][0] if p["images"] else None
    im = f'<img src="{pre}{img}" alt="" loading="lazy">' if img else ""
    return (f'<a class="proj reveal{"" if img else " no-img"}" style="--d:{(n % 4) * 0.08:.2f}s" href="{pre}{PATH[key]}">{im}'
            f'<span class="body"><h3>{LABEL[key]}</h3>'
            f'<span class="go">{icon("arrow")}</span></span></a>')


def p_home(pre, logo):
    blocks = CONTENT["home"]["blocks"]
    ps = [b["html"] for b in blocks if b["t"] == "p"]
    welcome, intro, tagline = plain(ps[0]), ps[1], plain(ps[2])
    art = images("home")[0]
    bg = banner("home")
    m = re.match(r"(.*?)(H2O Engineering Group)\s*(@.*)?$", welcome)
    h1 = (f'{esc(m.group(1))}<span class="grad-text">{m.group(2)}</span>'
          f'<span class="at">{esc(m.group(3) or "")}</span>') if m else esc(welcome)
    import random
    rnd = random.Random(7)
    bubbles = "".join(
        f'<span style="left:{rnd.uniform(2, 98):.1f}%;width:{s}px;height:{s}px;animation-duration:{rnd.uniform(9, 18):.1f}s;'
        f'animation-delay:-{rnd.uniform(0, 18):.1f}s"></span>'
        for s in [rnd.choice([6, 8, 10, 14, 18, 24]) for _ in range(18)])
    hazards = [("tsunami", "tsunami"), ("cyclone (storm surge)", "cyclone"), ("dam-break", "dam"),
               ("riverine floods", "river"), ("nature-based solutions", "leaf")]
    hz = "".join(f'<div class="hazard reveal" style="--d:{i * 0.08:.2f}s"><span class="ico">{icon(ic)}</span><b>{esc(n)}</b></div>'
                 for i, (n, ic) in enumerate(hazards))
    cards = "".join(proj_card(k, pre, n) for n, k in enumerate(PROJECTS[:4]))
    # latest news
    news_intro, _, posts = news()
    # grammar corrected from the old site's text
    outreach_text = ("As researchers, we believe that engaging with internal and external collaborators and "
                     "communicating science are crucial to achieving the end goals of research application and "
                     "implementation. To this end, we deliver guest lectures, organize workshops for early career "
                     "researchers and take part in conference activities.")
    outreach = (f'<section class="section statement-sec"><div class="wrap"><div class="statement reveal">'
                f'<span class="eyebrow">Outreach</span><p>{esc(outreach_text)}</p></div></div></section>'
                if news_intro else "")
    nc = []
    for n, p in enumerate(posts[:3]):
        title = p["title"] or (plain(p["body"][0])[:130].rsplit(" ", 1)[0] + "…" if p["body"] else "")
        img = p["imgs"][0] if p["imgs"] else None
        date = f'<span class="date-badge">{icon("cal")}{p["date"]}</span>' if p["date"] else ""
        thumb = f'<div class="thumb"><img src="{pre}{img}" alt="" loading="lazy"></div>' if img else ""
        nc.append(f'<a class="news-card reveal" style="--d:{n * 0.1:.2f}s" href="{pre}{PATH["news-and-updates"]}#post-{n + 1}">'
                  f'{thumb}<div class="txt">{date}<h3>{esc(title)}</h3></div></a>')
    entries, _, _, _ = experience()
    pi_photo = images("about-ananth")[0]
    bio = max((b["html"] for b in CONTENT["about-ananth"]["blocks"] if b["t"] == "p"), key=lambda h: len(plain(h)))
    ov = [b["html"] for b in CONTENT["research__research-overview"]["blocks"] if b["t"] == "p"][1]
    ov_sentence = re.search(r"Our main research interest[^.]*\.", plain(ov)).group(0)
    body = f"""<section class="hero"><div class="hero-bg" style="background-image:url('{pre}{bg}')"></div>
<div class="bubbles" aria-hidden="true">{bubbles}</div>
<div class="wrap">
<span class="eyebrow reveal" style="--d:.05s">{FULL}</span>
<h1 class="reveal" style="--d:.1s">{h1}</h1>
<p class="lead reveal" style="--d:.2s">{esc(tagline)}</p>
<div class="btn-row reveal" style="--d:.3s"><a class="btn btn-primary" href="{pre}{PATH['research']}">Explore our research {icon('arrow')}</a>
<a class="btn btn-ghost" href="{pre}{PATH['current-members']}">Meet the team</a></div>
</div><span class="scroll-cue" aria-hidden="true"></span>{WAVES}</section>

<section class="section"><div class="wrap">
<div class="intro-grid">
<div class="reveal"><span class="eyebrow">Who we are</span><p class="lead">{intro}</p>
<a class="btn btn-line" href="{pre}{PATH['research']}">Our research {icon('arrow')}</a></div>
<div class="art-card logo-art reveal" style="--d:.15s" data-logo-anim title="Click to replay">
<img src="{pre}{logo}" alt="H2O — Hydro Hazards and Ocean Engineering Group logo">
<template>{animated_logo("home")}</template></div>
</div>
<div class="hazards">{hz}</div>
</div></section>

<section class="section dark" style="--wave-fill:#061b2e"><div class="wrap">
<div class="section-head"><div class="reveal"><span class="eyebrow">Research</span><h2>Fluid&ndash;sediment&ndash;structure dynamics</h2></div>
<p class="reveal" style="--d:.1s">{esc(ov_sentence)}</p></div>
<div class="bento">{cards}</div>
<div class="btn-row reveal" style="margin-top:28px"><a class="btn btn-primary" href="{pre}{PATH['research']}">All {len(PROJECTS)} projects {icon('arrow')}</a></div>
</div></section>
{outreach}

<section class="section tint"><div class="wrap">
<div class="section-head"><div class="reveal"><span class="eyebrow">News and Updates</span><h2>Latest from the group</h2></div>
<a class="btn btn-line reveal" href="{pre}{PATH['news-and-updates']}">All news {icon('arrow')}</a></div>
<div class="news-grid">{''.join(nc)}</div>
</div></section>

<section class="section"><div class="wrap pi">
<div class="portrait-wrap reveal"><div class="portrait"><img src="{pre}{pi_photo}" alt="{PI_NAME}" loading="lazy"></div></div>
<div class="reveal" style="--d:.15s"><span class="eyebrow">Group lead</span><h2>{PI_NAME}</h2>
<p class="role">{esc(entries[0][1])}, {esc(entries[0][2])}</p>
<p>{bio}</p>
<div class="btn-row"><a class="btn btn-primary" href="{pre}{PATH['about-ananth']}">About Ananth {icon('arrow')}</a>
<a class="btn btn-line" href="{pre}{PATH['about-ananth__experience']}">Experience</a></div></div>
</div></section>"""
    return layout("home", pre, logo, body, home=True)


def p_about(key, pre, logo):
    blocks = CONTENT[key]["blocks"]
    heading = next(plain(b["html"]) for b in blocks if b["t"] in ("h1", "h2"))
    bio = [b["html"] for b in blocks if b["t"] == "p" and len(plain(b["html"])) > 40]
    photo = images(key)[0]
    entries, _, _, _ = experience()
    ql = [("about-ananth__education", "cap"), ("about-ananth__experience", "brief")]
    quick = "".join(f'<a class="quick reveal" style="--d:{i * .08:.2f}s" href="{pre}{PATH[k]}"><span class="ico">{icon(ic)}</span><b>{LABEL[k]}</b></a>'
                    for i, (k, ic) in enumerate(ql) if k != key)
    body = page_hero(key, pre, LABEL[key], f"{esc(entries[0][1])}, {esc(entries[0][2])}",
                     crumbs=["about-ananth"] if key != "about-ananth" else None)
    body += f"""<section class="section"><div class="wrap profile">
<div class="portrait-wrap reveal"><div class="portrait"><img src="{pre}{photo}" alt="{PI_NAME}"></div></div>
<div class="reveal" style="--d:.12s"><span class="eyebrow">{PI_NAME}</span><h2>{esc(heading)}</h2>
{''.join(f'<p class="lead">{fix(p, pre)}</p>' for p in bio)}
<div class="quick-links" style="grid-template-columns:repeat({len(quick.split('class="quick ')) - 1},1fr)">{quick}</div></div>
</div></section>"""
    return layout(key, pre, logo, body)


def p_education(pre, logo):
    key = "about-ananth__education"
    blocks = CONTENT[key]["blocks"]
    # the CV sentence is dropped: the old site never linked a CV file
    texts = [b["html"] for b in blocks if b["t"] == "p" and not is_bold_heading(b) and "in my CV" not in plain(b["html"])]
    img = images(key)[0]
    # degrees as printed in the Education image of the old site
    degrees = [("2017 – 2021", "Doctor of Philosophy", "Specialization: Coastal and Hydraulic Engineering",
                "The University of Queensland, Australia", ""),
               ("2013 – 2016", "Master of Science", "Specialization: Hydraulic Engineering",
                "Indian Institute of Technology Madras", "GPA: 9/10"),
               ("2009 – 2013", "Bachelor of Technology", "Specialization: Civil Engineering",
                "Sri Venkateswara University, India", "GPA: 8.14/10")]
    tl = "".join(f'<li{reveal(i)}><span class="when">{w}</span><h3>{d}</h3><p>{s}<br><em>{u}</em>'
                 f'{"<br>" + g if g else ""}</p></li>' for i, (w, d, s, u, g) in enumerate(degrees))
    body = page_hero(key, pre, "Education", crumbs=["about-ananth"])
    body += f"""<section class="section"><div class="wrap split">
<div><span class="eyebrow reveal">{PI_NAME}</span><ol class="timeline">{tl}</ol>
{''.join(f'<p class="lead">{fix(t, pre)}</p>' for t in texts)}
<div class="btn-row"><a class="btn btn-primary" href="{pre}{PATH['about-ananth__experience']}">Experience {icon('arrow')}</a>
<a class="btn btn-line" href="{pre}{PATH['about-ananth']}">About Ananth</a></div></div>
<div class="media-frame reveal" style="--d:.12s"><button type="button" data-lb="edu" style="all:unset;cursor:zoom-in;display:block"><img src="{pre}{img}" alt="Education" loading="lazy"></button></div>
</div></section>"""
    return layout(key, pre, logo, body)


def p_experience(pre, logo):
    key = "about-ananth__experience"
    entries, teach, photo, teach_img = experience()
    tl = "".join(f'<li{reveal(i)}><span class="when">{esc(w)}</span><h3>{esc(r)}</h3><p>{esc(o)}</p></li>'
                 for i, (w, r, o) in enumerate(entries))
    body = page_hero(key, pre, "Experience", crumbs=["about-ananth"])
    body += f"""<section class="section"><div class="wrap split flip" style="align-items:start">
<div><span class="eyebrow reveal">Career</span><h2 class="reveal">Professional experience</h2><ol class="timeline">{tl}</ol></div>
<div class="portrait-wrap reveal" style="position:sticky;top:110px"><div class="portrait"><img src="{pre}{photo}" alt="{PI_NAME}"></div></div>
</div></section>
<section class="section tint"><div class="wrap split">
<div class="reveal"><span class="eyebrow">Teaching</span><h2>Teaching experience</h2>{''.join(f'<p class="lead">{fix(t, pre)}</p>' for t in teach)}</div>
<div class="media-frame reveal" style="--d:.12s"><img src="{pre}{teach_img}" alt="Laboratory demonstration" loading="lazy"></div>
</div></section>"""
    return layout(key, pre, logo, body)


def p_members(pre, logo):
    key = "current-members"
    rows = []
    for n, m in enumerate(members()):
        ph = (f'<div class="member-photo reveal"><img src="{pre}{m["photo"]}" alt="{esc(m["name"])}" loading="lazy"></div>' if m["photo"]
              else f'<div class="member-photo none reveal">{esc(m["name"][0])}</div>')
        rows.append(f'<article class="member">{ph}<div class="reveal" style="--d:.12s"><span class="badge">{m["role"]}</span>'
                    f'<h2>{esc(m["name"])}</h2>{"".join(f"<p>{fix(p, pre)}</p>" for p in m["paras"])}</div></article>')
    body = page_hero(key, pre, "Current Members", "The people behind the H2O Engineering Group.")
    # not every member has sent their details yet (Nov 2026)
    note = ('<p class="members-note reveal">More group members will be added here soon.</p>')
    body += f'<section class="section"><div class="wrap">{"".join(rows)}{note}</div></section>'
    return layout(key, pre, logo, body)


THEMES = [("tsunami", "Tsunami"), ("scour", "Scour"), ("sediment", "Sediment transport"), ("reef", "Reef restoration")]


def theme_of(key):
    k = key.lower()
    return next((t for t, _ in THEMES if t in k), "other")


def rcard(key, pre, n):
    p = project(key)
    img = p["images"][0] if p["images"] else None
    th = theme_of(key)
    tag = dict(THEMES).get(th, "")
    first = plain(p["paras"][0]) if p["paras"] else ""
    m = re.match(r".+?[.!?](\s|$)", first)
    excerpt = (m.group(0) if m else first).strip()
    im = f'<img src="{pre}{img}" alt="" loading="lazy">' if img else ""
    return (f'<a class="rcard reveal" data-theme="{th}" style="--d:{(n % 3) * 0.08:.2f}s" href="{pre}{PATH[key]}">'
            f'<span class="rimg">{im}'
            f'{f"<span class=rtag>{tag}</span>" if tag else ""}</span>'
            f'<span class="rbody"><h3>{LABEL[key]}</h3><p>{esc(excerpt)}</p>'
            f'<span class="rmore">Read more {icon("arrow")}</span></span></a>')


def p_research(key, pre, logo):
    heading, text, imgs = research_intro(key)
    cards = "".join(rcard(k, pre, n) for n, k in enumerate(PROJECTS))
    used = {theme_of(k) for k in PROJECTS}
    chips = ('<button type="button" class="chip on" data-filter="all">All</button>' +
             "".join(f'<button type="button" class="chip" data-filter="{t}">{l}</button>' for t, l in THEMES if t in used))
    misc_img = project("research__scour-around-bridge-piers")["images"][-1]
    misc = (f'<a class="misc-band reveal" href="{pre}{PATH["research__miscellaneous"]}">'
            f'<img src="{pre}{misc_img}" alt="" loading="lazy"><span class="ply">{icon("play")}</span>'
            f'<span><small>Videos</small><b>Miscellaneous</b></span><span class="go">{icon("arrow")}</span></a>')
    body = page_hero(key, pre, LABEL[key], crumbs=["research"] if key != "research" else None)
    body += f"""<section class="section"><div class="wrap split">
<div class="reveal"><span class="eyebrow">{esc(heading)}</span><h2>Coastal and Hydraulic engineering</h2><p class="lead">{fix(text, pre)}</p>
<ul class="methods"><li>Physical modelling</li><li>Numerical modelling</li><li>Analytical modelling</li></ul></div>
<div class="media-frame reveal" style="--d:.12s"><img src="{pre}{imgs[0]}" alt="Laboratory flume" loading="lazy"></div>
</div></section>
<section class="section tint"><div class="wrap">
<div class="section-head"><div class="reveal"><span class="eyebrow">Projects</span><h2>Explore the research</h2></div>
<div class="chips reveal" data-filters>{chips}</div></div>
<div class="rgrid">{cards}</div>
{misc}
</div></section>"""
    return layout(key, pre, logo, body)


def p_project(key, pre, logo):
    p = project(key)
    idx = PROJECTS.index(key)
    nxt = PROJECTS[(idx + 1) % len(PROJECTS)]
    hero_img = p["images"][0] if p["images"] else banner("research")
    paras = "".join(f'<p class="proj-lead">{fix(t, pre)}</p>' for t in p["paras"])
    links = "".join(f'<a class="btn btn-primary" href="{esc(u)}" target="_blank" rel="noopener">{esc(l)} {icon("arrow")}</a>' for l, u in p["links"])
    gal = "".join(zoom(pre, im, f'{LABEL[key]} – image {i + 1}', "proj") for i, im in enumerate(p["images"]))
    vids = "".join(f'<div class="reveal" style="margin-top:40px">{video(s, t)}</div>' for s, t in p["videos"])
    body = page_hero(key, pre, p["heading"], img=hero_img, crumbs=["research"])
    body += f"""<section class="section"><div class="wrap proj-layout">
<div><div class="reveal"><span class="eyebrow">{dict(THEMES).get(theme_of(key), "Research")}</span>{paras}</div>
{f'<div class="btn-row reveal">{links}</div>' if links else ''}
{f'<div class="gallery reveal">{gal}</div>' if gal else ''}
{vids}</div>
</div></section>
<section class="section" style="padding-top:0"><div class="wrap">
<a class="next-proj reveal" href="{pre}{PATH[nxt]}"><span><small>Next project</small><b>{LABEL[nxt]}</b></span><span class="go">{icon('arrow')}</span></a>
</div></section>"""
    return layout(key, pre, logo, body)


def p_misc(pre, logo):
    key = "research__miscellaneous"
    vids = [(b["src"], b.get("title", "")) for b in CONTENT[key]["blocks"] if b["t"] == "iframe" and yt_id(b["src"])]
    v = "".join(f'<div class="reveal" style="--d:{i * .1:.2f}s">{video(s, t)}</div>' for i, (s, t) in enumerate(vids))
    extra = ""
    ev = CONTENT[key].get("expired_video")
    if ev:
        pid = re.search(r"/data/(UQ_\d+)/", ev).group(1).replace("_", ":")
        extra = (f'<a class="info reveal" style="margin-top:32px;text-decoration:none" href="https://espace.library.uq.edu.au/view/{pid}" target="_blank" rel="noopener">'
                 f'<span class="ico">{icon("play")}</span><span><small>UQ eSpace video</small><span>{esc(ev.rsplit("/", 1)[-1])}</span></span></a>')
    body = page_hero(key, pre, "Miscellaneous", crumbs=["research"])
    body += f'<section class="section"><div class="wrap"><div class="videos">{v}</div>{extra}</div></section>'
    return layout(key, pre, logo, body)


def p_empty(key, pre, logo):
    if key == "publications":
        ic, btns = "book", (f'<a class="btn btn-primary" href="{SOCIAL[2][1]}" target="_blank" rel="noopener">ResearchGate {icon("arrow")}</a>'
                            f'<a class="btn btn-line" href="{pre}{PATH["research"]}">Research</a>')
    else:
        ic, btns = "flask", (f'<a class="btn btn-primary" href="{pre}{PATH["research"]}">Research {icon("arrow")}</a>'
                             f'<a class="btn btn-line" href="{pre}{PATH["news-and-updates"]}">News and Updates</a>')
    body = page_hero(key, pre, LABEL[key])
    body += (f'<section class="section"><div class="wrap"><div class="empty reveal"><div class="ico">{icon(ic)}</div>'
             f'<h2>{LABEL[key]}</h2><p>This page is being updated. Please check back soon.</p>'
             f'</div></div></section>')
    return layout(key, pre, logo, body)


def p_news(pre, logo):
    key = "news-and-updates"
    intro, carousel, posts = news()
    carousel = carousel + [banner("contact")]  # the old Contact banner photo now lives in the gallery
    track ="".join(zoom(pre, c, f"News and Updates – photo {i + 1}", "hl") for i, c in enumerate(carousel))
    feed = []
    for n, p in enumerate(posts):
        pics = ""
        if p["imgs"]:
            cls = "pics two" if len(p["imgs"]) > 1 else "pics"
            pics = f'<div class="{cls}">' + "".join(zoom(pre, im, p["title"] or "News photo", f"post{n}") for im in p["imgs"]) + "</div>"
        vids = "".join(video(s, t) for s, t in p["vids"])
        media = pics + vids
        date = f'<span class="date-badge">{icon("cal")}{p["date"]}</span>' if p["date"] else ""
        title = f"<h3>{esc(p['title'])}</h3>" if p["title"] else ""
        text = "".join(f"<p>{fix(b, pre)}</p>" for b in p["body"])
        feed.append(f'<article class="post reveal{"" if media else " text-only"}" id="post-{n + 1}">'
                    + (f"<div>{media}</div>" if media else "") + f"<div>{date}{title}{text}</div></article>")
    body = page_hero(key, pre, "News and Updates")
    if track:
        body += f"""<section class="section dark highlights" data-track><div class="wrap">
<div class="section-head"><div class="reveal"><span class="eyebrow">Gallery</span><h2>Highlights</h2></div>
<div class="track-nav reveal"><button type="button" data-dir="-1" aria-label="Previous photos">{icon('left')}</button>
<button type="button" data-dir="1" aria-label="Next photos">{icon('right')}</button></div></div>
<div class="track reveal">{track}</div></div></section>"""
    body += f'<section class="section tint"><div class="wrap"><div class="feed">{"".join(feed)}</div></div></section>'
    return layout(key, pre, logo, body)


def p_contact(pre, logo):
    key = "contact"
    form = next((b["src"] for b in CONTENT[key]["blocks"] if b["t"] == "iframe" and "docs.google.com/forms" in b["src"]), None)
    lead = next(plain(b["html"]) for b in CONTENT[key]["blocks"] if b["t"] == "p" and "welcome" in plain(b["html"]).lower())
    soc = "".join(f'<a href="{u}" target="_blank" rel="noopener">{icon(i)} {n}</a>' for n, u, i in SOCIAL)
    form_link = form.replace("?embedded=true", "") if form else ""
    body = page_hero(key, pre, "Contact", esc(lead), img="assets/img/about-ananth-education-1.jpg")
    body += f"""<section class="section"><div class="wrap contact-grid">
<div><span class="eyebrow reveal">Get in touch</span><h2 class="reveal" style="font-size:clamp(1.5rem,2.5vw,2.05rem)">{RECRUIT}</h2>
<div class="info-cards">
<div class="info reveal"><span class="ico">{icon('mail')}</span><span><small>Email</small>
<a href="mailto:{EMAILS[0]}">{EMAILS[0]}</a><a href="mailto:{EMAILS[1]}">{EMAILS[1]}</a></span></div>
<div class="info reveal" style="--d:.08s"><span class="ico">{icon('phone')}</span><span><small>Phone</small><a href="tel:{PHONE.replace('-', '')}">{PHONE}</a></span></div>
<a class="info reveal" style="--d:.16s;text-decoration:none" href="{form_link}" target="_blank" rel="noopener"><span class="ico">{icon('form')}</span><span><small>Web contact form</small><span>Open in a new tab</span></span></a>
</div>
<div class="social-row reveal">{soc}</div></div>
{f'<div class="form-card reveal" style="--d:.12s"><iframe src="{esc(form)}" title="Web contact form" loading="lazy">Loading…</iframe></div>' if form else ''}
</div></section>"""
    return layout(key, pre, logo, body)


def animated_logo(uid="a"):
    """Inline copy of assets/img/logo-animated.svg with its CSS class names prefixed (lg-)
    so they cannot clash with the site's own classes, and its ids made unique per copy."""
    svg = (ROOT / "assets" / "img" / "logo-animated.svg").read_text(encoding="utf-8")
    svg = re.sub(r"^<\?xml[^>]*>\s*", "", svg)
    for i in ["sealTop", "sealBottom", "sealDisc", "oCounter"]:
        svg = svg.replace(f'id="{i}"', f'id="{i}-{uid}"').replace(f"#{i})", f"#{i}-{uid})").replace(f'"#{i}"', f'"#{i}-{uid}"')
    names = ["d", "f", "ring", "spin", "grow", "pop", "drop", "rise"]
    for n in names:
        svg = re.sub(rf"\.{n}\{{", f".lg-{n}{{", svg)
        svg = re.sub(rf'class="{n}"', f'class="lg-{n}"', svg)
    for kf in ["draw", "fade", "ring", "spin", "grow", "pop", "drop", "rise"]:
        svg = svg.replace(f"@keyframes {kf}{{", f"@keyframes lg-{kf}{{").replace(f"animation-name:{kf};", f"animation-name:lg-{kf};")
    svg = svg.replace('width="680" height="680"', 'role="img" aria-label="H2O Group logo"')
    return svg


def subscript_h2o(page):
    """Write H2O with a subscript 2: <sub> in visible text, Unicode H₂O in titles and attributes."""
    head, sep, body = page.partition("<body>")
    if not sep:
        return page.replace("H2O", "H₂O")
    head = head.replace("H2O", "H₂O")
    body = re.sub(r'(<script\b.*?</script>)|>([^<]+)<',
                  lambda m: m.group(1) or ">" + m.group(2).replace("H2O", "H<sub>2</sub>O") + "<",
                  body, flags=re.S)
    body = body.replace("H2O", "H₂O")  # anything left is inside an attribute (alt, aria-label…)
    return head + sep + body


def build():
    build_image_map()
    logo = "assets/img/logo.svg"  # new H2O Engineering Group seal (Nov 2026)
    for key, path, _ in PAGES:
        pre = "../" * path.count("/")
        if key == "home":
            out = p_home(pre, logo)
        elif key == "about-ananth__bio":
            out = redirect(key, pre, "about-ananth")
        elif key == "research__research-overview":
            out = redirect(key, pre, "research")
        elif key == "about-ananth":
            out = p_about(key, pre, logo)
        elif key == "about-ananth__education":
            out = p_education(pre, logo)
        elif key == "about-ananth__experience":
            out = p_experience(pre, logo)
        elif key == "current-members":
            out = p_members(pre, logo)
        elif key == "research":
            out = p_research(key, pre, logo)
        elif key in PROJECTS:
            out = p_project(key, pre, logo)
        elif key == "research__miscellaneous":
            out = p_misc(pre, logo)
        elif key in ("publications", "projects"):
            out = p_empty(key, pre, logo)
        elif key == "news-and-updates":
            out = p_news(pre, logo)
        elif key == "contact":
            out = p_contact(pre, logo)
        out = subscript_h2o(out)
        dest = ROOT / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(out, encoding="utf-8")
        print("wrote", path)


if __name__ == "__main__":
    build()
