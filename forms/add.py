from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    submit = SubmitField('Применить')