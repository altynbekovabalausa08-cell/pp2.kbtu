# 1) несколько аргументов
def full_name(fname, lname):
    print(fname, lname)
full_name("John", "Doe")


# 2) keyword arguments (порядок не важен)
def youngest(child3, child2, child1):
    print("Youngest is", child3)
youngest(child1="Emil", child2="Tobias", child3="Linus")


# 3) значение по умолчанию
def country(name, c="Norway"):
    print(name, "from", c)
country("John")
country("John", "Kazakhstan")


# 4) произвольные позиционные *args
def kids(*names):
    print("First:", names[0])
kids("Emil", "Tobias", "Linus")


# 5) произвольные именованные **kwargs
def person(**info):
    print(info["name"], info["age"])
person(name="John", age=36)