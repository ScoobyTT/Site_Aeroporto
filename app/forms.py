from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import Usuario
from app import db

class UsuarioForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    confirmSenha = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('senha')])
    submit = SubmitField('Cadastrar')

    def save(self):
        novo_usuario = Usuario(
            nome=self.nome.data,
            email=self.email.data,
            senha=self.senha.data
        )
        db.session.add(novo_usuario)   
        db.session.commit()
        return novo_usuario


class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

    def validate_senha(self, field):   
        user = getattr(self, 'user', None)
        if user is None or user.senha != self.senha.data:
            raise ValidationError('Senha incorreta. Por favor, tente novamente.')

    def authenticate(self):            
        return getattr(self, 'user', None)
