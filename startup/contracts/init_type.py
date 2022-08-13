import smartpy as sp

class InitType(sp.Contract):
    def __init__(self):
        self.init_type(sp.TRecord(const = sp.TNat))
        self.init(const = 1)

    @sp.offchain_view()
    def scan(self):
        sp.result(self.data.const)


sp.add_compilation_target("init_type_compiled", InitType())