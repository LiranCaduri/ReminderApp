from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ReminderAppDataBase.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'liran_is_the_boss'
db = SQLAlchemy(app)


class users(db.Model):
    # __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        usr = users.query.filter_by(email=email).first()
        if usr and usr.password == request.form['password']:
            return redirect(url_for('home'))
        else:
            flash("Couldn't login worng email and password", category='info')
    return render_template( 'index.html', reg=False)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name, email, password = request.form.values()
        usr = users(username=name, email=email, password=password)
        db.session.add(usr)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('index.html', reg=True)


@app.route('/home')
def home():
    print(users.query.all())
    return render_template('index.html', reg=False)


if __name__ == '__main__':
    db.create_all()
    app.run( debug=True )
    

