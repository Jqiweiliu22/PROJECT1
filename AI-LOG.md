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
