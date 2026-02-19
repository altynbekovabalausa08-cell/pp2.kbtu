# 1) общий атрибут класса
class MyClass:
    x = 5
print(MyClass.x)


# 2) доступ через объект
class MyClass:
    x = 5
p = MyClass()
print(p.x)


class A:
    x = 1
A.x = 99
print(A().x)


# 4) “перекрыть” атрибут класса
class A:
    x = 1
p = A()
p.x = 7
print(A.x, p.x)


# 5) проверка/получение 
class Person:
    age = 36
print(hasattr(Person, "age"))
print(getattr(Person, "age"))