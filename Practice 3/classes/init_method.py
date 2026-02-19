# 1) __init__ сохраняет параметры
class Person:
    def __init__(self, name):
        self.name = name
p = Person("Emil")
print(p.name)


# 2) __init__ с двумя полями
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
p = Person("John", 36)
print(p.age)


# 3) значения по умолчанию
class Box:
    def __init__(self, size=1):
        self.size = size
print(Box().size, Box(5).size)


# 4) вычисления при создании
class Circle:
    def __init__(self, r):
        self.r = r
        self.area = 3.14 * r * r
print(Circle(2).area)


# 5) хранение списка
class Bag:
    def __init__(self):
        self.items = []
b = Bag(); b.items.append("pen")
print(b.items)