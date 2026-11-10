"""Static checks for the published portfolio. Requires only Python's standard library."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
HTML = SITE / "index.html"


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.duplicates = set()
        self.links = []
        self.images_without_alt = []
        self.h1_count = 0
        self.has_main = False
        self.has_viewport = False
        self.has_title = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        ident = attributes.get("id")
        if ident:
            if ident in self.ids:
                self.duplicates.add(ident)
            self.ids.add(ident)
        if tag == "a":
            self.links.append(attributes.get("href", ""))
        if tag == "link" and attributes.get("rel") == "stylesheet":
            self.links.append(attributes.get("href", ""))
        if tag == "img" and "alt" not in attributes:
            self.images_without_alt.append(attributes.get("src", "<unknown>"))
        if tag == "h1":
            self.h1_count += 1
        if tag == "main":
            self.has_main = True
        if tag == "title":
            self.has_title = True
        if tag == "meta" and attributes.get("name") == "viewport":
            self.has_viewport = True


def check():
    errors = []
    if not HTML.is_file():
        raise SystemExit("Missing docs/index.html")
    page = HTML.read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(page)
    if parser.duplicates:
        errors.append(f"Duplicate HTML ids: {sorted(parser.duplicates)}")
    if parser.h1_count != 1:
        errors.append(f"Expected exactly one h1; found {parser.h1_count}")
    if not (parser.has_main and parser.has_title and parser.has_viewport):
        errors.append("Missing essential page landmark or metadata")
    if parser.images_without_alt:
        errors.append(f"Images without alt attributes: {parser.images_without_alt}")
    for href in parser.links:
        if not href:
            errors.append("Empty href attribute")
            continue
        url = urlsplit(href)
        if url.scheme or url.netloc:
            if url.netloc.lower() == "github.com" and url.path.startswith(
                "/MarlonTheEngineer/my-portfolio/tree/main/"
            ):
                repo_path = unquote(url.path.split("/tree/main/", 1)[1])
                if not (ROOT / repo_path).exists():
                    errors.append(f"Missing linked GitHub project path: {repo_path}")
            continue
        if url.path:
            candidate = (SITE / unquote(url.path)).resolve()
            if not candidate.is_relative_to(SITE.resolve()) or not candidate.is_file():
                errors.append(f"Missing or unsafe relative link: {href}")
        if url.fragment and url.fragment not in parser.ids:
            errors.append(f"Broken in-page anchor: {href}")
    css_file = SITE / "styles.css"
    if not css_file.is_file():
        errors.append("Missing docs/styles.css")
    else:
        css = css_file.read_text(encoding="utf-8")
        if css.count("{") != css.count("}"):
            errors.append("Unbalanced CSS braces")
        if ".navlinks a:not(.gitlink){display:none}" in css:
            errors.append("Mobile site navigation links are hidden")
    if errors:
        for message in errors:
            print("FAIL:", message)
        raise SystemExit(1)
    print(f"PASS: site structure and {len(parser.links)} links checked")


if __name__ == "__main__":
    check()
