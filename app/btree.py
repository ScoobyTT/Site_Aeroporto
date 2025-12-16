class BTreeNode:
    def __init__(self, t, leaf=False):  # ← CORRIGIDO: __init__ com duplo underscore
        self.t = t
        self.leaf = leaf
        self.keys = []
        self.children = []

class BTree:
    def __init__(self, t):  # ← CORRIGIDO: __init__ com duplo underscore
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
            node.children = node.children[0:t]

    def list_in_order(self):
        resultado = []
        self._in_order(self.root, resultado)
        return resultado

    def _in_order(self, node, resultado):
        if node is None:
            return
        for i in range(len(node.keys)):
            if not node.leaf and i < len(node.children):
                self._in_order(node.children[i], resultado)
            resultado.append(node.keys[i][1])
        if not node.leaf and len(node.children) > len(node.keys):
            self._in_order(node.children[len(node.keys)], resultado)

    # ← MELHORADO: Busca parcial otimizada
    def search_prefix(self, prefix):
        """Busca todas as chaves que começam com o prefixo (case-insensitive)"""
        results = []
        prefix_lower = prefix.lower()
        self._search_prefix(self.root, prefix_lower, results)
        return results

    def _search_prefix(self, node, prefix, results):
        for key, value in node.keys:
            if isinstance(key, str) and key.lower().startswith(prefix):
                results.append(value)
        
        if not node.leaf:
            for child in node.children:
                self._search_prefix(child, prefix, results)
    
    # ← NOVO: Busca parcial em qualquer parte da string
    def search_partial(self, substring):
        """Busca chaves que contenham o substring em qualquer posição"""
        results = []
        substring_lower = substring.lower()
        self._search_partial(self.root, substring_lower, results)
        return results
    
    def _search_partial(self, node, substring, results):
        for key, value in node.keys:
            if isinstance(key, str) and substring in key.lower():
                results.append(value)
        
        if not node.leaf:
            for child in node.children:
                self._search_partial(child, substring, results)

    # ← NOVO: Método delete (caso precise)
    def delete(self, k):
        """Remove uma chave da árvore"""
        self._delete(self.root, k)
        if len(self.root.keys) == 0:
            if not self.root.leaf and len(self.root.children) > 0:
                self.root = self.root.children[0]
    
    def _delete(self, node, k):
        i = 0
        while i < len(node.keys) and k > node.keys[i][0]:
            i += 1
        
        if i < len(node.keys) and k == node.keys[i][0]:
            if node.leaf:
                node.keys.pop(i)
            else:
                self._delete_internal_node(node, k, i)
        elif not node.leaf:
            self._delete(node.children[i], k)
    
    def _delete_internal_node(self, node, k, i):
        if node.leaf:
            node.keys.pop(i)
            return
        
        # Simplificação: pega predecessor ou sucessor
        if len(node.children[i].keys) >= self.t:
            predecessor = self._get_predecessor(node, i)
            node.keys[i] = predecessor
            self._delete(node.children[i], predecessor[0])
        else:
            successor = self._get_successor(node, i)
            node.keys[i] = successor
            self._delete(node.children[i + 1], successor[0])
    
    def _get_predecessor(self, node, i):
        current = node.children[i]
        while not current.leaf:
            current = current.children[len(current.children) - 1]
        return current.keys[len(current.keys) - 1]
    
    def _get_successor(self, node, i):
        current = node.children[i + 1]
        while not current.leaf:
            current = current.children[0]
        return current.keys[0]