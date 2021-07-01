import struct
import os
import re
import sys
import gzip
import pickle
from config import *
from varbyte import VarbyteEncoder


def save_obj(obj, name, out_path):

    with open( '/'.join( (out_path, name + '.pkl') ), 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print('Too few arguments: expected dump directory(./data) and mode: compressed_flow, flow or simple')
        exit()

    in_data_path = sys.argv[1]
    if sys.argv[2] not in ['compressed_flow', 'flow', 'simple']:
        print('Expected mode: compressed_flow, flow or simple')
        exit()
    mode = sys.argv[2]

    record_len_bytes = 4
    opt_len = 2

    docs_id = dict()
    doc_id_set = {MAX_DOC_ID}
    doc_id_list = [MAX_DOC_ID]
    id_docs = dict()
    inv_index = dict()
    index = dict()
    counter = 0

    print('Prepare data...')

    for i, filename in enumerate(os.listdir(in_data_path)):
        print('#', sep='', end='')
        if filename.endswith('.gz'):
            path = '/'.join((in_data_path, filename))
            with gzip.open(path, 'rb') as fin:
                while True:
                    record_len = fin.read(record_len_bytes)
                    if len(record_len) == 0:
                        break

                    record_len = struct.unpack('I', record_len)[0]
                    buffer = fin.read(record_len)

                    url_len = struct.unpack('B', buffer[1:2])[0]
                    url = struct.unpack(''.join((str(url_len), 's')), buffer[2: 2 + url_len])[0]
                    url = url.decode("utf-8", "ignore")
                    opt = struct.unpack('H', buffer[2 + url_len: 2 + url_len + opt_len])[0]

                    content_len = len(buffer) - (2 + url_len + opt_len)

                    if content_len == 0:
                        continue

                    content = struct.unpack(''.join((str(content_len - 1), 's')),
                                            buffer[2 + url_len + opt_len + 1:])[0].decode("utf-8", "ignore")

                    content_tokens = list(set(map(lambda token: token.lower(), re.findall(r'\w+', content))))

                    if url in docs_id:
                        print('duplicate', file=sys.stderr)
                        continue

                    id_docs[counter] = url
                    doc_id_set.add(counter)
                    doc_id_list.append(counter)
                    docs_id[url] = counter
                    index[counter] = content

                    for token in content_tokens:
                        if token not in inv_index:
                            inv_index[token] = [MAX_DOC_ID]

                        inv_index[token].append(counter)

                    counter += 1
    print()
    index[MAX_DOC_ID] = "---"
    id_docs[MAX_DOC_ID] = "---"
    doc_id_list.sort()

    for key in inv_index:
        inv_index[key].sort()

    save_obj(id_docs, 'id_docs', OUT_DATA_PATH)

    if mode == 'compressed_flow':
        encoder = VarbyteEncoder()
        encoder.encode(inv_index)
        encoder.encode({'_id_list': doc_id_list})
    elif mode == 'simple':
        save_obj(doc_id_set, 'doc_id_list', OUT_DATA_PATH)
    else:
        save_obj(inv_index, 'inv_index', OUT_DATA_PATH)
        save_obj(doc_id_list, 'doc_id_list', OUT_DATA_PATH)

    print('Done!')
