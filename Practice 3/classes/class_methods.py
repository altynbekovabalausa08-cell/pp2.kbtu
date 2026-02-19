class Person:
    def __init__(self, name):
        self.name = name
    def greet(self):
        print("Hello, my name is " + self.name)
Person("Emil").greet()



class Student:
    def __init__(self, grade):   # constructor: sets the initial grade
        self.grade = grade

    def improve(self):           # method: increases the grade
        self.grade += 1

s = Student(9)                   # create object
s.improve()
print(s.grade)

class Math:
    def multiply(self, a, b):
        return a * b

print(Math().multiply(4, 5))

