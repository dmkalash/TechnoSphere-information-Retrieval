def rpn(tokens):
    ops = {
        '!': 2,
        '&': 1,
        '|': 0,
    }
    res = []
    stack = []

    for token in tokens:
        if token == '(':
            stack.append('(')
        elif token == ')':
            while stack[-1] != '(':
                res.append(stack.pop())
            stack.pop()
        elif token == '!':
            stack.append('!')
        elif token in ops.keys():
            while len(stack) > 0 and (stack[-1] == '!' or
                                      stack[-1] in ops and ops[token] <= ops[stack[-1]]):
                res.append(stack.pop())
            stack.append(token)
        else:
            res.append(token)

    while len(stack) > 0:
        res.append(stack.pop())

    return res


def tokenize(query):
    ops = ['!', '&', '|', '(', ')']
    st = 0
    en = 0
    res = []
    for c in query:
        if c in ops:
            tmp = query[st: en].strip()
            if len(tmp) > 0:
                res.append(tmp)
            res.append(c)
            st = en + 1

        en += 1

    tmp = query[st: en + 1].strip()
    if len(tmp) > 0:
        res.append(tmp)
    return res


def get_query_tree(query, NodeType):
    """
    return: leafs, tree
    """
    tree = dict()
    last_node_key = 0
    tokens = rpn(tokenize(query))

    stack = []
    leafs = []
    for i, token in enumerate(tokens):
        if token == '&' or token == '|':
            tree[last_node_key] = NodeType(2, token)
            node_id_right = stack.pop()
            node_id_left = stack.pop()
            tree[node_id_left].parent = last_node_key
            tree[node_id_right].parent = last_node_key
            tree[last_node_key].left_ind = node_id_left
            tree[last_node_key].right_ind = node_id_right
            stack.append(last_node_key)

        elif token == '!':
            tree[last_node_key] = NodeType(3, token)
            node_id_left = stack.pop()
            tree[node_id_left].parent = last_node_key
            tree[last_node_key].left_ind = node_id_left
            stack.append(last_node_key)

        else:
            tree[last_node_key] = NodeType(1, token)
            stack.append(last_node_key)
            leafs.append(last_node_key)

        last_node_key += 1

    if len(stack) != 1:  # stack[-1] - root
        return None, tree

    return stack[0], tree


def get_query_tree_compressed(query, NodeType):
    """
    return: leafs, tree
    """
    tree = dict()
    last_node_key = 0
    raw_tokens = tokenize(query)
    tokens = []
    for i, token in enumerate(raw_tokens):
        if token not in ['&', '|', '!', '(', ')']:
            token = '_'.join((token, str(i)))
        tokens.append(token)

    tokens = rpn(tokens)

    stack = []
    leafs = []
    for i, token in enumerate(tokens):
        if token == '&' or token == '|':
            tree[last_node_key] = NodeType(2, token)
            node_id_right = stack.pop()
            node_id_left = stack.pop()
            tree[node_id_left].parent = last_node_key
            tree[node_id_right].parent = last_node_key
            tree[last_node_key].left_ind = node_id_left
            tree[last_node_key].right_ind = node_id_right
            stack.append(last_node_key)

        elif token == '!':
            tree[last_node_key] = NodeType(3, token)
            node_id_left = stack.pop()
            tree[node_id_left].parent = last_node_key
            tree[last_node_key].left_ind = node_id_left
            stack.append(last_node_key)

        else:
            tree[last_node_key] = NodeType(1, token)
            stack.append(last_node_key)
            leafs.append(last_node_key)

        last_node_key += 1

    if len(stack) != 1:  # stack[-1] - root
        return None, tree

    return stack[0], tree
