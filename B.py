from bisect import bisect
import random

class Node:
    def __init__(self, tree):
        self.vals = []
        self.children = []
        self.parent = None
        self.tree = tree

    def degree(self):
        return len(self.vals) + 1

    def split(self):
        mid = len(self.vals) // 2
        left = Node(self.tree)
        left.vals = self.vals[:mid]
        left.set_children(self.children[:mid + 1])
        right = Node(self.tree)
        right.vals = self.vals[mid + 1:]
        right.set_children(self.children[mid + 1:])
        return self.vals[mid], left, right

    def absorb(self, mid, left, right):
        # absorb a split child node
        for i, val in enumerate(self.vals):
            if mid < val:
                self.vals = self.vals[:i] + [mid] + self.vals[i:]
                self.set_children(self.children[:i] + [left, right] + self.children[i + 1:])
                break
        else:
            self.vals = self.vals + [mid]
            self.set_children(self.children[:-1] + [left, right])

    def insert(self, insert_val):
        # must insert to a leaf node
        for i, val in enumerate(self.vals):
            if insert_val < val:
                self.vals = self.vals[:i] + [insert_val] + self.vals[i:]
                return
        self.vals.append(insert_val)

    def borrow(self, to, fr):
        to_node = self.children[to]
        fr_node = self.children[fr]
        if to < fr:
            to_node.vals.append(self.vals[to])
            self.vals[to] = fr_node.vals[0]
            fr_node.vals = fr_node.vals[1:]
            # if they have children to deal with
            if to_node.children:
                to_node.children.append(fr_node.children[0])
                fr_node.children = fr_node.children[1:]
                to_node.children[-1].parent = to_node
        else:
            to_node.vals = [self.vals[fr]] + to_node.vals
            self.vals[fr] = fr_node.vals[-1]
            fr_node.vals = fr_node.vals[:-1]
            # if they have children to deal with
            if to_node.children:
                to_node.children = [fr_node.children[-1]] + to_node.children
                fr_node.children = fr_node.children[:-1]
                to_node.children[0].parent = to_node

    def fuse(self, a, b):
        a, b = min(a, b), max(a, b)
        node_a, node_b = self.children[a], self.children[b]
        new_node = Node(self.tree)
        new_node.vals = node_a.vals + [self.vals[a]] + node_b.vals
        new_node.set_children(node_a.children + node_b.children)
        new_node.parent = self
        del self.vals[a]
        # the chidren of root node is fused and become new root
        self.children[a:b + 1] = [new_node]
        if not self.vals and self is self.tree.root:
            self.tree.root = self.children[0]
            self.tree.root.parent = None
        return new_node

    def set_children(self, children):
        self.children = children
        for child in children:
            child.parent = self

    def validate(self):
        if self.vals != sorted(self.vals):
            print('vals not in order!')
            return False
        return not self.children or len(self.vals) == len(self.children) - 1

class BTree:
    def __init__(self, d):
        self.root = Node(self)
        self.d = d

    def _search_insert_node(self, val, root):
        if not root.children:
            return root
        return self._search_insert_node(val, root.children[bisect(root.vals, val)])

    def search_val_node(self, val, root=None):
        if root is None:
            root = self.root
        if val in root.vals:
            return root
        if not root.children:
            return None
        return self.search_val_node(val, root.children[bisect(root.vals, val)])

    def has_val(self, val):
        return self.search_val_node(val) is not None

    def insert(self, val):
        # bottom-up insertion
        if self.has_val(val):
            return
        node = self._search_insert_node(val, self.root)
        node.insert(val)
        while node is not None: 
            # node needs to be split
            if node.degree() > 2 * self.d:
                mid, left, right = node.split()
                # push value and new nodes to parent node
                if node.parent is not None:
                    node.parent.absorb(mid, left, right)
                else:
                    # root was split
                    new_root = Node(self)
                    new_root.vals = [mid]
                    new_root.set_children([left, right])
                    left.parent = new_root
                    right.parent = new_root
                    self.root = new_root
                    return
                node = node.parent
            else:
                break
    
    def delete(self, target, node=None):
        # top-down delete
        if node is None:
            # case 0: value not in tree
            if not self.has_val(target):
                return
            node = self.root
        # case 1: value in children
        if target not in node.vals:
            for i, val in enumerate(node.vals):
                if target < val:
                    target_node = node.children[i]
                    break
            else:
                i = len(node.vals)
                target_node = node.children[-1]
            # if target node doesn't have enough degree to delete, we need to either borrow or fuse
            if target_node.degree() == self.d:
                if i > 0 and node.children[i - 1].degree() > self.d:
                    # can borrow from left sibling
                    sibling = i - 1
                elif i + 1 < len(node.children) and node.children[i + 1].degree() > self.d:
                    # can borrow from right sibling
                    sibling = i + 1
                else:
                    # cannot borrow
                    sibling = None
                if sibling is not None:
                    # can borrow
                    node.borrow(i, sibling)
                else:
                    # cannot borrow, we need to fuse two nodes
                    sibling = i - 1 if i > 0 else i + 1
                    target_node = node.fuse(i, sibling)
            # now the target node must have enough degree to delete
            self.delete(target, target_node)
        # case 2: target value is in current node. 
        else:
            index = node.vals.index(target)
            # if in leaf node, just delete 
            # it must be the root
            # or its degree must be larger than d (otherwise the caller will help borrow or fuse)
            if not node.children:
                del node.vals[index]
            else:
                left, right = node.children[index], node.children[index + 1]
                # delete a value from left or right child node may reduce the degree of the node
                # so before recursively delete, we must make sure its degree larger than d
                if left.degree() == right.degree() == self.d:
                    # cannot delete in either left or right node, must fuse first
                    new_child = node.fuse(index, index + 1)
                    # after fusng, the target value is in the child node
                    self.delete(target, new_child)
                elif left.degree() > self.d:
                    left_max = self.get_max(left)
                    self.delete(left_max, left)
                    node.vals[index] = left_max
                else:
                    right_min = self.get_min(right)
                    self.delete(right_min, right)
                    node.vals[index] = right_min

    def get_max(self, node):
        if not node.children:
            return node.vals[-1]
        return self.get_max(node.children[-1])

    def get_min(self, node):
        if not node.children:
            return node.vals[0]
        return self.get_min(node.children[0])

    def _get_nodes_depth(self, depth, node, depths):
        if not node.children:
            depths.append(depth)
        for child in node.children:
            self._get_nodes_depth(depth + 1, child, depths)

    def _get_nodes_degree(self, node, degrees):
        degrees.append(node.degree())
        for child in node.children:
            self._get_nodes_degree(child, degrees)

    def _collect_vals(self, arr, node):
        if not node.children:
            arr += node.vals
        else:
            for i, val in enumerate(node.vals):
                self._collect_vals(arr, node.children[i])
                arr.append(val)
            self._collect_vals(arr, node.children[-1])

    def _validate_val_children_count(self, node):
        if not node.children:
            return True
        if len(node.vals) != len(node.children) - 1:
            return False
        ans = True
        for child in node.children:
            return ans or self._validate_val_children_count(child)
        return ans

    def get_vals(self):
        arr = []
        self._collect_vals(arr, self.root)
        return arr

    def validate(self):
        # check if all elements are in order
        vals = self.get_vals()
        if not all(v1 < v2 for v1, v2 in zip(vals, vals[1:])):
            print('values not in order:', vals)
            return False
        # all nodes must have n_values = n_children + 1, except for leaf nodes
        if not self._validate_val_children_count(self.root):
            print('value count and children count mismatch!')
            return False
        # all leaf nodes must have the same depth
        depths = []
        self._get_nodes_depth(0, self.root, depths)
        if any(depth != depths[0] for depth in depths):
            print('depths not all the same!')
            return False
        # all nodes must have d <= degree <= 2d
        # except root node, who must have 2 <= degree <= 2d when there are other nodes
        degrees = []
        self._get_nodes_degree(self.root, degrees)
        if not all(degree <= 2 * self.d for degree in degrees):
            print('degrees illegal with d =', self.d, ':', degrees)
            return False
        # the first is root
        if not all(degree >= self.d for degree in degrees[1:]):
            print('degrees illegal!')
            return False
        if len(degrees) > 1 and degrees[0] < 2:
            print('degrees illegal!')
            return False
        return True

if __name__ == '__main__':
    for _ in range(10):
        arr = [i for i in range(-1000, 1000)]
        random.shuffle(arr)
        delete = arr[:200]
        random.shuffle(arr)
        tree = BTree(random.randint(2, 10))
        expected = set()
        for i, a in enumerate(arr):
            tree.insert(a)
            expected.add(a)
            assert(tree.validate())
            assert(tree.get_vals() == sorted(list(expected)))
            while delete and tree.has_val(delete[-1]):
                deleted = delete.pop()
                tree.delete(deleted)
                expected.remove(deleted)
                assert(tree.validate())
                assert(tree.get_vals() == sorted(list(expected)))