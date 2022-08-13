# Some Syntax - Example for illustrative purposes only.

# This contract here is simply to show a few syntax constructions.

import smartpy as sp

class SyntaxDemo(sp.Contract):
    def __init__(self, b, s, h, i, **kargs):
        self.bb = s
        self.init(b = b,
                  s = s,
                  h = h,
                  i = i,
                  pkh = sp.key_hash("tz1YB12JHVHw9GbN66wyfakGYgdTBvokmXQk"),
                  n = sp.nat(123),
                  m = sp.map(),
                  aaa = sp.set([1, 2, 3]),
                  abc=[sp.some(123), sp.none],
                  abca = sp.utils.vector([sp.some(123), sp.none]),
                  ddd = sp.range(0, 10),
                  **kargs)

    @sp.entry_point
    def comparisons(self):
        sp.verify(self.data.i <= 123)
        sp.verify(2 + self.data.i == 12)
        sp.verify(2 + self.data.i != 1234)
        sp.verify(self.data.i + 4 != 123)
        sp.verify(self.data.i - 5 < 123)
        sp.verify(7 - self.data.i < 123)
        sp.verify(self.data.i > 3)
        sp.verify(4 * self.data.i > 3)
        sp.verify(self.data.i * 5 > 3)
        sp.verify(self.data.i >= 3)
        sp.verify(3 < self.data.i)
        sp.verify(3 <= self.data.i)
        sp.verify(3000 > self.data.i)
        sp.verify(3000 >= self.data.i)
        sp.verify(self.data.b & ((self.bb in "abcd") | (self.bb in "dcba")))
        sp.if 3 < self.data.i:
            sp.verify(4 < self.data.i)

    @sp.entry_point
    def someComputations(self, params):
        sp.verify(self.data.i <= 123)
        self.data.i = self.data.i + params.y
        self.data.acb = params.x
        self.data.i = 100
        self.data.i = self.data.i - 1
        sp.verify(sp.add(sp.nat(4), sp.nat(5)) == 9)
        sp.verify(sp.add(sp.int(-4), sp.nat(5)) == 1)
        sp.verify(sp.add(sp.nat(5), sp.int(-4)) == 1)
        sp.verify(sp.add(sp.int(-4), sp.int(5)) == 1)
        sp.verify(sp.mul(sp.nat(4), sp.nat(5)) == 20)
        sp.verify(sp.mul(sp.int(-4), sp.nat(5)) == -20)
        sp.verify(sp.mul(sp.nat(5), sp.int(-4)) == -20)
        sp.verify(sp.mul(sp.int(-4), sp.int(5)) == -20)

    @sp.entry_point
    def localVariable(self):
        x = sp.local('x', self.data.i)
        x.value *= 2
        self.data.i = 10
        self.data.i = x.value

    @sp.entry_point
    def iterations(self):
        x = sp.local('x', self.data.i)
        for i in range(0, 5):
            x.value = i
        sp.for i in sp.range(0, 5):
            x.value = i
        self.data.i = sp.to_int(self.data.n)
        self.data.i = 5
        with sp.while_(self.data.i <= 42):
            self.data.i += 2
        sp.if self.data.i <= 123:
            x.value = 12
            self.data.i += x.value
        sp.else:
            x.value = 5
            self.data.i = x.value

    @sp.entry_point
    def myMessageName4(self):
        sp.for x in self.data.m.items():
            self.data.i += x.key * x.value

    @sp.entry_point
    def myMessageName5(self):
        sp.for x in self.data.m.keys():
            self.data.i += 2 * x

    @sp.entry_point
    def myMessageName6(self, params):
        sp.for x in self.data.m.values():
            self.data.i += 3 * x
        self.data.aaa.remove(2)
        self.data.aaa.add(12)
        self.data.abc.push(sp.some (16))
        self.data.abca[0] = sp.some (16)
        sp.if self.data.aaa.contains(12):
            self.data.m[42] = 43
        self.data.aaa.add(sp.as_nat(-params))

# Tests
@sp.add_test(name = "Syntax")
def test():
    # define a contract
    c1 = SyntaxDemo(True, "abc", sp.bytes('0x0000ab112233aa'), 7, toto = "ABC", acb = 'toto', f = False)
    # show its representation
    scenario = sp.test_scenario()
    scenario.h1("Syntax")
    scenario.h2("Contract")
    scenario += c1
    scenario.h2("Message execution")
    c1.comparisons().run(valid = False)
    scenario.h2("Message execution")
    c1.someComputations(x = 'abcd', y = 12)
    scenario.h2("Message execution")
    c1.localVariable()
    c1.iterations()
    scenario.h2("Message execution")
    c1.myMessageName6(-18)
    scenario.verify(c1.data.b)
    scenario.verify(c1.data.i == 55)
    scenario.show(c1.data)
    scenario.show(c1.data, html = False)
    scenario.verify_equal(c1.data, sp.record(acb = 'abcd', abc = [sp.some(16), sp.some(123), sp.none],abca = sp.utils.vector([sp.some(16),  sp.none]), b = True, f = False, h = sp.bytes('0x0000ab112233aa'), i = 55, n = 123, s = 'abc', toto = 'ABC', aaa = sp.set([1, 3, 12, 18]), m = {42:43}, ddd = sp.list([0,1,2,3,4,5,6,7,8,9]), pkh = sp.key_hash("tz1YB12JHVHw9GbN66wyfakGYgdTBvokmXQk")))
    scenario.simulation(c1)

sp.add_compilation_target("syntax", SyntaxDemo(True, "abc", sp.bytes("0xaabb"), 7, toto = "ABC", acb = "toto", f = False))
