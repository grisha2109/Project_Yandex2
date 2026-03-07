from flask import Flask, render_template, redirect, url_for, request
from models import db, Task
from datetime import datetime
import calendar

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()
@app.route('/')
@app.route('/index')
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
    tasks = Task.query.filter(Task.date >= start_date, Task.date < end_date).all()
    tasks_by_day = {}
    for task in tasks:
        day = task.date.day
        if day not in tasks_by_day:
            tasks_by_day[day] = []
        tasks_by_day[day].append(task)
    return render_template('index.html',
                           year=year,
                           month=month,
                           month_name=month_name,
                           month_days=month_days,
                           tasks_by_day=tasks_by_day)

@app.route('/add_task', methods=['POST'])
def add_task():
    title = request.form.get('title')
    task_date = datetime.strptime(request.form.get('task_date'), '%Y-%m-%d').date()
    year = request.form.get('year', datetime.now().year)
    month = request.form.get('month', datetime.now().month)

    if title:
        new_task = Task(title=title, date=task_date)
        db.session.add(new_task)
        db.session.commit()

    return redirect(url_for('index', year=year, month=month))

@app.route('/toggle_task/<int:task_id>')
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('index', year=task.date.year, month=task.date.month))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    year = task.date.year
    month = task.date.month
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index', year=year, month=month))

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)