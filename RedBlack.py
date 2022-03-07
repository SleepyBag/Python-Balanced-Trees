import random

class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.parent = None
        # True for black, False for red
        self.black = False

    def set_left(self, child):
        self.left = child
        if child is not None:
            child.parent = self

    def set_right(self, child):
        self.right = child
        if child is not None:
            child.parent = self
    
    def __str__(self) -> str:
        return ("%s:%d:%s" % (('b' if self.black else 'r'), self.val, self.parent if self.parent is None else self.parent.val))

class RedBlackTree:
    def __init__(self):
        self.root = None

    def _has_val(self, val, node):
        # reach leaf node
        if node is None:
            return False
        if node.val == val:
            return True
        if node.val < val:
            return self._has_val(val, node.right)
        else:
            return self._has_val(val, node.left)
            

    def has_val(self, val):
        return self._has_val(val, self.root)

    def _insert_leaf(self, node, new_node):
        # add a new node to where it should be
        # simply dfs find the location and insert
        # node is None only when root is None, so just set the root
        if node == None:
            # root node is black
            new_node.black = True
            self.root = new_node
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

    def get_black_parent(self, node):
        if node.black:
            return node
        if node.parent is None:
            return None
        if node.parent.black:
            return node.parent
        if node.parent.parent.black:
            return node.parent.parent
        # node, parent, and grandparent must not be all red
        assert(False)

    def _rotate(self, root, new_root, l, r, lr, rl):
        parent = root.parent
        if parent is None:
            self.root = new_root
            new_root.parent = None
        elif parent.left is root:
            parent.set_left(new_root)
        else:
            parent.set_right(new_root)
        new_root.set_left(l)
        new_root.set_right(r)
        l.set_right(lr)
        r.set_left(rl)
        # root is black, and two children are both red
        new_root.black = True
        l.black = False
        r.black = False
            

    def adjust_cluster(self, root):
        # adjust a 2-3-4 cluster so that there is no red grandson, return the new root node
        # there is at most one red grandson
        left = root.left
        right = root.right
        lred = left and not left.black
        rred = right and not right.black
        if lred and rred:
            # if it is a 4 cluster, push black down
            for grandson in [left.left, left.right, right.left, right.right]:
                if grandson and not grandson.black:
                    root.black = False
                    left.black = True
                    right.black = True
                    # need to adjust parents
                    return root
            return root
        elif lred:
            llred = left.left and not left.left.black
            lrred = left.right and not left.right.black
            # ll and lr could not be both red
            assert(not (llred and lrred))
            # let's rotate
            if llred:
                self._rotate(root, left, left.left, root, left.left.right, left.right)
                return left
            elif lrred:
                self._rotate(root, left.right, left, root, left.right.left, left.right.right)
                return left.right
        elif rred:
            rlred = right.left and not right.left.black
            rrred = right.right and not right.right.black
            # ll and lr could not be both red
            assert(not (rlred and rrred))
            # let's _rotate
            if rlred:
                self._rotate(root, right.left, root, right, right.left.left, right.left.right)
                return right.left
            elif rrred:
                self._rotate(root, right, root, right.right, right.left, right.right.left)
                return right
        return root

    def insert(self, val):
        if self.has_val(val):
            return

        # insert the new value to a leaf node
        new_node = Node(val)
        self._insert_leaf(self.root, new_node)

        node = new_node
        # while current node is red, adjust this cluster
        while node is not None and not node.black:
            # find the root of this 2-3-4 cluster
            black = self.get_black_parent(node)

            if black is None:
                # we are at the root
                node.black = True
                node = None
            else:
                node = self.adjust_cluster(black)

    def delete(self, val):
        if not self.has_val(val):
            return

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

    def get_black_depths(self, node, depth, depths):
        if node is None:
            depths.append(depth)
            return
        if node.black:
            depth += 1
        self.get_black_depths(node.left, depth, depths)
        self.get_black_depths(node.right, depth, depths)

    def _validate_consequent_red(self, node):
        if node is None:
            return True
        if not node.black and node.parent is not None and not node.parent.black:
            return False
        if not self._validate_consequent_red(node.left):
            return False
        if not self._validate_consequent_red(node.right):
            return False
        return True

    def validate(self):
        if self.root is not None and not self.root.black:
            print('root is red:', self.root)
            print(self)
            return False
        depths = []
        self.get_black_depths(self.root, 0, depths)
        if not all(depth == depths[0] for depth in depths):
            print('depths in term of black nodes not the same:', depths)
            print(self)
            return False
        if not self._validate_consequent_red(self.root):
            print('find two consequent red nodes!')
            print(self)
            return False
        return True

    def _to_str(self, node):
        if node is None:
            return ''
        return ' ' + str(node) + ' ' + self._to_str(node.left) + self._to_str(node.right)

    def __str__(self):
        return self._to_str(self.root)

if __name__ == '__main__':
    for _ in range(10):
        arr = [i for i in range(-1000, 1000)]
        random.shuffle(arr)
        delete = arr[:200]
        random.shuffle(arr)
        tree = RedBlackTree()
        expected = set()
        for i, a in enumerate(arr):
            tree.insert(a)
            expected.add(a)
            assert(tree.validate())
            assert(tree.get_vals() == sorted(list(expected)))
            # while delete and tree.has_val(delete[-1]):
            #     deleted = delete.pop()
            #     tree.delete(deleted)
            #     expected.remove(deleted)
            #     assert(tree.validate())
            #     assert(tree.get_vals() == sorted(list(expected)))