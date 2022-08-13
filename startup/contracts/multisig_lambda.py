import smartpy as sp

# !!! useful for DAO design to execute functions 
class MultisigLambda(sp.Contract):
    """Multiple members vote for executing lambdas.

    This contract can be originated with a list of addresses and a number of
    required votes. Any member can submit as much lambdas as he wants and vote
    for active proposals. When a lambda reaches the required votes, its code is
    called and the output operations are executed. This allows this contract to
    do anything that a contract can do: transferring tokens, managing assets,
    administrating another contract...

    When a lambda is applied, all submitted lambdas until now are inactivated.
    The members can still submit new lambdas.
    """

    def __init__(self, members, required_votes):
        """Constructor

        Args:
            members (sp.TSet(sp.TAddress)): people who can submit and vote for
                lambda.
            required_votes (sp.TNat): number of votes required
        """
        assert required_votes <= len(members), "required_votes must be <= len(members)"
        self.init(
            lambdas=sp.big_map(
                tkey=sp.TNat, tvalue=sp.TLambda(sp.TUnit, sp.TList(sp.TOperation))
            ),
            votes=sp.big_map(tkey=sp.TNat, tvalue=sp.TSet(sp.TAddress)),
            nextId=0,
            inactiveBefore=0,
            members=sp.set(members, t=sp.TAddress),
            required_votes=required_votes,
        )

    @sp.entry_point
    def submit_lambda(self, lambda_):
        """Submit a new lambda to the vote.

        Submitting a proposal does not imply casting a vote in favour of it.

        Args:
            lambda_(sp.TLambda(sp.TUnit,sp.TList(sp.TOperation))): lambda
                proposed to vote.
        Raises:
            `You are not a member`
        """
        sp.verify(self.data.members.contains(sp.sender), "You are not a member")
        self.data.lambdas[self.data.nextId] = lambda_
        self.data.votes[self.data.nextId] = sp.set()
        self.data.nextId += 1

    @sp.entry_point
    def vote_lambda(self, id):
        """Vote for a lambda.

        Args:
            id(sp.TNat): id of the lambda to vote for.
        Raises:
            `You are not a member`, `The lambda is inactive`, `Lambda not found`

        There is no vote against or pass. If someone disagrees with a lambda
        they can avoid to vote.
        """
        sp.verify(self.data.members.contains(sp.sender), "You are not a member")
        sp.verify(id >= self.data.inactiveBefore, "The lambda is inactive")
        sp.verify(self.data.lambdas.contains(id), "Lambda not found")
        self.data.votes[id].add(sp.sender)
        with sp.if_(sp.len(self.data.votes[id]) >= self.data.required_votes):
            sp.add_operations(self.data.lambdas[id](sp.unit))
            self.data.inactiveBefore = self.data.nextId

    @sp.onchain_view()
    def get_lambda(self, id):
        """Return the corresponding lambda.

        Args:
            id (sp.TNat): id of the lambda to get.

        Return:
            pair of the lambda and a boolean showing if the lambda is active.
        """
        sp.result(sp.pair(self.data.lambdas[id], id >= self.data.inactiveBefore))


if "templates" not in __name__:

    class Administrated(sp.Contract):
        def __init__(self, admin):
            self.init(admin=admin, value=sp.int(0))

        @sp.entry_point
        def set_value(self, value):
            sp.verify(sp.sender == self.data.admin)
            self.data.value = value

    @sp.add_test(name="MultisigLambda basic scenario", is_default=True)
    def basic_scenario():
        """Use the multisigLambda as an administrator of an example contract.

        Tests:
        - Origination
        - Lambda submission
        - Lambda vote
        """
        sc = sp.test_scenario()
        sc.h1("Basic scenario.")

        member1 = sp.test_account("member1")
        member2 = sp.test_account("member2")
        member3 = sp.test_account("member3")
        members = [member1.address, member2.address, member3.address]

        sc.h2("MultisigLambda: origination")
        c1 = MultisigLambda(members, required_votes=2)
        sc += c1

        sc.h2("Administrated: origination")
        c2 = Administrated(c1.address)
        sc += c2

        sc.h2("MultisigLambda: submit_lambda")

        def set_42(params):
            administrated = sp.contract(sp.TInt, c2.address, entry_point="set_value")
            sp.transfer(sp.int(42), sp.tez(0), administrated.open_some())

        lambda_ = sp.utils.lambda_operations_only(set_42)
        c1.submit_lambda(lambda_).run(sender=member1)

        sc.h2("MultisigLambda: vote_lambda")
        c1.vote_lambda(0).run(member1)
        c1.vote_lambda(0).run(member2)

        # We can check that the administrated contract received the transfer.
        sc.verify(c2.data.value == 42)
