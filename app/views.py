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
        user = form.authenticate()
        if user:
            return redirect(url_for('homepage'))
        else:
            form.login.errors.append('Login ou senha inválidos.')
    return render_template('login.html', form=form)
        return render_template('login.html', login=login_data, form=form)
    return render_template('login.html', form=form)

@app.route('/cadastro/', methods=['GET', 'POST'])
def cadastro():
    form = CadastroLogin()
    if form.validate_on_submit():
        form.save()
        return redirect(url_for('homepage'))
    return render_template('cadastro.html', form=form)

@app.route('/nova/')
def novapag():
     
    

    return render_template('voos.html', login=login)
