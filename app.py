from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import *
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ReminderAppDataBase.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'liran_is_the_boss'
db.init_app(app=app)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        try:
            usr = User.query.filter_by(email=email).first()
            if usr and usr.password == request.form['password']:
                session['user_id'] = usr.id
                return redirect(url_for('home'))
        except OperationalError:
            db.create_all()
            flash("If you dont have an account, you should create one..")
        else:
            flash("Couldn't login worng email and password")
    return render_template( 'index.html', reg=False)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name, email, password = request.form.values()
        usr = User(username=name, email=email, password=password)
        db.session.add(usr)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('index.html', reg=True)


@app.route('/home')
def home():
    if 'user_id' in session.keys():
        user = User.query.filter_by(id=session['user_id']).first()
        return render_template('home.html', user=user)
    else:
        return '401'


@app.route('/todos', methods=['GET', 'POST'])
def todos():
    if 'user_id' in session.keys():
        user = User.query.filter_by(id=session['user_id']).first()
        return render_template('list.html', data=user.todos)
    else:
        return '401'

        
@app.route('/lists', methods=['GET', 'POST'])
def lists():
    return render_template('home.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You were logged out')
    return redirect(url_for('index', reg=False))

if __name__ == '__main__':
    db.create_all(app=app)
    app.run( debug=True )
    

