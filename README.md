# Collection Explorer

A CITS1501 team project for exploring collection records from the National Museum of Australia (NMA) and the State Library of Western Australia (SLWA).

## Run locally

Requires Python 3.9 or later. No third-party packages are required.
From the project folder, run:

```sh
python3 app.py --port 8000 --no-browser
```

Open http://127.0.0.1:8000/ in a browser. Stop the server with Ctrl+C.
If port 8000 is occupied, use `--port 8001` and open the corresponding URL.
Restart the server after changing the dataset.

## Using the application

Search by keyword, combine filters, choose a sort order and move between
result pages. Open a record for details and source links. The statistics
view describes all matched records, rather than only the current page.
Images load from external institutional URLs and require a network connection.

## Files and responsibilities

- `collection_core.py`: dataset validation, search, filtering, sorting, statistics and pagination.
- `data/collections.json`: local collection snapshot.
- `tests/test_core.py`: data contributor's core tests.
- `check_data.py` and `check_search.py`: command-line checks.
- `app.py`, `index.html`, `styles.css` and `script.js`: web contributor's server and interface.
- `docs/architecture.md`: architecture and data flow.
- `docs/integration-review.md`: core interface and handoff notes.
- `docs/data-sources.md` and `docs/language-sources.md`: source checks and outstanding use conditions.
- `AI-LOG.md`: AI assistance and verification records.

## Testing

```sh
python3 -m unittest discover -s tests -v
python3 check_data.py
python3 check_search.py
```

The current core suite has 34 passing tests. The root `test_core.py` file
has been removed, so its eight API tests are not currently retained in the
repository. The core tests use synthetic fixtures and do not check browser
workflows or live image loading.

## Data and sources

The current snapshot has 316 records: 305 SLWA and 11 NMA. There are
44 records with unknown starting years and 314 nonempty image URLs.
Unknown years remain null; image URL availability does not establish reuse permission.

Collection Explorer was developed using the National Museum of Australia's Collection API.
Source details and outstanding conditions are recorded in `docs/data-sources.md`.
The five existing Noongar interface labels are documented in
`docs/language-sources.md`; they are sourced expressions, not AI-generated language.

## Current status

The core, local server and interface are present, and the automated suites pass.
The prototype is currently intended for personal use. Full browser workflows,
external image loading, remaining source conditions, deployment and the final
report still need checking or completion. No public deployment is documented.
