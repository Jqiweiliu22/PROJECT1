"""Automated checks with synthetic fixtures; no museum or internet requests.

Run from the application folder: python3 -m unittest discover -s tests -v
The HTTP tests exercise real request parsing in memory with temporary public files.
"""

import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import make_handler
from collection_core import (DatasetError, QueryError, load_dataset,
                             query_records, relevance_score, tokenize)


def make_record(identifier="a", **changes):
    """A complete synthetic catalogue entry, unrelated to real cultural content."""
    record = {
        "id": identifier, "title": "Sample object", "category": "Vessel",
        "materials": ["wood"], "places": ["Example place"],
        "collection": "Test collection", "identifier": "TEST-" + identifier,
        "date": "1905", "year": 1905, "year_end": None,
        "source_url": "https://example.org/objects/" + identifier,
        "source_name": "Test museum",
        "modified": "2026-01-01", "licence": "Test licence",
        "description": "", "image_url": "", "image_licence": "",
        "physical_description": "", "significance_statement": "",
        "educational_significance": "", "acknowledgement": "",
        "source_copyright": "", "all_categories": ["Vessel"],
        "measurements": {}, "creators": [], "related_dates": [],
        "related_links": [],
    }
    record.update(changes)
    return record


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            make_record("a", title="Wood sample", year=1905, date="1905"),
            make_record("b", title="Metal sample", category="Tool", materials=["metal"],
                        places=["Other place"], year=1950, year_end=1960, date="1950–1960"),
            make_record("c", title="Uncatalogued date", year=None, date="Date unknown"),
            make_record("d", title="Another vessel", year=1909, date="1909"),
        ]

    def ids(self, result):
        return [record["id"] for record in result["items"]]

    def test_weighted_ranking_prefers_title_over_category_over_material(self):
        records = [make_record("material", materials=["needle"]),
                   make_record("category", category="needle"),
                   make_record("title", title="needle")]
        result = query_records(records, {"q": "needle"})
        self.assertEqual(self.ids(result), ["title", "category", "material"])

    def test_score_adds_all_six_matching_field_weights_once(self):
        record = make_record(title="match match", category="match", materials=["match", "match"],
                             places=["match"], collection="match", date="match")
        self.assertEqual(relevance_score(record, ["match"]), 19)

    def test_all_tokens_must_match_but_can_match_different_fields(self):
        self.assertEqual(self.ids(query_records(self.records, {"q": "sample metal"})), ["b"])
        self.assertEqual(query_records(self.records, {"q": "sample absent"})["total"], 0)

    def test_unicode_casefold_punctuation_and_repeated_tokens(self):
        record = make_record(title="Straße SAMPLE")
        self.assertEqual(tokenize("STRASSE, sample sample!"), ["strasse", "sample"])
        self.assertEqual(query_records([record], {"q": "STRASSE, sample!"})["total"], 1)
        self.assertEqual(query_records([record], {"q": "sample sample"})["total"], 1)

    def test_relevance_ties_have_deterministic_id_order(self):
        records = [make_record("z"), make_record("a"), make_record("m")]
        self.assertEqual(self.ids(query_records(records, {"q": "sample"})), ["a", "m", "z"])

    def test_category_material_place_and_query_combine(self):
        params = {"category": "Vessel", "material": "wood", "place": "Example place", "q": "wood"}
        self.assertEqual(self.ids(query_records(self.records, params)), ["a", "c", "d"])
        params["place"] = "Other place"
        self.assertEqual(query_records(self.records, params)["total"], 0)

    def test_filter_labels_are_exact_and_not_case_insensitive_substrings(self):
        self.assertEqual(query_records(self.records, {"category": "vessel"})["total"], 0)
        self.assertEqual(query_records(self.records, {"material": "woo"})["total"], 0)

    def test_inclusive_date_interval_overlap_excludes_undated(self):
        self.assertEqual(self.ids(query_records(self.records, {"year_start": 1960, "year_end": 1960})), ["b"])
        self.assertEqual(query_records(self.records, {"year_start": 1961})["total"], 0)
        self.assertEqual(self.ids(query_records(self.records, {"year_end": 1905})), ["a"])

    def test_undated_records_stay_null_and_sort_last_in_both_directions(self):
        oldest = query_records(self.records, {"sort": "oldest"})
        newest = query_records(self.records, {"sort": "newest"})
        self.assertEqual(self.ids(oldest), ["a", "d", "b", "c"])
        self.assertEqual(self.ids(newest), ["b", "d", "a", "c"])
        self.assertIsNone(newest["items"][-1]["year"])

    def test_title_sort_casefolds_and_breaks_ties_by_id(self):
        records = [make_record("z", title="alpha"), make_record("b", title="Beta"),
                   make_record("a", title="ALPHA")]
        self.assertEqual(self.ids(query_records(records, {"sort": "title"})), ["a", "z", "b"])

    def test_stats_use_all_results_before_pagination(self):
        result = query_records(self.records, {"page_size": 1})
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["stats"], {
            "total": 4, "dated": 3, "undated": 1,
            "categories": [{"label": "Vessel", "count": 3}, {"label": "Tool", "count": 1}],
            "decades": [{"label": "1900s", "count": 2}, {"label": "1950s", "count": 1}],
        })

    def test_stats_use_filtered_records_but_facets_use_full_dataset(self):
        result = query_records(self.records, {"category": "Tool"})
        self.assertEqual(result["stats"]["total"], 1)
        self.assertEqual(result["stats"]["categories"], [{"label": "Tool", "count": 1}])
        self.assertEqual(result["facets"], {"categories": ["Tool", "Vessel"],
                                           "materials": ["metal", "wood"],
                                           "places": ["Example place", "Other place"],
                                           "sources": ["Test museum"]})

    def test_source_filter_is_exact_and_combines_with_search(self):
        records = [make_record("one", source_name="Museum A"),
                   make_record("two", source_name="Library B")]
        self.assertEqual(self.ids(query_records(records, {"source": "Library B", "q": "sample"})), ["two"])
        self.assertEqual(query_records(records, {"source": "library b"})["total"], 0)

    def test_image_filter_defaults_to_false_and_preserves_complete_catalogue(self):
        self.records[0]["image_url"] = "https://example.org/a.jpg"
        self.assertEqual(query_records(self.records, {})["total"], 4)
        self.assertEqual(query_records(self.records, {"image_only": "false"})["total"], 4)

    def test_image_filter_precedes_statistics_pagination_and_keeps_all_facets(self):
        self.records[0]["image_url"] = "https://example.org/a.jpg"
        self.records[2]["image_url"] = "https://example.org/c.jpg"
        result = query_records(self.records, {"image_only": "true", "page_size": 1, "page": 99})
        self.assertEqual((result["total"], result["page"], result["pages"]), (2, 2, 2))
        self.assertEqual(self.ids(result), ["c"])
        self.assertEqual(result["stats"], {"total": 2, "dated": 1, "undated": 1,
                                           "categories": [{"label": "Vessel", "count": 2}],
                                           "decades": [{"label": "1900s", "count": 1}]})
        self.assertEqual(result["facets"], query_records(self.records, {})["facets"])
        self.assertIn("Tool", result["facets"]["categories"])

    def test_image_filter_combines_with_query_and_exact_filters(self):
        self.records[0]["image_url"] = "https://example.org/a.jpg"
        self.records[2]["image_url"] = "https://example.org/c.jpg"
        params = {"image_only": "true", "q": "sample", "category": "Vessel", "material": "wood"}
        self.assertEqual(self.ids(query_records(self.records, params)), ["a"])
        params["category"] = "Tool"
        self.assertEqual(query_records(self.records, params)["total"], 0)

    def test_image_filter_handles_empty_and_whitespace_image_urls(self):
        self.records[0]["image_url"] = "   "
        result = query_records(self.records, {"image_only": "true"})
        self.assertEqual((result["items"], result["total"], result["page"], result["pages"]), ([], 0, 1, 1))
        self.assertEqual(result["stats"]["total"], 0)

    def test_image_filter_rejects_invalid_and_repeated_flags(self):
        for value in ("", "True", "yes", "1", "0", True, ["true", "false"]):
            with self.subTest(value=value), self.assertRaises(QueryError):
                query_records(self.records, {"image_only": value})
        self.assertEqual(query_records(self.records, {"image_only": ["false"]})["total"], 4)

    def test_page_beyond_end_clamps_to_last_page(self):
        result = query_records(self.records, {"page_size": 3, "page": 999})
        self.assertEqual((result["page"], result["pages"], result["total"]), (2, 2, 4))
        self.assertEqual(self.ids(result), ["d"])

    def test_empty_dataset_and_empty_match_are_valid_single_empty_pages(self):
        for records, params in (([], {}), (self.records, {"q": "impossible", "page": 2})):
            with self.subTest(params=params):
                result = query_records(records, params)
                self.assertEqual((result["items"], result["total"], result["page"], result["pages"]), ([], 0, 1, 1))
                self.assertEqual(result["stats"], {"total": 0, "dated": 0, "undated": 0,
                                                   "categories": [], "decades": []})

    def test_invalid_year_ranges_and_boundaries(self):
        for params in ({"year_start": 2000, "year_end": 1900}, {"year_start": 0},
                       {"year_end": 2101}, {"year_start": "1900.5"}, {"year_end": "unknown"}):
            with self.subTest(params=params), self.assertRaises(QueryError):
                query_records(self.records, params)
        self.assertEqual(query_records(self.records, {"year_start": 1, "year_end": 2100})["total"], 3)

    def test_invalid_sort_page_and_page_size(self):
        for params in ({"sort": "random"}, {"page": 0}, {"page": -1}, {"page": "1.2"},
                       {"page_size": 0}, {"page_size": 51}, {"page": "9" * 100}, {"page": True}):
            with self.subTest(params=params), self.assertRaises(QueryError):
                query_records(self.records, params)
        self.assertEqual(query_records(self.records, {"page_size": 50})["page_size"], 50)

    def test_query_length_boundary_and_duplicate_parameters(self):
        self.assertEqual(query_records(self.records, {"q": " " * 160})["total"], 4)
        for params in ({"q": " " * 161}, {"q": ["one", "two"]}, {"page": ["1", "2"]}):
            with self.subTest(params=params), self.assertRaises(QueryError):
                query_records(self.records, params)
        self.assertEqual(query_records(self.records, {"q": ["metal"], "page": ["1"]})["total"], 1)

    def test_search_and_returned_items_do_not_mutate_input(self):
        original = copy.deepcopy(self.records)
        result = query_records(self.records, {"q": "wood"})
        result["items"][0]["title"] = "Changed in caller"
        result["items"][0]["materials"].append("changed in caller")
        self.assertEqual(self.records, original)


class DatasetTests(unittest.TestCase):
    def load(self, payload):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "dataset.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return load_dataset(path)

    def test_valid_dataset_preserves_exact_source_description_and_nulls(self):
        record = make_record(description="  Source text.\nSecond line.",
                             physical_description="Original physical text.",
                             significance_statement="Original significance text.",
                             measurements={"height": 10, "unitText": "mm"},
                             related_dates=[{"title": "About 1900", "roleName": "Associated date"}],
                             year=None, date="")
        metadata, records = self.load({"metadata": {"source": "test"}, "records": [record]})
        self.assertEqual(metadata, {"source": "test"})
        self.assertEqual(records, [record])

    def test_invalid_enriched_field_types_are_rejected(self):
        bad_records = [make_record(physical_description=[]), make_record(all_categories="Vessel"),
                       make_record(measurements=[]), make_record(creators=["unknown"]),
                       make_record(related_dates={}), make_record(related_links=["https://example.org"])]
        for record in bad_records:
            with self.subTest(record=record), self.assertRaises(DatasetError):
                self.load({"metadata": {}, "records": [record]})

    def test_duplicate_ids_are_rejected_not_silently_deduplicated(self):
        with self.assertRaisesRegex(DatasetError, "Duplicate record ID"):
            self.load({"metadata": {}, "records": [make_record("a"), make_record("a")]})

    def test_invalid_schema_types_and_date_intervals_are_rejected(self):
        bad_records = [make_record(title=3), make_record(materials="wood"), make_record(year=True),
                       make_record(year_end=1800), make_record(year=None, year_end=1900), make_record(id="")]
        missing = make_record()
        del missing["year_end"]
        bad_records.append(missing)
        for record in bad_records:
            with self.subTest(record=record), self.assertRaises(DatasetError):
                self.load({"metadata": {}, "records": [record]})

    def test_empty_dataset_is_valid_but_malformed_envelope_is_rejected(self):
        self.assertEqual(self.load({"metadata": {}, "records": []}), ({}, []))
        for payload in ([], {}, {"metadata": [], "records": []}):
            with self.subTest(payload=payload), self.assertRaises(DatasetError):
                self.load(payload)

    def test_missing_or_non_json_files_report_dataset_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "missing.json"
            with self.assertRaises(DatasetError):
                load_dataset(path)
            path.write_text("this is not JSON", encoding="utf-8")
            with self.assertRaises(DatasetError):
                load_dataset(path)


class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory()
        cls.root = Path(cls.folder.name).resolve()
        (cls.root / "index.html").write_text("<!doctype html><title>Test</title>", encoding="utf-8")
        (cls.root / "app.py").write_text("SECRET_SOURCE", encoding="utf-8")
        (cls.root / "data").mkdir()
        (cls.root / "data" / "collections.json").write_text("PRIVATE_DATA", encoding="utf-8")
        (cls.root / "assets").mkdir()
        (cls.root / "assets" / "public.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        (cls.root / "assets" / "alias.svg").symlink_to(cls.root / "app.py")
        cls.record = make_record("sample")
        handler = make_handler({"source": "Synthetic fixture"}, [cls.record], cls.root)
        handler.log_message = lambda self, *args: None
        cls.handler = handler

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def request(self, path, method="GET", handler=None):
        class MemoryConnection:
            """The minimal socket interface used by BaseHTTPRequestHandler."""
            def __init__(self, request):
                self.incoming = io.BytesIO(request)
                self.outgoing = io.BytesIO()

            def makefile(self, *args, **kwargs):
                return self.incoming

            def sendall(self, data):
                self.outgoing.write(data)

        request = "{} {} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n".format(method, path)
        connection = MemoryConnection(request.encode("ascii"))
        (handler or self.handler)(connection, ("127.0.0.1", 0), object())
        header_bytes, _separator, body = connection.outgoing.getvalue().partition(b"\r\n\r\n")
        lines = header_bytes.decode("iso-8859-1").split("\r\n")
        status = int(lines[0].split()[1])
        headers = dict(line.split(": ", 1) for line in lines[1:])
        return status, headers, body

    def test_api_search_meta_and_detail(self):
        status, headers, body = self.request("/api/collections?q=sample")
        self.assertEqual(status, 200)
        self.assertIn("application/json", headers["Content-Type"])
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(json.loads(body)["items"], [self.record])
        self.assertEqual(json.loads(self.request("/api/meta")[2]), {"source": "Synthetic fixture", "count": 1})
        self.assertEqual(json.loads(self.request("/api/objects/sample")[2]), self.record)

    def test_invalid_search_returns_helpful_json_400(self):
        status, _headers, body = self.request("/api/collections?year_start=2000&year_end=1900")
        self.assertEqual(status, 400)
        self.assertIn("start year", json.loads(body)["error"])
        self.assertNotIn("Traceback", body.decode())

    def test_image_filter_api_and_invalid_flag(self):
        status, _headers, body = self.request("/api/collections?image_only=true")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["total"], 0)
        status, _headers, body = self.request("/api/collections?image_only=yes")
        self.assertEqual(status, 400)
        self.assertIn("image_only", json.loads(body)["error"])

    def test_closed_or_failed_log_stream_does_not_interrupt_responses(self):
        handler = make_handler({}, [self.record], self.root)
        closed_stream = io.StringIO()
        closed_stream.close()
        with patch("app.sys.stderr", closed_stream):
            status, _headers, body = self.request("/api/meta", handler=handler)
        self.assertEqual((status, json.loads(body)["count"]), (200, 1))
        with patch("app.sys.stderr") as failed_stream:
            failed_stream.write.side_effect = OSError("Terminal unavailable")
            status, _headers, body = self.request("/api/meta", handler=handler)
        self.assertEqual((status, json.loads(body)["count"]), (200, 1))

    def test_unknown_object_and_route_return_json_404(self):
        for path in ("/api/objects/missing", "/api/missing", "/missing.html"):
            with self.subTest(path=path):
                status, _headers, body = self.request(path)
                self.assertEqual(status, 404)
                self.assertIn("error", json.loads(body))

    def test_static_allowlist_blocks_source_data_traversal_and_symlinks(self):
        for path in ("/app.py", "/data/collections.json", "/assets/", "/assets/../app.py",
                     "/assets/%2e%2e/app.py", "/assets/alias.svg", "/assets/a%5c..%5capp.py"):
            with self.subTest(path=path):
                status, _headers, body = self.request(path)
                self.assertEqual(status, 404)
                self.assertNotIn(b"SECRET_SOURCE", body)
                self.assertNotIn(b"PRIVATE_DATA", body)

    def test_public_assets_and_head_are_served_with_types(self):
        status, headers, body = self.request("/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn(b"<!doctype html>", body)
        status, headers, body = self.request("/assets/public.svg", method="HEAD")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "image/svg+xml")
        self.assertEqual(body, b"")
        self.assertGreater(int(headers["Content-Length"]), 0)

    def test_api_is_read_only(self):
        status, _headers, body = self.request("/api/objects/sample", method="POST")
        self.assertEqual(status, 405)
        self.assertIn("GET", json.loads(body)["error"])


if __name__ == "__main__":
    unittest.main()
