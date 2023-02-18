from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField("Sign in")

class RegForm(FlaskForm):
    img = FileField('Upload your profile pic', validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired(), Length(min=4, max=64)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=32)])
    password = PasswordField('Password',validators=[DataRequired(), Length(min=8, max=128)])
    about = TextAreaField('About you', validators=[DataRequired()])
    submit = SubmitField("Sign up")
    
class PostForm(FlaskForm):
    img = FileField('Upload an image for your post')
    title = StringField('Post title', validators=[DataRequired()])
    content = TextAreaField('Post content', validators=[DataRequired()])
    submit = SubmitField('Post')
    
class SendMessageForm(FlaskForm):
    message = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')