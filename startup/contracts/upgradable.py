import smartpy as sp

class Upgradable(sp.Contract):
    def __init__(self, logic):
        self.init(logic = logic, value = 9)

    
    @sp.entry_point(lazify = True, lazy_no_code = True)
    def calc(self, value):
        self.data.value = self.data.logic(value)

    
    @sp.entry_point
    def upgrad_logic(self, logic):
        self.data.logic = logic


class UpgradContract(sp.Contract):
    def __init__(self, address):
        self.init(address = address)

    def calc_logic(data):
        t = sp.TNat
        unpacked = sp.unpack(data, t).open_some(message = "unpack nat failed")
        sp.result(unpacked+2)

    @sp.entry_point
    def do_upgrade(self):
        # sp.TLambda(t1, t2) t1 is the parameter type and the t2 is the result type 
        contract = sp.contract(sp.TLambda(sp.TBytes, sp.TNat), self.data.address, "upgrade_logic").open_some()
        sp.transfer(sp.build_lambda(UpgradContract.calc_logic), sp.tez(0), contract)

def origin_logic(data):
    t = sp.TNat
    unpacked = sp.unpack(data, t).open_some(message = "unpack nat failed")
    sp.result(unpacked+1)

sp.add_compilation_target("upgradable_target", Upgradable(sp.build_lambda(origin_logic)))
sp.add_compilation_target("upgradable_trigger", UpgradContract(sp.address("KT1C58ssiuw2Y92kK5VwXhE9k69P9aqhtP1Q")))