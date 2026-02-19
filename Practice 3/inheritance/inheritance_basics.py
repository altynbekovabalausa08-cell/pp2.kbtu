# 1) Adding a new method to the child class
class Student(Person):
    def welcome(self):
        print("Welcome", self.name)
Student("Linus").welcome()


# 2) Calling the parent __init__ explicitly by name
class Student(Person):
    def __init__(self, name):
        Person.__init__(self, name)


# 3) Using super() to handle multiple arguments
class Student(Person):
    def __init__(self, name, year):
        super().__init__(name)
        self.year = year


# 4) Overriding a parent method with a child-specific version
class Student(Person):
    def printname(self):
        print("Student:", self.name)