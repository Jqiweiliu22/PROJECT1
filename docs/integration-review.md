# Core handoff

## Functions and errors

`load_dataset(path)` returns `(metadata, records)` and raises `DatasetError`
for unreadable or invalid data. `query_records(records, params)` returns a
query response and raises `QueryError` for invalid parameters. Input records
are not modified; returned items are deep copies.

## Query parameters

- `q`: up to 160 characters; casefolded, distinct tokens, AND matching.
- `category`, `material`, `place`, `source`: exact dataset labels.
- `era`: empty, before-1900, 1900-1949, 1950-present or unknown.
- `group`: empty, tools, artworks, daily-life, photographs or community.
- `year_start`, `year_end`: inclusive bounds from 1 to 2100; start must not exceed end.
- `image_only`: string true or false; defaults to false.
- `sort`: relevance, title, oldest or newest; defaults to relevance.
- `page`: positive integer; defaults to 1 and clamps to the last page.
- `page_size`: integer from 1 to 50; defaults to 12.

Parameters can be ordinary scalar values or single-value lists from `parse_qs`.
Repeated values and invalid types are rejected. An empty result has page 1 of 1.
Search uses seven weighted fields: title 8, category 4, materials 3, places 2,
collection 1, date 1 and source name 1. Era filters use the starting year,
whereas numeric year filters use inclusive interval overlap. Collection-type
groups use keyword matches in catalogue fields and are broad browsing aids,
not authoritative institutional classifications.

## Response

`items`, `total`, `page`, `page_size`, `pages`, `stats` and `facets`.
`stats` contains total, dated, undated, categories and decades. Category and
decade entries contain label and count. Intervals count once in the decade
of their starting year. `facets` contains categories, materials, places and
sources from the full dataset.

## Validation and next work

41 core tests pass, including independent matching for all seven search fields,
era boundaries, collection-type groups, combined filters and invalid parameters.
The root `test_core.py` file has been removed,
so its eight API tests are not currently retained in the repository.
Current automated validation covers the core; API test coverage needs
restoring separately.
The real dataset loads with 316 records, 314 nonempty image URLs, 44 unknown
starting years and no missing IDs, missing titles or duplicate IDs.

The existing server already imports the required functions and error classes.
The application is publicly deployed at
https://collection-explorer-93n8.onrender.com. AI checked basic public static-file
and API availability on 2026-10-10. A report draft has been prepared separately;
final team review, browser workflows, mobile checks and external image loading
remain outstanding.
Image and language use conditions are documented separately in the source files;
passing code tests does not resolve those conditions.
