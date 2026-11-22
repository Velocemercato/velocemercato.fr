import unittest

from tools import liens_publications_meta as mod


PAGE = "1384363904759072"
UNIVERS_PAGE = "1349998758205153"
IG_UNIVERS = "17841400000000001"


class State:
    def __init__(self):
        self.data = {
            "tokens": {
                "meta": {"page_id": PAGE, "page_token": "test-page-token", "ig_id": "17841400000000002", "ig_username": "veloce.mercato"},
                "meta_univers": {"page_id": UNIVERS_PAGE, "page_token": "test-page-token", "ig_id": IG_UNIVERS, "ig_username": "vmunivers.fr"},
            },
            "meta": {},
            "meta_univers_accuses": {},
        }


class Graph:
    def __init__(self, account="meta", network="facebook", url=None):
        self.account, self.network, self.url = account, network, url
        self.calls = []
        self.page = PAGE if account == "meta" else UNIVERS_PAGE
        self.ig = "17841400000000002" if account == "meta" else IG_UNIVERS
        self.post = self.page + "_123" if network == "facebook" else "999123"
        self.url = url or ("https://www.facebook.com/" + self.page + "/posts/123"
                           if network == "facebook" else "https://www.instagram.com/reel/Abc123/")

    def call(self, method, path, params):
        self.calls.append((method, path, params))
        if method != "GET":
            raise AssertionError("Le synchroniseur ne doit jamais publier.")
        if path == self.page:
            return {"id": self.page, "name": "VM"}
        if path == self.ig:
            return {"id": self.ig, "username": "vmunivers.fr" if self.account == "meta_univers" else "veloce.mercato"}
        if path == self.page + "/published_posts":
            return {"data": [{
                "id": self.post,
                "created_time": "2026-11-22T19:00:00+0000",
                "from": {"id": self.page},
                "permalink_url": self.url,
            }]}
        if path == self.ig + "/media":
            return {"data": [{
                "id": self.post,
                "timestamp": "2026-11-22T22:02:00+0000",
                "permalink": self.url,
                "media_type": "VIDEO",
            }]}
        if path == self.post:
            return ({"id": self.post, "from": {"id": self.page}, "permalink_url": self.url}
                    if self.network == "facebook" else {"id": self.post, "permalink": self.url})
        raise AssertionError("Appel inattendu : " + path)


class MetaLinkTests(unittest.TestCase):
    def test_latest_facebook_post_is_read_directly_from_graph(self):
        state = State()
        graph = Graph("meta", "facebook")
        result = mod.derniere_publication_graph(state, graph, "meta", "facebook")
        self.assertEqual(result["url"], graph.url)
        self.assertEqual(result["rubrique"], "meta")
        self.assertTrue(all(call[0] == "GET" for call in graph.calls))

    def test_latest_instagram_reel_is_read_directly_from_graph(self):
        state = State()
        graph = Graph("meta_univers", "instagram")
        result = mod.derniere_publication_graph(state, graph, "meta_univers", "instagram")
        self.assertEqual(result["url"], graph.url)
        self.assertEqual(result["rubrique"], "meta")
        self.assertTrue(all(call[0] == "GET" for call in graph.calls))

    def test_invalid_instagram_domain_is_not_written(self):
        state = State()
        graph = Graph("meta_univers", "instagram", "https://example.com/not-a-post")
        result = mod.derniere_publication_graph(state, graph, "meta_univers", "instagram")
        self.assertIsNone(result)

    def test_graph_date_accepts_meta_timezone_format(self):
        stamp = mod.date_graph("2026-11-22T22:02:00+0000")
        self.assertEqual(stamp.isoformat(), "2026-11-22T22:02:00+00:00")


if __name__ == "__main__":
    unittest.main()
