#!/usr/bin/env python3
"""Diagnostic de veille football : aucune publication."""
import datetime as dt
import email.utils
import html
import json
import pathlib
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent

QUERIES = {
    "LIGUE_1": "mercato Ligue 1 football",
    "LIGUE_2": "mercato Ligue 2 football",
    "NATIONAL": "football National 1 recrutement",
    "N2_N3": "football National 2 National 3 transferts",
    "FEMININ": "football féminin transferts",
    "AMATEUR": "football amateur régional recrutement",
    "INTERNATIONAL": "football transferts Europe",
}

def main():
    path = ROOT / "articles.json"
    articles = json.loads(path.read_text(encoding="utf-8"))
    print("Articles existants :", len(articles), flush=True)
    now = dt.datetime.now(dt.timezone.utc)
    total = 0

    for zone, query in QUERIES.items():
        params = urllib.parse.urlencode({
            "q": query,
            "hl": "fr",
            "gl": "FR",
            "ceid": "FR:fr",
        })
        url = "https://news.google.com/rss/search?" + params
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 VeloceMercatoDiagnostic/1.0"}
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                data = response.read(1500000)
                print(zone, "HTTP", response.status, flush=True)

            root = ET.fromstring(data)
            items = root.findall("./channel/item")
            recent = 0

            for item in items:
                title = html.unescape(
                    re.sub(r"<[^>]*>", "", item.findtext("title") or "")
                ).strip()
                pub = item.findtext("pubDate") or ""
                try:
                    date = email.utils.parsedate_to_datetime(pub)
                    date = date.astimezone(dt.timezone.utc)
                except (TypeError, ValueError, OverflowError):
                    continue

                if title and now - dt.timedelta(hours=36) <= date <= now + dt.timedelta(minutes=10):
                    recent += 1

            print(zone, "resultats RSS :", len(items),
                  "| recents 36h :", recent, flush=True)
            total += recent

        except Exception as exc:
            print(zone, "ERREUR :", type(exc).__name__,
                  str(exc)[:200], flush=True)

    print("TOTAL RESULTATS RECENTS :", total, flush=True)
    print("MODE DIAGNOSTIC : aucun fichier modifie.", flush=True)

if __name__ == "__main__":
    main()
