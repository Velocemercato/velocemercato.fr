"""Tests sans réseau : actualités d'accueil lisibles sans JavaScript."""
import datetime as dt
import tempfile
import unittest
from pathlib import Path

from tools.home_news_static import START, END, render, update_index


class ActualitesAccueilTests(unittest.TestCase):
    now = dt.datetime(2026, 11, 1, 10, 0, tzinfo=dt.timezone.utc)

    def row(self, stamp="2026-11-01T08:30:00Z", title="Info football"):
        return {
            "id": "article-test-001", "titre": title, "resume": "Information factuelle",
            "publishedAt": stamp, "sources": [
                {"nom": "Média source", "url": "https://example.org/article"}],
        }

    def test_recent_sourced_article_visible_without_js(self):
        s = render([self.row()], now=self.now)
        self.assertIn("Info football", s)
        self.assertIn('/a/article-test-001.html', s)
        self.assertIn("Média source", s)
        self.assertIn(START, s)
        self.assertIn(END, s)

    def test_future_stale_or_unsourced_are_ignored(self):
        old = self.row("2026-10-20T12:00:00Z")
        future = self.row("2026-11-02T10:00:00Z")
        missing = self.row()
        missing["sources"] = []
        for row in (old, future, missing):
            with self.subTest(row=row):
                self.assertNotIn('/a/article-test-001.html', render([row], now=self.now))

    def test_html_injection_is_escaped(self):
        r = self.row(title="<script>alert(1)</script>")
        s = render([r], now=self.now)
        self.assertNotIn("<script>", s)
        self.assertIn("&lt;script&gt;", s)

    def test_same_input_does_not_rewrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "index.html"
            path.write_text("avant\n" + START + "\nancien\n" + END + "\napres", encoding="utf-8")
            self.assertTrue(update_index(tmp, [self.row()], now=self.now))
            c = path.read_text(encoding="utf-8")
            self.assertIn("avant", c)
            self.assertIn("apres", c)
            self.assertFalse(update_index(tmp, [self.row()], now=self.now))

    def test_current_index_contains_markers(self):
        s = Path("index.html").read_text(encoding="utf-8")
        self.assertEqual(s.count(START), 1)
        self.assertEqual(s.count(END), 1)


if __name__ == "__main__":
    unittest.main()
