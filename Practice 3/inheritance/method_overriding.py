# 1) Calling parent method before adding child behavior
class Dog(Animal):
    def speak(self):
        super().speak()
        print("Woof")
Dog().speak()


# 2) Polymorphism: Using the same method name for different classes
class Car:
    def move(self): print("Drive")
class Boat:
    def move(self): print("Sail")
for v in (Car(), Boat()):
    v.move()


# 3) Overriding a method to change how data is displayed
class Person:
    def __init__(self, name): self.name = name
    def show(self): print(self.name)

class Student(Person):
    def show(self): print("Student:", self.name)
Student("Emil").show()


# 4) Basic Method Overriding (Child replaces Parent's logic)
class Parent:
    def welcome(self): print("Welcome (parent)")
class Child(Parent):
    def welcome(self): print("Welcome (child)")
Child().welcome()