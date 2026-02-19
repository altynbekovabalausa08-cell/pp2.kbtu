# 1) class inherits from two classes
class A:
    def a(self): print("A")

class B:
    def b(self): print("B")

class C(A, B):
    pass

C().a(); C().b()


# 2) name conflict: method chosen by MRO (left to right)
class A:
    def f(self): print("A")

class B:
    def f(self): print("B")

class C(A, B):
    pass

C().f()   # A


# 3) explicitly calling a specific class method
B.f(C())


# 4) mixin style
class Logger:
    def log(self, msg): print("LOG:", msg)

class Service(Logger):
    def run(self): self.log("running")

Service().run()


# 5) super() in method chain
class A:
    def f(self): print("A")

class B(A):
    def f(self):
        super().f()
        print("B")

B().f()
