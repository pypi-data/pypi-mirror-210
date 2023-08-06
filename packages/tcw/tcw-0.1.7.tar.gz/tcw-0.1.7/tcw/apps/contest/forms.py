from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (StringField, IntegerField, TextAreaField, SubmitField,
    SelectField)
from wtforms.validators import DataRequired
from wtforms.fields import EmailField


class ContestForm(FlaskForm):
    """
    Form definition class for new contest    
    """

    title = StringField('contest title', validators=[DataRequired()],)
    instructions = TextAreaField('sign-up instructions', validators=[DataRequired()])
    email = EmailField('contest owner email', validators=[DataRequired()])
    winners = IntegerField('number of winners (1-50)', validators=[DataRequired()])
    maximum = IntegerField('max number of entrants (1-500)', validators=[DataRequired()])
    hours = SelectField('contest expires after', choices=[
        ('1', '1 hour'),
        ('4', '4 hours'),
        ('12', '12 hours'),
        ('24', '1 day'),
        ('72', '3 days'),
        ('120', '5 days'),
        ],  validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('submit')


class SignupForm(FlaskForm):
    """
    Form definition for user signup form
    """

    name = StringField('sign up!')
    submit = SubmitField('submit')
