# 1) оставить только чётные
nums = [1, 2, 3, 4, 5]
print(list(filter(lambda x: x % 2 == 0, nums)))


# 2) оставить >= 18
ages = [5, 12, 17, 18, 24, 32]
print(list(filter(lambda x: x >= 18, ages)))


# 3) оставить слова длиной > 3
words = ["a", "to", "pear", "banana"]
print(list(filter(lambda w: len(w) > 3, words)))


# 4) убрать пустые строки
texts = ["hi", "", "ok", ""]
print(list(filter(lambda s: s != "", texts)))

