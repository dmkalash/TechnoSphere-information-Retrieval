import pickle5 as pickle
import sys

from utils import *
from split_checker import *
from trie import *
from config import *
import copy

en_ru, ru_en = None, None

# TODO: проблема с точки зрения статистики для биграмм: p(word1|word2) = p(word1 & word2) / p(word2)

def get_stat():

    with open('bigramm_words_dict.pkl', 'rb') as output:
        bigramm_words_dict = pickle.load(output)
    with open('words_prior_dict.pkl', 'rb') as output:
        words_prior_dict = pickle.load(output)
    with open('letter_dict.pkl', 'rb') as output:
        letter_dict = pickle.load(output)
        sm = sum(letter_dict.values())
        for key in letter_dict:
            letter_dict[key] = letter_dict[key] / sm

    # with open('hard_queries.pkl', 'rb') as output:
    #     hard_queries = pickle.load(output)
    # with open('words_dict.pkl', 'rb') as output:
    #     words_dict = pickle.load(output)

    with open('trie.pkl', 'rb') as output:
        trie = pickle.load(output)

    with open('query_dict.pkl', 'rb') as output:
        query_dict = pickle.load(output)
    with open('model.pkl', 'rb') as output:
        model = pickle.load(output)
    with open('scaler.pkl', 'rb') as output:
        scaler = pickle.load(output)

    global en_ru, ru_en
    with open('en_ru.pkl', 'rb') as output:
        en_ru = pickle.load(output)
    with open('ru_en.pkl', 'rb') as output:
        ru_en = pickle.load(output)

    return bigramm_words_dict, words_prior_dict, letter_dict, trie,\
            query_dict, model, scaler



def spell_checker(query, trie, letter_dict, bigramm_words_dict, model, scaler,
                  query_dict, words_prior_dict, max_size=CAND_SIZE):
    #print('getting candidates...', file=sys.stderr)
    candidates = get_candidates(query, trie, letter_dict, bigramm_words_dict,
                                max_size=max_size, max_ans_size=FIX_MAX_ANS_SIZE, alpha=FIX_ALPHA, gamma=FIX_GAMMA)
    #print('candidates gotten...', file=sys.stderr)

    if equal(query, candidates[0][1]):
        return False, query  # или candidates[0]

    need_to_fix = False
    # print(candidates)

    p_best = get_biprior(query, bigramm_words_dict, words_prior_dict)
    for i, cand in enumerate(candidates):
        #print('getting test features...', file=sys.stderr)

        need_to_fix = predict(query, cand, model, scaler, query_dict, words_prior_dict, bigramm_words_dict)
        # X_test = get_features_test(query, query_dict, trie, letter_dict,
        #                                bigramm_words_dict, words_prior_dict)
        # if X_test is None:
        #     return False, query
        #
        # X_test = scaler.transform(X_test)
        # need_to_fix = model.predict(X_test)
        #print(need_to_fix, cand[1])

        #print(query, cand[1], need_to_fix)
        p2 = get_biprior(cand[1], bigramm_words_dict, words_prior_dict)
        if p2 > p_best and need_to_fix:
            p_best = p2
            query = cand[1]

        if not need_to_fix:
            return need_to_fix, cand[1]

    return need_to_fix, query


def spell_checker_split(query, trie, bigramm_words_dict, words_prior_dict, max_size=SPLIT_MAX_ANS_SIZE):
    #print('getting candidates...', file=sys.stderr)
    candidates = get_candidates_split(query, trie, bigramm_words_dict, words_prior_dict, max_size=max_size,
                                      max_ans_size=MAX_SPLIT_SEARCH_SIZE, alpha=SPLIT_ALPHA, gamma=SPLIT_GAMMA)
    #print('candidates gotten...', file=sys.stderr)

    if len(candidates) == 0 or len(candidates[0][1]) == 0 or equal(query, ' '.join(candidates[0][1])):
        return False, query

    eps = 1e4
    need_to_fix = False
    for cand in candidates:
        need_to_fix = (cand[0] < eps)
        if need_to_fix:
            return need_to_fix, ' '.join(cand[1])
        break

    return need_to_fix, query


def spell_checker_layout(query_t, words_prior_dict, en_ru, ru_en):
    query = prepare_query(query_t)
    new_query = ""
    cand_ru, cand_en = [], []

    for word in query:
        word_ru, word_en = "", ""
        for symb in word:
            word_ru += en_ru.get(symb, symb)
            word_en += ru_en.get(symb, symb)
        cand_ru.append(word_ru)
        cand_en.append(word_en)

    ru_cnt, en_cnt = 0, 0
    for word_ru, word_en in zip(cand_ru, cand_en):
        p_ru = words_prior_dict.get(word_ru, 0)
        p_en = words_prior_dict.get(word_en, 0)
        if p_ru > p_en:
            new_query = ' '.join((new_query, word_ru))
            ru_cnt += 1
        elif p_en > p_ru:
            new_query = ' '.join((new_query, word_en))
            en_cnt += 1
        else:
            new_query = ' '.join((new_query, word_en if en_cnt > ru_cnt else word_ru))

    new_query = new_query[1:]
    return new_query.split() != query, new_query


def get_biprior(line, bigramm_words_dict, words_prior_dict):
    tokens = line.split()
    prior = 0
    for word1, word2 in zip(tokens, tokens[1:]):
        prior += math.log(1 + bigramm_words_dict.get('_'.join((word1, word2)), 0))
        #print(math.log(1 + bigramm_words_dict.get('_'.join((word1, word2)), 0)))
    prior += FIX_TETA * math.log(1 + LEN_WORDS_DICT * words_prior_dict.get(tokens[-1], 0))
    return prior


def run(model, trie, letter_dict, bigramm_words_dict, scaler, query_dict,
            words_prior_dict, n_iter=N_ITER):

    for query_t in sys.stdin:
        query = query_t.strip()
        query2 = copy.copy(query)

        if len(query) == 0:
            print(query_t)
            continue

        try:
            fixed = None
            for i in range(n_iter):
                need_to_fix, fixed = spell_checker(query, trie, letter_dict, bigramm_words_dict, model,
                                                   scaler, query_dict, words_prior_dict, max_size=CAND_SIZE)
                #print('need to fix:', need_to_fix, fixed)
                if not need_to_fix:
                    break

                query = fixed
                # break

            fixed1 = query
            prior1 = get_biprior(fixed1, bigramm_words_dict, words_prior_dict)

            need_to_fix2, fixed2 = spell_checker_split(query2, trie, bigramm_words_dict, words_prior_dict,
                                                     max_size=SPLIT_MAX_ANS_SIZE)

            prior2 = get_biprior(fixed2, bigramm_words_dict, words_prior_dict)

            need_to_fix3, fixed3 = spell_checker_layout(query2, words_prior_dict, en_ru, ru_en)
            prior3 = get_biprior(fixed3, bigramm_words_dict, words_prior_dict)

            need_to_fix4, fixed4 = spell_checker_split(fixed3, trie, bigramm_words_dict, words_prior_dict,
                                                       max_size=SPLIT_MAX_ANS_SIZE)
            need_to_fix4, fixed4 = spell_checker(fixed4, trie, letter_dict, bigramm_words_dict, model,
                                               scaler, query_dict, words_prior_dict, max_size=CAND_SIZE)
            prior4 = get_biprior(fixed4, bigramm_words_dict, words_prior_dict)

            priors = [prior1, prior2, prior3, prior4]
            res = [ fixed1, fixed2, fixed3, fixed4 ]
            fixed = res[ np.argmax(priors) ]

            # if not need_to_fix2 or prior1 > prior2:
            #     fixed = query

            print(fixed)
        except Exception as e:
            print(query_t)
            print(e, file=sys.stderr)


if __name__ == '__main__':
    #print('loading collections...', file=sys.stderr)
    bigramm_words_dict, words_prior_dict, letter_dict,\
        trie, query_dict, model, scaler = get_stat()
    #print('collections loaded...', file=sys.stderr)

    run(model, trie, letter_dict, bigramm_words_dict, scaler, query_dict, words_prior_dict)
