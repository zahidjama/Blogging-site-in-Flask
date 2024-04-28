from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, logout_user, UserMixin
import uuid
import hashlib
app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///sqlite.db"
app.config["SECRET_KEY"]="zahid"

db=SQLAlchemy()
loginManager=LoginManager()
loginManager.init_app(app)
db.init_app(app)

class Users(UserMixin, db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, name, phone, email, password):
        self.id = str(uuid.uuid4())
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password

class Post(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    caption = db.Column(db.String(255), nullable=False)
    post = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('Users', backref=db.backref('posts', lazy=True))

    def __init__(self, caption, post, user):
        self.id=str(uuid.uuid4())
        self.caption=caption
        self.post=post
        self.user=user







with app.app_context():
    db.create_all()

@loginManager.user_loader
def loader_user(userid):
    return Users.query.get(userid)


def hashPassword(password):
    password=hashlib.md5(password.encode())
    password=password.hexdigest()
    return password


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]
        password=hashPassword(password)
        user=Users.query.filter_by(email=email).first()
        
        if user.password==password:
            login_user(user=user)
            return redirect(url_for('home'))

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method=="POST":
        name=request.form["name"]
        phone=request.form["phone"]
        email=request.form["email"]
        password=request.form["password"]
        password=hashPassword(password)
        user=Users(name=name, phone=phone, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('info', 'User Created Successfully')
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/home", methods=["GET", "POST"])
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method=="POST":
        caption=request.form["caption"]
        post=request.form["post"]
        myPost=Post(caption=caption, post=str(post), user=current_user)
        db.session.add(myPost)
        db.session.commit()
        flash('info', "Post added successfully")

    posts=[i for i in Post.query.all()]
    return render_template("home.html", posts=posts)

@app.route("/post/<postId>")
def postFunc(postId):
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    post=Post.query.filter_by(id=postId).first()
    return render_template('post.html', post=post)

@app.route("/delete")
def Delete():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    # post=Post.query.filter_by(id=postId).first()
    postId=request.args["id"]
    post=Post.query.filter_by(id=postId).first()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("home"))


app.run(debug=True)