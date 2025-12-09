from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'KDJGUY6U46U4YU6Y4-U32HSUDUIOGPASDTRY!!RYRYERYHHFFH'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views
from app.views import homepage


if __name__ == '__main__':
    app.run(debug=True)
    db.create_all()
    app.run()   
