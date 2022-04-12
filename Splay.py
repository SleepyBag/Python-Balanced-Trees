import random
from tkinter import W

class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.parent = None
    
    def set_left(self, left):
        self.left = left
        if left is not None:
            left.parent = self

    def set_right(self, right):
        self.right = right
        if right is not None:
            right.parent = self
    
    def __str__(self):
        return "%d:%s" % (self.val, self.parent if self.parent is None else self.parent.val)

class SplayTree:
    def __init__(self):
        self.root = None
        self.rotate_cnt = 0

    def _splay_query(self, val, node, path):
        if node.val == val:
            return node
        elif node.val < val:
            # True for right
            path.append(True)
            return self._splay_query(val, node.right, path)
        else:
            # False for left
            path.append(False)
            return self._splay_query(val, node.left, path)

    def _set_root(self, node):
        self.root = node
        if node is not None:
            node.parent = None

    def _rotate(self, node):
        self.rotate_cnt += 1
        assert node is not self.root
        parent = node.parent
        # transplant current node to parent
        if parent.parent is None:
            self._set_root(node)
        elif parent.parent.left is parent:
            parent.parent.set_left(node)
        else:
            parent.parent.set_right(node)
        # rotate
        if node is parent.left:
            # rotate to right
            parent.set_left(node.right)
            node.set_right(parent)
        elif node is parent.right:
            # rotate to left
            parent.set_right(node.left)
            node.set_left(parent)
        else:
            assert False

    def _splay_path(self, node, path):
        while path:
            if len(path) == 1:
                # zig
                self._rotate(node)
                path.pop()
            elif path[-1] == path[-2]:
                # zig-zig
                self._rotate(node.parent)
                self._rotate(node)
                path.pop()
                path.pop()
            else:
                # zig-zag
                self._rotate(node)
                self._rotate(node)
                path.pop()
                path.pop()

    def _splay(self, val):
        # val must exist before splay
        path = []
        node = self._splay_query(val, self.root, path)
        self._splay_path(node, path)

    def _insert_leaf(self, node, new_node):
        # add a new node to where it should be
        # simply dfs find the location and insert
        # node is None only when root is None, so just set the root
        if node == None:
            self._set_root(new_node)
        elif new_node.val < node.val:
            if node.left is None:
                node.set_left(new_node)
            else:
                self._insert_leaf(node.left, new_node)
        else:
            if node.right is None:
                node.set_right(new_node)
            else:
                self._insert_leaf(node.right, new_node)

    def has_val(self, val):
        ans = self._has_val(val, self.root)
        return ans

    def _has_val(self, val, node):
        if node is None:
            return False
        if val == node.val:
            return True
        elif val < node.val:
            return self._has_val(val, node.left)
        else:
            return self._has_val(val, node.right)

    def insert(self, val):
        if self._has_val(val, self.root):
            return
        new_node = Node(val)
        self._insert_leaf(self.root, new_node)
        self._splay(val)

    def _get_max_node(self, node):
        """get the max node, with the searching path"""
        path = []
        assert node is not None
        while node.right is not None:
            path.append(node)
            node = node.right
        return node, path

    def delete(self, val):
        if not self._has_val(val, self.root):
            return
        # first, splay it to root
        self._splay(val)
        deleted_node = self.root
        if deleted_node.left is None:
            self._set_root(deleted_node.right)
        elif deleted_node.right is None:
            self._set_root(deleted_node.left)
        else:
            # splay the left tree so that the root has no right child, set it as root
            self._set_root(deleted_node.left)
            self._splay_path(*self._get_max_node(deleted_node.left))
            # combine left and right subtree
            self.root.set_right(deleted_node.right)

    def _collect_vals(self, root, arr):
        if root is None:
            return
        self._collect_vals(root.left, arr)
        arr.append(root.val)
        self._collect_vals(root.right, arr)

    def get_vals(self):
        ans = []
        self._collect_vals(self.root, ans)
        return ans

    def _to_str(self, node):
        if node is None:
            return ''
        return ' ' + str(node) + ' ' + self._to_str(node.left) + self._to_str(node.right)

    def __str__(self):
        return self._to_str(self.root)


if __name__ == '__main__':
    for n in [100, 1000, 2000, 5000]:
        arr = [i for i in range(-n, n)]
        random.shuffle(arr)
        delete = arr[:200]
        random.shuffle(arr)
        tree = SplayTree()
        expected = set()
        for i, a in enumerate(arr):
            tree.insert(a)
            expected.add(a)
            assert(tree.get_vals() == sorted(list(expected)))
            while delete and tree.has_val(delete[-1]):
                deleted = delete.pop()
                tree.delete(deleted)
                expected.remove(deleted)
                assert(tree.get_vals() == sorted(list(expected)))
        print('When there are', n, 'elements, the Splay tree rotated for', tree.rotate_cnt, 'times')