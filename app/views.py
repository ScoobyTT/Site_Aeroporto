from flask import render_template, request, redirect, url_for
from app import app, db
from app.models import User
from app.forms import CadastroLogin, LoginForm

@app.route('/')
def homepage():
    usuario = 'Erik Pulga'
    idade = 17
    login = {'usuario': usuario, 'idade': idade}
    return render_template('index.html', login=login)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_data = {
            'login': form.login.data,
            'senha': form.senha.data
        }
        return render_template('login.html', login=login_data, form=form)
    return render_template('login.html', form=form)

@app.route('/cadastro/', methods=['GET', 'POST'])
def cadastro():
    form = CadastroLogin()
    if form.validate_on_submit():
        novo_usuario = User(username=form.nome.data, email=form.email.data)
        db.session.add(novo_usuario)
        db.session.commit()
        return redirect(url_for('homepage'))
    return render_template('cadastro.html', form=form)

@app.route('/nova/')
def novapag():
     
    

    return render_template('voos.html', login=login)
