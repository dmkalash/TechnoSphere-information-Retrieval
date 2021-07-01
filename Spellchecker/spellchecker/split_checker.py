import math

from utils import prepare_query
from heap import QueryMinHeap


def split_search(trie, words, max_heap_size=100, max_ans_size=3):
    words = prepare_query(words)  # TODO

    heap = QueryMinHeap(max_heap_size, init=[(1e8, (), '', 0, 0)])  #
    heap.insert((-trie.data[0].freq, (), '', 0, 0))  #
    end_ind = len(words)

    ans = dict()

    while len(ans) < max_heap_size and len(heap) > 0:

        # 0, [], '', 0, 0
        score, ready_list, preffix, cur_word_ind, cur_node_num = heap.delete_min()

        if cur_word_ind == end_ind:
            if trie.data[cur_node_num].is_term:
                ans[ready_list] = min(ans.get(ready_list, 1e9), score)

                if len(ans) >= max_ans_size:
                    break
            continue

        add = trie.data[cur_node_num].freq
        for symb in words[cur_word_ind]:  # продолжаем префикс
            children = trie.data[cur_node_num].children
            cur_node_num = children.get(symb, -1)
            if cur_node_num == -1:
                break
        if cur_node_num == -1:
            continue

        if trie.data[cur_node_num].is_term:
            new_score = score - trie.data[cur_node_num].freq
            heap.insert((new_score, ready_list + (''.join((preffix, words[cur_word_ind])),), '',
                         cur_word_ind + 1, 0,))

        if cur_word_ind + 1 < end_ind:
            new_score = score + add - trie.data[cur_node_num].freq
            heap.insert((new_score, ready_list, ''.join((preffix, words[cur_word_ind])),
                         cur_word_ind + 1, cur_node_num,))

    return sorted([(-ans[key],) + (key,) for key in ans])


def get_candidates_split(query, trie, bigramm_words_dict, words_prior_dict,
                   max_size=10, max_ans_size=10, alpha=0.01, gamma=1.0):
    word_candidates = split_search(trie, query, max_heap_size=100, max_ans_size=max_ans_size)
    scores = []

    for i, pair in enumerate(word_candidates):
        word1 = pair[1][0]
        cur_score = words_prior_dict.get(word1, 0)

        eps = 1e-8
        for j, word2 in enumerate(pair[1][1:]):
            path_weight = -gamma * math.log(1 + bigramm_words_dict.get('_'.join((word1, word2)), 0))
            cur_score = cur_score + path_weight - alpha * math.log(words_prior_dict.get(word2, eps))
            word1 = word2
        scores.append((cur_score, pair[1]))

    return sorted(scores)[:max_size]
