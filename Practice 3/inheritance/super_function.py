# 1) super() calls the parent's __init__
class Person:
    def __init__(self, fname):
        self.fname = fname

class Student(Person):
    def __init__(self, fname):
        super().__init__(fname)

print(Student("Emil").fname)


# 2) super() + a new field
class Student(Person):
    def __init__(self, fname, year):
        super().__init__(fname)
        self.year = year
print(Student("Emil", 2026).year)


# 3) super() can call parent methods
class Person:
    def hello(self):
        print("Hello")

class Student(Person):
    def hello(self):
        super().hello()
        print("from Student")
Student().hello()


# 4) super() without arguments (the standard way to write it)
class A:
    def f(self): print("A")
class B(A):
    def f(self):
        super().f()
B().f()


# 5) super() as “access to parent behavior”
class Parent:
    def info(self): return "Parent"
class Child(Parent):
    def info(self): return super().info() + " + Child"
print(Child().info())