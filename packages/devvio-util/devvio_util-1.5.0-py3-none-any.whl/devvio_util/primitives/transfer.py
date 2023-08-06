from devvio_util.primitives.devv_constants import kUINT64_SIZE, kTRANSFER_NONADDR_DATA_SIZE
from devvio_util.primitives.address import Address
from devvio_util.primitives.utils import InputBuffer, set_int64, set_uint64


class Transfer:
    def __init__(self, xfer: dict or bytes or InputBuffer or None = None):
        self._addr = None
        self._delay = None
        self._amount = None
        self._coin_id = None
        self._canonical = None
        self._size = 0
        if isinstance(xfer, bytes):
            self.from_canonical(xfer)
        if isinstance(xfer, InputBuffer):
            self.from_buffer(xfer)
        elif isinstance(xfer, dict):
            self.from_dict(xfer)
        elif xfer is not None:
            raise Exception(f"Invalid Transfer: could not initialize from {type(xfer)}")

    def from_canonical(self, xfer_bin: bytes):
        self._canonical = None
        try:
            addr_size = int.from_bytes(xfer_bin[1], 'little') + 1
            self._addr = Address(bytes(xfer_bin[:addr_size]))
            self._coin_id = int.from_bytes(xfer_bin[addr_size: addr_size + kUINT64_SIZE], 'little')
            self._amount = int.from_bytes(xfer_bin[addr_size + kUINT64_SIZE: addr_size + kUINT64_SIZE * 2], 'little',
                                          signed=True)
            self._delay = int.from_bytes(xfer_bin[addr_size + kUINT64_SIZE * 2: addr_size + kUINT64_SIZE * 3], 'little')
            self._canonical = bytes(xfer_bin)
            self._size = addr_size + kTRANSFER_NONADDR_DATA_SIZE
        except IndexError:
            raise Exception("Invalid Transfer: bytes index error")

    def from_buffer(self, buffer: InputBuffer):
        self._canonical = None
        buffer_index = buffer.tell()
        addr_size = buffer.get_next_uint8()
        addr_bin = buffer.get_next_bytes(addr_size)
        if not addr_bin:
            raise Exception("Invalid Transfer: buffer EOF")
        self._addr = Address(addr_bin)
        self._size = addr_size + kTRANSFER_NONADDR_DATA_SIZE
        self._canonical = buffer.get_bytes(buffer_index, self._size)
        if not self._canonical:
            raise Exception("Invalid Transfer: buffer too small")
        self._coin_id = buffer.get_next_uint64()
        self._amount = buffer.get_next_int64()
        self._delay = buffer.get_next_uint64()

    def set_canonical(self):
        if not isinstance(self._amount, int):
            raise Exception("Invalid Transfer: invalid amount")
        if not isinstance(self._delay, int):
            raise Exception("Invalid Transfer: invalid delay")
        if not isinstance(self._coin_id, int):
            raise Exception(f"Invalid Transfer: invalid coin_id {self._coin_id}")
        if isinstance(self._addr, str):
            self._addr = Address(self._addr)
        if not isinstance(self._addr, Address):
            raise Exception("Invalid Transfer: invalid Address")
        self._canonical = bytes()
        self._size = self._addr.get_size() + kTRANSFER_NONADDR_DATA_SIZE
        self._canonical += self._addr.get_canonical()
        self._canonical += set_uint64(self._coin_id)
        self._canonical += set_int64(self._amount)
        self._canonical += set_uint64(self._delay)
        if len(self._canonical) != self._size + 1:
            raise Exception(f"Invalid Transfer: canonical size invalid ({self._size} != {len(self._canonical)})")

    def __bool__(self):
        return self._canonical is not None

    def __str__(self):
        return str(self.get_dict())

    def get_dict(self):
        res = {
            "amount": self._amount,
            "delay": self._delay,
            "coin": self._coin_id,
            "address": str(self._addr)
        }
        return res

    def get_coin(self) -> int:
        return self._coin_id

    def get_addr(self) -> Address:
        return self._addr

    def get_addr_str(self) -> str:
        return str(self._addr)

    def get_amount(self) -> int:
        return self._amount

    def get_delay(self) -> int:
        return self._delay

    def get_size(self) -> int:
        return self._size

    def get_canonical(self) -> bytes:
        return self._canonical

    def to_dict(self) -> dict:
        dict_transfer = dict()
        dict_transfer['address'] = self.get_addr()
        dict_transfer['amount'] = self.get_amount()
        dict_transfer['coin'] = self.get_coin_id()
        dict_transfer['delay'] = self.get_delay()
        return dict_transfer

    def from_dict(self, xfer_dict: dict):
        self._delay = xfer_dict.get('delay')
        self._coin_id = xfer_dict.get('coin')
        self._amount = xfer_dict.get('amount')
        addr = xfer_dict.get('address')
        if isinstance(addr, str):
            self._addr = Address(addr)
        if isinstance(addr, Address):
            self._addr = addr
        self.set_canonical()

    @staticmethod
    def get_xfers_from_buffer(buffer: InputBuffer, offset: int, num_bytes: int):
        xfers = []
        buffer.seek(offset)
        while buffer.tell() < offset + num_bytes:
            xfers.append(Transfer(buffer))
        return xfers
