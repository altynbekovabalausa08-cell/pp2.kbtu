print("Hello")
print('Hello')

# String checking
text = "Python123"
print(text.isalpha())       # False (has numbers)
print(text.isalnum())       # True
print(text.isdigit())       # False
print(text.startswith("Py")) # True
print(text.endswith("123"))  # True

for x in "banana":
  print(x)


b = "Hello, World!"
print(b[2:5])