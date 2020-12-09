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
        user_todos_top_5 = user.todos[0:5]
        user_lists_top_5 = user.lists[0:5]
        return render_template('home.html', user=user, todos=user_todos_top_5, lists=user_lists_top_5)
    else:
        return '401'


@app.route('/todos', methods=['GET', 'POST'])
@app.route('/todos/<editmode>/<item>', methods=['GET', 'POST'])
def todos(editmode=False, item=None):
    if 'user_id' in session.keys():
        user = User.query.filter_by(id=session['user_id']).first()
        
        if request.method == 'POST':
            title, desc = request.form.values()
            new_todo = Todos(title=title, description=desc, owner=user)
            db.session.add(new_todo)
            db.session.commit()

        if editmode is False:
            session.pop('title', None)
            session.pop('desc', None)

        return render_template('todos.html', data=user.todos, editmode=editmode, item=item)
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
    
    if resp is not None and func == 'edit':
        return redirect(url_for('todos', editmode=resp, item=item))
    elif resp:
        return redirect(url_for('todos'))
    elif not resp:
        flash("Could'nt deploy the action")
        return redirect(url_for('todos'))
    else:
        flash('Oops, something went wrong..')
        return redirect(url_for('logout'))


def delete(item):
    user = User.query.filter_by(id=session['user_id']).first()
    for todo in user.todos:
        if todo.id == int(item):
            user.todos.remove(todo)
            break

    todo = Todos.query.filter_by(id=item).delete()
    db.session.commit()

    return True


def check(item):
    todo = Todos.query.filter_by(id=item).first()
    todo.completed = not todo.completed
    db.session.commit()
    return True


@app.route('/edit/<item>', methods=['POST'])
def update(item):
    if request.method == 'POST':
        todo = Todos.query.filter_by(id=item).first()
        todo.title = request.form['title']
        todo.description = request.form['desc']
        db.session.commit()
        session.pop('title', None)
        session.pop('desc', None)
        return redirect(url_for('todos'))
    else:
        todo = Todos.query.filter_by(id=item).first()
        session['title'] = todo.title
        session['desc'] = todo.description
    return True
        

@app.route('/lists', methods=['GET', 'POST'])
def lists():
    if 'user_id' in session.keys():
        user = User.query.filter_by(id=session['user_id']).first()
        if request.method == 'POST':
            title = request.form['title']
            new_list = List(owner=user, title=title)
            db.session.add(new_list)
            db.session.commit()
        return render_template('list.html', lists=user.lists)
        
    else:
        return '401'


@app.route('/view/<items_list>', methods=['GET', 'POST'])
def list_view(items_list):
    if 'user_id' in session.keys() and items_list is not None:
        il = List.query.filter_by(id=items_list).first()
        if request.method == 'POST':
            new_item = ListItem(owner_id=il.id, name=request.form['list_item'])
            db.session.add(new_item)
            db.session.commit()
        session['current_list'] = il.id
        if 'view' not in request.referrer.split('/'):
            drop_update_session()
        
        return render_template('list_view.html', list=il)
    else:
        return '401'


@app.route('/handle-list/<item>/<func>')
def handle_crud_list(item, func):
    actions = {
        'full-del': list_delete,
        'item-del': list_delete,
        'edit-title': list_update,
        'edit-item': list_update,
    }

    resp = None
    if 'user_id' in session.keys():
        if func in actions.keys():
            resp = actions[func](item, func)

    page_direct = url_for('list_view', items_list=session['current_list']) if func == 'item-del' or func == 'edit-item' or func == 'edit-title' else url_for('lists')

    if resp:
        return redirect(page_direct)
    elif not resp:
        flash("Could'nt deploy the action")
        return redirect(page_direct)
    else:
        flash('Oops, something went wrong..')
        return redirect(url_for('logout'))


def list_delete(item, func):
    if func == 'full-del':
        list_items = ListItem.query.filter_by(owner_id=item).all()
        for list_item in list_items:
            db.session.delete(list_item)
        
        user = User.query.filter_by(id=session['user_id']).first()
        for list in user.lists:
            if list.id == int(item):
                user.lists.remove(list)
                break

        list = List.query.filter_by(id=item).delete()
        db.session.commit()
        return True

    elif func == 'item-del':
        list_id = session['current_list']
        list = List.query.filter_by(id=list_id).first()
        for li in list.items:
            if li.id == int(item):
                list.items.remove(li)
                break

        ListItem.query.filter_by(id=item).delete()
        db.session.commit()
        return True
    else:
        return False


@app.route('/list-update/<item>/<func>', methods=['GET','POST'])
def list_update(item, func=None):
    if func == 'edit-item':
        if request.method == 'POST':
            li = ListItem.query.filter_by(id=item).first()
            li.name = request.form['list_item']        
            db.session.commit()
            
            drop_update_session()
            return redirect(url_for('list_view', items_list=session['current_list']))
        else:
            li = ListItem.query.filter_by(id=item).first()
            session['item_name'] = li.name
            session['item_editmode'] = True
            session['item_id'] = li.id
        return True
    elif func == 'edit-title':
        if request.method == 'POST':
            li = List.query.filter_by(id=session['current_list']).first()
            li.title = request.form['title']
            db.session.commit()
            
            drop_update_session()
            return redirect(url_for('list_view', items_list=session['current_list']))
        else:
            li = List.query.filter_by(id=session['current_list']).first()
            session['list_title'] = li.title
            session['list_editmode'] = True

        return True
    else:
        drop_update_session()
        return redirect(url_for('list_view', items_list=session['current_list']))


def drop_update_session():
    session.pop('item_name', None)
    session.pop('item_id', None)
    session.pop('item_editmode', None)
    session.pop('list_title', None)
    session.pop('list_editmode', None)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('current_list', None)
    session.pop('item_name', None)
    session.pop('item_id', None)
    session.pop('item_editmode', None)
    session.pop('list_title', None)
    session.pop('list_editmode', None)
    flash('You were logged out')
    return redirect(url_for('index', reg=False))


if __name__ == '__main__':
    db.create_all(app=app)
    app.run( debug=True )


