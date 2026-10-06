# AI Usage Log

## Entry 1: Initial repository setup

### Purpose
Get guidance on setting up the GitHub repository.

### AI assistance
AI suggested an initial README, a Python .gitignore,
and a structure for recording AI use.

### Review and verification
The user confirmed that the initial files appeared on GitHub.

### Changes made by the team
Reviewed the suggested README, .gitignore and AI log.
Kept the initial contents without changes.

## Entry 2: Dataset loading and basic checks

### Purpose
Read the supplied JSON dataset and check its basic data quality.

### AI assistance
AI suggested check_data.py for inspecting record counts, missing IDs,
missing titles, duplicate IDs, image URLs and unknown years.
AI then suggested extracting load_dataset into collection_core.py
and validating the JSON structure, nonempty string IDs and titles,
and duplicate IDs.

### Review and verification
Ran check_data.py locally before and after extracting the loading
function and shared screenshots of the successful results:
- Total records: 316
- Declared records: 316
- Missing IDs: 0
- Missing titles: 0
- Duplicate IDs: 0
- Records with image URLs: 316
- Records with unknown years: 44

Invalid dataset cases have not yet been tested.
Codex also reran the current version with validation on 2026-10-07
and confirmed the same counts.

### Changes made by the team
The user fixed a NameError by defining seen_ids before the checking
loop and shared a successful rerun. The current code includes the
AI-suggested reusable loading function and basic validation.

### Current limitations
Image URLs have been counted, but their availability and usage
permissions have not yet been verified. Unknown years remain missing.

## Entry 3: Basic title search

### Purpose
Implement case-insensitive keyword searching in collection titles.

### AI assistance
AI suggested search_records in collection_core.py and a check_search.py
script. Empty queries return a copy of the complete records list.

### Review and verification
Ran check_search.py locally with four inputs:
- Aboriginal: 67 matching records.
- aboriginal: 67 matching records.
- Empty input: 316 matching records.
- zzzz_no_match_12345: 0 matching records.

All four runs completed without errors.
Confirmed that capitalization did not affect the matching count,
an empty query returned all records, and an unmatched query
returned zero records.

### Changes made by the team
The current search function and checking script match the AI-suggested
code. No additional changes to the search implementation were observed.
At the user's request, Codex reorganized this log, moved dataset checks
out of Entry 1, removed the duplicated heading, and recorded verification.

### Current limitations
Search currently checks titles only. Other search fields, relevance
ranking and automated search tests are not yet implemented.
## Entry 4: Automated search tests

### Purpose
Verify basic title search behaviour with automated tests.

### AI assistance
AI suggested seven unittest cases in tests/test_core.py.

### Review and verification
Ran the following command locally:

py -m unittest discover -s tests -p test_core.py -v

All seven tests passed. The tests checked:
- Keyword matching.
- Case-insensitive search.
- Surrounding whitespace.
- Empty queries.
- Unmatched queries.
- Empty datasets.
- Preservation of the original records.

### Changes made by the team
Used the suggested test code without changes and ran it locally.

### Current limitations
These tests cover basic title search only.
Dataset validation and later search features need additional tests.
## Entry 5: Dataset validation tests

### Purpose
Check that the dataset loader accepts valid data and rejects
invalid structures, missing identifiers and duplicate IDs.

### AI assistance
AI suggested nine DatasetTests using temporary JSON files.
The original collection dataset was not modified.

### Review and verification
Ran locally:

py -m unittest discover -s tests -p test_core.py -v

The latest run passed all 16 tests:
- 7 search tests.
- 9 dataset loading and validation tests.

An earlier run failed. After editing the test file,
the tests were rerun successfully.

### Changes made by the team
Added DatasetTests to tests/test_core.py and ran the tests locally.

### Current limitations
The tests do not yet cover all collection fields, missing files
or malformed JSON. Image availability and permissions remain
to be checked.
## Entry 6: Search across multiple fields

### Purpose
Expand keyword search beyond collection titles.

### AI assistance
AI suggested searching seven fields: title, category, materials,
places, collection, date and source_name.

AI also suggested tests for matching each additional field and
returning a record only once when multiple fields match.

### Review and verification
Ran locally:

py -m unittest discover -s tests -p test_core.py -v

All 18 tests passed, including the two new search tests.
The existing search and dataset tests continued to pass.

### Changes made by the team
Replaced the title-only search function with the suggested
multi-field search and added the two tests.

### Current limitations
Search treats the query as a single phrase.
Relevance ranking is not yet implemented.
## Entry 7: Multi-keyword search and relevance ranking

### Purpose
Support multiple query words and rank matching records by relevance.

### AI assistance
AI suggested splitting queries into words, requiring every word
to match, and calculating scores using field weights:
title 8, category 4, materials 3, places 2,
collection 1, date 1 and source_name 1.

AI also suggested three additional search tests.

### Review and verification
Ran locally:

py -m unittest discover -s tests -p test_core.py -v

All 21 tests passed. The new tests confirmed:
- Every query word must match.
- Words can match different fields.
- A title match ranks above a material match.

### Changes made by the team
Added the suggested search algorithm and three tests,
then ran the complete core test suite locally.

### Current limitations
Matching uses substrings rather than whole words.
The field weights are application design choices.
Filtering, alternative sorting and pagination are not yet implemented.