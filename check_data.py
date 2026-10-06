from collection_core import load_dataset

metadata, records = load_dataset("data/collections.json")

print("Dataset:", metadata["title"])
print("Total records:", len(records))
print("Declared records:", metadata["record_count"])

if len(records) > 0:
    first_record = records[0]

    print("First ID:", first_record["id"])
    print("First title:", first_record["title"])
    print("First category:", first_record["category"])
    print("First source:", first_record["source_name"])
    print("First image URL:", first_record["image_url"])
else:
    print("The dataset is empty.")
seen_ids = set()
missing_id_count = 0
missing_title_count = 0
duplicate_id_count = 0
image_url_count = 0
unknown_year_count = 0

for record in records:
    record_id = record.get("id", "").strip()
    title = record.get("title", "").strip()

    if record_id == "":
        missing_id_count += 1
    elif record_id in seen_ids:
        duplicate_id_count += 1
    else:
        seen_ids.add(record_id)

    if title == "":
        missing_title_count += 1

    if record.get("image_url", "").strip() != "":
        image_url_count += 1

    if record.get("year") is None:
        unknown_year_count += 1

print("\nData checks:")
print("Missing IDs:", missing_id_count)
print("Missing titles:", missing_title_count)
print("Duplicate IDs:", duplicate_id_count)
print("Records with image URLs:", image_url_count)
print("Records with unknown years:", unknown_year_count)