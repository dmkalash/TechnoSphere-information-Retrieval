from tqdm import tqdm
from levenstein import *
from heap import *
import re

from sklearn.preprocessing import StandardScaler as SS
from sklearn.linear_model import LogisticRegression as LogReg


def prepare_query(query):
    tokens = re.findall(r'\w+', query)
    # tokens = re.findall(r'[A-Za-zа-яА-Я]+', pair[0])

    tokens = list(map(lambda s: s.lower(), tokens))
    return tokens


def fuzzy_search(trie, origin, letter_dict, max_heap_size=100, max_ans_size=10, alpha=1.0):  # absf, absd
    lev = Levenstein(letter_dict)
    heap = MinHeap(max_heap_size)  # [(0, 0, 0, '')] # cur_weight, node_num, origin_i, preffix
    heap.insert((0, 0, 0, ''))

    # ans = MinHeap(max_ans_size) # origin_i в конце, вершина в боре - терминальная. Соответствующий префикс - ответ
    # ans = set()
    ans = dict()
    # fixed = ''.join(('^', fixed))

    while len(ans) < max_heap_size and len(heap) > 0:

        # new_heap = MinHeap(max_heap_size) # []
        cur_weight, node_num, origin_i, fixed_pref = heap.delete_min()  # heapq.heappop(heap)
        # print(len(heap), len(ans), node_num, origin_i)

        if origin_i == len(origin):
            if trie.data[node_num].is_term:
                # ans.insert( (cur_weight, node_num, origin_i, fixed_pref) )
                # ans.add( (cur_weight, node_num, origin_i, fixed_pref) )
                ans[(node_num, origin_i, fixed_pref)] = min(ans.get((node_num, origin_i, fixed_pref), 1e9), cur_weight)

                if len(ans) >= max_ans_size:
                    break
            continue

        children = trie.data[node_num].children

        if len(children) > 0:
            prior = lev.get_distance(origin[:origin_i + 1], fixed_pref)
            weight = math.log(prior)  # alpha * math.log( trie.data[child_node_num].freq + 1 )
            # TODO: возвращать ответ без экспоненты, а то лишние действия
            # print(prior, weight)
            # return
            heap.insert((-weight + cur_weight, node_num, origin_i + 1, fixed_pref))

        for symb in children:
            child_node_num = children[symb]

            prior = lev.get_distance(origin[:origin_i + 1], ''.join((fixed_pref, symb)))
            # print(alpha * math.log( trie.data[child_node_num].freq + 1 ), math.log( prior ))
            weight = alpha * math.log(trie.data[child_node_num].freq + 1) + math.log(prior)
            heap.insert((-weight + cur_weight, child_node_num, origin_i + 1, ''.join((fixed_pref, symb))))
            # new_heap.insert( (-weight + cur_weight, child_node_num, origin_i + 1, fixed_pref + symb) )

            prior = lev.get_distance(origin[:origin_i], ''.join((fixed_pref, symb)))
            weight = alpha * math.log(trie.data[child_node_num].freq + 1) + math.log(prior)
            heap.insert((-weight + cur_weight, child_node_num, origin_i, ''.join((fixed_pref, symb))))

            # heapq.heappush(new_heap, (-weight + cur_weight, child_node_num, origin_i + 1, fixed_pref + symb))

    #             prior = lev.get_distance(origin[:origin_i], fixed_pref + symb)
    #             weight = alpha * math.log( trie.data[child_node_num].freq + 1 ) - math.log( prior ) # TODO: + вероятность
    #             heapq.heappush(new_heap, (-weight + cur_weight, child_node_num, origin_i, fixed_pref + symb))

    # TODO: а нужно ли сделать alpha * m ? Вроде учли уже этот переход alpha * math.log( trie.data[node_num].freq + 1 )
    #             prior = lev.get_distance(origin[:origin_i + 1], fixed_pref)
    #             weight = -math.log( prior ) # TODO: + вероятность
    #             heapq.heappush(new_heap, (-weight + cur_weight, node_num, origin_i + 1, fixed_pref))

    # new_heap = new_heap[:max_heap_size]

    # print('new_heap:', new_heap.heap_list)
    # heap.merge(new_heap)
    # heap += new_heap
    # heapq.heapify(heap)
    # heap.cut()

    return [(ans[key],) + key[2:3] for key in ans]
    # return ans.heap_list[1 : ans.current_size + 1]


def get_candidates(query, trie, letter_dict, bigramm_words_dict,
                   max_size=10, max_ans_size=3, alpha=0.1, gamma=1.0, return_query=True):
    words = prepare_query(query)
    word_candidates = []
    for word in words:
        # TODO: проигнорировать числа
        sugg = fuzzy_search(trie, word, letter_dict, alpha=alpha, max_heap_size=100, max_ans_size=max_ans_size)
        word_candidates.append(sugg)  # min weight => best

    heap = QueryMinHeap(max_size)
    for i, cand in enumerate(word_candidates[0]):
        heap.insert((cand[0], (i,)))

    ans = dict()
    # heapq.heapify(heap)
    while len(ans) < max_size and len(heap) > 0:
        weight, cur_seq = heap.delete_min()
        if len(cur_seq) >= len(words):
            ans[cur_seq] = min(ans.get(cur_seq, 1e9), weight)
            continue

        for j, (cand_weight, word2) in enumerate(word_candidates[len(cur_seq)]):
            word1 = word_candidates[len(cur_seq) - 1][cur_seq[-1]][1]
            # print(word1, word2)
            path_weight = -gamma * math.log(1 + bigramm_words_dict.get('_'.join((word1, word2)), 0))
            # print( weight, path_weight, cand_weight )
            res = weight + path_weight + cand_weight

            heap.insert((res, cur_seq + (j,)))

    if return_query:
        res = []
        for key in ans:
            q = ' '.join(word_candidates[j][elem][1] for j, elem in enumerate(key))
            res.append((ans[key], q))
        return sorted(res)

    return sorted([(ans[key], key) for key in ans])


def get_query_stat(fname='queries_all.txt'):
    query_dict = dict()

    with open(fname) as fin:

        for i, line in tqdm(enumerate(fin)):

            pair = line.split('\t')

            tokens = prepare_query(pair[0])
            alpha_tokens = list(filter(lambda s: s.isalpha(), tokens))
            if len(alpha_tokens) == 0:
                continue
            query = ' '.join(alpha_tokens)

            query_dict[query] = query_dict.get(query, 0) + 1
    return query_dict


def get_features_train(query_dict, trie, letter_dict, bigramm_words_dict, words_dict, words_prior_dict,
                       fname='queries_all.txt', stop_iter=500, teta=0.01):
    X = []
    y = []

    with open(fname) as fin:
        fix_iter, origin_iter = stop_iter, stop_iter
        for i, line in tqdm(enumerate(fin)):

            pair = line.split('\t')

            tokens = prepare_query(pair[0])
            alpha_tokens = list(filter(lambda s: s.isalpha(), tokens))
            if len(alpha_tokens) == 0:
                continue
            query = ' '.join(alpha_tokens)

            if origin_iter == 0 and fix_iter == 0:
                break

            if len(pair) > 1:
                if fix_iter == 0:
                    continue
                fix_iter -= 1
            else:
                if origin_iter == 0:
                    continue
                origin_iter -= 1

            eng_symb_cnt = len(list(filter(lambda symb: 'a' <= symb <= 'z', query)))
            symb_cnt = len(list(filter(lambda symb: symb.isalpha, query)))

            eng_part = eng_symb_cnt / symb_cnt

            corr_score, corr_query = get_candidates(query, trie, letter_dict, bigramm_words_dict)[0]
            corr_tokens = corr_query.split()
            bigramm_prior = 0
            for word1, word2 in zip(corr_tokens, corr_tokens[1:]):
                bigramm_prior += math.log(1 + bigramm_words_dict.get('_'.join((word1, word2)), 0))
            bigramm_prior += teta * math.log(1 + len(words_dict) * words_prior_dict.get(corr_tokens[-1], 0))

            X.append(
                [len(alpha_tokens), len(pair[0]), len(query), eng_part,
                 corr_score, bigramm_prior, query_dict.get(query, 0) / len(query_dict)]  #
            )
            y.append(1 if len(pair) > 1 else 0)

        return X, y


def get_features_test(line, query_dict, trie, letter_dict, bigramm_words_dict, words_dict, words_prior_dict,
                        teta=0.01):
    pair = line.split('\t')

    tokens = prepare_query(pair[0])
    alpha_tokens = list(filter(lambda s: s.isalpha(), tokens))
    if len(alpha_tokens) == 0:
        return None

    query = ' '.join(alpha_tokens)

    eng_symb_cnt = len(list(filter(lambda symb: 'a' <= symb <= 'z', query)))
    symb_cnt = len(list(filter(lambda symb: symb.isalpha, query)))

    eng_part = eng_symb_cnt / symb_cnt

    corr_score, corr_query = get_candidates(query, trie, letter_dict, bigramm_words_dict)[0]
    corr_tokens = corr_query.split()
    bigramm_prior = 0
    for word1, word2 in zip(corr_tokens, corr_tokens[1:]):
        bigramm_prior += math.log(1 + bigramm_words_dict.get('_'.join((word1, word2)), 0))
    bigramm_prior += teta * math.log(1 + len(words_dict) * words_prior_dict.get(corr_tokens[-1], 0))

    X = [[len(alpha_tokens), len(pair[0]), len(query), eng_part,
          corr_score, bigramm_prior, query_dict.get(query, 0) / len(query_dict)]]

    return X


def get_model(query_dict, trie, letter_dict, bigramm_words_dict, words_dict, words_prior_dict,
              stop_iter=100):
    X, y = get_features_train(query_dict, trie, letter_dict, bigramm_words_dict, words_dict, words_prior_dict,
                              stop_iter=stop_iter)
    scaler = SS()
    scaler.fit(X)
    X = scaler.transform(X)
    model = LogReg()
    model.fit(X, y)
    return model, scaler


def equal(query, cand):
    return prepare_query(query) == prepare_query(cand)
