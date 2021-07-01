class Node:
    def __init__(self, num, freq=0, is_term=False):
        self.num = num
        self.children = dict()  # symb : num
        self.freq = freq
        self.is_term = is_term


class Trie:
    def __init__(self):
        self.data = {0: Node(0, 0, True)}

    def build_tree(self, words):
        # words.sort()
        for word in words:
            cur_node_num = 0

            for symb in word:
                cur_node = self.data[cur_node_num]
                cur_node.freq += 1
                if symb not in cur_node.children:
                    new_num = len(self.data)
                    self.data[new_num] = Node(new_num)
                    cur_node.children[symb] = new_num
                    cur_node_num = new_num

                cur_node_num = cur_node.children[symb]

            self.data[cur_node_num].is_term = True
