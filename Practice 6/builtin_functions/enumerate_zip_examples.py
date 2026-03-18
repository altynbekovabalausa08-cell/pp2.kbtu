fruits = ["apple", "banana", "cherry"]

print("Using enumerate():")
for index, fruit in enumerate(fruits):
    print(index, fruit)

names = ["Alice", "Bob", "Charlie"]
scores = [85, 90, 78]

print("\nUsing zip():")
for name, score in zip(names, scores):
    print(name, score)