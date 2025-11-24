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
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')
    def authenticate(self):
        usuario = Usuario.query.filter_by(email=self.email.data).first()
        if usuario and usuario.senha == self.senha.data:
            return usuario
        return None
    


class VooForm(FlaskForm):
    origem = StringField('Origem', validators=[DataRequired()])
    destino = StringField('Destino', validators=[DataRequired()])
    data = StringField('Data do voo', validators=[DataRequired()])
    horario = StringField('Horário', validators=[DataRequired()])
    preco = StringField('Preço', validators=[DataRequired()])
    submit = SubmitField('Cadastrar Voo')
        

