from collection_core import load_dataset, query_records

metadata, records = load_dataset("data/collections.json")
query = input("Enter a keyword: ")
result = query_records(records, {"q": query})
print("Matching records:", result["total"])
for record in result["items"][:5]:
    print(record["id"], "-", record["title"])
