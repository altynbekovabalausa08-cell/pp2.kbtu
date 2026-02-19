# 1) *args как кортеж
def total(*nums):
    print(sum(nums))
total(1, 2, 3)


# 2) **kwargs как словарь
def show(**d):
    print(d)
show(age=25, city="Oslo")


# 3) вместе: обычные + *args + **kwargs
def my_function(title, *args, **kwargs):
    print("Title:", title)
    print("Args:", args)
    print("Kwargs:", kwargs)
my_function("User", "Emil", "Tobias", age=25, city="Oslo")


# 4) *args + доступ по индексу
def first(*a):
    print(a[0])
first("A", "B", "C")


# 5) **kwargs + get
def safe(**k):
    print(k.get("name", "Unknown"))
safe(city="Almaty")