# 1) умножить каждый элемент на 2
nums = [1, 2, 3]
print(list(map(lambda x: x * 2, nums)))


# 2) длина каждого слова
words = ("apple", "banana", "cherry")
print(list(map(lambda w: len(w), words)))


# 3) привести к строкам
nums = [7, 8, 9]
print(list(map(lambda x: str(x), nums)))


# 4) квадрат каждого числа
nums = [2, 4, 6]
print(list(map(lambda x: x ** 2, nums)))


# 5) map по двум спискам
a = [1, 2, 3]
b = [10, 20, 30]
print(list(map(lambda x, y: x + y, a, b)))