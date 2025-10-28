from flask import render_template, request, redirect, url_for
from app import app, db
from app.models import Usuario
from app.forms import UsuarioForm, LoginForm

@app.route('/')
def homepage():
    usuario = 'Erik Pulga'
    idade = 17
    login = {'usuario': usuario, 'idade': idade}
    return render_template('index.html', login=login)

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


from app.forms import VooForm
from flask import render_template, redirect, url_for, flash

@app.route('/voo/', methods=['GET', 'POST'])
def voo():
    form = VooForm()
    if form.validate_on_submit():
        # Aqui você pode salvar no banco se tiver um modelo Voo
        flash('Voo cadastrado com sucesso!', 'success')
        return redirect(url_for('homepage'))
    return render_template('voo.html', form=form)


@app.route('/voos/')
def voos():
    voos_info = [
        {
            'origem': 'Salvador',
            'destino': 'São Paulo',
            'data': '25/12/2025',
            'horario': '14:30',
            'preco': 'R$ 499,90'
        },
        {
            'origem': 'Rio de Janeiro',
            'destino': 'Fortaleza',
            'data': '10/01/2026',
            'horario': '09:00',
            'preco': 'R$ 620,00'
        },
        {
            'origem': 'Brasília',
            'destino': 'Recife',
            'data': '05/11/2025',
            'horario': '18:45',
            'preco': 'R$ 550,00'
        }
    ]
    return render_template('voos.html', voos=voos_info)
