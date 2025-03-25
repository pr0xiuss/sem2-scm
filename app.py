from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import pytz
from datetime import datetime
import humanize
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'blog-project'  #sessions

#database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:pr0xius@localhost/blog'
db = SQLAlchemy(app)

#reg humanize filter for Jinja2
app.jinja_env.filters['humanize'] = humanize.naturaltime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow().replace(tzinfo=pytz.utc)) #store in utc 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('posts', lazy=True))

    def formatted_date(self):
        local_timezone = pytz.timezone("Asia/Kolkata") #utc to kolkata
        if self.created_at.tzinfo is None:
            utc_time = self.created_at.replace(tzinfo=pytz.utc)  #ensuring UTC
        else:
            utc_time = self.created_at
        created_at_local = utc_time.astimezone(local_timezone)  #convert to Kolkata
        return humanize.naturaltime(created_at_local)

#create the database(run once to initialize it)
with app.app_context():
    db.create_all()

#route for newhome
@app.route("/")
@app.route('/newhome')
def newhome():
    return render_template("newhome.html")



@app.route("/home")
def home():
    if 'user_id' not in session:
        return redirect(url_for("login"))  #to login if not authenticated

    posts = Post.query.all()  #fetch all posts
    return render_template("home.html", username=session.get('username'), posts=posts)


#route for signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if 'user_id' in session:
        return redirect(url_for("home"))  #if logged in ->to home

    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        #log user in by storing id & username in session
        session['user_id'] = new_user.id
        session['username'] = new_user.username

        flash('Account created successfully!', 'success')
        return redirect(url_for("home"))

    return render_template("signup.html")

#route for login
@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user_id' in session:
        return redirect(url_for("home"))  #if logged in-> to home

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  #store id in session
            session['username'] = user.username  #store username in session
            flash('Logged in successfully!', 'success') 
            return redirect(url_for("home"))
        else:
            flash('Invalid username or password!', 'danger')
            return redirect(url_for("login"))

    return render_template("login.html")

#route for creating post
@app.route("/create", methods=["GET", "POST"])
def create_post():
    if 'user_id' not in session:
        return redirect(url_for('login')) 

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")

        #current kolkata time to UTC
        local_timezone = pytz.timezone("Asia/Kolkata")
        created_at_local = datetime.now(local_timezone)  #kolkata
        created_at_utc = created_at_local.astimezone(pytz.utc)  #convert to UTC

        #create a with UTC timestamp
        new_post = Post(title=title, content=content, created_at=created_at_utc, user_id=session['user_id'])

        #add post to database and commit
        db.session.add(new_post)
        db.session.commit()

        flash('Post created successfully!', 'success')
        return redirect(url_for("home"))

    return render_template("create_post.html")

#route for showing post
@app.route("/post/<int:post_id>")
def show_post(post_id):
    post = Post.query.get_or_404(post_id)

    #convert UTC to Kolkata
    local_timezone = pytz.timezone("Asia/Kolkata")
    post.created_at = post.created_at.replace(tzinfo=pytz.utc).astimezone(local_timezone)

    return render_template("show_post.html", post=post)

#route for logging out
@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for("newhome"))

@app.route("/profile")
def profile():
    if 'user_id' not in session:
        return redirect(url_for("login"))  #if not logged in

    user_id = session['user_id']
    user = User.query.get(user_id)
    posts = Post.query.filter_by(user_id=user_id).all()  #get user's posts

    return render_template("profile.html", username=user.username, posts=posts)


if __name__ == "__main__":
    app.run(debug=True)
