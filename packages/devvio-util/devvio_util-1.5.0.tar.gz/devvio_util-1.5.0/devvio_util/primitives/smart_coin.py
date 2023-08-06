from devvio_util.primitives.address import Address


class SmartCoin:

    def __init__(self, addr: Address, coin: int, amount: int = 0):
        self._add = addr
        self._coin = coin
        self._amount = amount

    def get_address(self) -> Address:
        return self._addr

    def get_coin(self) -> int:
        return self._coin

    def get_amount(self) -> int:
        return self._amount
