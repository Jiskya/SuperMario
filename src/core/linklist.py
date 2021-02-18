class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class NoneNodeData:
    pass

noneNodeData = NoneNodeData()

class LinkList:
    def __init__(self):
        self._head_ = Node(0)
        self._tail_ = None
        self._len_ = 0

    def push(self, data):
        n = Node(data)
        if self._len_ == 0:
            self._head_.next = self._tail_ = n
        else:
            self._tail_.next = n
            self._tail_ = n
        self._len_ += 1

    def push_stack(self, data):
        n = Node(data)
        if self._len_ == 0:
            self._tail_ = n
        n.next = self._head_.next
        self._head_.next = n

        self._len_ += 1

    def pop(self):
        if self._len_ == 0:
            return noneNodeData
        n = self._head_.next
        self._head_.next = n.next
        self._len_ -= 1
        return n.data

    def first(self):
        if self._len_ == 0:
            return noneNodeData
        return self._head_.next.data

    def tail(self):
        if self._len_ == 0:
            return noneNodeData
        return self._tail_.data

    def length(self):
        return self._len_
    def empty(self):
        return self._len_ == 0

        # n = Node(data)
        # if self._len_ == 0:
        #     self._head_.next = self._tail_ = n
        # else:
        #     self._tail_.next = n
        #     self._tail_ = n
        # self._len_ += 1
    def link(self, l2):
        if l2.empty():
            return
        if self.empty():
            self._head_.next = l2._head_.next
        else:
            self._tail_.next = l2._head_.next
        self._tail_ = l2._tail_
        self._len_ += l2._len_

    def _link_next_(self, pre_node, l2):
        if l2.empty():
            return
        l2._tail_.next = pre_node.next
        pre_node.next = l2._head_.next
        if self.empty() or pre_node == self._tail_:
            self._tail_ = l2._tail_

    def _insert_next_(self, pre_node, data):
        '''
            如果 pre_node不是本List節點將會導致bug
        '''
        n = Node(data)
        n.next = pre_node.next
        pre_node.next = n
        if self.empty() or pre_node == self._tail_:
            self._tail_ = n
        self._len_ += 1

    def _remove_next_(self, pre_node):
        if self._len_ == 0:
            return noneNodeData
        n = pre_node.next
        if n:
            pre_node.next = n.next
            self._len_ -= 1
            if n == self._tail_:
                self._tail_ = pre_node
            return n.data
        return noneNodeData

    def __str__(self):
        s = '['
        itr = ListIter(self)

        while itr.next():
            n = itr.get()
            if itr.this_is_tail():
                s += str(n)
            else:
                s += str(n) + ', '
        return s + ']'

    def __repr__(self):
        return 'LinkList' + self.__repr__()

    # def __eq__(self, l2):
    #     if super().__eq__(l2):
    #         return True
    #     if not isinstance(l2, LinkList):
    #         return False
    #     if self.length() != l2.length():
    #         return False
    #     itr1 = ListIter(self)
    #     itr2 = ListIter(l2)
    #     while itr1.next():
    #         itr2.next()
    #         if itr1.get() != itr2.get():
    #             return False
    #     return True

    # def __ne__(self, l2):
    #     return not self.__eq__(l2):




class ListIter:
    def __init__(self, _linklist_):
        self.list = _linklist_
        self.reset()

    def reset(self):
        self._pre_node_ = None
        self._node_ = self.list._head_

    def next(self):
        self._pre_node_ = self._node_
        self._node_ = self._node_.next
        return self._node_
    
    def get(self):
        return self._node_.data

    def this_is_first(self):
        return self._node_ == self.list._head_.next

    def this_is_tail(self):
        return self._node_ == self.list._tail_

    def insert_beforethis(self, data):
        self.list._insert_next_(self._pre_node_, data)
        self._pre_node_ = self._pre_node_.next

    # def insert_pre_dont_skip(self, data):
    #     self.list._insert_next_(self._pre_node_, data)

    def insert_afterthis(self, data):
        self.list._insert_next_(self._node_, data)

    def insert_afterthis_skip(self, data):
        self.list._insert_next_(self._node_, data)
        self.next()

    def link_beforethis(self, l2):
        self.list._link_next_(self._pre_node_, l2)
        self._pre_node_ = l2._tail_

    # def insert_pre_dont_skip(self, data):
    #     self.list._insert_next_(self._pre_node_, data)

    def link_afterthis(self, l2):
        self.list._link_next_(self._node_, l2)

    def link_afterthis_skip(self, l2):
        self.list._link_next_(self._node_, l2)
        self._node_ = l2._tail_


    def remove_this(self):
        '''
            注意本方法使用后 self._node_ <---- self._pre_node_
        '''
        self._node_ = self._pre_node_
        return self.list._remove_next_(self._pre_node_)