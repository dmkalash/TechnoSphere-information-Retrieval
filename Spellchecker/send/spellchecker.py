import pickle
import sys

from utils import *


def get_stat():
    with open('words_dict.pkl', 'rb') as output:
        words_dict = pickle.load(output)
    with open('bigramm_words_dict.pkl', 'rb') as output:
        bigramm_words_dict = pickle.load(output)
    with open('words_prior_dict.pkl', 'rb') as output:
        words_prior_dict = pickle.load(output)
    with open('letter_dict.pkl', 'rb') as output:
        letter_dict = pickle.load(output)
    with open('hard_queries.pkl', 'rb') as output:
        hard_queries = pickle.load(output)
    with open('trie.pkl', 'rb') as output:
        trie = pickle.load(output)

    with open('query_dict.pkl', 'rb') as output:
        query_dict = pickle.load(output)
    with open('model.pkl', 'rb') as output:
        model = pickle.load(output)
    with open('scaler.pkl', 'rb') as output:
        scaler = pickle.load(output)

    return words_dict, bigramm_words_dict, words_prior_dict, letter_dict, hard_queries, trie,\
            query_dict, model, scaler


## Одна компонента
def spell_checker(query, trie, letter_dict, bigramm_words_dict, model, scaler, query_dict, max_size=3):
    print('getting candidates...', file=sys.stderr)
    candidates = get_candidates(query, trie, letter_dict, bigramm_words_dict,
                                max_size=max_size, max_ans_size=1, alpha=0.1, gamma=1.0)
    print('candidates gotten...', file=sys.stderr)

    if equal(query, candidates[0][1]):
        return False, query  # или candidates[0]

    need_to_fix = False
    for cand in candidates:
        print('getting test features...', file=sys.stderr)
        X_test = get_features_test(query, query_dict=query_dict)
        X_test = scaler.transform(X_test)
        need_to_fix = model.predict(X_test)
        if need_to_fix:
            return need_to_fix, cand[1]

    return need_to_fix, query


def run(model, trie, letter_dict, bigramm_words_dict, scaler, query_dict, n_iter=3):

    while True:
        query = input()
        fixed = None
        for i in range(n_iter):
            need_to_fix, fixed = spell_checker(query, trie, letter_dict, bigramm_words_dict,
                                               model, scaler, query_dict, max_size=3)
            if not need_to_fix:
                break
            query = fixed

        print(fixed)


if __name__ == '__main__':
    print('loading collections...', file=sys.stderr)
    words_dict, words_prior_dict, bigramm_words_dict, letter_dict,\
        hard_queries, trie, query_dict, model, scaler = get_stat()
    print('collections loaded...', file=sys.stderr)

    run(model, trie, letter_dict, bigramm_words_dict, scaler, query_dict)
