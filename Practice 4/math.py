import math
import random

# Example 1: Calculate square root
print("Example 1 - sqrt(25):", math.sqrt(25))

# Example 2: Calculate power
print("Example 2 - 2^3:", math.pow(2, 3))

# Example 3: Ceiling and floor functions
print("Example 3 - ceil(4.2):", math.ceil(4.2), "floor(4.8):", math.floor(4.8))

# Convert degree to radian
degree = float(input("Input degree: "))
radian = degree * (math.pi / 180)
print("Output radian:", round(radian, 6))

# Print value of pi
print("Pi value:", math.pi)

# Generate a random integer between 1 and 10
print("Random number:", random.randint(1, 10))