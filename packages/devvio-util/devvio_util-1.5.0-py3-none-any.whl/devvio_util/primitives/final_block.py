from devvio_util.primitives.summary import Summary
from devvio_util.primitives.transaction import Transaction
from devvio_util.primitives.utils import InputBuffer
from devvio_util.primitives.validation import Validation


class FinalBlock:
    def __init__(self,
                 raw_blk: InputBuffer = None,
                 prior=None,
                 keys=None,
                 is_legacy: bool = False,
                 do_validate: bool = True):
        self._shard_index = None
        self._block_height = None
        self._block_time = None
        self._prev_hash = None
        self._merkle = None
        self._summary = None
        self._tx_size = None
        self._sum_size = None
        self._val_count = None
        self._vals = None
        self._is_legacy = is_legacy
        self._txs = []
        if not isinstance(raw_blk, InputBuffer):
            raise Exception(f"Invalid FinalBlock input type {type(raw_blk)}")
        if raw_blk and isinstance(raw_blk, InputBuffer):
            self.from_buffer(raw_blk, prior, keys, is_legacy, do_validate)

    def from_buffer(self, raw_blk: InputBuffer, prior=None, keys=None,
                    is_legacy: bool = False, do_validate: bool = True):
        # Back to begin
        raw_blk.seek(0)
        self._is_legacy = is_legacy

        version_ = raw_blk.get_next_uint8()
        if not version_:
            raise Exception("Invalid serialized FinalBlock, buffer empty!")

        if version_ > 1:
            raise Exception(f"Invalid FinalBlock.version: {version_}")

        num_bytes_ = raw_blk.get_next_uint64()
        if not num_bytes_:
            raise Exception("Invalid serialized FinalBlock, wrong size!")

        if not self._is_legacy:
            self._shard_index = raw_blk.get_next_uint64()
            self._block_height = raw_blk.get_next_uint64()

        self._block_time = raw_blk.get_next_uint64()
        self._prev_hash = raw_blk.get_next_prev_hash()
        self._merkle = raw_blk.get_next_merkle()

        self._tx_size = raw_blk.get_next_uint64()
        self._sum_size = raw_blk.get_next_uint64()
        self._val_count = raw_blk.get_next_uint32()

        tx_start = raw_blk.tell()

        while raw_blk.tell() < tx_start + self._tx_size:
            one_tx = Transaction(raw_blk, self._is_legacy)
            self._txs.append(one_tx)

        # if (do_validate):
        #     summary = Summary()
        #     for tx in self._txs:
        #         tx.isValid(None, keys, summary)

        self._summary = Summary(raw_blk)
        self._vals = Validation(raw_blk)

    def __bool__(self):
        return bool(self._txs)

    def get_shard_index(self) -> int:
        return self._shard_index

    def get_block_height(self) -> int:
        return self._block_height

    def get_block_time(self) -> int:
        return self._block_time

    def get_tx_size(self) -> int:
        return self._tx_size

    def get_sum_size(self) -> int:
        return self._sum_size

    def get_val_count(self) -> int:
        return self._val_count

    def get_summary(self) -> Summary:
        return self._summary

    def get_txs(self) -> list:
        return self._txs
