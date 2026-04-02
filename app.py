from flask import Flask, render_template, redirect, url_for, request, session, flash
from models import db, Task, User
from datetime import datetime
import calendar
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-123'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "tasks.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Войдите в систему', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Заполните все поля', 'error')
        elif len(username) < 3:
            flash('Имя слишком короткое (мин. 3 символа)', 'error')
        elif len(password) < 4:
            flash('Пароль слишком короткий (мин. 4 символа)', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Пользователь уже существует', 'error')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация успешна! Теперь войдите.', 'success')
            return redirect(url_for('login'))

    return render_template('auth.html', action='register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            flash('Неверное имя или пароль', 'error')

    return render_template('auth.html', action='login')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/about')
@login_required
def about():
    return render_template('about.html', current_user=session.get('username'))


@app.route('/')
@app.route('/index')
@login_required
def index():
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)

    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)
    month_name = calendar.month_name[month]

    start_date = datetime(year, month, 1)
    end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

    tasks = Task.query.filter(
        Task.user_id == session['user_id'],
        Task.date >= start_date,
        Task.date < end_date
    ).all()

    tasks_by_day = {}
    for task in tasks:
        day = task.date.day
        tasks_by_day.setdefault(day, []).append(task)

    return render_template('index.html',
                           year=year, month=month, month_name=month_name,
                           month_days=month_days, tasks_by_day=tasks_by_day,
                           current_user=session.get('username'))


@app.route('/toggle_task/<int:task_id>')
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != session['user_id']:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('index'))
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('index', year=task.date.year, month=task.date.month))


@app.route('/delete_task/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != session['user_id']:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('index'))
    year, month = task.date.year, task.date.month
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index', year=year, month=month))


@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    title = request.form.get('title')
    task_date = datetime.strptime(request.form.get('task_date'), '%Y-%m-%d').date()
    task_time = request.form.get('task_time')
    year = request.form.get('year', datetime.now().year)
    month = request.form.get('month', datetime.now().month)

    if title:
        time_obj = None
        if task_time:
            time_obj = datetime.strptime(task_time, '%H:%M').time()

        new_task = Task(title=title, date=task_date, time=time_obj, user_id=session['user_id'])
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('index', year=year, month=month))

if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1', debug=True)