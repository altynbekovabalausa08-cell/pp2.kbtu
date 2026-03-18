import os

os.makedirs("test_folder/subfolder1/subfolder2", exist_ok=True)
print("Nested directories created.")

with open("test_folder/file1.txt", "w") as f:
    f.write("Text file 1")

with open("test_folder/file2.py", "w") as f:
    f.write("print('Hello')")

with open("test_folder/file3.txt", "w") as f:
    f.write("Text file 3")

print("\nFiles and folders inside test_folder:")
for item in os.listdir("test_folder"):
    print(item)

print("\nFiles with .txt extension:")
for item in os.listdir("test_folder"):
    full_path = os.path.join("test_folder", item)
    if os.path.isfile(full_path) and item.endswith(".txt"):
        print(item)