"""Unit tests for the portfolio release and deployment verification toolkit."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

MODULE_PATH = Path(__file__).resolve().parents[1] / "pipeline.py"
SPEC = importlib.util.spec_from_file_location("release_pipeline", MODULE_PATH)
pipeline = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = pipeline
SPEC.loader.exec_module(pipeline)

TEMPLATE = """<!doctype html><html lang="en"><head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Release Test</title><link rel="stylesheet" href="styles.css"></head>
<body><main><h1 id="top">Hello</h1><a href="#top">Top</a></main></body></html>"""


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        self.site = self.root / "docs"
        for relative in pipeline.REQUIRED_PAGES:
            path = self.site / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(TEMPLATE, encoding="utf-8")
            (path.parent / "styles.css").write_text("body { color: white; }", encoding="utf-8")
        (self.site / ".nojekyll").write_text("", encoding="utf-8")

    def tearDown(self):
        self.folder.cleanup()

    def test_audit_accepts_valid_nested_site(self):
        result = pipeline.audit_site(self.site)
        self.assertEqual(result["pages"], len(pipeline.REQUIRED_PAGES))
        self.assertGreaterEqual(result["local_references"], 4)

    def test_audit_rejects_broken_relative_link(self):
        path = self.site / "pipeline" / "index.html"
        path.write_text(TEMPLATE.replace('href="#top"', 'href="missing.html"'), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "missing link"):
            pipeline.audit_site(self.site)

    def test_audit_rejects_missing_fragment(self):
        path = self.site / "index.html"
        path.write_text(TEMPLATE.replace('href="#top"', 'href="#does-not-exist"'), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "missing anchor"):
            pipeline.audit_site(self.site)

    def test_audit_rejects_escape_from_docs(self):
        path = self.site / "index.html"
        path.write_text(TEMPLATE.replace('href="#top"', 'href="../../secrets.txt"'), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "escapes website root"):
            pipeline.audit_site(self.site)

    def test_audit_rejects_script_without_file(self):
        path = self.site / "index.html"
        path.write_text(TEMPLATE.replace("</body>", '<script src="missing.js"></script></body>'), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "missing script"):
            pipeline.audit_site(self.site)

    def test_build_and_verify_manifest(self):
        archive = self.root / "dist" / "release.zip"
        result = pipeline.build_release(self.site, archive, commit="example-sha")
        verified = pipeline.verify_release(archive)
        self.assertEqual(verified["source_commit"], "example-sha")
        self.assertEqual(result["files"], verified["files_verified"])
        with ZipFile(archive) as z:
            manifest = json.loads(z.read("RELEASE-MANIFEST.json"))
            paths = [row["path"] for row in manifest["files"]]
            self.assertIn("site/.nojekyll", paths)
            self.assertIn("site/index.html", paths)

    def test_build_is_reproducible(self):
        a = pipeline.build_release(self.site, self.root / "a.zip", "same-commit")
        b = pipeline.build_release(self.site, self.root / "b.zip", "same-commit")
        self.assertEqual(a["sha256"], b["sha256"])

    def test_verify_detects_tampering(self):
        archive = self.root / "release.zip"
        pipeline.build_release(self.site, archive, "test")
        changed = self.root / "changed.zip"
        with ZipFile(archive) as source, ZipFile(changed, "w", ZIP_DEFLATED) as dest:
            for item in source.namelist():
                content = source.read(item)
                if item == "site/index.html":
                    content = b"<h1>Modified without new hash</h1>"
                dest.writestr(item, content)
        with self.assertRaisesRegex(ValueError, "Content digest mismatch"):
            pipeline.verify_release(changed)

    def test_verify_rejects_extraneous_archive_file(self):
        archive = self.root / "release.zip"
        pipeline.build_release(self.site, archive)
        with ZipFile(archive, "a") as z:
            z.writestr("site/unlisted.txt", "unlisted")
        with self.assertRaisesRegex(ValueError, "do not match"):
            pipeline.verify_release(archive)


if __name__ == "__main__":
    unittest.main()
