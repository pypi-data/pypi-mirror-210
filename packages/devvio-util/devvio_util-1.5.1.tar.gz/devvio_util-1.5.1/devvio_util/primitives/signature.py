from devvio_util.primitives.devv_constants import kWALLET_SIG_SIZE, kNODE_SIG_SIZE, kWALLET_SIG_BUF_SIZE, \
    kNODE_SIG_BUF_SIZE
from devvio_util.primitives.utils import InputBuffer


class Signature:
    def __init__(self, sig: str or bytes or InputBuffer = None):
        self._canonical = None
        self._size = None
        self.set_sig(sig)

    def set_sig(self, sig: str or bytes or InputBuffer):
        if not sig:
            raise Exception("Invalid Signature: no bytes or string given")
        if isinstance(sig, str):
            sig_bin = bytes.fromhex(sig)
        elif isinstance(sig, bytes):
            sig_bin = sig
        elif isinstance(sig, InputBuffer):
            sig_bin = sig.get_next_prefixed_obj()
        else:
            raise Exception(f"Invalid Signature: cannot initialize from type {type(sig)}")
        if not sig_bin:
            return None
        self._size = len(sig_bin)
        if self._size == kWALLET_SIG_SIZE or self._size == kNODE_SIG_SIZE:
            self._canonical = bytes([self._size]) + sig_bin
        elif self._size != (prefix_size := sig_bin[0] + 1):
            raise Exception(f"Invalid Signature: prefix != num bytes given ({prefix_size} != {self._size})")
        elif self._size == kWALLET_SIG_BUF_SIZE or self._size == kNODE_SIG_BUF_SIZE:
            self._canonical = sig_bin
            self._size -= 1
        else:
            raise Exception(f"Invalid Signature: invalid size {self._size}")

    # compare signatures
    def __eq__(self, other) -> bool:
        return self._canonical == other.get_canonical()

    # evaluate as boolean, serves as isNull()
    def __bool__(self) -> bool:
        return self._canonical is not None

    # get formatted signature
    def __str__(self) -> str:
        return self.get_hex_str()

    # get sig length (without prefix)
    def get_size(self) -> int:
        return self._size

    # get raw sig
    def get_canonical(self) -> bytes:
        return self._canonical

    # return hex representation (without prefix)
    def get_hex_str(self) -> str:
        if not self._canonical:
            raise Exception('Signature is not initialized!')
        return self._canonical.hex()[2:].upper()

    def is_wallet_sig(self) -> bool:
        if not self.__bool__():
            return False
        return self._size == kWALLET_SIG_SIZE

    def is_node_sig(self) -> bool:
        if not self.__bool__():
            return False
        return self._size == kNODE_SIG_SIZE

    @staticmethod
    def is_valid_sig_size(sig_size: int) -> bool:
        return sig_size in [kWALLET_SIG_SIZE, kWALLET_SIG_BUF_SIZE, kNODE_SIG_SIZE, kNODE_SIG_BUF_SIZE]
