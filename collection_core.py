import json
from collections import Counter


def load_dataset(path):
    """Read and validate collection metadata and records."""
    with open(path, encoding="utf-8") as file:
        dataset = json.load(file)

    if not isinstance(dataset, dict):
        raise ValueError("The dataset must be a JSON object.")

    metadata = dataset.get("metadata")
    records = dataset.get("records")

    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be a JSON object.")

    if not isinstance(records, list):
        raise ValueError("Records must be a list.")

    seen_ids = set()

    for position, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ValueError(
                f"Record {position} must be a JSON object."
            )

        record_id = record.get("id")
        title = record.get("title")

        if not isinstance(record_id, str) or record_id.strip() == "":
            raise ValueError(
                f"Record {position} needs a nonempty string ID."
            )

        if not isinstance(title, str) or title.strip() == "":
            raise ValueError(
                f"Record {position} needs a nonempty string title."
            )

        if record_id in seen_ids:
            raise ValueError(f"Duplicate record ID: {record_id}")

        seen_ids.add(record_id)

    return metadata, records
def search_records(records, query):
    """Match every query word and rank results by field weights."""
    tokens = query.strip().lower().split()

    if not tokens:
        return records.copy()

    field_weights = [
        ("title", 8),
        ("category", 4),
        ("materials", 3),
        ("places", 2),
        ("collection", 1),
        ("date", 1),
        ("source_name", 1),
    ]

    scored_results = []

    for record in records:
        score = 0
        matches_all = True

        for token in tokens:
            token_score = 0

            for field, weight in field_weights:
                value = record.get(field, "")

                if isinstance(value, list):
                    value = " ".join(value)

                if token in value.lower():
                    token_score += weight

            if token_score == 0:
                matches_all = False
                break

            score += token_score

        if matches_all:
            scored_results.append((score, record))

    # Higher scores come first. Equal scores keep their original order.
    scored_results.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [record for score, record in scored_results]


def filter_records(
    records, category="", source_name="", start_year=None, end_year=None
):
    """Filter by category, source and overlapping year ranges."""
    category = category.strip().lower()
    source_name = source_name.strip().lower()

    for value in (start_year, end_year):
        if value is not None and type(value) is not int:
            raise ValueError("Year limits must be integers or None.")

    if (
        start_year is not None
        and end_year is not None
        and start_year > end_year
    ):
        raise ValueError("Start year must not exceed end year.")

    results = []

    for record in records:
        record_category = record.get("category", "").strip().lower()
        record_source = record.get("source_name", "").strip().lower()

        if category and record_category != category:
            continue

        if source_name and record_source != source_name:
            continue

        if start_year is not None or end_year is not None:
            record_start = record.get("year")
            if record_start is None:
                continue

            record_end = record.get("year_end")
            if record_end is None:
                record_end = record_start

            if start_year is not None and record_end < start_year:
                continue
            if end_year is not None and record_start > end_year:
                continue

        results.append(record)

    return results


def sort_records(records, sort_by="relevance"):
    """Return a new list ordered by relevance, title or starting year."""
    if sort_by == "relevance":
        return records.copy()

    if sort_by == "title":
        return sorted(records, key=lambda record: record["title"].lower())

    if sort_by not in ("oldest", "newest"):
        raise ValueError("Unknown sort option.")

    known_years = []
    unknown_years = []

    for record in records:
        if record.get("year") is None:
            unknown_years.append(record)
        else:
            known_years.append(record)

    known_years.sort(
        key=lambda record: record["year"],
        reverse=(sort_by == "newest"),
    )

    return known_years + unknown_years


def paginate_records(records, page=1, page_size=12):
    """Return one page and navigation counts without changing the input."""
    for value in (page, page_size):
        if type(value) is not int or value < 1:
            raise ValueError("Page and page size must be positive integers.")

    total = len(records)
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = min(page, total_pages)
    start = (page - 1) * page_size

    return {
        "records": records[start:start + page_size],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def analyse_records(records):
    """Count categories, sources and starting-year decades before pagination."""
    categories = Counter()
    sources = Counter()
    decades = Counter()
    unknown_years = 0

    for record in records:
        category = record.get("category", "").strip() or "Unknown"
        source = record.get("source_name", "").strip() or "Unknown"
        categories[category] += 1
        sources[source] += 1

        year = record.get("year")
        if year is None:
            unknown_years += 1
        else:
            decade = (year // 10) * 10
            decades[decade] += 1

    return {
        "total": len(records),
        "categories": dict(categories.most_common()),
        "sources": dict(sources.most_common()),
        "decades": {
            str(decade): decades[decade] for decade in sorted(decades)
        },
        "unknown_years": unknown_years,
    }
