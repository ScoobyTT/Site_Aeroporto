from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from app.models import Usuario, Passagem
from app.forms import UsuarioForm, LoginForm, VooForm


# -------------------------
# Páginas principais
# -------------------------
@app.route("/", methods=["GET", "POST"])
def homepage():
    resultados = None

    if request.method == "POST":
        origem = request.form.get("origem")
        destino = request.form.get("destino")
        data = request.form.get("data")

        if origem and destino and data:
            resultados = Passagem.query.filter_by(
                origem=origem,
                destino=destino,
                data=data
            ).all()

    return render_template("index.html", resultados=resultados)

@app.route('/teste/')
def teste():
    return render_template('teste.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    erro = None
    if form.validate_on_submit():
        user = form.authenticate()
        if user:
            return redirect(url_for('homepage'))
        else:
            erro = 'Login ou senha inválidos.'
    return render_template('login.html', form=form, erro=erro)

@app.route('/cadastro/', methods=['GET', 'POST'])
def cadastro():
    form = UsuarioForm()
    if form.validate_on_submit():
        form.save()
        return redirect(url_for('homepage'))
    return render_template('cadastro.html', form=form)

from flask import render_template, session, flash
from app import app
from app.models import Usuario, Passagem

@app.route("/voos/")
def voos():
    usuario_id = 1  # Teste fixo
    usuario = Usuario.query.get(usuario_id)
    voos_info = Passagem.query.filter_by(usuario_id=usuario_id).all()
    print("Passagens encontradas:", voos_info)
    return render_template("voos.html", usuario=usuario, voos=voos_info)


@app.route('/voo/', methods=['GET', 'POST'])
def voo():
    form = VooForm()
    if form.validate_on_submit():
        flash('Voo cadastrado com sucesso!', 'success')
        return redirect(url_for('homepage'))
    return render_template('voo.html', form=form)

# -------------------------
# Página principal de passagens
# -------------------------
@app.route('/passagens')
def pagina_passagens():
    passagens = Passagem.query.all()
    return render_template('passagens.html', passagens=passagens)

# -------------------------
# API de Passagens
# -------------------------
@app.route('/api/passagens', methods=['POST'])
def adicionar_passagem():
    dados = request.get_json()
    nova = Passagem(
        origem=dados.get("origem"),
        destino=dados.get("destino"),
        preco=float(dados.get("preco", 0)),
        usuario_id=int(dados.get("usuario_id", 0))
    )
    db.session.add(nova)
    db.session.commit()
    return jsonify({"mensagem": "Passagem adicionada com sucesso!"}), 201

@app.route("/api/passagens/<int:usuario_id>", methods=["GET"])
def listar_passagens(usuario_id):
    passagens = Passagem.query.filter_by(usuario_id=usuario_id).all()
    resultado = [
        {"id": p.id, "origem": p.origem, "destino": p.destino, "preco": p.preco}
        for p in passagens
    ]
    return jsonify(resultado), 200

@app.route("/api/passagens/<int:id>", methods=["PUT"])
def editar_passagem(id):
    dados = request.get_json()
    passagem = Passagem.query.get(id)
    if not passagem:
        return jsonify({"erro": "Passagem não encontrada"}), 404

    passagem.origem = dados.get("origem", passagem.origem)
    passagem.destino = dados.get("destino", passagem.destino)
    preco = dados.get("preco", passagem.preco)
    passagem.preco = float(preco) if preco is not None else passagem.preco

    db.session.commit()
    return jsonify({"mensagem": "Passagem atualizada com sucesso!"}), 200

@app.route("/api/passagens/<int:id>", methods=["DELETE"])
def remover_passagem(id):
    passagem = Passagem.query.get(id)
    if not passagem:
        return jsonify({"erro": "Passagem não encontrada"}), 404

    db.session.delete(passagem)
    db.session.commit()
    return jsonify({"mensagem": "Passagem removida com sucesso!"}), 200



    
