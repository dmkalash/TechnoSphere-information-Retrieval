import numpy as np
import pickle
import sys
import pickle5 as pickle
from config import *

from utils import prepare_query, get_query_stat


def get_part_letter_dict(origin, fixed):
    table = np.zeros((len(fixed) + 1, len(origin) + 1))
    table[0] = np.arange(len(origin) + 1)
    table[:, 0] = np.arange(len(fixed) + 1)

    for i in range(1, len(fixed) + 1):
        for j in range(1, len(origin) + 1):
            # print(len(origin), j - 1, len(fixed), i - 1, (origin[j - 1] != fixed[i - 1]))
            table[i, j] = min(table[i - 1, j] + 1,
                              table[i, j - 1] + 1,
                              table[i - 1, j - 1] + (origin[j - 1] != fixed[i - 1]))

    part_letter_dict = dict()
    # one_letter_dict = dict()

    i, j = len(fixed), len(origin)
    while i != 0 and j != 0:
        #         m = min( table[i - 1, j] + 1,
        #                     table[i, j - 1] + 1,
        #                     table[i - 1, j - 1] + (origin[j - 1] != fixed[i - 1]) )
        if table[i - 1, j - 1] + (origin[j - 1] != fixed[i - 1]) == table[i, j]:
            symb = origin[j - 1] + fixed[i - 1]
            part_letter_dict[symb] = part_letter_dict.get(symb, 0) + 1
            # one_letter_dict[origin[j - 1]] = one_letter_dict.get(origin[j - 1], 0) + 1
            i -= 1
            j -= 1

        elif table[i - 1, j] + 1 == table[i, j]:
            symb = '_' + fixed[i - 1]
            part_letter_dict[symb] = part_letter_dict.get(symb, 0) + 1
            # one_letter_dict[origin[j - 1]] = one_letter_dict.get(origin[j - 1], 0) + 1
            i -= 1
        else:
            symb = origin[j - 1] + '_'
            part_letter_dict[symb] = part_letter_dict.get(symb, 0) + 1
            # one_letter_dict['_'] = one_letter_dict.get('_', 0) + 1
            j -= 1

    while i != 0:
        symb = '_' + fixed[i - 1]
        part_letter_dict[symb] = part_letter_dict.get(symb, 0) + 1
        # one_letter_dict[origin[j - 1]] = one_letter_dict.get(origin[j - 1], 0) + 1
        i -= 1

    while j != 0:
        symb = origin[j - 1] + '_'
        part_letter_dict[symb] = part_letter_dict.get(symb, 0) + 1
        # one_letter_dict['_'] = one_letter_dict.get('_', 0) + 1
        j -= 1

    return part_letter_dict  # , one_letter_dict


def get_words_prior_dict(fname='queries_all.txt', stop_iter=1e9):
    with open(fname) as fin:
        #words_dict = dict()
        bigramm_words_dict = dict()
        #letter_dict = dict()
        # hard_queries = []

        for i, line in enumerate(fin):
            pair = line.split('\t')
            if len(pair) > 1:
                pair[0], pair[1] = pair[1], pair[0]
            else:
                pair.append(pair[0])

            tokens = prepare_query(pair[0])
            alpha_tokens = list(filter(lambda s: s.isalpha(), tokens))

            # for token in set(alpha_tokens):
            #     words_dict[token] = words_dict.get(token, 0) + 1

            for w12 in zip(alpha_tokens, alpha_tokens[1:]):
                key = '_'.join(w12)
                bigramm_words_dict[key] = bigramm_words_dict.get(key, 0) + 1

            # if len(pair) > 1:
            #     origin_tokens = prepare_query(pair[1])
            #     if len(origin_tokens) != len(tokens):
            #         #hard_queries.append((i, line))
            #         continue

                # for origin, fixed in zip(origin_tokens, tokens):
                #     part_letter_dict = get_part_letter_dict(origin, fixed)  # , part_one_letter_dict
                #     for key in part_letter_dict:
                #         letter_dict[key] = letter_dict.get(key, 0) + 1

            if i > stop_iter:
                break

        # words_prior_dict = dict()
        # for key in words_dict:
        #     words_prior_dict[key] = words_dict[key] #  / len(words_dict)

        # for key in letter_dict:
        #     letter_dict[key] = letter_dict[key] / len(letter_dict)  # one_letter_dict[key[0]]

        # sm = sum(letter_dict.values()) # TODO: вроде в файле без нормировки, надо проверить
        # for key in letter_dict:
        #     letter_dict[key] = letter_dict[key] / sm

        return bigramm_words_dict # , letter_dict



if __name__ == '__main__':
    print('start indexing...', file=sys.stderr)
    print('create collections...', file=sys.stderr)
    bigramm_words_dict = get_words_prior_dict()
    print('collections created...', file=sys.stderr)

    # print('normalize...', file=sys.stderr)
    # sm = sum(letter_dict.values())
    # for key in letter_dict:
    #     letter_dict[key] = letter_dict[key] / sm
    # print('normalized...', file=sys.stderr)

    # print('creating trie...', file=sys.stderr)
    # trie = Trie()
    # trie.build_tree(list(words_dict.keys()))
    # print('trie created...', file=sys.stderr)

    print('query dict creating...', file=sys.stderr)
    query_dict = get_query_stat()
    print('query dict created...', file=sys.stderr)

    # print('model creating...', file=sys.stderr)
    # model, scaler = get_model(query_dict, trie, letter_dict, bigramm_words_dict, words_prior_dict,
    #                           stop_iter=50)
    # print('model created...', file=sys.stderr)

    # print('saving collections...', file=sys.stderr)
    # with open('words_dict.pkl', 'wb') as output:
    #     pickle.dump(words_dict, output, pickle.HIGHEST_PROTOCOL)

    second_words = dict()
    for key in bigramm_words_dict:
        word1, word2 = key.split('_')
        second_words[word2] = second_words.get(word2, 0) + bigramm_words_dict[key]

    for key in bigramm_words_dict:
        word1, word2 = key.split('_')
        bigramm_words_dict[key] = bigramm_words_dict[key] / second_words[word2]

    with open('bigramm_words_dict.pkl', 'wb') as output:
        pickle.dump(bigramm_words_dict, output, pickle.HIGHEST_PROTOCOL)
    # with open('words_prior_dict.pkl', 'wb') as output:
    #     pickle.dump(words_prior_dict, output, pickle.HIGHEST_PROTOCOL)

    # with open('letter_dict.pkl', 'wb') as output:
    #     pickle.dump(letter_dict, output, pickle.HIGHEST_PROTOCOL)
    # with open('hard_queries.pkl', 'wb') as output:
    #     pickle.dump(hard_queries, output, pickle.HIGHEST_PROTOCOL)
    # with open('trie.pkl', 'wb') as output:
    #     pickle.dump(trie, output, pickle.HIGHEST_PROTOCOL)
    with open('query_dict.pkl', 'wb') as output:
        pickle.dump(query_dict, output, pickle.HIGHEST_PROTOCOL)
    # with open('model.pkl', 'wb') as output:
    #     pickle.dump(model, output, pickle.HIGHEST_PROTOCOL)
    # with open('scaler.pkl', 'wb') as output:
    #     pickle.dump(scaler, output, pickle.HIGHEST_PROTOCOL)
