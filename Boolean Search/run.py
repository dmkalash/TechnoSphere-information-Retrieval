import sys
import pickle
from config import *
from search_handlers import simple_bool_search, flow_bool_search, compressed_flow_bool_search


def load_obj(name, in_path):
    with open(in_path + '/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def run(search_func):
    while True:
        input_query = input('Ваш запрос: ')
        query = input_query.strip().lower()

        inv_index = load_obj('inv_index', OUT_DATA_PATH)
        doc_id_list = load_obj('doc_id_list', OUT_DATA_PATH)
        id_docs = load_obj('id_docs', OUT_DATA_PATH)

        doc_ids = search_func(query, inv_index, doc_id_list)

        print(input_query)
        print(len(doc_ids))
        for doc_id in doc_ids:
            print(id_docs[doc_id])


def run_compressed(search_func):
    while True:
        input_query = input('Ваш запрос: ')
        query = input_query.strip().lower()
        doc_ids = search_func(query)
        id_docs = load_obj('id_docs', OUT_DATA_PATH)

        print(input_query)
        print(len(doc_ids))
        for doc_id in doc_ids:
            print(id_docs[doc_id])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Enter search type: simple, flow or compressed_flow - in term your index type')
        exit()
    if sys.argv[1] == 'simple':
        run(simple_bool_search)
    elif sys.argv[1] == 'flow':
        run(flow_bool_search)
    else:
        run_compressed(compressed_flow_bool_search)
