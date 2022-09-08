import smartpy as sp


t_market_item_state = sp.TVariant(
    created = sp.TAddress,
    release = sp.TAddress,
    inactive = sp.TAddress,
)
t_market_item = sp.TRecord(
    id = sp.TNat,
    address = sp.TAddress,
    token_id = sp.TNat,
    seller = sp.TAddress,
    buyer = sp.TOption(sp.TAddress),
    price = sp.TMutez,
    state = t_market_item_state
)

# FA2 parameters specifications

t_operator_permission = sp.TRecord(
    owner=sp.TAddress, operator=sp.TAddress, token_id=sp.TNat
).layout(("owner", ("operator", "token_id")))

t_transfer_batch = sp.TRecord(
    from_=sp.TAddress,
    txs=sp.TList(
        sp.TRecord(
            to_=sp.TAddress,
            token_id=sp.TNat,
            amount=sp.TNat,
        ).layout(("to_", ("token_id", "amount")))
    ),
).layout(("from_", "txs"))

t_transfer_params = sp.TList(t_transfer_batch)

class Market(sp.Contract):

    def __init__(self, owner, list_fee):
        
        self.init(
            item_id = sp.nat(1),
            owner_address = owner,
            list_fee = list_fee,
            market_items = sp.big_map(
                tkey=sp.TNat,
                tvalue=t_market_item,
            ),
            user_items = sp.big_map(
                tkey=sp.TAddress,
                tvalue=sp.TList(sp.TNat)
            )
        )
    
    @sp.offchain_view()
    def get_list_fee(self):
        sp.result(self.data.list_fee)
    
    @sp.entry_point
    def crerate_market_item(self, params):
        """
        list an NFT on market the parameter is 
        sp.TRecord(
            contract_address = sp.TAddress,
            token_id = sp.TNat,
            price = sp.TMutez
        ).layout("contract_address", ("token_id", "price"))
        """
        sp.set_type(
            params,
            sp.TRecord(
                contract_address = sp.TAddress,
                token_id = sp.TNat,
                price = sp.TMutez
            ).layout(("contract_address", ("token_id", "price")))
        )
        sp.verify(params.price > sp.mutez(0), "price must be at least 1 mutez")
        sp.verify(sp.amount == self.data.list_fee, "fee must be equal to listing fee")

        # current FA2 contract has no on-chain view 
        is_operator = sp.contract(
            t_operator_permission, 
            params.contract_address, 
            "is_operator"
            ).open_some("is_operator must be defined")
        
        # TODO: using the balance_of to check the permission or offchain-view check 

        item_id = self.data.item_id
        item = sp.record(
            id = item_id,
            address = params.contract_address,
            token_id = params.token_id,
            seller = sp.sender,
            buyer = sp.none,
            price = params.price,
            state = sp.variant("created", sp.sender)
        )
        self.data.market_items[item_id] = item
        with sp.if_(self.data.user_items.contains(sp.sender)):
            self.data.user_items[sp.sender].push(item_id)
        with sp.else_():
            self.data.user_items[sp.sender] = sp.list([item_id], t = sp.TNat)

        self.data.item_id += sp.nat(1)



    @sp.entry_point
    def delete_market_item(self, params):
        """
        make the item inactive 
        """
        sp.set_type(params, sp.TNat)
        sp.verify(params < self.data.item_id, "id must < current id")
        sp.verify(self.data.market_items.contains(params), "item is not exists")
        item = self.data.market_items[params]
        with sp.if_(item.state.is_variant("created")):
            item.state = sp.variant("inactive", sp.sender)

    @sp.entry_point
    def create_market_sale(self, params):
       sp.set_type(
           params,
           sp.TRecord(
               address = sp.TAddress,
               item_id = sp.TNat
           ).layout(("address", "item_id"))
       )
       sp.verify(self.data.market_items.contains(params.item_id), "item is not exists")
       item = self.data.market_items[params.item_id]
       sp.verify(item.price == sp.amount, "please the asking price")
       transfer = sp.contract(t_transfer_params, params.address, "transfer").open_some("address is not a FA2 contract")
       
       # transfer amount 
       sp.transfer(sp.list([
           sp.record(
               from_ = item.seller,
               txs = sp.list([
                   sp.record(
                       to_ = sp.sender,
                       token_id = item.token_id,
                       amount = sp.nat(1)
                   )
               ])
           )
       ], t= t_transfer_batch), sp.tez(0), transfer)

       profit = sp.amount - self.data.list_fee
       sp.send(self.data.owner_address, self.data.list_fee)
       sp.send(item.seller, profit)

       item_id = item.id
       
       with sp.if_(self.data.user_items.contains(sp.sender)):
           self.data.user_items[sp.sender].push(item_id)     
       with sp.else_():
            self.data.user_items[sp.sender] = sp.list([item_id], t = sp.TNat)

       item.buyer = sp.some(sp.sender)
       item.state = sp.variant("release", sp.sender)



    @sp.offchain_view()
    def fetch_active_items(self):
        """
        fetch the active items
        """
        result = sp.local("result", sp.list(l=[], t=t_market_item)).value
        sp.compute
        with sp.for_("index", sp.range(1, self.data.item_id+1)) as index:
            item = self.data.market_items[index]
            with sp.if_(item.state.is_variant("created")):
                result.push(item)
        
        sp.result(result)

    @sp.offchain_view()
    def fetch_purchased_items(self):
        """
        it is your turn  
        """
        pass

    @sp.offchain_view()
    def fetch_created_items(self):
        """
        it it your turn
        """
        pass


sp.add_compilation_target(
    "nft_market", 
    Market(
        sp.address("tz1TZBoXYVy26eaBFbTXvbQXVtZc9SdNgedB"), 
        sp.tez(1))
)