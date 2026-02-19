# 1) обычная сортировка
a = ("b", "g", "a", "d")
print(sorted(a))


# 2) сортировка по убыванию
nums = [3, 1, 4, 2]
print(sorted(nums, reverse=True))


# 3) сортировка строк по длине
words = ["banana", "kiwi", "apple"]
print(sorted(words, key=lambda w: len(w)))


# 4) сортировка пар по второму элементу
pairs = [(1, 9), (2, 3), (4, 1)]
print(sorted(pairs, key=lambda t: t[1]))


# 5) сортировка слов без учёта регистра
names = ["bob", "Alice", "dave"]
print(sorted(names, key=lambda s: s.lower()))