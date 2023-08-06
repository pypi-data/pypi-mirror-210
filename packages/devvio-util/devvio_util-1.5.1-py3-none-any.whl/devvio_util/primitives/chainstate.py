from devvio_util.primitives.devv_constants import kPROTOCOL_VERSION
from devvio_util.primitives.address import Address
from devvio_util.primitives.smart_coin import SmartCoin
from devvio_util.primitives.summary import Summary


class Chainstate:

    def __init__(self):
        self._state_map = dict()

    def get_state_map(self) -> dict:
        return self._state_map

    def get_amount(self, coin_id: int, addr: Address):
        addr_iter = self._state_map.get(addr.get_hex_str())
        if addr_iter:
            coin_map = addr_iter[1]
            coin_iter = coin_map[coin_id]
            if coin_iter:
                amount = coin_map[coin_id]
                return amount
        return 0

    def add_coin(self, coin: SmartCoin) -> bool:
        no_error = True
        if not coin:
            return False
        if not isinstance(self._state_map, dict):
            return False
        it = self._state_map.get(coin.get_address().get_hex_str())
        if it and it.get(coin.get_coin()):
            it[coin.get_coin()] += coin.get_amount()
        elif it:
            it[coin.get_coin()] = coin.get_amount()
        else:
            inner = dict()
            inner[coin.get_coin()] = coin.get_amount()
            self._state_map[coin.get_address().get_hex_str()] = inner
        return no_error

    def update(self, summ: Summary) -> bool:
        if not summ.is_sane():
            raise Exception('Chainstate update failed: Summary is not sane')
        prev_state = self._state_map
        for xfer in summ.get_xfers():
            coin = SmartCoin(xfer.get_addr(), xfer.get_coin(), xfer.get_amount())
            if not self.add_coin(coin):
                self._state_map = prev_state
                raise Exception(f'Chainstate update failed: failed to add SmartCoin to state '
                                f'(addr:{coin.get_address()}; coin:{coin.get_coin()}; amount:{coin.get_amount()})')
        return True


class ChainCheckpoint:
    def __init__(self):
        self._version = kPROTOCOL_VERSION
        self._highest_block_hash = None
        self._chainstate_summary = None
        self._signer = None
        self._checkpoint_hash = None
        self._signature = None
