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

## Entry 13: Source and language checks

### Purpose
Check collection and language sources for our personal-use prototype.

### AI assistance
AI helped compare source information and document the five existing
Noongar labels in docs/language-sources.md.

### Review and verification
We checked and confirmed the collection sources and the published
sources of the five Noongar labels. We confirmed that the prototype
is intended for personal use.

### Changes made by the team
Recorded the sources and clarified the intended personal use.

### Current limitations
Remaining item-level image conditions and image loading still need checking.
Language material reuse permission has not been established.

## Entry 14: Core architecture changes

### Purpose
Organise the core functions into a consistent query workflow.

### AI assistance
AI helped implement query_records, parameter validation, search,
filtering, sorting, statistics and pagination, and updated the core tests.

### Review and verification
AI ran 30 core tests and the existing 38-test suite successfully.
The latter includes the same core cases and eight API tests.
The dataset still contains 316 records and 44 unknown starting years.

### Changes made by the team
Adopted the core architecture needed for server integration.

### Current limitations
Complete browser workflows and image loading still need checking.

## Entry 15: Core testing

### Purpose
Check normal inputs, invalid inputs and boundary cases.

### AI assistance
AI helped add four core tests for individual search-field weights,
punctuation-only queries, unmatched tokens and decade boundaries.

### Review and verification
AI ran all 34 core tests successfully. They cover dataset validation,
search, filters, sorting, pagination and statistics.

### Changes made by the team
Added the boundary tests to our existing core test suite.

### Current limitations
Browser workflows, image loading and deployment still need checking.

## Entry 16: Documentation and handoff

### Purpose
Document our work and prepare the core for team integration.

### AI assistance
AI helped update the README, source documents and core handoff notes.

### Review and verification
I reviewed the source documentation. The core handoff records its
parameters, response format and current validation results.

### Changes made by the team
Organised our data and core work for the web contributor to integrate.

### Current limitations
Full interface checks, deployment and report completion remain outstanding.

## Entry 17: Technical report draft

### Purpose
Prepare a report based on the current project and our question workbook.

### AI assistance
AI helped draft the eleven report sections and produce a PDF with an architecture diagram.

### Review and verification
AI checked the current code, data and Git history and ran all 34 core tests successfully.
The draft records missing student details and outstanding verification and deployment work.

### Changes made by the team
Prepared the report draft for student review and completion.

### Current limitations
Student review, formal identities, deployment evidence and final browser checks remain outstanding.

## Entry 18: Final interface wording and current verification

### Purpose
Align the public-facing wording with the current dataset, source documentation and student-project scope.

### AI assistance
At Leyi Jiang's direction, AI helped refine the About-page source and permission wording, the footer, the collection count sentence and the image-rights labels. AI also helped correct a spelling error and remove an unsupported statement about the website's visual reference.

### Review and verification
On 10 October 2026, AI-assisted checks ran all 41 automated tests successfully. The data checker confirmed 316 records, 314 non-empty image URLs and 44 records with unknown years. Local browser checks covered search, combined filters, a record detail page, Insights, a no-results state, invalid year input and the About page. The deployed site also loaded successfully and returned the expected result for a sample search. These AI-assisted checks do not replace the two students' own dated verification evidence.

### Changes made by the team
Leyi Jiang reviewed the website wording and requested precise replacements so that the interface describes the available content accurately and does not imply that every image has the same reuse licence. The project continues to distinguish dataset or catalogue-text licences from item-level image conditions.

### Current limitations
Both students personally ran the 41-test command at commit `d1073c4` and retained dated screenshots. Qiwei Liu recorded 41 passing tests at 22:03 AWST, and Leyi Jiang recorded 41 passing tests at 23:06 AWST, on 10 October 2026. Team browser checks covered the main public-site workflow. Most SLWA records still use a dataset-level source link rather than a verified item page, so users must check source information and image conditions before reuse.

## Entry 19: Scope and local-language wording review

### Purpose
Align the public website with the assignment's requirement for a specific user and purpose without implying that the project represents every Aboriginal or Torres Strait Islander culture.

### AI assistance
At Leyi Jiang's direction, AI helped revise the landing-page scope, catalogue heading, Insights limitation, local-language explanation, NMA attribution and labels for dataset-level source links.

### Review and verification
The project brief was re-read before the changes. It explicitly permits a Collection Explorer and requires a suitable, bounded purpose rather than comprehensive cultural coverage. The revised wording describes a selected catalogue sample and treats five Noongar words as small interface labels, not a full translation or language-learning feature.

### Changes made by the team
Leyi Jiang chose to retain the limited Noongar labels as an acknowledgement of the local Western Australian context while reducing the prominence of the language claim. Source links and the lack of institutional endorsement remain visible.

### Current limitations
This wording change does not establish permission to reuse the Noongar labels or every image. The team must retain source evidence, seek facilitator guidance where permission remains unclear, and remove uncertain material if it cannot be cleared for the final public submission.

## Entry 20: Final content and verification check

### Purpose
Record the final team checks and remove statements that were no longer accurate.

### AI assistance
At Leyi Jiang's direction, AI compared the public wording, current data counts, verification notes and Git status. AI helped replace ambiguous licence wording, remove an unsupported design-reference statement and update outdated testing notes.

### Review and verification
The repository was clean and matched `origin/main` at commit `d1073c4` before these local wording changes. All 41 core tests passed again on 10 October 2026. The deployed application loaded 316 records, displayed 314 records with non-empty image URLs and provided 27 result pages in its default illustrated view.

### Changes made by the team
Both students retained dated evidence of personally running the 41-test suite. Leyi Jiang reviewed the final public wording and requested that only statements supported by the current project evidence be kept.

### Current limitations
The automated suite covers the Python core rather than complete browser or API workflows. Mobile layout, long-term external image availability and unresolved item-level image and language reuse conditions remain limitations and are not presented as completed checks.
