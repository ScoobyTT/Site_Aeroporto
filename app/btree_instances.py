from app.btree import BTree
from app.utils import VOOS_FILE, USUARIOS_FILE, carregar_json

btree_voos = BTree(t=3)
btree_usuarios = BTree(t=3)

for voo in carregar_json(VOOS_FILE):
    btree_voos.insert(voo["id"], voo)

for usuario in carregar_json(USUARIOS_FILE):
    btree_usuarios.insert(usuario["id"], usuario)
