import sys
from config import *
from varbyte import VarbyteDecoder


class Node:
    def __init__(self, node_type, val=None, left_ind=-1, right_ind=-1):
        """
        node_type:
            1 - leaf - one query string
            2 - not leaf - &|
            3 - not leaf - ! - use only left child

        """
        self.type = node_type
        self.left_ind = left_ind
        self.right_ind = right_ind
        self.parent = -1
        self.val = val

    def whole_up(self, tree, inv_index, doc_id_set):
        if self.type == 1:
            self.doc_ids = set(inv_index.get(self.val, []))
        elif self.val == '!':
            self.doc_ids = doc_id_set - tree[self.left_ind].doc_ids
        elif self.val == '&':
            self.doc_ids = tree[self.left_ind].doc_ids & tree[self.right_ind].doc_ids
        elif self.val == '|':
            self.doc_ids = tree[self.left_ind].doc_ids | tree[self.right_ind].doc_ids
        else:
            print('Unknown bool operation', file=sys.stderr)


class FlowNode:
    def __init__(self, node_type, val=None, left_ind=-1, right_ind=-1):
        """
        node_type:
            1 - leaf - one query string
            2 - not leaf - &|
            3 - not leaf - ! - use only left child

        """
        self.type = node_type
        self.left_ind = left_ind
        self.right_ind = right_ind
        self.parent = -1
        self.val = val

        self.is_matched = False
        self.acceptable_doc_id = -1
        if node_type == 1:
            self.list_pos = -1

    def set_state(self, tree, inv_index, cur_doc_id, fantom_list):
        if self.type == 1:
            if self.val not in inv_index:
                self.acceptable_doc_id = MAX_DOC_ID
                self.is_matched = False
            else:
                while self.list_pos < len(inv_index[self.val]) and \
                        (self.list_pos < 0 or inv_index[self.val][self.list_pos] < cur_doc_id):
                    self.list_pos += 1
                fantom_list.update(cur_doc_id)
                self.acceptable_doc_id = inv_index[self.val][self.list_pos]
                self.is_matched = (self.acceptable_doc_id == cur_doc_id)

        elif self.val == '!':
            if tree[self.left_ind].is_matched:
                self.is_matched = False
                self.acceptable_doc_id = fantom_list.get_next_id()
            else:
                if tree[self.left_ind].acceptable_doc_id == fantom_list.get_current_id():
                    self.is_matched = False
                    self.acceptable_doc_id = fantom_list.get_next_id()
                else:
                    self.is_matched = True
                    self.acceptable_doc_id = fantom_list.get_current_id()


        elif self.val == '&':
            self.acceptable_doc_id = max(tree[self.left_ind].acceptable_doc_id,
                                         tree[self.right_ind].acceptable_doc_id)
            self.is_matched = tree[self.left_ind].is_matched & tree[self.right_ind].is_matched

        elif self.val == '|':
            self.acceptable_doc_id = min(tree[self.left_ind].acceptable_doc_id,
                                         tree[self.right_ind].acceptable_doc_id)
            self.is_matched = tree[self.left_ind].is_matched | tree[self.right_ind].is_matched
        else:
            print('Unknown bool operation', file=sys.stderr)


class CompressedFlowNode:
    def __init__(self, node_type, val=None, left_ind=-1, right_ind=-1):
        """
        node_type:
            1 - leaf - one query string
            2 - not leaf - &|
            3 - not leaf - ! - use only left child

        """
        self.type = node_type
        self.left_ind = left_ind
        self.right_ind = right_ind
        self.parent = -1
        self.val = val

        self.is_matched = False
        self.acceptable_doc_id = -1
        if node_type == 1:
            self.list_doc_id = -1

    def set_state(self, tree, struct_inv_index, fantom_list, cur_doc_id):
        if self.type == 1:
            if not struct_inv_index.has(self.val):
                self.acceptable_doc_id = MAX_DOC_ID
                self.is_matched = False
            else:
                while self.list_doc_id < 0 or self.list_doc_id < cur_doc_id:
                    self.list_doc_id = struct_inv_index.update_step(self.val)

                fantom_list.update(cur_doc_id)
                self.acceptable_doc_id = self.list_doc_id
                self.is_matched = (self.acceptable_doc_id == cur_doc_id)

        elif self.val == '!':
            if tree[self.left_ind].is_matched:
                self.is_matched = False
                self.acceptable_doc_id = fantom_list.get_next_id()
            else:
                if tree[self.left_ind].acceptable_doc_id == fantom_list.get_current_id():
                    self.is_matched = False
                    self.acceptable_doc_id = fantom_list.get_next_id()
                else:
                    self.is_matched = True
                    self.acceptable_doc_id = fantom_list.get_current_id()

        elif self.val == '&':
            self.acceptable_doc_id = max(tree[self.left_ind].acceptable_doc_id,
                                         tree[self.right_ind].acceptable_doc_id)
            self.is_matched = tree[self.left_ind].is_matched & tree[self.right_ind].is_matched

        elif self.val == '|':
            self.acceptable_doc_id = min(tree[self.left_ind].acceptable_doc_id,
                                         tree[self.right_ind].acceptable_doc_id)
            self.is_matched = tree[self.left_ind].is_matched | tree[self.right_ind].is_matched
        else:
            print('Unknown bool operation', file=sys.stderr)


class CompressedFantomList:
    def __init__(self, list_fname='_id_list'):
        self.list_pos = -1
        self.doc_id_iter = VarbyteDecoder().decode(list_fname)
        self.list_doc_id = None

    def update(self, cur_doc_id):
        if self.list_doc_id is None:
            self.list_doc_id = next(self.doc_id_iter)

        while self.list_doc_id < cur_doc_id:
            self.list_doc_id = next(self.doc_id_iter, MAX_DOC_ID)

    def get_current_id(self):
        return self.list_doc_id

    def get_next_id(self):
        self.list_doc_id = next(self.doc_id_iter, MAX_DOC_ID)
        return self.list_doc_id



class FantomList:
    def __init__(self, doc_id_list):
        self.list_pos = -1
        self.doc_id_list = doc_id_list

    def update(self, cur_doc_id):
        while self.list_pos < 0 or self.doc_id_list[self.list_pos] < cur_doc_id:
            self.list_pos += 1

    def get_current_id(self):
        return self.doc_id_list[self.list_pos] if self.list_pos < len(self.doc_id_list) else MAX_DOC_ID

    def get_next_id(self):
        return self.doc_id_list[self.list_pos + 1] if self.list_pos + 1 < len(self.doc_id_list) else MAX_DOC_ID



class InvIndex:
    def __init__(self):
        self.inv_index = dict()

    def reset(self, keys):
        self.keys = set(keys)
        for i, token in enumerate(keys):
            raw_key = token.split('_')[0]
            self.inv_index[token] = VarbyteDecoder().decode(raw_key)

    def has(self, val):
        return val in self.keys

    def update_step(self, key):
        return next(self.inv_index[key])
