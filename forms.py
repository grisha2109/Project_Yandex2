from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Length

class TaskForm(FlaskForm):
    title = StringField('Название задачи', validators=[
        DataRequired(message="Введите название задачи"),
        Length(min=1, max=100, message="Максимум 100 символов")
    ])
    task_date = DateField('Дата', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Добавить')