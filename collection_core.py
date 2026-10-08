"""Search and analysis for Collection Explorer, using only the Python standard library.

The algorithm is deliberately explicit: tokenize a query, visit each record, test
every token against six fields, accumulate weighted scores, then filter, sort,
count and paginate. No search library performs the main task for us.
"""

import copy
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


class QueryError(ValueError):
    """A user supplied an invalid search parameter."""


class DatasetError(ValueError):
    """A data file does not meet the application's documented schema."""


STRING_FIELDS = (
    "id", "title", "category", "collection", "identifier", "date",
    "source_url", "modified", "licence", "description", "image_url",
    "image_licence", "source_name", "physical_description", "significance_statement",
    "educational_significance", "acknowledgement", "source_copyright",
)
FIELD_WEIGHTS = (
    ("title", 8), ("category", 4), ("materials", 3),
    ("places", 2), ("collection", 1), ("date", 1), ("source_name", 1),
)
SORT_OPTIONS = {"relevance", "title", "oldest", "newest"}
ERA_OPTIONS = {"", "before-1900", "1900-1949", "1950-present", "unknown"}
GROUP_KEYWORDS = {
    "tools": ("tool", "implement", "equipment", "hook", "knife", "spear", "boomerang", "axe", "weapon", "whip", "bridle"),
    "artworks": ("art", "painting", "print", "poster", "drawing", "sculpture", "carving", "batik", "craft"),
    "daily-life": ("clothing", "shirt", "dress", "hat", "bag", "container", "household", "furniture", "food", "textile", "vessel", "saddle"),
    "photographs": ("photograph", "portrait", "photographic", "negative", "slide"),
    "community": ("community", "ceremon", "festival", "banner", "badge", "award", "breastplate", "document", "ephemera", "gathering", "parade"),
}


def _matches_group(record: Mapping[str, Any], group: str) -> bool:
    """Map varied institutional labels into broad, visitor-friendly families."""
    if not group:
        return True
    haystack = " ".join([record["title"], record["category"], record["collection"],
                         *record["all_categories"], *record["materials"]]).casefold()
    return any(keyword in haystack for keyword in GROUP_KEYWORDS[group])


def load_dataset(path: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Load metadata and records from JSON, rejecting malformed or duplicate IDs.

    Source descriptions and labels are preserved exactly. Missing dates must be
    represented by null, rather than invented years. Duplicate IDs are rejected
    instead of silently removing records and making counts misleading.
    """
    try:
        with Path(path).open(encoding="utf-8") as data_file:
            payload = json.load(data_file)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DatasetError("Cannot read the collection dataset: {}".format(exc)) from exc
    if not isinstance(payload, dict):
        raise DatasetError("The dataset must be a JSON object.")
    metadata = payload.get("metadata")
    records = payload.get("records")
    if not isinstance(metadata, dict) or not isinstance(records, list):
        raise DatasetError("The dataset needs a metadata object and a records list.")
    seen_ids = set()
    for position, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise DatasetError("Record {} must be an object.".format(position))
        for field in STRING_FIELDS:
            if not isinstance(record.get(field), str):
                raise DatasetError("Record {} needs a string field: {}.".format(position, field))
        if not record["id"].strip() or not record["title"].strip():
            raise DatasetError("Record {} needs a nonempty ID and title.".format(position))
        if record["id"] in seen_ids:
            raise DatasetError("Duplicate record ID: {}.".format(record["id"]))
        seen_ids.add(record["id"])
        for field in ("materials", "places"):
            values = record.get(field)
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                raise DatasetError("Record {} needs a list of strings: {}.".format(position, field))
        categories = record.get("all_categories")
        if not isinstance(categories, list) or any(not isinstance(value, str) for value in categories):
            raise DatasetError("Record {} needs a list of strings: all_categories.".format(position))
        if not isinstance(record.get("measurements"), dict):
            raise DatasetError("Record {} needs an object field: measurements.".format(position))
        for field in ("creators", "related_dates", "related_links"):
            values = record.get(field)
            if not isinstance(values, list) or any(not isinstance(value, dict) for value in values):
                raise DatasetError("Record {} needs a list of objects: {}.".format(position, field))
        for field in ("year", "year_end"):
            if field not in record or (record[field] is not None and type(record[field]) is not int):
                raise DatasetError("Record {} needs an integer or null: {}.".format(position, field))
        if record["year_end"] is not None:
            if record["year"] is None or record["year_end"] < record["year"]:
                raise DatasetError("Record {} has an invalid date interval.".format(position))
    return metadata, records


def _parameter(params: Mapping[str, Any], name: str, default: str = "", strip: bool = True) -> str:
    """Accept plain values or the single-value lists returned by parse_qs."""
    value = params.get(name, default)
    if isinstance(value, (list, tuple)):
        if len(value) != 1:
            raise QueryError("Supply {} only once.".format(name))
        value = value[0]
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise QueryError("{} must be a text or integer value.".format(name))
    return str(value).strip() if strip else str(value)


def _integer_parameter(params: Mapping[str, Any], name: str, default: Optional[int],
                       minimum: int, maximum: Optional[int] = None) -> Optional[int]:
    value = _parameter(params, name)
    if not value:
        return default
    if not re.fullmatch(r"[0-9]+", value):
        raise QueryError("{} must be a whole number.".format(name))
    # A length check also avoids accepting enormous integers from hostile URLs.
    if len(value) > 10:
        raise QueryError("{} is too large.".format(name))
    number = int(value)
    if number < minimum or (maximum is not None and number > maximum):
        limit = "{}–{}".format(minimum, maximum) if maximum is not None else "{} or greater".format(minimum)
        raise QueryError("{} must be {}.".format(name, limit))
    return number


def tokenize(query: str) -> List[str]:
    """Casefold, split on punctuation/whitespace, and keep distinct word tokens.

    Casefold handles Unicode text (for example Straße and STRASSE). Repeated
    words are counted once, so typing a word twice does not inflate its score.
    """
    return list(dict.fromkeys(re.findall(r"\w+", query.casefold())))


def relevance_score(record: Mapping[str, Any], tokens: Sequence[str]) -> Optional[int]:
    """Return the AND-match score, or None if any token is absent.

    For each token, a substring match earns each field's weight at most once:
    title 8, category 4, materials 3, places 2, collection 1, date 1. A token
    found in several fields earns their sum. All tokens must match somewhere;
    they may occur in different fields. Empty token lists match with score 0.
    """
    searchable = []
    for field, weight in FIELD_WEIGHTS:
        value = record[field]
        if isinstance(value, list):
            value = " ".join(value)
        searchable.append((value.casefold(), weight))
    total = 0
    for token in tokens:
        token_score = 0
        for value, weight in searchable:
            if token in value:
                token_score += weight
        if token_score == 0:
            return None
        total += token_score
    return total


def _sorted_labels(values: Sequence[str]) -> List[str]:
    return sorted(set(value for value in values if value), key=lambda value: (value.casefold(), value))


def dataset_facets(records: Sequence[Mapping[str, Any]]) -> Dict[str, List[str]]:
    """Build exact filter choices from the full dataset, including zero-hit choices."""
    categories, materials, places, sources = [], [], [], []
    for record in records:
        categories.append(record["category"])
        materials.extend(record["materials"])
        places.extend(record["places"])
        sources.append(record["source_name"])
    return {"categories": _sorted_labels(categories),
            "materials": _sorted_labels(materials), "places": _sorted_labels(places),
            "sources": _sorted_labels(sources)}


def summarise(records: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Count the complete filtered set; use start years for decade groupings.

    Null years remain undated, even if a title or description contains a year.
    Date intervals count once in the decade of their earliest catalogued year.
    """
    category_counts = Counter()
    decade_counts = Counter()
    dated = 0
    for record in records:
        category_counts[record["category"]] += 1
        if record["year"] is not None:
            dated += 1
            decade_counts[(record["year"] // 10) * 10] += 1
    categories = [{"label": label, "count": count} for label, count in
                  sorted(category_counts.items(), key=lambda entry: (-entry[1], entry[0].casefold(), entry[0]))]
    decades = [{"label": "{}s".format(decade), "count": decade_counts[decade]}
               for decade in sorted(decade_counts)]
    return {"total": len(records), "dated": dated, "undated": len(records) - dated,
            "categories": categories, "decades": decades}


def query_records(records: Sequence[Mapping[str, Any]], params: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate input, rank AND matches, apply filters, analyse, and paginate.

    Filters for category/material/place use exact dataset labels. image_only
    accepts "true" or "false" (default); true requires a nonblank image URL.
    This filter runs before ranking, counting and pagination, while facet
    choices continue to describe the complete dataset. A date filter
    includes intervals overlapping the requested inclusive range, and excludes
    undated records. Oldest/newest use the start year; undated records sort last.
    Every sort uses the ID as a deterministic tie-breaker. Page numbers beyond
    the results clamp to the final page, with empty results represented by page
    1 of 1. All analysis precedes pagination, and input records are not modified.

    For N records, T tokens and six fields, matching takes O(N*T*L), where L is
    the text scanned per record. Sorting at most N matches takes O(N log N).
    """
    query = _parameter(params, "q", strip=False)
    if len(query) > 160:
        raise QueryError("Search text must be at most 160 characters.")
    tokens = tokenize(query)
    category = _parameter(params, "category")
    material = _parameter(params, "material")
    place = _parameter(params, "place")
    source = _parameter(params, "source")
    era = _parameter(params, "era")
    if era not in ERA_OPTIONS:
        raise QueryError("Era must be a listed browse period.")
    group = _parameter(params, "group")
    if group and group not in GROUP_KEYWORDS:
        raise QueryError("Group must be tools, artworks, daily-life, photographs, or community.")
    image_only = _parameter(params, "image_only", "false")
    if image_only not in {"true", "false"}:
        raise QueryError("image_only must be true or false.")
    year_start = _integer_parameter(params, "year_start", None, 1, 2100)
    year_end = _integer_parameter(params, "year_end", None, 1, 2100)
    if year_start is not None and year_end is not None and year_start > year_end:
        raise QueryError("The start year must be no later than the end year.")
    sort = _parameter(params, "sort", "relevance")
    if sort not in SORT_OPTIONS:
        raise QueryError("Sort must be relevance, title, oldest, or newest.")
    page = _integer_parameter(params, "page", 1, 1)
    page_size = _integer_parameter(params, "page_size", 12, 1, 50)
    matches = []
    for record in records:
        if image_only == "true" and not record["image_url"].strip():
            continue
        if category and record["category"] != category:
            continue
        if material and material not in record["materials"]:
            continue
        if place and place not in record["places"]:
            continue
        if source and record["source_name"] != source:
            continue
        if not _matches_group(record, group):
            continue
        year = record["year"]
        if era == "unknown" and year is not None:
            continue
        if era == "before-1900" and (year is None or year >= 1900):
            continue
        if era == "1900-1949" and (year is None or not 1900 <= year <= 1949):
            continue
        if era == "1950-present" and (year is None or year < 1950):
            continue
        if year_start is not None or year_end is not None:
            start = record["year"]
            end = record["year_end"] if record["year_end"] is not None else start
            if start is None:
                continue
            if year_start is not None and end < year_start:
                continue
            if year_end is not None and start > year_end:
                continue
        score = relevance_score(record, tokens)
        if score is not None:
            matches.append((record, score))
    if sort == "relevance":
        matches.sort(key=lambda match: (-match[1], match[0]["id"]))
    elif sort == "title":
        matches.sort(key=lambda match: (match[0]["title"].casefold(), match[0]["id"]))
    else:
        direction = -1 if sort == "newest" else 1
        matches.sort(key=lambda match: (match[0]["year"] is None,
                                       direction * (match[0]["year"] or 0), match[0]["id"]))
    filtered = [record for record, _score in matches]
    total = len(filtered)
    pages = max(1, (total + page_size - 1) // page_size)
    page = min(page, pages)
    offset = (page - 1) * page_size
    return {"items": copy.deepcopy(filtered[offset:offset + page_size]), "total": total,
            "page": page, "page_size": page_size, "pages": pages,
            "stats": summarise(filtered), "facets": dataset_facets(records)}
