import json
import tempfile
import unittest
from pathlib import Path

from collection_core import (
    load_dataset,
    search_records,
    filter_records,
)
import unittest

from collection_core import search_records


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            {"id": "1", "title": "Aboriginal artwork"},
            {"id": "2", "title": "Wooden basket"},
            {"id": "3", "title": "Aboriginal tools"},
        ]

    def test_keyword_matches_titles(self):
        results = search_records(self.records, "Aboriginal")

        self.assertEqual(
            [record["id"] for record in results],
            ["1", "3"],
        )

    def test_search_ignores_case(self):
        results = search_records(self.records, "ABORIGINAL")

        self.assertEqual(
            [record["id"] for record in results],
            ["1", "3"],
        )

    def test_search_removes_surrounding_spaces(self):
        results = search_records(self.records, "  basket  ")

        self.assertEqual(
            [record["id"] for record in results],
            ["2"],
        )

    def test_empty_query_returns_all_records(self):
        results = search_records(self.records, "")

        self.assertEqual(results, self.records)
        self.assertIsNot(results, self.records)

    def test_unmatched_query_returns_empty_list(self):
        results = search_records(self.records, "zzzz")

        self.assertEqual(results, [])

    def test_empty_dataset_returns_empty_list(self):
        results = search_records([], "basket")

        self.assertEqual(results, [])

    def test_search_does_not_change_original_records(self):
        original = [record.copy() for record in self.records]

        search_records(self.records, "basket")

        self.assertEqual(self.records, original)
    def test_search_matches_each_additional_field(self):
        examples = [
            {"category": "basket"},
            {"materials": ["Wood", "basket"]},
            {"places": ["basket"]},
            {"collection": "basket"},
            {"date": "basket"},
            {"source_name": "basket"},
        ]

        for fields in examples:
            with self.subTest(fields=fields):
                record = {"id": "1", "title": "Example item"}
                record.update(fields)

                results = search_records([record], "basket")

                self.assertEqual(results, [record])

    def test_search_returns_record_only_once(self):
        record = {
            "id": "1",
            "title": "Wooden basket",
            "category": "Basket",
            "materials": ["Wood", "Basket"],
        }

        results = search_records([record], "basket")

        self.assertEqual(results, [record])
    def test_all_query_words_must_match(self):
        records = [
            {"id": "1", "title": "Wooden basket"},
            {"id": "2", "title": "Wooden tool"},
            {"id": "3", "title": "Metal basket"},
        ]

        results = search_records(records, "wood basket")

        self.assertEqual(
            [record["id"] for record in results],
            ["1"],
        )

    def test_query_words_can_match_different_fields(self):
        record = {
            "id": "1",
            "title": "Basket",
            "materials": ["Wood"],
        }

        results = search_records([record], "wood basket")

        self.assertEqual(results, [record])

    def test_title_match_ranks_above_material_match(self):
        records = [
            {
                "id": "1",
                "title": "Example item",
                "materials": ["Wood"],
            },
            {
                "id": "2",
                "title": "Wooden basket",
            },
        ]

        results = search_records(records, "wood")

        self.assertEqual(
            [record["id"] for record in results],
            ["2", "1"],
        )
    def test_filter_by_category(self):
        records = [
            {"id": "1", "category": "Tools"},
            {"id": "2", "category": "Advertisements"},
            {"id": "3", "category": "Tools"},
        ]

        results = filter_records(records, category=" tools ")

        self.assertEqual(
            [record["id"] for record in results],
            ["1", "3"],
        )

    def test_filter_by_source(self):
        records = [
            {"id": "1", "source_name": "Museum"},
            {"id": "2", "source_name": "Library"},
        ]

        results = filter_records(records, source_name="library")

        self.assertEqual(
            [record["id"] for record in results],
            ["2"],
        )

    def test_filter_requires_both_conditions(self):
        records = [
            {"id": "1", "category": "Tools", "source_name": "Museum"},
            {"id": "2", "category": "Tools", "source_name": "Library"},
            {"id": "3", "category": "Art", "source_name": "Museum"},
        ]

        results = filter_records(
            records,
            category="Tools",
            source_name="Museum",
        )

        self.assertEqual(
            [record["id"] for record in results],
            ["1"],
        )

    def test_filter_without_conditions_preserves_order(self):
        results = filter_records(self.records)

        self.assertEqual(results, self.records)
        self.assertIsNot(results, self.records)


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)

        self.path = Path(self.temp_directory.name) / "test_data.json"

        self.dataset = {
            "metadata": {"title": "Test dataset"},
            "records": [
                {"id": "1", "title": "Test item"}
            ],
        }

    def write_dataset(self, dataset):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(dataset, file)

    def test_valid_dataset_loads(self):
        self.write_dataset(self.dataset)

        metadata, records = load_dataset(self.path)

        self.assertEqual(metadata, self.dataset["metadata"])
        self.assertEqual(records, self.dataset["records"])

    def test_empty_records_are_allowed(self):
        self.dataset["records"] = []
        self.write_dataset(self.dataset)

        metadata, records = load_dataset(self.path)

        self.assertEqual(records, [])

    def test_rejects_invalid_outer_structure(self):
        self.write_dataset([])

        with self.assertRaises(ValueError):
            load_dataset(self.path)

    def test_rejects_missing_metadata(self):
        del self.dataset["metadata"]
        self.write_dataset(self.dataset)

        with self.assertRaises(ValueError):
            load_dataset(self.path)

    def test_rejects_invalid_records_type(self):
        self.dataset["records"] = {}
        self.write_dataset(self.dataset)

        with self.assertRaises(ValueError):
            load_dataset(self.path)

    def test_rejects_non_object_record(self):
        self.dataset["records"] = ["invalid record"]
        self.write_dataset(self.dataset)

        with self.assertRaises(ValueError):
            load_dataset(self.path)

    def test_rejects_missing_id(self):
        del self.dataset["records"][0]["id"]
        self.write_dataset(self.dataset)

        with self.assertRaises(ValueError):
            load_dataset(self.path)

    def test_rejects_blank_title(self):
        self.dataset["records"][0]["title"] = "   "
        self.write_dataset(self.dataset)

        with self.assertRaises(ValueError):
            load_dataset(self.path)

    def test_rejects_duplicate_ids(self):
        self.dataset["records"].append(
            {"id": "1", "title": "Another item"}
        )
        self.write_dataset(self.dataset)

        with self.assertRaises(ValueError):
            load_dataset(self.path)


if __name__ == "__main__":
    unittest.main()