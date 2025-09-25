from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, BooleanField, ValidationError
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length, EqualTo


""" FORMS """
# Add User Form
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=200)])
    email = EmailField('Email', validators=[DataRequired(), Length(max=120)])
    username = StringField('Username', validators=[DataRequired()])
    fav_color = StringField('Favorite Color', validators=[Length(max=120)])
    password = PasswordField('Password', validators=[Length(min=6, max=16), DataRequired(), EqualTo('password2', message='Passwords must match!')])
    password2 = PasswordField('Confirm Password', validators=[Length(min=6, max=16), DataRequired()]) 
    submit = SubmitField('Submit')
    """ Create another UpdateUserForm() since this will not work when updating"""

# User login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Naming Form
class NamerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Posts Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    submit = SubmitField("Submit")
