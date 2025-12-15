from app.btree import BTree
from app.utils import VOOS_FILE, USUARIOS_FILE, carregar_json

# Inicializa as árvores vazias
btree_voos = BTree(t=3)
btree_usuarios = BTree(t=3)
arvore_nome = BTree(t=3)
arvore_cpf = BTree(t=3)
arvores_email = BTree(t=3)


def recarregar_arvores():
    """Recarrega todas as árvores do JSON"""
    global btree_voos, btree_usuarios, arvore_nome, arvore_cpf, arvores_email
    
    # Recria as árvores
    btree_voos = BTree(t=3)
    btree_usuarios = BTree(t=3)
    arvore_nome = BTree(t=3)
    arvore_cpf = BTree(t=3)
    arvores_email = BTree(t=3)
    
    # Carrega usuários
    usuarios = carregar_json(USUARIOS_FILE)
    for cliente in usuarios:
        arvore_nome.insert(cliente["nome"], cliente)
        arvore_cpf.insert(cliente["cpf"], cliente)
        arvores_email.insert(cliente["email"], cliente)
        btree_usuarios.insert(cliente["id"], cliente)
    
    # Carrega voos
    voos = carregar_json(VOOS_FILE)
    for voo in voos:
        btree_voos.insert(voo["id"], voo)
    
    print(f" Árvores recarregadas: {len(voos)} voos, {len(usuarios)} usuários")


#  Carrega as árvores na inicialização
recarregar_arvores()