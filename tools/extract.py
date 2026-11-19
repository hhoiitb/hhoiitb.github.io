"""Extract main-content blocks (headings, paragraphs, list items, images, links) in order
from saved Google Sites HTML pages. Usage: python -I extract.py <raw_dir> <out_json>"""
import json, sys, re, html
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, parse_qs

BLOCK = {"h1": "h1", "h2": "h2", "h3": "h3", "h4": "h4", "p": "p", "li": "li"}
VOID = {"img", "br", "meta", "link", "input", "hr", "source", "area", "base", "col", "embed", "wbr"}


def unwrap(u):
    if u and "google.com/url" in u:
        q = parse_qs(urlparse(u).query).get("q")
        if q:
            return q[0]
    return u


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.main_depth = None
        self.blocks = []
        self.cur = None  # current text block
        self.cur_depth = None
        self.link = None
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in VOID:
            self.depth += 1
        if self.main_depth is None:
            if tag == "section":
                self.main_depth = self.depth
            else:
                return
        if self.main_depth == -1:
            return
        if a.get("role") in ("menu", "contentinfo") or a.get("aria-label") == "Report abuse":
            self.main_depth = -1
            return
        if tag == "section":
            self.blocks.append({"t": "section"})
        st = a.get("style", "")
        m = re.search(r"background-image:\s*url\(([^)]+)\)", st)
        if m:
            kind = "banner" if "IFuOkc" in a.get("class", "") else "img"
            self.blocks.append({"t": kind, "src": m.group(1).strip("'\""), "alt": a.get("aria-label", "")})
        if tag in ("script", "style"):
            self.skip += 1
        if tag == "img":
            src = a.get("src") or a.get("data-src")
            if src and "sitesv-images" in src or (src and "googleusercontent" in src):
                self.blocks.append({"t": "img", "src": src, "alt": a.get("alt", "")})
        elif tag == "iframe":
            self.blocks.append({"t": "iframe", "src": a.get("src") or a.get("data-src", ""),
                                "title": a.get("aria-label", "")})
        elif tag in BLOCK and self.cur is None:
            self.cur = {"t": BLOCK[tag], "html": ""}
            self.cur_depth = self.depth
        elif tag == "a":
            href = unwrap(a.get("href", ""))
            self.link = href
            if self.cur is not None:
                self.cur["html"] += f'<a href="{html.escape(href or "", quote=True)}">'
            else:
                self.blocks.append({"t": "a", "href": href, "text": ""})
        elif tag == "br" and self.cur is not None:
            self.cur["html"] += "<br>"
        elif tag in ("strong", "b", "em", "i") and self.cur is not None:
            t = {"b": "strong", "i": "em"}.get(tag, tag)
            self.cur["html"] += f"<{t}>"
        elif tag == "span" and self.cur is not None:
            st = a.get("style", "")
            if "font-weight: 700" in st or "font-weight:700" in st:
                self.cur["html"] += "<strong>"
                self.cur.setdefault("_bstack", []).append(self.depth)
            if "font-style: italic" in st:
                self.cur["html"] += "<em>"
                self.cur.setdefault("_istack", []).append(self.depth)

    def handle_endtag(self, tag):
        if self.main_depth is not None and tag in ("script", "style") and self.skip:
            self.skip -= 1
        if self.cur is not None:
            if tag == "a":
                self.cur["html"] += "</a>"
            elif tag in ("strong", "b", "em", "i"):
                t = {"b": "strong", "i": "em"}.get(tag, tag)
                self.cur["html"] += f"</{t}>"
            elif tag == "span":
                for k, close in (("_istack", "</em>"), ("_bstack", "</strong>")):
                    s = self.cur.get(k)
                    if s and s[-1] == self.depth:
                        s.pop(); self.cur["html"] += close
        if tag == "a":
            self.link = None
        if self.cur is not None and tag in BLOCK and self.depth == self.cur_depth:
            self.cur.pop("_bstack", None); self.cur.pop("_istack", None)
            h = self.cur["html"].strip()
            if re.sub(r"<[^>]+>", "", h).strip():
                self.cur["html"] = h
                self.blocks.append(self.cur)
            self.cur = None
        if tag not in VOID:
            self.depth -= 1

    def handle_data(self, d):
        if self.main_depth in (None, -1) or self.skip:
            return
        if self.cur is not None:
            self.cur["html"] += html.escape(d, quote=False)
        elif self.blocks and self.blocks[-1]["t"] == "a" and self.link is not None:
            self.blocks[-1]["text"] += d


raw, out = Path(sys.argv[1]), Path(sys.argv[2])
res = {}
for f in sorted(raw.glob("*.html")):
    p = P(); p.feed(f.read_text(encoding="utf-8"))
    title = re.search(r"<title>(.*?)</title>", f.read_text(encoding="utf-8"), re.S)
    txt = f.read_text(encoding="utf-8")
    res[f.stem] = {"title": html.unescape(title.group(1)) if title else "", "blocks": p.blocks}
    logo = re.search(r'<img src="([^"]+)" class="r9CsCb"', txt)
    if logo and "_logo" not in res:
        res["_logo"] = logo.group(1)
    vid = re.search(r'data-url="(https://espace\.library\.uq\.edu\.au/data/[^"?]+)', txt)
    if vid:
        res[f.stem]["expired_video"] = vid.group(1)
out.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
for k, v in res.items():
    print(k, len(v["blocks"]))
