from collection_core import load_dataset, search_records

metadata, records = load_dataset("data/collections.json")

query = input("Enter a keyword: ")
results = search_records(records, query)

print("Matching records:", len(results))

for record in results[:5]:
    print(record["id"], "-", record["title"])