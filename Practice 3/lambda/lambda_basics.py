# 1) lambda как “маленькая функция”
x = lambda a: a + 10
print(x(5))


# 2) lambda с 2 параметрами
mul = lambda a, b: a * b
print(mul(2, 3))


# 3) функция, которая возвращает lambda
def make_multiplier(n):
    return lambda a: a * n
doubler = make_multiplier(2)
print(doubler(11))


# 4) lambda в обычном вызове
print((lambda s: s.upper())("hello"))
