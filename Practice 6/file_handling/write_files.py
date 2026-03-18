with open("sample.txt", "w") as file:
    file.write("Hello, this is the first line.\n")
    file.write("This is the second line.\n")

print("File created and sample data written.")

with open("sample.txt", "a") as file:
    file.write("This line was appended.\n")
    file.write("Another appended line.\n")

print("New lines appended.")

with open("sample.txt", "r") as file:
    content = file.read()

print("\nUpdated file content:")
print(content)