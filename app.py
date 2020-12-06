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
        if request.method == 'POST':
            title, desc = request.form.values()
            new_todo = Todos(title=title, description=desc, owner=user)
            db.session.add(new_todo)
            db.session.commit()
        print('p', user.todos)
        return render_template('todos.html', data=user.todos)
    else:
        return '401'

@app.route('/handle/<item>/<func>')
def handle_crud(item, func):
    actions = {
        'del': delete,
        'check': check,
        'edit': update,
    }

    resp = None
    if 'user_id' in session.keys():
        if func in actions.keys():
            resp = actions[func](item)
    
    if resp:
        return redirect(url_for('todos'))
    elif not resp:
        flash("Could'nt deploy the action")
        return redirect(url_for('todos'))
    else:
        flash('Oops, something went wrong..')
        return redirect(url_for('logout'))


def delete(item):
    todo = Todos.query.filter_by(id=item).delete()
    print(Todos.query.all())
    print(User.query.filter_by(id=session['user_id']).first().todos)
    return True


def check(item):
    todo = Todos.query.filter_by(id=item).first()
    todo.completed = not todo.completed
    db.session.commit()
    return True


def update(item):
    # mark - make it work
    Todos.query.filter_by(id=item).first()
    return True

        
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
    # test = User('test', 'test@test.com', 'test')
    # db.session.add(test)
    # db.session.commit()
    

