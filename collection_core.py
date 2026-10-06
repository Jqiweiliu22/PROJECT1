import json


def load_dataset(path):
    """Read collection metadata and records from a JSON file."""
    with open(path, encoding="utf-8") as file:
        dataset = json.load(file)

    metadata = dataset["metadata"]
    records = dataset["records"]

    return metadata, records