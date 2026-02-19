# 1) класс с атрибутом
class MyClass:
    x = 5
p1 = MyClass()
print(p1.x)


# 2) пустой класс (заготовка)
class Empty:
    pass


# 3) несколько объектов
class Counter:
    value = 0
a = Counter(); b = Counter()
print(a.value, b.value)


# 4) атрибут можно “добавить” объекту
class A:
    pass
obj = A()
obj.name = "John"
print(obj.name)


# 5) удаление объекта (в учебных примерах)
class B:
    x = 1
p = B()