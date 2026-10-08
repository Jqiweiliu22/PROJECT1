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
## Entry 9: Year range filtering

### Purpose
Filter collection records by overlapping year ranges.

### AI assistance
At my request, Codex directly added year filtering to
collection_core.py and five tests to tests/test_core.py.

The function includes boundary years, supports one-sided limits,
excludes unknown years when a year filter is active, and rejects
invalid year limits.

### Review and verification
Codex ran the updated tests successfully.
I then ran the following command locally:

py -m unittest discover -s tests -p test_core.py -v

All 30 tests passed.

### Changes made by the team
An unsaved editor version contained an incomplete function
definition. I reverted that unsaved version to the saved file
and reran the tests successfully.

### Current limitations
Alternative sorting and pagination are not yet implemented.
## Entry 10: Sorting collection results

### Purpose
Support relevance, title, oldest and newest sorting.

### AI assistance
AI provided and applied the sorting function and four automated tests.

### Review and verification
I ran the test suite locally and confirmed that all 34 tests passed.

### Changes made by the team
Integrated AI-assisted sorting into the project and verified it locally.

### Current limitations
Pagination and collection statistics are not yet implemented.
## Entry 9: Pagination

### Purpose
Split collection results into pages.

### AI assistance
AI provided and applied paginate_records and five automated tests.
The default page size is 12. Pages beyond the last page are
adjusted to the last page. Empty results use page 1.

### Review and verification
I ran the following command locally:

py -m unittest discover -s tests -p test_core.py -v

All 39 tests passed, covering first and last pages, exact page
boundaries, empty results, excessive page numbers and invalid inputs.

### Changes made by the team
Verified the AI-assisted pagination locally.
No further changes were made to the provided code.

### Current limitations
Collection statistics are not yet implemented.
Pagination still needs integration with the server and interface.
## Entry 10: Stronger dataset validation

### Purpose
Prevent invalid field types and year ranges from causing errors
during search, filtering, sorting and analysis.

### AI assistance
AI provided and applied additional checks in load_dataset
and five automated tests.

The checks validate text fields, lists of strings, integer or
null years, and valid year ranges. Empty optional values remain
allowed.

### Review and verification
I ran the following command locally:

py -m unittest discover -s tests -p test_core.py -v

All 49 tests passed, including the five new dataset validation tests.

### Changes made by the team
Verified the updated validation locally.
No further changes were made to the provided code.

### Current limitations
Source details and image permissions still require verification.
Passing these tests does not confirm permission to display images.

## Entry 11: First item-level image permission review

### Purpose
Verify the source and image usage conditions of SLWA record slwa:b18396392.

### AI assistance
AI located the official item page, identified a conflict with the supplied
CC BY 4.0 image label, and applied corrections to the record and source audit.

### Review and verification
I opened https://purl.slwa.wa.gov.au/slwa_b1839639_1 and confirmed
the Terms of use: publication or display requires contacting SLWA.
No display permission has been obtained.
AI reran the 49 core tests after the data correction; all passed.

### Changes made by the team
Confirmed the official usage conditions and retained the corrected record.
The correction replaces the generic source link with the specific item
page, clears the display image URLs, and records permission_required.
The dataset still contains 316 records, with 315 nonempty image URLs.

### Current limitations
The remaining 304 SLWA image records and 11 NMA image records still
need individual rights verification. Image URL counts do not indicate
permission to display the images.

## Entry 12: Correcting the second SLWA record

### Purpose
Resolve source discrepancies and avoid unsupported image permission labels.

### AI assistance
AI read the official image page in a browser and corrected the dataset.
The team member supplied the catalogue screenshot and official item URL.

### Review and verification
I located and checked the official SLWA catalogue and image page:
https://purl.slwa.wa.gov.au/slwa_b1903014_1

I confirmed the official title, the year 1908 and call number 1935B.
I supplied the catalogue screenshot and item URL for comparison.

The page did not show an explicit item-level reuse licence.
Image display permission therefore remains unverified.

AI ran the core tests after the corrections; all 49 tests passed.

### Changes made by the team
I verified the source information and identified discrepancies
in the supplied record.

AI applied the corrections to the dataset and preserved the
original record in the review file.
