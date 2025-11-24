from app import db
from datetime import datetime

# ------------------ USUÁRIO ------------------ #
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)

    # relação com passagens
    passagens = db.relationship('Passagem', backref='usuario', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.nome}>'


# ------------------ PASSAGEM ------------------ #
class Passagem(db.Model):
    __tablename__ = 'passagem'
    id = db.Column(db.Integer, primary_key=True)
    origem = db.Column(db.String(50), nullable=False)
    destino = db.Column(db.String(50), nullable=False)
    preco = db.Column(db.Float, nullable=False)

    # vínculo com usuário
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    def __repr__(self):
        return f'<Passagem {self.origem} -> {self.destino}>'
