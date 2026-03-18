from functools import reduce

numbers = [1, 2, 3, 4, 5, 6]

squared = list(map(lambda x: x ** 2, numbers))
print("Squared numbers:", squared)

even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
print("Even numbers:", even_numbers)

total = reduce(lambda a, b: a + b, numbers)
print("Sum of numbers:", total)

value = "123"
print("Original value:", value)
print("Type:", type(value))

converted_value = int(value)
print("Converted value:", converted_value)
print("Converted type:", type(converted_value))

float_value = float(converted_value)
print("Float value:", float_value)
print("Float type:", type(float_value))