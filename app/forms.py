from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from app.models import Cadastro
from app import db

class CadastroLogin(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    confirmSenha = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('senha')])
    submit = SubmitField('Cadastrar')

    def save(self):
        cadastro = Cadastro(
            nome=self.nome.data,
            email=self.email.data,
            senha=self.senha.data
        )
        db.session.add(cadastro)
        db.session.commit()
        return cadastro

class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

    def validate_login(self):
        user = Cadastro.query.filter_by(email=self.login.data).first()
        if user is None:
            raise ValidationError('Login inválido. Por favor, tente novamente.')
        return user
