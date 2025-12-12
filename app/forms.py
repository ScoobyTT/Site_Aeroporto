from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
import json
import os
from datetime import datetime
from app.btree import BTree
from app.btree_instances import btree_voos, btree_usuarios
from app.utils import carregar_json, salvar_json, proximo_id, VOOS_FILE, USUARIOS_FILE

# =======================
# Caminhos dos arquivos
# =======================

#zzzzzzzzzzzzzzzzzzzzzzzzzz


# =======================
# Funções utilitárias JSON
# =======================

#zzzzzzzzzzzzzzzzzzzzzzzzzz

# =======================
# Formulário de Cadastro
# =======================
class UsuarioForm(FlaskForm):
    nome = StringField(
        "Nome",
        validators=[
            DataRequired(message="O nome é obrigatório."),
            Length(min=2, message="O nome deve ter pelo menos 2 caracteres.")
        ]
    )
    cpf = StringField(
        "CPF",
        validators=[
            DataRequired(message="O CPF é obrigatório."),
            Length(min=11, max=11, message="O CPF deve ter 11 caracteres.")
        ]
    )


    email = StringField(
        "Email",
        validators=[
            DataRequired(message="O email é obrigatório."),
            Email(message="Digite um email válido.")
        ]
    )

    confirmar_email = StringField(
        "Confirmar Email",
        validators=[
            DataRequired(message="Confirme seu email."),
            Email(message="Digite um email válido."),
            EqualTo("email", message="Os emails não coincidem.")
        ]
    )

    senha = PasswordField(
        "Senha",
        validators=[
            DataRequired(message="A senha é obrigatória."),
            Length(min=4, message="A senha deve ter pelo menos 4 caracteres.")
        ]
    )

    confirmar_senha = PasswordField(
        "Confirmar Senha",
        validators=[
            DataRequired(message="Confirme sua senha."),
            EqualTo("senha", message="As senhas não coincidem.")
        ]
    )

    submit = SubmitField("Cadastrar")

    # Salva usuário em JSON
    def save(self):
        usuarios = carregar_json(USUARIOS_FILE)

        novo_usuario = {
            "id": proximo_id(usuarios),
            "cpf": self.cpf.data,
            "nome": self.nome.data,
            "email": self.email.data,
            "senha": self.senha.data
        }

        usuarios.append(novo_usuario)
        salvar_json(USUARIOS_FILE, usuarios)
        btree_usuarios.insert(novo_usuario["id"], novo_usuario)

        return novo_usuario


# =======================
# Formulário de Login
# =======================

class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="O email é obrigatório."),
            Email(message="Digite um email válido.")
        ]
    )

    senha = PasswordField(
        "Senha",
        validators=[
            DataRequired(message="A senha é obrigatória.")
        ]
    )

    submit = SubmitField("Entrar")

    # Autentica lendo JSON
    def authenticate(self):
        usuarios = carregar_json(USUARIOS_FILE)

        for usuario in usuarios:
            if usuario["email"] == self.email.data and usuario["senha"] == self.senha.data:
                return usuario

        return None


# =======================
# Formulário de Voo
# =======================

class VooForm(FlaskForm):
    origem = StringField("Origem", validators=[DataRequired()])
    destino = StringField("Destino", validators=[DataRequired()])
    data = StringField("Data do voo", validators=[DataRequired()])
    horario = StringField("Horário", validators=[DataRequired()])
    preco = StringField("Preço", validators=[DataRequired()])
    n_assentos = StringField("Número de Assentos", validators=[DataRequired()])
    n_aeronave = StringField("Número da Aeronave", validators=[DataRequired()])
    submit = SubmitField("Cadastrar Voo")

    def save(self, usuario_id):
            voos = carregar_json(VOOS_FILE)

            novo_voo = {
                "id": proximo_id(voos),
                "origem": self.origem.data,
                "destino": self.destino.data,
                "data": self.data.data,
                "horario": self.horario.data,
                "preco": float(self.preco.data),
                "usuario_id": usuario_id,
                "data_cadastro": datetime.utcnow().isoformat()
            }

            voos.append(novo_voo)
            salvar_json(VOOS_FILE, voos)

            # integração com árvore B
            btree_voos.insert(novo_voo["id"], novo_voo)

            return novo_voo
