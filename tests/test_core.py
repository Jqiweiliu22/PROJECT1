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


if __name__ == "__main__":
    unittest.main()