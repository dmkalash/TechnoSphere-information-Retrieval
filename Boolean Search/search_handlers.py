from config import *
from tree_node import Node, FlowNode, FantomList, CompressedFlowNode, CompressedFantomList, InvIndex
from utils import get_query_tree, get_query_tree_compressed, tokenize


def simple_bool_search(query, inv_index, doc_id_set):
    root, tree = get_query_tree(query, Node)
    if root is None or len(tree) == 0:
        return []
    stack = [root]
    used = [False] * len(tree)
    used[root] = True

    while len(stack) != 0:
        if tree[stack[-1]].left_ind != -1 and not used[tree[stack[-1]].left_ind]:
            stack.append(tree[stack[-1]].left_ind)
            used[stack[-1]] = True
        elif tree[stack[-1]].right_ind != -1 and not used[tree[stack[-1]].right_ind]:
            stack.append(tree[stack[-1]].right_ind)
            used[stack[-1]] = True
        else:
            tree[stack.pop()].whole_up(tree, inv_index, doc_id_set)

    return sorted(list(tree[root].doc_ids))[:-1]


def flow_bool_search(query, inv_index, doc_id_list):
    root, tree = get_query_tree(query, FlowNode)
    if root is None or len(tree) == 0:
        return []
    posting_list = []
    cur_doc_id = -1

    fantom_list = FantomList(doc_id_list)

    while cur_doc_id != MAX_DOC_ID:

        stack = [root]
        used = [False] * len(tree)
        used[root] = True

        while len(stack) != 0:
            if tree[stack[-1]].left_ind != -1 and not used[tree[stack[-1]].left_ind]:
                stack.append(tree[stack[-1]].left_ind)
                used[stack[-1]] = True
            elif tree[stack[-1]].right_ind != -1 and not used[tree[stack[-1]].right_ind]:
                stack.append(tree[stack[-1]].right_ind)
                used[stack[-1]] = True
            else:
                tree[stack.pop()].set_state(tree, inv_index, cur_doc_id, fantom_list)

        if tree[root].acceptable_doc_id == cur_doc_id:
            posting_list.append(cur_doc_id)
            cur_doc_id += 1
        else:
            cur_doc_id = tree[root].acceptable_doc_id

    return posting_list


def compressed_flow_bool_search(query):
    root, tree = get_query_tree_compressed(query, CompressedFlowNode)
    if root is None or len(tree) == 0:
        return []

    raw_tokens = tokenize(query)
    tokens = []
    for i, token in enumerate(raw_tokens):
        if token not in ['&', '|', '!', '(', ')']:
            tokens.append('_'.join((token, str(i))))

    compr_inv_index = InvIndex()
    compr_inv_index.reset(tokens)
    posting_list = []
    cur_doc_id = -1

    fantom_list = CompressedFantomList()

    while cur_doc_id != MAX_DOC_ID:

        stack = [root]
        used = [False] * len(tree)
        used[root] = True

        while len(stack) != 0:
            if tree[stack[-1]].left_ind != -1 and not used[tree[stack[-1]].left_ind]:
                stack.append(tree[stack[-1]].left_ind)
                used[stack[-1]] = True
            elif tree[stack[-1]].right_ind != -1 and not used[tree[stack[-1]].right_ind]:
                stack.append(tree[stack[-1]].right_ind)
                used[stack[-1]] = True
            else:
                tree[stack.pop()].set_state(tree, compr_inv_index, fantom_list, cur_doc_id)

        if tree[root].acceptable_doc_id == cur_doc_id:
            posting_list.append(cur_doc_id)
            cur_doc_id += 1
        else:
            cur_doc_id = tree[root].acceptable_doc_id

    return posting_list
