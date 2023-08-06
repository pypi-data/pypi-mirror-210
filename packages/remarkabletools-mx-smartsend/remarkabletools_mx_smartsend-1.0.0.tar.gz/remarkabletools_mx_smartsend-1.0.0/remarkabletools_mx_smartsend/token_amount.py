from multiversx_sdk_core import Address, TokenPayment

class TokenAmount:
    def __init__(self, addr: str, amount: TokenPayment):
        self.address: Address = Address.from_bech32(addr)
        self.amount: TokenPayment = amount