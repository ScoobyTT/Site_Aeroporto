from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app
from app.forms import UsuarioForm, LoginForm, VooForm
from app.forms import carregar_json, salvar_json, proximo_id
from app.forms import USUARIOS_FILE, VOOS_FILE
from datetime import datetime
from flask import Flask
import json, os
from app.btree_instances import btree_voos, btree_usuarios, arvore_nome, arvore_cpf, btree_usuarios

# Homepage: busca passagens por origem/destino/data
@app.route("/", methods=["GET", "POST"])
def homepage():
    if request.method == "POST":
        origem = request.form.get("origem") or (request.json or {}).get("origem")
        destino = request.form.get("destino") or (request.json or {}).get("destino")
        data = request.form.get("data") or (request.json or {}).get("data")

        if not (origem and destino and data):
            return jsonify({"erro": "Parâmetros inválidos. Envie origem, destino e data."}), 400

        voos = carregar_json(VOOS_FILE)
        resultados = [
            v for v in voos
            if v.get("origem") == origem and v.get("destino") == destino and v.get("data") == data
        ]
        return jsonify({"resultados": resultados}), 200

    # GET
    return render_template("index.html")
    
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_SENHA = "admin123"


@app.route('/conf')
def config():
    print("SESSION ATUAL:", dict(session))   # <<< debug importante
    # 1. Verifica se existe login
    if "usuario" not in session:
        return redirect(url_for("login"))
    
    session_usuario = session["usuario"]
    # 2. Verifica se o usuário logado é o admin
    if session["usuario"] != ADMIN_EMAIL:
        flash("Acesso negado: apenas administradores podem acessar esta página.", "danger")
        return redirect(url_for("login"))
    if "usuario" in session:
        return render_template("configa.html")
    
    voos = carregar_json(VOOS_FILE)
    return render_template("configa.html", voos=voos)




@app.route('/logouti')
def logout():
    session.clear()
    return redirect(url_for('login'))



# Login: mantém rota e método, responde JSON
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = form.authenticate()
            if user:#por um if de verificacao pra saber qual o login
                session["usuario"] = user["email"]
                flash("Login realizado com sucesso!", "success")
                if user["email"] == ADMIN_EMAIL:
                    return redirect(url_for("config"))
                else:
                    return redirect(url_for("homepage"))
            return jsonify({"erro": "Login ou senha inválidos."}), 401
        return jsonify({"erro": "Dados inválidos", "detalhes": form.errors}), 400

    # GET
    return render_template('login.html', form=form)




from flask import flash

@app.route('/cadastro/', methods=['GET', 'POST'])
def cadastro():
    form = UsuarioForm()

    if form.validate_on_submit():
        usuario = form.save()
        flash("Usuário cadastrado com sucesso!", "success")
        return redirect(url_for('cadastro'))

    return render_template('cadastro.html', form=form)



# Página de voos do usuário: mantém rota
@app.route("/voos/")
def voos():
    usuario_id = 1  # Teste fixo
    usuarios = carregar_json(USUARIOS_FILE)
    usuario = next((u for u in usuarios if u["id"] == usuario_id), None)
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    voos_info = [v for v in carregar_json(VOOS_FILE) if v.get("usuario_id") == usuario_id]
    return render_template("voos.html", usuario=usuario, voos=voos_info)




# Cadastro de voo: mantém rota e método
@app.route('/voo/', methods=['GET', 'POST'])
def voo():
    form = VooForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            novo = form.save(usuario_id=1)  # ajuste se tiver sessão
            return jsonify({
                "mensagem": "Voo cadastrado com sucesso!",
                "voo": novo
            }), 201
        return jsonify({"erro": "Dados inválidos", "detalhes": form.errors}), 400

    # GET
    return render_template('voo.html', form=form)




# -------------------------
# API de Passagens (JSON)
# -------------------------

# Adicionar passagem via API: mantém rota e método
@app.route('/api/passagens', methods=['POST'])
def adicionar_passagem():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "JSON de entrada é obrigatório"}), 400

    voos = carregar_json(VOOS_FILE)
    try:
        nova = {
            "id": proximo_id(voos),
            "origem": dados.get("origem"),
            "destino": dados.get("destino"),
            "data": dados.get("data"),
            "horario": dados.get("horario"),
            "preco": float(dados.get("preco", 0)),
            "usuario_id": int(dados.get("usuario_id", 0))
        }
    except (TypeError, ValueError):
        return jsonify({"erro": "Tipos inválidos em preço/usuario_id"}), 400

    voos.append(nova)
    salvar_json(VOOS_FILE, voos)
    return jsonify({"mensagem": "Passagem adicionada com sucesso!", "id": nova["id"]}), 201


# Listar passagens por usuário: mantém rota e método
@app.route("/api/passagens/<int:usuario_id>", methods=["GET"])
def listar_passagens(usuario_id):
    voos = carregar_json(VOOS_FILE)
    resultado = [
        {"id": v["id"], "origem": v["origem"], "destino": v["destino"], "data": v.get("data"), "preco": v.get("preco")}
        for v in voos if v.get("usuario_id") == usuario_id
    ]
    return jsonify(resultado), 200


# Editar passagem: mantém rota e método
@app.route("/api/passagens/<int:id>", methods=["PUT"])
def editar_passagem(id):
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "JSON de entrada é obrigatório"}), 400

    voos = carregar_json(VOOS_FILE)
    encontrado = False
    for v in voos:
        if v["id"] == id:
            v["origem"] = dados.get("origem", v["origem"])
            v["destino"] = dados.get("destino", v["destino"])
            v["data"] = dados.get("data", v.get("data"))
            v["horario"] = dados.get("horario", v.get("horario"))
            if "preco" in dados:
                try:
                    v["preco"] = float(dados["preco"])
                except (TypeError, ValueError):
                    return jsonify({"erro": "Preço inválido"}), 400
            encontrado = True
            break

    if not encontrado:
        return jsonify({"erro": "Passagem não encontrada"}), 404

    salvar_json(VOOS_FILE, voos)
    return jsonify({"mensagem": "Passagem atualizada com sucesso!"}), 200


# Remover passagem: mantém rota e método
@app.route("/api/passagens/<int:id>", methods=["DELETE"])
def remover_passagem(id):
    voos = carregar_json(VOOS_FILE)
    tamanho_antes = len(voos)
    voos = [v for v in voos if v["id"] != id]

    if len(voos) == tamanho_antes:
        return jsonify({"erro": "Passagem não encontrada"}), 404

    salvar_json(VOOS_FILE, voos)
    return jsonify({"mensagem": "Passagem removida com sucesso!"}), 200


@app.route("/api/passagens", methods=["GET"])
def buscar_passagens():
    origem = request.args.get("origem", "").lower()
    destino = request.args.get("destino", "").lower()

    voos = carregar_json(VOOS_FILE)

    filtrados = [
        v for v in voos 
        if origem in v["origem"].lower()
        and destino in v["destino"].lower()
    ]

    return jsonify(filtrados), 200













@app.route("/api/voos/<int:id>", methods=["GET"])
def buscar_voo(id):
    voo = btree_voos.search(id)
    if voo:
        return jsonify(voo), 200
    return jsonify({"erro": "Voo não encontrado"}), 404





@app.route("/comprar_passag")
def comprar_pass():
    return render_template("comprar.html")

# -------------------------
# API de COMPRAS (JSON)
# -------------------------
COMPRAS_FILE = "compras.json"

from datetime import datetime  # no topo

@app.route('/api/comprar', methods=['POST'])
def comprar_passagem():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "JSON de entrada é obrigatório"}), 400

    try:
        voo_id = int(dados.get("voo_id"))
        usuario_id = int(dados.get("usuario_id"))
    except (TypeError, ValueError):
        return jsonify({"erro": "voo_id/usuario_id inválidos"}), 400

    # valida se o voo existe
    voos = carregar_json(VOOS_FILE)
    if not any(v.get("id") == voo_id for v in voos):
        return jsonify({"erro": "Voo não encontrado"}), 404

    compras = carregar_json(COMPRAS_FILE)
    nova_compra = {
        "id": proximo_id(compras),
        "voo_id": voo_id,
        "usuario_id": usuario_id,
        "data_compra": datetime.utcnow().isoformat()
    }
    compras.append(nova_compra)
    salvar_json(COMPRAS_FILE, compras)

    # opcional: marcar voo como comprado
    for v in voos:
        if v["id"] == voo_id:
            v["usuario_id"] = usuario_id
            salvar_json(VOOS_FILE, voos)
            break

    return jsonify({
        "mensagem": "Compra registrada com sucesso!",
        "compra_id": nova_compra["id"]
    }), 201

@app.route('/api/compras/<int:usuario_id>', methods=['GET'])
def listar_compras(usuario_id):
    compras = carregar_json(COMPRAS_FILE)
    resultado = [
        c for c in compras if c.get("usuario_id") == usuario_id
    ]
    return jsonify(resultado), 200

@app.route('/api/compras/<int:compra_id>', methods=['DELETE'])
def cancelar_compra(compra_id):
    compras = carregar_json(COMPRAS_FILE)
    tamanho_antes = len(compras)
    compras = [c for c in compras if c["id"] != compra_id]

    if len(compras) == tamanho_antes:
        return jsonify({"erro": "Compra não encontrada"}), 404

    salvar_json(COMPRAS_FILE, compras)
    return jsonify({"mensagem": "Compra cancelada com sucesso!"}), 200


@app.route("/api/compras/<int:compra_id>", methods=['PUT'])
def editar_compra(compra_id):
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "JSON de entrada é obrigatório"}), 400

    compras = carregar_json(COMPRAS_FILE)
    encontrado = False
    for c in compras:
        if c["id"] == compra_id:
            if "voo_id" in dados:
                try:
                    c["voo_id"] = int(dados["voo_id"])
                except (TypeError, ValueError):
                    return jsonify({"erro": "Voo ID inválido"}), 400
            if "usuario_id" in dados:
                try:
                    c["usuario_id"] = int(dados["usuario_id"])
                except (TypeError, ValueError):
                    return jsonify({"erro": "Usuário ID inválido"}), 400
            encontrado = True
            break

    if not encontrado:
        return jsonify({"erro": "Compra não encontrada"}), 404

    salvar_json(COMPRAS_FILE, compras)
    return jsonify({"mensagem": "Compra atualizada com sucesso!"}), 200



# Exemplo de uso de Árvore B para armazenar voos (teste)
from app.btree import BTree  # supondo que você crie um módulo btree.py
btree_voos = BTree(3)  # grau mínimo 3
# carregar voos do JSON e inserir na árvore
for v in carregar_json(VOOS_FILE):
    btree_voos.insert(v["id"], v)

@app.route("/api/voos")
def api_voos():
    origem = request.args.get("origem", "").lower()
    destino = request.args.get("destino", "").lower()

    resultados = []
    # percorre a árvore B (em vez da lista)
    def percorrer(node):
        for k, v in node.keys:
            if (not origem or origem in v["origem"].lower()) and \
               (not destino or destino in v["destino"].lower()):
                resultados.append(v)
        for child in node.children:
            percorrer(child)

    percorrer(btree_voos.root)
    return jsonify(resultados), 200








# GET 1 cliente específico
@app.route('/api/clientt/<int:id>', methods=['GET'])
def cliente(id):
    clientes = carregar_json(USUARIOS_FILE)
    cliente = next((c for c in clientes if c["id"] == id), None)
    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404
    return jsonify(cliente), 200


USUARIOS_FILE = "usuarios.json"

def carregar_json(file):
    if not os.path.exists(file):
        return []
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def salvar_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def proximo_id(registros):
    if not registros:
        return 1
    return max(item.get("id", 0) for item in registros) + 1

# Página HTML
@app.route("/clientes")
def cliente_page():
    return render_template("cliente.html")

# GET - listar todos
from flask import jsonify

@app.route("/api/clientes", methods=["GET"])
def listar_clientes():
    clientes = arvore_nome.list_in_order()

    # converter objetos Python para JSON
    clientes_json = []
    for c in clientes:
        clientes_json.append({
            "id": c["id"],
            "cpf": c["cpf"],
            "nome": c["nome"],
            "email": c["email"]
        })

    return jsonify(clientes_json)

# POST - criar novo cliente
@app.route("/api/clientes", methods=["POST"])
def criar_cliente():
    dados = request.get_json()
    if not dados or "nome" not in dados or "email" not in dados or "senha" not in dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    clientes = carregar_json(USUARIOS_FILE)
    novo_cliente = {
        "id": proximo_id(clientes),
        "nome": dados["nome"],
        "email": dados["email"],
        "senha": dados["senha"]
    }
    clientes.append(novo_cliente)
    salvar_json(USUARIOS_FILE, clientes)
    return jsonify({"mensagem": "Cliente criado com sucesso!"}), 201



# PUT - editar cliente
@app.route("/api/clientes/<int:id>", methods=["PUT"])
def editar_cliente(id):
    dados = request.get_json()
    clientes = carregar_json(USUARIOS_FILE)

    for c in clientes:
        if c["id"] == id:
            c["nome"] = dados.get("nome", c["nome"])
            c["email"] = dados.get("email", c["email"])
            if "senha" in dados:
                c["senha"] = dados["senha"]
            salvar_json(USUARIOS_FILE, clientes)
            return jsonify({"mensagem": "Cliente atualizado com sucesso!"}), 200

    return jsonify({"erro": "Cliente não encontrado"}), 404

# DELETE - remover cliente
@app.route("/api/clientes/<int:id>", methods=["DELETE"])
def remover_cliente(id):
    clientes = carregar_json(USUARIOS_FILE)
    tamanho_antes = len(clientes)
    clientes = [c for c in clientes if c["id"] != id]

    if len(clientes) == tamanho_antes:
        return jsonify({"erro": "Cliente não encontrado"}), 404

    salvar_json(USUARIOS_FILE, clientes)
    return jsonify({"mensagem": "Cliente removido com sucesso!"}), 200

@app.route("/api/clientes/buscar")
def buscar_cliente():
    chave = request.args.get("q")

    if chave is None:
        return jsonify({"erro": "Parâmetro 'q' é obrigatório"}), 400

    # tenta nome
    cliente = arvore_nome.search(chave)

    # tenta cpf
    if not cliente:
        cliente = arvore_cpf.search(chave)

    # tenta ID (apenas se for número)
    if not cliente and chave.isdigit():
        cliente = btree_usuarios.search(int(chave))

    if cliente:
        return jsonify(cliente), 200

    return jsonify({"mensagem": "Cliente não encontrado"}), 404

