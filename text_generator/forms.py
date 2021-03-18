from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField("Username",
                           validators=[DataRequired(),
                                       Length(min=2, max=20)])
    email = StringField("Email",
                        validators=[DataRequired(),
                                    Email()])
    password = PasswordField("Password",
                             validators=[DataRequired(),
                                         EqualTo("password")])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(),
                                                 EqualTo("password")])
    submit = SubmitField('Sign up')

    # def validate_username(self, username):
    #     user = User.query.filter_by(username=username.data).first()
    #     if user:
    #         raise ValidationError('That username is taken. Please choose a different one.')
    # def validate_username(self, email):
    #     email = User.query.filter_by(email=email.data).first()
    #     if email:
    #         raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = StringField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class TextGeneratingForm(FlaskForm):
    inputText = StringField("Please input some thoughts", validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Go')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    poetry = TextAreaField('Generated AI Poetry')
    generate = SubmitField('Generate')
    submit = SubmitField('Save')


class SpeechForm(FlaskForm):
    poetry = TextAreaField('Generated AI Poetry', validators=[DataRequired()])
    submit = SubmitField('Save')
