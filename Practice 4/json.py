import json

print("=== JSON Examples ===")

# Example 1: Python → JSON
data = {"name": "Alex", "age": 17, "is_student": True}
json_string = json.dumps(data)
print("Example 1 - Python to JSON:", json_string)

# Example 2: JSON → Python
parsed_data = json.loads(json_string)
print("Example 2 - JSON to Python:", parsed_data)

# Example 3: Access JSON fields
print("Example 3 - Access name:", parsed_data["name"])

# Example 4: Read & Write JSON file
with open("data.json", "w") as f:
    json.dump(data, f)
with open("data.json", "r") as f:
    loaded_data = json.load(f)
print("Example 4 - Loaded from file:", loaded_data)