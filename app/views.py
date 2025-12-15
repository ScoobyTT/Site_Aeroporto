from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app
from app.forms import UsuarioForm, LoginForm, VooForm
from app.forms import carregar_json, salvar_json, proximo_id, USUARIOS_FILE, VOOS_FILE
from datetime import datetime
import app.btree_instances as trees
from app.btree import BTree
from flask import flash



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
    usuario = usuario_logado()
    
    if not usuario:
        flash("Faça login primeiro.", "warning")
        return redirect(url_for("login"))
    
    if usuario["email"] != ADMIN_EMAIL:
        flash("Acesso negado: apenas administradores.", "danger")
        return redirect(url_for("homepage"))
    
    voos = carregar_json(VOOS_FILE)
    return render_template("configa.html", voos=voos, usuario=usuario)


@app.route('/logouti')
def logout():
    session.clear()
    return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    #  Se já está logado, redireciona direto
    usuario = usuario_logado()
    if usuario:
        if usuario["email"] == ADMIN_EMAIL:
            return redirect(url_for("config"))
        return redirect(url_for("homepage"))
    
    form = LoginForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            user = form.authenticate()
            
            if user:
                session["usuario"] = user["email"]
                flash("Login realizado com sucesso!", "success")
                
                if user["email"] == ADMIN_EMAIL:
                    return redirect(url_for("config"))
                return redirect(url_for("homepage"))
            
            flash("Email ou senha inválidos.", "danger")
    
    return render_template('login.html', form=form)




@app.route('/cadastro/', methods=['GET', 'POST'])
def cadastro():
    form = UsuarioForm()

    if form.validate_on_submit():
        usuario = form.save()
        flash("Usuário cadastrado com sucesso!", "success")
        return redirect(url_for('cadastro'))

    return render_template('cadastro.html', form=form)

def usuario_logado():
    if "usuario" not in session:
        return None

    email = session["usuario"]
    usuarios = carregar_json(USUARIOS_FILE)

    return next((u for u in usuarios if u["email"] == email), None)

@app.route('/api/usuario-logado', methods=['GET'])
def api_usuario_logado():
    """Retorna dados do usuário logado via API"""
    usuario = usuario_logado()
    
    if not usuario:
        return jsonify({"erro": "Usuário não está logado"}), 401
    
    return jsonify({
        "id": usuario["id"],
        "nome": usuario["nome"],
        "email": usuario["email"]
    }), 200


@app.route("/voos/")
def voos():
    usuario = usuario_logado()
    if not usuario:
        flash("Por favor, faça login para ver seus voos.", "warning")
        return redirect(url_for("login"))

    usuario_id = usuario["id"]

    # 1. Busca as compras do usuário
    compras = carregar_json(COMPRAS_FILE)
    voos_comprados_ids = [
        c["voo_id"] for c in compras 
        if c.get("usuario_id") == usuario_id
    ]
    
    # 2. Coleta todos os voos da árvore B
    todos_voos = []
    def percorrer(node):
        if node is None:
            return
        for k, v in node.keys:
            todos_voos.append(v)
        for child in node.children:
            percorrer(child)
    
    percorrer(trees.btree_voos.root)
    
    # 3. Filtra apenas os voos que o usuário comprou
    voos_comprados = [
        v for v in todos_voos 
        if v["id"] in voos_comprados_ids
    ]
    
    # 4. Enriquece os voos com dados do usuário
    for voo in voos_comprados:
        voo['cliente_nome'] = usuario.get('nome', 'N/A')
        voo['cliente_cpf'] = usuario.get('cpf', 'N/A')
        voo['cliente_email'] = usuario.get('email', 'N/A')
        
        # Adiciona campos padrão se não existirem
        voo.setdefault('tipo_aeronave', voo.get('t_aeronave', 'Boeing 737'))
        voo.setdefault('assento', 'A definir')
        voo.setdefault('milhagem', voo.get('milhagem', 0))
        voo.setdefault('data_cadastro', voo.get('data_cadastro', 'N/A'))
    
    print(f"🛒 Compras do usuário {usuario_id}: {voos_comprados_ids}")
    print(f"✈️ Voos comprados: {len(voos_comprados)}")
    
    return render_template("voos.html", usuario=usuario, btree_voos=voos_comprados)


# Cadastro de voo: mantém rota e método
@app.route('/voo/', methods=['GET', 'POST'])
def voo():
    usuario = usuario_logado()
    if not usuario:
        flash("Por favor, faça login para cadastrar voos.", "warning")
        return redirect(url_for("login"))
        
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
            "usuario_id": int(dados.get("usuario_id", 0)),
            "n_assentos": int(dados.get("n_assentos", 100)),
            "t_aeronave": dados.get("t_aeronave", ""),
            "tipo_passagem": dados.get("tipo_passagem", ""),
            "milhagem": int(dados.get("milhagem", 0)),
            "data": dados.get("data", ""),
            "horario": dados.get("horario", ""),
            "data_cadastro": datetime.utcnow().isoformat()
        }
    except (TypeError, ValueError):
        return jsonify({"erro": "Tipos inválidos em preço/usuario_id"}), 400

    voos.append(nova)
    salvar_json(VOOS_FILE, voos)
    trees.btree_voos.insert(nova["id"], nova)
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
    trees.btree_voos.delete(id)
    trees.btree_voos.insert(id, voo_atualizado)
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
    trees.btree_voos.delete(id)
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

















@app.route("/comprar_passag")
def comprar_pass():
    return render_template("comprar.html")

# -------------------------
# API de COMPRAS (JSON)
# -------------------------
COMPRAS_FILE = "compras.json"

@app.route('/api/comprar', methods=['POST'])
def comprar_passagem():
    dados = request.get_json()
    print(f" Dados recebidos: {dados}")  # DEBUG
    
    if not dados:
        return jsonify({"erro": "JSON de entrada é obrigatório"}), 400

    try:
        voo_id = int(dados.get("voo_id"))
        usuario_id = int(dados.get("usuario_id"))
        print(f" voo_id: {voo_id}, usuario_id: {usuario_id}")  # DEBUG
    except (TypeError, ValueError) as e:
        print(f" Erro ao converter IDs: {e}")  # DEBUG
        return jsonify({"erro": "voo_id/usuario_id inválidos"}), 400

    # valida se o voo existe
    voos = carregar_json(VOOS_FILE)
    if not any(v.get("id") == voo_id for v in voos):
        print(f" Voo {voo_id} não encontrado")  # DEBUG
        return jsonify({"erro": "Voo não encontrado"}), 404

    compras = carregar_json(COMPRAS_FILE)
    print(f" Compras antes: {len(compras)}")  # DEBUG
    
    nova_compra = {
        "id": proximo_id(compras),
        "voo_id": voo_id,
        "usuario_id": usuario_id,
        "data_compra": datetime.utcnow().isoformat()
    }
    compras.append(nova_compra)
    salvar_json(COMPRAS_FILE, compras)
    
    print(f" Nova compra: {nova_compra}")  # DEBUG
    print(f" Compras depois: {len(compras)}")  # DEBUG

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





@app.route("/api/voos")
def api_voos():
    origem = request.args.get("origem", "").lower()
    destino = request.args.get("destino", "").lower()

    print(f"\n BUSCA: origem='{origem}', destino='{destino}'")

    resultados = []
    # percorre a árvore B (em vez da lista)
    def percorrer(node):
        if node is None:
            return

        for k, v in node.keys:
            print(f"    Voo na árvore: {v.get('id')} | {v['origem']} → {v['destino']}")
            if (not origem or origem in v["origem"].lower()) and \
               (not destino or destino in v["destino"].lower()):
                resultados.append(v)
        for child in node.children:
            percorrer(child)

    percorrer(trees.btree_voos.root)
    print(f" Total encontrados: {len(resultados)}\n")
    return jsonify(resultados), 200








# GET 1 cliente específico
@app.route('/api/clientt/<int:id>', methods=['GET'])
def cliente(id):
    clientes = carregar_json(USUARIOS_FILE)
    cliente = next((c for c in clientes if c["id"] == id), None)
    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404
    return jsonify(cliente), 200




# Página HTML
@app.route("/clientes")
def cliente_page():
    return render_template("cliente.html")

# GET - listar todos
from flask import jsonify

@app.route("/api/clientes", methods=["GET"])
def listar_clientes():
    clientes = trees.arvore_nome.list_in_order()

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

# ====================
# ROTAS DE GRAFO (ADICIONAR NO FINAL DO views.py)
# ====================

from app.grafo import Grafo

@app.route("/api/voos/com-conexao", methods=["GET"])
def buscar_voos_com_conexao():
    """
    Busca voos diretos + voos com 1 conexão
    Parâmetros: ?origem=xxx&destino=yyy
    """
    origem = request.args.get("origem", "")
    destino = request.args.get("destino", "")
    
    if not origem or not destino:
        return jsonify({"erro": "Parâmetros origem e destino são obrigatórios"}), 400
    
    # Carrega todos os voos da árvore B
    voos = []
    def percorrer(node):
        if node is None:
            return
        for k, v in node.keys:
            voos.append(v)
        for child in node.children:
            percorrer(child)
    
    percorrer(trees.btree_voos.root)
    
    # Cria e popula o grafo
    grafo = Grafo()
    grafo.carregar_voos(voos)
    
    # Busca todas as rotas
    resultados = grafo.buscar_todas_rotas(origem, destino)
    
    print(f"\n🔍 BUSCA COM GRAFO: {origem} → {destino}")
    print(f"   Diretos: {resultados['total_diretos']}")
    print(f"   Com conexão: {resultados['total_com_conexao']}")
    
    return jsonify(resultados), 200


@app.route("/api/grafo/estatisticas", methods=["GET"])
def estatisticas_grafo():
    """
    Retorna estatísticas do grafo de voos
    """
    # Carrega todos os voos
    voos = []
    def percorrer(node):
        if node is None:
            return
        for k, v in node.keys:
            voos.append(v)
        for child in node.children:
            percorrer(child)
    
    percorrer(trees.btree_voos.root)
    
    # Cria grafo e gera estatísticas
    grafo = Grafo()
    grafo.carregar_voos(voos)
    stats = grafo.obter_estatisticas()
    stats['cidades'] = grafo.obter_cidades()
    
    return jsonify(stats), 200