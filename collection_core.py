import json


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