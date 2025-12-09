from flask import Flask
from app.btree_instances import btree_voos, btree_usuarios
app = Flask(__name__)
app.config['SECRET_KEY'] = 'KDJGUY6U46U4YU6Y4-U32HSUDUIOGPASDTRY!!RYRYERYHHFFH'

# =======================
# Inicialização das árvores B
# =======================
from app.btree import BTree
from app.forms import VOOS_FILE, USUARIOS_FILE, carregar_json


# Importar views só depois que tudo está pronto
from app import views

if __name__ == '__main__':
    app.run(debug=True)
