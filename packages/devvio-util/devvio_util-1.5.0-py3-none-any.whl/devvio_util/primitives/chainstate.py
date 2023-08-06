from devvio_util.primitives.devv_constants import kPROTOCOL_VERSION
from devvio_util.primitives.address import Address
from devvio_util.primitives.smart_coin import SmartCoin


class Chainstate:

    def __init__(self):
        self._state_map = {}

    def get_amount(self, coin_id: int, addr: Address):
        addr_iter = self._state_map.get(addr.get_hex_str())
        if addr_iter:
            coin_map = addr_iter[1]
            coin_iter = coin_map[coin_id]
            if coin_iter:
                amount = coin_map[coin_id]
                return amount
        return 0

    def add_coin(self, coin: SmartCoin):
        no_error = True
        it = self._state_map.get(coin.get_address().get_hex_str())
        if it:
            it[1][coin.get_coin()] += coin.get_amount()
            print(
                f"ChainState::addCoin(): addr({coin.get_address().get_hex_str()}) coin({coin.getCoin()}): \
                    added {coin.getAmount()} new balance({it[1][coin.get_coin()]})")
        else:
            inner = {}
            inner[coin.get_coin()] = coin.get_amount()
            self._state_map[coin.get_address().get_hex_str()] = inner
            print(
                f"ChainState::AddCoin(): addr({coin.get_address().get_hex_str()}) coin({coin.get_coin()}) \
                    amount({coin.get_amount()}) result({no_error})")
        return no_error


class ChainCheckpoint:
    def __init__(self):
        self._version = kPROTOCOL_VERSION
        self._highest_block_hash = None
        self._chainstate_summary = None
        self._signer = None
        self._checkpoint_hash = None
        self._signature = None
