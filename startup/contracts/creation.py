import smartpy as sp

# very useful for NFT market 
class Created(sp.Contract):
    def __init__(self):
        self.init_type(sp.TRecord(a = sp.TInt, b = sp.TNat))

    @sp.entry_point
    def myEntryPoint(self, params):
        self.data.a += params.x
        self.data.b += params.y

class Created2(sp.Contract):
    def __init__(self):
        self.init(sp.record(a = sp.int(1), b = sp.nat(2)))

    @sp.entry_point
    def myEntryPoint(self, params):
        self.data.a += params.x
        self.data.b += params.y

class Creator(sp.Contract):
    def __init__(self, baker):
        self.baker = baker
        self.created = Created()
        self.created2 = Created2()
        self.init(x = sp.none,
                  l = sp.build_lambda(self.opopop))


    @sp.entry_point
    def create1(self):
        self.data.x = sp.some(sp.create_contract(storage = sp.record(a = 12, b = 15),
            contract = self.created))

    @sp.entry_point
    def create2(self):
        sp.create_contract(storage = sp.record(a = 12, b = 15), contract = self.created, amount = sp.tez(2))
        sp.create_contract(storage = sp.record(a = 12, b = 16), contract = self.created, amount = sp.tez(2))

    @sp.entry_point
    def create3(self):
        self.data.x = sp.some(sp.create_contract(storage = sp.record(a = 12, b = 15), contract = self.created, baker = self.baker))
        pass

    @sp.entry_point
    def create4(self, l):
        sp.for x in l:
        sp.create_contract(storage = sp.record(a = x, b = 15), contract = self.created, baker = sp.none)

    @sp.entry_point
    def create5(self):
        self.data.x = sp.some(sp.create_contract(contract = self.created2))

    def opopop(self, x):
        sp.result(sp.create_contract_operation(storage = sp.record(a = x, b = 15), contract = self.created))

    @sp.entry_point
    def create_op(self):
        operation, address = sp.match_record(self.data.l(42), "operation", "address")
        sp.operations().push(operation)
        self.data.x = sp.some(address)
@sp.add_test(name = "Create")
def test():
    scenario = sp.test_scenario()
    scenario.h1("Create Contract")
    baker = sp.test_account("Ma Baker")
    c1 = Creator(sp.some(baker.public_key_hash))
    c1.set_initial_balance(sp.tez(10))
    scenario += c1
    c1.create1()
    c1.create2()
    # c1.create3()
    c1.create4([1, 2])
    scenario.register(c1.created)
    dyn0 = scenario.dynamic_contract(0, c1.created)

    dyn0.call("myEntryPoint", sp.record(x = 1, y = 16))
    scenario.verify(dyn0.data.a == 13)
    scenario.verify(dyn0.balance == sp.tez(0))

    dyn0.call("myEntryPoint", sp.record(x = 1, y = 15)).run(amount = sp.tez(2))
    scenario.verify(dyn0.data.a == 14)
    scenario.verify(dyn0.balance == sp.tez(2))
    scenario.show(dyn0.baker)
    scenario.show(dyn0.address)

sp.add_compilation_target("create_contract", Creator(sp.none))