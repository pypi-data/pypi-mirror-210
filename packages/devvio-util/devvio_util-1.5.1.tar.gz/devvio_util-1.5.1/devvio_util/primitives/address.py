from devvio_util.primitives.devv_constants import kNODE_ADDR_SIZE, kWALLET_ADDR_SIZE, kWALLET_ADDR_BUF_SIZE, \
    kNODE_ADDR_BUF_SIZE, kWALLET_SIG_BUF_SIZE, kNODE_SIG_BUF_SIZE
from devvio_util.primitives.utils import InputBuffer


class Address:
    def __init__(self, addr: str or bytes or InputBuffer = None):
        self._canonical = None
        self._size = None
        self.set_addr(addr)

    def set_addr(self, addr: str or bytes or InputBuffer):
        if not addr:
            raise Exception("Invalid Address: no bytes or string given")
        if isinstance(addr, str):
            addr_bin = bytes.fromhex(addr)
        elif isinstance(addr, bytes):
            addr_bin = addr
        elif isinstance(addr, InputBuffer):
            addr_bin = addr.get_next_prefixed_obj()
        else:
            raise Exception(f"Invalid Address: cannot initialize from type {type(addr)}")
        if not addr_bin:
            return None
        self._size = len(addr_bin)
        if self._size == kWALLET_ADDR_SIZE or self._size == kNODE_ADDR_SIZE:
            self._canonical = bytes([self._size]) + addr_bin
        elif self._size != (prefix_size := addr_bin[0] + 1):
            raise Exception(f"Invalid Address: prefix != num bytes given ({prefix_size} != {self._size}")
        elif self._size == kWALLET_ADDR_BUF_SIZE or self._size == kNODE_ADDR_BUF_SIZE:
            self._canonical = addr_bin
            self._size -= 1
        else:
            raise Exception(f"Invalid Address: invalid size {self._size}")

    # compare addresses
    def __eq__(self, other) -> bool:
        return self._canonical == other.get_canonical()

    # evaluate as boolean, serves as isNull()
    def __bool__(self) -> bool:
        return self._canonical is not None

    # get formatted address
    def __str__(self) -> str:
        return self.get_hex_str()

    # get address size (without buffer)
    def get_size(self) -> int:
        return self._size

    # get address bytes
    def get_canonical(self) -> bytes:
        return self._canonical

    # get formatted address
    def get_hex_str(self) -> str:
        if not self._canonical:
            raise Exception('Address is not initialized!')
        return self._canonical.hex()[2:].upper()

    # methods for checking addr size/type
    def is_wallet_addr(self):
        return self._size == kWALLET_ADDR_SIZE

    def is_node_addr(self):
        return self._size == kNODE_ADDR_SIZE

    def get_corresponding_sig_size(self):
        if self.is_wallet_addr():
            return kWALLET_SIG_BUF_SIZE
        elif self.is_node_addr():
            return kNODE_SIG_BUF_SIZE
        else:
            return 0

    @staticmethod
    def is_valid_addr_size(addr_size: int) -> bool:
        return addr_size in [kWALLET_ADDR_SIZE, kWALLET_ADDR_BUF_SIZE, kNODE_ADDR_SIZE, kNODE_ADDR_BUF_SIZE]
