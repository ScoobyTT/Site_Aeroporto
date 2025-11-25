class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t  # grau mínimo
        self.leaf = leaf
        self.keys = []      # lista de pares (chave, valor)
        self.children = []  # filhos

class BTree:
    def __init__(self, t):
        self.root = BTreeNode(t, True)
        self.t = t

    def search(self, k, node=None):
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and k > node.keys[i][0]:
            i += 1
        if i < len(node.keys) and k == node.keys[i][0]:
            return node.keys[i][1]
        if node.leaf:
            return None
        return self.search(k, node.children[i])

    def insert(self, k, value):
        root = self.root
        if len(root.keys) == (2 * self.t - 1):
            temp = BTreeNode(self.t)
            self.root = temp
            temp.children.insert(0, root)
            self._split_child(temp, 0)
            self._insert_non_full(temp, k, value)
        else:
            self._insert_non_full(root, k, value)

    def _insert_non_full(self, node, k, value):
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append((k, value))
            node.keys.sort(key=lambda x: x[0])
        else:
            while i >= 0 and k < node.keys[i][0]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == (2 * self.t - 1):
                self._split_child(node, i)
                if k > node.keys[i][0]:
                    i += 1
            self._insert_non_full(node.children[i], k, value)

    def _split_child(self, parent, i):
        t = self.t
        node = parent.children[i]
        new_node = BTreeNode(t, node.leaf)
        parent.children.insert(i + 1, new_node)
        parent.keys.insert(i, node.keys[t - 1])
        new_node.keys = node.keys[t:(2 * t - 1)]
        node.keys = node.keys[0:(t - 1)]
        if not node.leaf:
            new_node.children = node.children[t:(2 * t)]
            node.children = node.children[0:t - 1]
