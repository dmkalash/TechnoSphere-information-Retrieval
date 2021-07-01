

class MinHeap:
    def __init__(self, max_heap_size, init=[-1e8, -1, -1, '']):
        """
        On this implementation the heap list is initialized with a value
        """
        self.init = init
        self.heap_list = [init] + [None] * max_heap_size  # cur_weight, node_num, origin_i, preffix
        self.current_size = 0
        self.map = dict()  # {(init[2], init[3]) : 0} # (origin_i, preffix): heap_node_num
        self.max_heap_size = max_heap_size

    def merge(self, heap_b):  # TODO: new_heap можно через обычный список делать и индексировать с 0
        for elem in heap_b.heap_list[1: heap_b.current_size + 1]:
            self.insert(elem)

    def sift_up(self, i):
        """
        Moves the value up in the tree to maintain the heap property.
        """
        # print('sift_up')
        while i // 2 > 0:
            if self.heap_list[i][0] < self.heap_list[i // 2][0]:
                self.map_swap(i, i // 2)
                self.heap_list[i], self.heap_list[i // 2] = self.heap_list[i // 2], self.heap_list[i]
            i = i // 2

    def insert(self, k):
        """
        Inserts a value into the heap
        """
        # print(my_heap.heap_list, self.map.get((k[2], k[1]), None))

        heap_node_num = self.map.get((k[2], k[3]), None)
        if heap_node_num is None:
            self.current_size += 1
            self.heap_list[self.current_size] = k
            self.map[(k[2], k[3])] = self.current_size

            self.sift_up(self.current_size)
            if self.current_size >= self.max_heap_size:
                # TODO: может быть по порогу лучше отсекать(правда мб будет 0 вариантов), тк
                # сейчас мы не максимальный штраф удаляем, а рандомный в конце списка

                # print('DELETE!')
                # print( len(self.map, len(self.heap_list)) )
                del self.map[
                    (self.heap_list[self.current_size][2], self.heap_list[self.current_size][3])]  # TODO: change
                # del self.heap_list[-1]
                self.current_size -= 1
                # print( len(self.map, len(self.heap_list)) )
                # print()


        elif k[0] < self.heap_list[heap_node_num][0]:
            self.heap_list[heap_node_num] = k
            self.sift_up(heap_node_num)


    def sift_down(self, i):
        # print('sift_down')
        while i * 2 <= self.current_size:
            mc = self.min_child(i)
            if self.heap_list[i][0] > self.heap_list[mc][0]:
                self.map_swap(i, mc)
                self.heap_list[i], self.heap_list[mc] = self.heap_list[mc], self.heap_list[i]
                i = mc
            else:
                break

    def min_child(self, i):
        if i * 2 + 1 > self.current_size:
            return i * 2
        else:
            if self.heap_list[i * 2] < self.heap_list[i * 2 + 1]:
                return i * 2
            else:
                return i * 2 + 1

    def map_swap(self, i, j):
        self.map[(self.heap_list[i][2], self.heap_list[i][3])], \
        self.map[(self.heap_list[j][2], self.heap_list[j][3])] = j, i

    def __len__(self):
        return self.current_size

    def delete_min(self):

        root = self.heap_list[1]
        self.heap_list[1], self.heap_list[self.current_size] = self.heap_list[self.current_size], self.heap_list[1]

        self.map_swap(1, self.current_size)

        del self.map[(self.heap_list[self.current_size][2], self.heap_list[self.current_size][3])]

        self.current_size -= 1

        self.sift_down(1)

        return root

    # def free(self):
    #     del self.heap_list
    #     del self.map
    #
    #     self.heap_list = self.init  # cur_weight, node_num, origin_i, preffix
    #     self.current_size = 0
    #     self.map = {(t[2], t[3]): 0}  # (origin_i, trie_node_num): heap_node_num

    # def get_head_origin_index(self):
    #     if self.curent_size > 0:
    #         return self.heap_list[1][2]
    #     return None


class QueryMinHeap:
    def __init__(self, max_heap_size, init=[-1e8, [-1]]):
        """
        On this implementation the heap list is initialized with a value
        """
        self.init = init
        self.heap_list = [init] + [None] * max_heap_size  # cur_weight, node_num, origin_i, preffix
        self.current_size = 0
        self.map = dict()  # {(init[2], init[3]) : 0} # (origin_i, preffix): heap_node_num
        self.max_heap_size = max_heap_size

    def merge(self, heap_b):  # TODO: new_heap можно через обычный список делать и индексировать с 0
        for elem in heap_b.heap_list[1: heap_b.current_size + 1]:
            self.insert(elem)

    def sift_up(self, i):
        """
        Moves the value up in the tree to maintain the heap property.
        """
        # print('sift_up')
        while i // 2 > 0:
            if self.heap_list[i][0] < self.heap_list[i // 2][0]:
                self.map_swap(i, i // 2)
                self.heap_list[i], self.heap_list[i // 2] = self.heap_list[i // 2], self.heap_list[i]
            i = i // 2

    def insert(self, k):
        """
        Inserts a value into the heap
        """
        # print(my_heap.heap_list, self.map.get((k[2], k[1]), None))

        heap_node_num = self.map.get(k[1], None)
        if heap_node_num is None:
            self.current_size += 1
            self.heap_list[self.current_size] = k
            self.map[k[1]] = self.current_size

            self.sift_up(self.current_size)
            if self.current_size >= self.max_heap_size:
                del self.map[self.heap_list[self.current_size][1]]
                self.current_size -= 1

        elif k[0] < self.heap_list[heap_node_num][0]:
            self.heap_list[heap_node_num] = k
            self.sift_up(heap_node_num)

    def sift_down(self, i):
        # print('sift_down')
        while i * 2 <= self.current_size:
            mc = self.min_child(i)
            if self.heap_list[i][0] > self.heap_list[mc][0]:
                self.map_swap(i, mc)
                self.heap_list[i], self.heap_list[mc] = self.heap_list[mc], self.heap_list[i]
                i = mc
            else:
                break

    def min_child(self, i):
        if i * 2 + 1 > self.current_size:
            return i * 2
        else:
            if self.heap_list[i * 2] < self.heap_list[i * 2 + 1]:
                return i * 2
            else:
                return i * 2 + 1

    def map_swap(self, i, j):
        # t = len(self.map)
        # ind_i =
        # ind_j =
        self.map[self.heap_list[i][1]], self.map[self.heap_list[j][1]] = j, i

    def __len__(self):
        return self.current_size

    def delete_min(self):
        #         if len(self.heap_list) == 1:
        #             raise ValueError('empty heap')

        root = self.heap_list[1]
        self.heap_list[1], self.heap_list[self.current_size] = self.heap_list[self.current_size], self.heap_list[1]

        self.map_swap(1, self.current_size)

        del self.map[self.heap_list[self.current_size][1]]

        self.current_size -= 1

        self.sift_down(1)

        return root

    # def free(self):
    #     del self.heap_list
    #     del self.map
    #
    #     self.heap_list = self.init  # cur_weight, node_num, origin_i, preffix
    #     self.current_size = 0
    #     self.map = {(t[2], t[3]): 0}  # (origin_i, trie_node_num): heap_node_num

    # def get_head_origin_index(self):
    #     if self.curent_size > 0:
    #         return self.heap_list[1][2]
    #     return None