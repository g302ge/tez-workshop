import smartpy as sp

class StoreContract(sp.Contract):
    def __init__(self, value):
        self.init(storedValue = value)

    @sp.entry_point
    def store(self, value):
        self.data.storedValue = value


@sp.add_test(name = "StoreContract")
def test():
    scenario = sp.test_scenario()
    contract = StoreContract(1)
    scenario += contract
    contract.store(2)

sp.add_compilation_target("stored_contract_compiled", StoreContract(1))
