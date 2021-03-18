from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from flask import Blueprint, render_template, request, redirect, flash, url_for
from generator import ai
from mutipleLivePoetryGenerate import aiLive
from forms import RegistrationForm, LoginForm, TextGeneratingForm, PostForm, SpeechForm

from datetime import datetime
from flask_login import UserMixin
from flask_login import login_user, logout_user, current_user, login_required
from flask import request, abort


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app(config_file='settings.py'):
    app = Flask(__name__, static_url_path="/static", static_folder="static")
    app.config.from_pyfile(config_file)
    app.config["SECRET_KEY"] = 'bec336f9fb5b8f79aa77ded3ebbf2934'
    app.config['DEBUG'] = True
    app.register_blueprint(generator)
    bcrypt = Bcrypt(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'generator.login'
    login_manager.login_message_category = 'infor'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    with app.app_context():
        db.create_all()
    # app.jinja_env.globals.update(speech_generate=speech_generate)
    return app


# env FLASK_APP=__init__.py python -m flask run


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
    posts = Post.query.all()
    form = TextGeneratingForm()
    if form.validate_on_submit():
        text = ai.generate_text('love')
        return render_template('index.html', poetryText=text, infos=infos, form=form)
    return render_template('index.html', posts=posts, form=form)

@generator.route('/info', methods=["GET", "POST"])
def info():
    return render_template('info.html', infos=infos)

@generator.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('generator.index'))
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
        return redirect(url_for('generator.index'))
    return render_template('register.html', title='Register', form=form)

@generator.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('generator.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'you have been logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('generator.index'))
        else:
            flash(f'login unsuccessful. Please check password or username!')
    return render_template('login.html', title='Login In', form=form)

@generator.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('generator.index'))

@generator.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@generator.route('/post/new', methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    mytext = form.content.data
    title = form.title.data
    if form.validate_on_submit():
        if form.generate.data:
            text = aiLive.generatePeriod(mytext)
            form.poetry.data = text
            return render_template('create_post.html', title='New Post', form=form)
        if form.submit.data:
            if form.poetry.data != "":
                post = Post(title=form.title.data,
                            content=form.content.data,
                            author=current_user,
                            generated=form.poetry.data)
                db.session.add(post)
                db.session.commit()
                flash('Your post have been created', 'success')
                return redirect(url_for('generator.index'))
            else:
                flash('Please generate something first', 'error')

    return render_template('create_post.html', title='New Post', form=form)


@generator.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@generator.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('generator.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

@generator.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('generator.index'))


def speech_generate(mystr):
    print(mystr)

@generator.route('/handle_poetrySave', methods=['GET', 'POST'])
def handle_poetrySave():
    form = SpeechForm()
    if form.validate_on_submit():
        print("sumnit=====")
        speech = form.poetry
        print('get submit'+speech)
    return render_template('speechPost.html', title='New Post', form=form)

@generator.route('/speechpost/new', methods=["GET", "POST"])
@login_required
def new_speechpost():
    if request.method == "POST":
        speech = request.form.get('name')
        print("speech:" + speech)
        text = aiLive.generatePeriod(speech)
        print("generate:" + text)
        post = Post(title="",
                    content="",
                    author=current_user,
                    generated=text)
        db.session.add(post)
        db.session.commit()
        return text
    form = SpeechForm()
    # if form.validate_on_submit():
    #     print('get submit')
    #     speech = form.poetry
    #     text = aiLive.generatePeriod(speech)
    #     form.poetry.data = speech
    #     return render_template('speechPost.html', title='New Post', form=form)
    return render_template('speechPost.html', title='New Post', form=form)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), unique=False, nullable=False)
    image_file = db.Column(db.String(20), unique=False, default='default.jpg')
    posts = db.relationship('Post', backref='author', lazy=True)


def __repr__(self):
    return f"User('{self.username}, {self.email}, {self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=True)
    content = db.Column(db.String(2000), nullable=True)
    date_posted = db.Column(db.DateTime(), nullable=True, default=datetime.utcnow())
    generated = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


