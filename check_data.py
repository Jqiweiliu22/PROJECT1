import json

with open("data/collections.json", encoding="utf-8") as file:
    dataset = json.load(file)

metadata = dataset["metadata"]
records = dataset["records"]

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