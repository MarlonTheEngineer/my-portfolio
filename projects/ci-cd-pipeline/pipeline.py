"""Dependency-free CI/CD release toolkit for the GitHub Pages portfolio.

Commands:
  python projects/ci-cd-pipeline/pipeline.py check
  python projects/ci-cd-pipeline/pipeline.py build --output dist/site-release.zip
  python projects/ci-cd-pipeline/pipeline.py verify dist/site-release.zip
  python projects/ci-cd-pipeline/pipeline.py smoke --url https://.../my-portfolio/
"""
import argparse
import hashlib
import json
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import Request, urlopen
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "docs"
REQUIRED_PAGES = (
    "index.html",
    "neural-network/index.html",
    "helpdesk-copilot/index.html",
    "pipeline/index.html",
)
MANIFEST_NAME = "RELEASE-MANIFEST.json"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []
        self.ids = set()
        self.duplicates = set()
        self.h1_count = 0
        self.has_main = False
        self.has_title = False
        self.has_viewport = False
        self.images_without_alt = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            if a["id"] in self.ids:
                self.duplicates.add(a["id"])
            self.ids.add(a["id"])
        if tag == "h1":
            self.h1_count += 1
        if tag == "main":
            self.has_main = True
        if tag == "title":
            self.has_title = True
        if tag == "meta" and a.get("name", "").lower() == "viewport":
            self.has_viewport = True
        if tag == "a" and a.get("href") is not None:
            self.refs.append(("link", a["href"]))
        if tag == "link" and "stylesheet" in a.get("rel", "").split() and a.get("href"):
            self.refs.append(("stylesheet", a["href"]))
        if tag == "script" and a.get("src"):
            self.refs.append(("script", a["src"]))
        if tag == "img":
            if "alt" not in a:
                self.images_without_alt.append(a.get("src", "<missing src>"))
            if a.get("src"):
                self.refs.append(("image", a["src"]))


def read_page(path):
    page = PageParser()
    page.feed(path.read_text(encoding="utf-8"))
    return page


def audit_site(site=SITE):
    """Check every HTML page and every local link/asset, not only the homepage."""
    site = Path(site).resolve()
    errors = []
    html_files = sorted(site.rglob("*.html"))
    if not html_files:
        errors.append("No HTML pages found")
    for page in REQUIRED_PAGES:
        if not (site / page).is_file():
            errors.append("Required page missing: " + page)
    parsed = {}
    for html in html_files:
        rel = html.relative_to(site).as_posix()
        parser = read_page(html)
        parsed[html] = parser
        if parser.h1_count != 1:
            errors.append(rel + ": expected one h1, got " + str(parser.h1_count))
        if not (parser.has_main and parser.has_title and parser.has_viewport):
            errors.append(rel + ": missing main/title/viewport")
        if parser.duplicates:
            errors.append(rel + ": duplicate IDs " + repr(sorted(parser.duplicates)))
        if parser.images_without_alt:
            errors.append(rel + ": images missing alt: " + repr(parser.images_without_alt))
    refs_checked = 0
    for html, parser in parsed.items():
        rel = html.relative_to(site).as_posix()
        for kind, href in parser.refs:
            if not href:
                errors.append(rel + ": empty " + kind + " reference")
                continue
            parsed_url = urlsplit(href)
            if parsed_url.scheme.lower() in ("javascript", "data"):
                errors.append(rel + ": unsafe " + kind + " URL: " + href)
                continue
            if parsed_url.scheme or parsed_url.netloc:
                continue  # External resources are outside this local-link audit.
            if parsed_url.path.startswith("/"):
                errors.append(rel + ": site-root absolute link breaks project Pages: " + href)
                continue
            target = (html.parent / unquote(parsed_url.path)).resolve() if parsed_url.path else html
            if not target.is_relative_to(site):
                errors.append(rel + ": link escapes website root: " + href)
                continue
            if target.is_dir():
                target = target / "index.html"
            refs_checked += 1
            if not target.is_file():
                errors.append(rel + ": missing " + kind + " " + href)
            elif parsed_url.fragment and target.suffix == ".html":
                target_page = parsed.get(target)
                if target_page and unquote(parsed_url.fragment) not in target_page.ids:
                    errors.append(rel + ": missing anchor " + href)
    result = {"pages": len(html_files), "local_references": refs_checked, "errors": errors}
    if errors:
        raise ValueError("Site audit failed:\n- " + "\n- ".join(errors))
    return result


def _zip_entry(archive, name, data):
    info = ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def build_release(site=SITE, destination=ROOT / "dist" / "site-release.zip", commit="local"):
    """Build a reproducible zip from static source plus SHA-256 manifest."""
    site = Path(site).resolve()
    destination = Path(destination)
    if not site.is_dir():
        raise ValueError("Static site folder does not exist")
    audit_site(site)
    files = sorted(
        (p for p in site.rglob("*") if p.is_file() and not p.is_symlink()),
        key=lambda p: p.relative_to(site).as_posix()
    )
    manifest = {"schema_version": 1, "source_commit": commit, "files": []}
    for path in files:
        data = path.read_bytes()
        manifest["files"].append({
            "path": "site/" + path.relative_to(site).as_posix(),
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        })
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w") as archive:
        for entry, path in zip(manifest["files"], files):
            _zip_entry(archive, entry["path"], path.read_bytes())
        _zip_entry(archive, MANIFEST_NAME, (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    verify_release(destination)
    return {"files": len(files), "archive": str(destination), "sha256": hashlib.sha256(destination.read_bytes()).hexdigest()}


def verify_release(archive_path):
    """Check manifest, membership, content hashes, sizes and safe ZIP paths."""
    with ZipFile(archive_path, "r") as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate filenames in release")
        if MANIFEST_NAME not in names:
            raise ValueError("Manifest missing")
        manifest = json.loads(archive.read(MANIFEST_NAME))
        if manifest.get("schema_version") != 1 or not isinstance(manifest.get("files"), list):
            raise ValueError("Invalid manifest schema")
        expected = {MANIFEST_NAME}
        for entry in manifest["files"]:
            path = entry["path"]
            path_parts = Path(path).parts
            if not path.startswith("site/") or ".." in path_parts or "\\" in path or path.endswith("/"):
                raise ValueError("Unsafe archive member: " + path)
            if path in expected:
                raise ValueError("Duplicate manifest entry: " + path)
            expected.add(path)
            data = archive.read(path)
            if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
                raise ValueError("Content digest mismatch: " + path)
        if set(names) != expected:
            raise ValueError("Archive members do not match the manifest")
        if "site/index.html" not in expected:
            raise ValueError("Release has no homepage")
        if archive.testzip() is not None:
            raise ValueError("Corrupted archive")
    return {"files_verified": len(expected) - 1, "source_commit": manifest["source_commit"]}


def smoke_test(base_url, attempts=5, wait_seconds=12):
    """Verify public Pages routes after publication. Never reports an unverified success."""
    if not base_url.startswith("https://"):
        raise ValueError("Published URL must use HTTPS")
    checks = {
        "": "Marlon Taylor",
        "neural-network/": "Neural Network Playground",
        "helpdesk-copilot/": "AI Helpdesk Copilot",
        "pipeline/": "Release Control Room",
    }
    failures = []
    for attempt in range(1, attempts + 1):
        failures = []
        for route, needle in checks.items():
            url = urljoin(base_url.rstrip("/") + "/", route)
            request = Request(url, headers={"User-Agent": "Portfolio-Release-Smoke/1.0"})
            try:
                with urlopen(request, timeout=15) as response:
                    body = response.read(250_000).decode("utf-8", errors="replace")
                    if response.status != 200 or needle not in body:
                        failures.append(url + ": unexpected content or status")
            except (HTTPError, URLError, TimeoutError, OSError) as exc:
                failures.append(url + ": " + str(exc))
        if not failures:
            return {"status": "passed", "routes_verified": len(checks), "attempts": attempt}
        if attempt != attempts:
            time.sleep(wait_seconds)
    raise ValueError("Deployment smoke test failed:\n- " + "\n- ".join(failures))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit, package, verify, and smoke-test this static portfolio")
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("check", help="Audit all HTML and linked local assets")
    build = subs.add_parser("build", help="Build ZIP release with SHA-256 manifest")
    build.add_argument("--output", default=str(ROOT / "dist" / "site-release.zip"))
    build.add_argument("--commit", default="local")
    verify = subs.add_parser("verify", help="Validate a release archive's integrity")
    verify.add_argument("archive")
    smoke = subs.add_parser("smoke", help="Check real published site routes")
    smoke.add_argument("--url", default="https://marlontheengineer.github.io/my-portfolio/")
    smoke.add_argument("--attempts", type=int, default=5)
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            result = audit_site()
        elif args.command == "build":
            result = build_release(destination=args.output, commit=args.commit)
        elif args.command == "verify":
            result = verify_release(args.archive)
        else:
            result = smoke_test(args.url, attempts=args.attempts)
        print(json.dumps({"result": "PASS", **result}, indent=2))
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print("FAIL:", str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
