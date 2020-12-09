from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    todos = db.relationship('Todos', backref='owner', cascade="all, delete-orphan, delete")
    lists = db.relationship('List', backref='owner', cascade="all, delete-orphan, delete")
   
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class Todos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=True)


class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    title = db.Column(db.String(80), nullable=False)
    items = db.relationship('ListItem', backref='owner', cascade="all, delete-orphan, delete")
    

class ListItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('list.id', ondelete='CASCADE'))