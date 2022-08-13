import smartpy as sp

class Ancestor(sp.Contract):
    def __init__(self, x, y):
        self.init(
            x = x,
            y = y,
            t = 0,
        )
    
    @sp.entry_point
    def add_x(self, v):
        self.data.x += v

    @sp.entry_point
    def mul_y(self):
        self.data.y *= 2

    @sp.entry_point
    def double_t(self):
        self.data.t *= 2

    @sp.entry_point
    def set_t(self, v):
        self.data.t = v

class Descendant(Ancestor):
    def __init__(self):
        Ancestor.__init__(self, 1, 2)
        self.update_initial_storage(z = 42)

    @sp.entry_point
    def add_x(self, v):
        # call parent class method, very useful in using FA template 
        super().add_x.f(self, v)
        self.data.y = 20
        super().mul_y.f(self)

@sp.add_test(name = "inheritance")
def test():
    sc = sp.test_scenario()
    c = Descendant()
    sc += c
    c.add_x(1)
    sc.verify_equal(c.data.x, sp.nat(2))
    sc.verify_equal(c.data.y, sp.nat(40))


sp.add_compilation_target("inheritance_compiler", Descendant())