from devvio_util.primitives.transfer import Transfer
from devvio_util.primitives.address import Address
from devvio_util.primitives.devv_constants import kUINT32_SIZE
from devvio_util.primitives.utils import InputBuffer, set_uint64, set_int64

MIN_SIZE = 4


class DelayedItem:
    """
     * Constructor
     * @param delay
     * @param delta
     """

    def __init__(self, delay_val: int = 0, delta_val: int = 0):
        self.delay = delay_val
        self.delta = delta_val


class Summary:

    def __init__(self, buffer: InputBuffer):
        self._summaryMap = {}

        addr_count = buffer.get_next_uint32()
        for i in range(addr_count):
            addr_size = buffer.get_next_uint8()
            one_addr = Address(buffer.get_next_bytes(addr_size, increment=True))
            delayed = {}
            coin_map = {}
            delayed_count = buffer.get_next_uint64()
            coin_count = buffer.get_next_uint64()
            for j in range(delayed_count):
                coin = buffer.get_next_uint64()
                delay = buffer.get_next_uint64()
                delta = buffer.get_next_int64()
                delayed_item = DelayedItem(delay, delta)
                delayed[coin] = delayed_item

            for j in range(coin_count):
                coin = buffer.get_next_uint64()
                delta = buffer.get_next_int64()
                coin_map[coin] = delta

            self._summaryMap[one_addr.get_hex_str()] = (delayed, coin_map)  # TODO: validate this key 'get_hex_str'

    def get_map(self) -> dict:
        return self._summaryMap

    def is_sane(self) -> bool:
        if not self._summaryMap:
            return False
        coin_total = 0
        for addr, summaryPair in self._summaryMap.items():
            delayed_map = summaryPair[0]
            delta_map = summaryPair[1]
            for coin_id, delayPair in delayed_map.items():
                coin_total += delayPair[1]
            for coin_id, delta in delta_map.items():
                coin_total += delta
        if coin_total != 0:
            print(f"Summary state invalid: {self.get_map()}")
            return False
        return True

    def get_xfers(self) -> list:
        xfers = []
        for addr, summaryPair in self._summaryMap.items():
            delayed_map = summaryPair[0]
            delta_map = summaryPair[1]
            for coin_id, delayPair in delayed_map.items():
                one_xfer = {
                    'address': addr,
                    'coin': coin_id,
                    'amount': delayPair[1],
                    'delay': delayPair[0]
                }
                xfers.append(Transfer(one_xfer))
            for coin_id, delta in delta_map.items():
                one_xfer = {
                    'address': addr,
                    'coin': coin_id,
                    'amount': delta,
                    'delay': 0
                }
                xfers.append(Transfer(one_xfer))
        return xfers

    def get_canonical(self):
        out = bytes()
        addr_count = len(self._summaryMap)
        out += addr_count.to_bytes(kUINT32_SIZE, 'little', signed=False)
        for addr, pair in self._summaryMap.items():
            out += Address(addr).get_canonical()
            delayed_map, coin_map = pair
            out += set_uint64(len(delayed_map))
            out += set_uint64(len(coin_map))
            for coin, xfer in delayed_map.items():
                out += set_uint64(coin)
                out += set_uint64(xfer['delay'])
                out += set_int64(xfer['delta'])
            for coin, delta in coin_map.items():
                out += set_uint64(coin)
                out += set_int64(delta)
        return out
