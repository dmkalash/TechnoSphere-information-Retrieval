import struct
import sys
from config import *

class VarbyteEncoder:
    def __init__(self):
        pass

    def encode(self, inv_index):
        for key in inv_index:
            with open('/'.join((COMPRESSED_DATA_PATH, key)), 'wb') as fout:
                prev = inv_index[key][0]
                res = self._encode_digit(prev)
                for doc_id in inv_index[key][1:]:
                    res += self._encode_digit(doc_id - prev)
                    prev = doc_id
                res += self._encode_digit(0)  # end-of-list marker
                fout.write(res)

    def _encode_digit(self, num):
        res = b''
        while num >= 128:
            res += struct.pack('B', num % 128)
            num //= 128
        res += struct.pack('B', 128 + num)
        return res


class Buffer:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.data_len = self.buffer_size
        self.pos = -1

    def create(self, token):
        try:
            self.fin = open('/'.join(('index', token)), 'rb')
        except:
            self.fin = None


    def get_byte(self):
        if self.pos == -1 or self.pos == self.data_len:
            self.data = self.fin.read(self.buffer_size)
            self.data_len = len(self.data)
            self.pos = 0
            if self.data_len == 0:
                print('End of file reached', file=sys.stderr)
                return None

        self.pos += 1
        return self.data[self.pos - 1:self.pos]


class VarbyteDecoder:
    def __init__(self, buffer_size=128):
        self.buffer = Buffer(buffer_size)

    def _decode_digit(self):
        num = 0
        mlt = 1
        while True:
            part = struct.unpack('B', self.buffer.get_byte())[0]
            if part >= 128:
                num = num + mlt * (part - 128)
                break
            num = num + mlt * part
            mlt *= 128
        return num

    def decode(self, token):
        self.buffer.create(token)
        if self.buffer.fin is None:
            yield MAX_DOC_ID
        else:
            start = self._decode_digit()
            while True:
                yield start
                num = self._decode_digit()
                if num == 0:
                    break
                start += num