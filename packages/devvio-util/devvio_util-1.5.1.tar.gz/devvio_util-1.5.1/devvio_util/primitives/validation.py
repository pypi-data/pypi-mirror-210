from devvio_util.primitives.utils import InputBuffer
from devvio_util.primitives.address import Address
from devvio_util.primitives.signature import Signature
from devvio_util.primitives.devv_constants import kNODE_ADDR_BUF_SIZE, kNODE_SIG_BUF_SIZE, kNODE_ADDR_SIZE, \
    kNODE_SIG_SIZE


class Validation:

    def __init__(self, buffer: InputBuffer, count: int = None):
        self._raw_addrs = False
        self._sigs = {}

        remainder = count
        offset = buffer.tell()

        if remainder is not None:
            if offset + remainder * self.pair_size() > len(buffer):
                raise Exception(f"Invalid Validation: buffer too small for {remainder} node addr/sig pairs")
            while remainder > 0:
                self.create_sig(buffer)
                remainder = remainder - 1
        else:
            while self.create_sig(buffer):
                pass

    def create_sig(self, buffer: InputBuffer) -> bool:
        one_addr = Address(buffer)
        one_sig = Signature(buffer)
        if not (one_sig and one_addr):
            return False
        one_pair = {one_addr.get_hex_str(): one_sig}
        self._sigs.update(one_pair)
        return True

    def add_validation(self, address: Address, sig: Signature):
        if not address.is_node_addr():
            raise Exception("Address must be a node Address")

        if not sig.is_node_sig():
            raise Exception("Signature must be a node Signature")

        it = self._sigs.get(address.get_hex_str())
        if it:
            return False

        self._sigs.update({address.get_hex_str(): sig})
        return True

    def add_validations(self, other):
        added = 0
        for address, sig in other._sigs.items():
            if self.add_validation(address, sig):
                added = added + 1
        return added

    def get_first_validation(self):
        if not len(self._sigs):
            return None
        return next(iter(self._sigs))

    def get_canonical(self):
        out = bytes()
        for addr, sig in self._sigs.items():
            out += Address(addr).get_canonical()
            out += sig.get_canonical()
        return out

    def get_size(self):
        return self.get_validation_count() * self.pair_size()

    def get_validation_count(self) -> int:
        return len(self._sigs)

    def pair_size(self):
        if self._raw_addrs:
            return kNODE_ADDR_SIZE + kNODE_SIG_SIZE
        return kNODE_ADDR_BUF_SIZE + kNODE_SIG_BUF_SIZE

    def get_validation_map(self):
        return self._sigs

    def set_raw_addrs(self, new_raw_addrs: bool):
        self._raw_addrs = new_raw_addrs

    # def hash(self) -> DevvHash:
    #     return DevvHash(self.get_canonical())
