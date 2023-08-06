import msgpack
import zmq
import pandas as pd
from dataclasses import dataclass
from hexbytes import HexBytes


_DEFAULT_HOST = 'tcp://blockpipe_db:5555'


@dataclass
class Query:
    __slot__ = ['address', 'topic0', 'limit']

    address: HexBytes
    topic0: HexBytes
    limit: int

    def to_bytes(self):
        return msgpack.packb([self.address, self.topic0, self.limit])


class Client:
    def __init__(self, host: str = _DEFAULT_HOST):
        context = zmq.Context()
        self.socket = context.socket(zmq.DEALER)
        self.socket.setsockopt(zmq.SNDHWM, 10000)
        self.socket.setsockopt(zmq.RCVHWM, 10000)
        self.socket.connect(host)

    def load_event_df(self, address: str | bytes, topic0: str | bytes, limit: int = 100):
        query = Query(HexBytes(address), HexBytes(topic0), limit)
        self.socket.send(query.to_bytes())
        data = []
        while True:
            if (e := self.socket.recv()) == b'':
                break
            data.append(msgpack.unpackb(e))
        return pd.DataFrame(data, columns=[
            'log_index', 'tx_index', 'tx_hash', 'block_hash', 'block_number', 'block_timestamp',
            'address', 'data', 'topic0', 'topic1', 'topic2', 'topic3',
        ])
