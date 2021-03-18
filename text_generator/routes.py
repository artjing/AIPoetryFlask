from flask import Blueprint, render_template, request, redirect, flash, url_for
from generator import ai
from forms import RegistrationForm, LoginForm, TextGeneratingForm
import __init__
from models import User, Post

generator = Blueprint('generator', __name__)

infos = [
    {
        'name': 'Jing',
        'title': 'The first generated poetry',
        'content': '......',
        'data_posted': 'Feb 16'
    },
    {
        'name': 'Jing',
        'title': 'The second generated poetry',
        'content': '......',
        'data_posted': 'Feb 17'
    }
]
@generator.route('/home', methods=["GET", "POST"])
@generator.route('/', methods=["GET", "POST"])
def index():
    form = TextGeneratingForm()
    if form.validate_on_submit():
        text = ai.generate_text('love')
        return render_template('index.html', poetryText=text, infos=infos, form=form)
    return render_template('index.html',infos=infos, form=form)

@generator.route('/info', methods=["GET", "POST"])
def info():
    return render_template('info.html', infos=infos)

@generator.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created of { form.username.data}', 'success')
        User.query.all()
        return redirect(url_for('generator.login'))
    return render_template('register.html', title='Register', form=form)

@generator.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    return render_template('login.html', title='Login In', form=form)
