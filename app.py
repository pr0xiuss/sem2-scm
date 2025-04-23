from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
import pytz
from datetime import datetime
import humanize
from werkzeug.security import generate_password_hash, check_password_hash
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name='dciud6yuq',
    api_key='463293421394546',
    api_secret='_h-PzGVB25edoT1trv4d3VZXif8'
)

app = Flask(__name__)
app.secret_key = 'blog-project'

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:pr0xius@localhost/blog'
db = SQLAlchemy(app)

# Register humanize filter for Jinja2
app.jinja_env.filters['humanize'] = humanize.naturaltime

DEFAULT_PROFILE_PIC_URL = 'https://res.cloudinary.com/dciud6yuq/image/upload/v1744963258/pfp_kniw7o.jpg'

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(120))
    password = db.Column(db.String(100))
    bio = db.Column(db.Text)
    profile_pic_url = db.Column(db.String(500))
    posts = db.relationship('Post', backref='user', passive_deletes=True)
    comments = db.relationship('Comment', backref='user', passive_deletes=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow().replace(tzinfo=pytz.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    comments = db.relationship("Comment", backref="post", passive_deletes=True)

    def formatted_date(self):
        local_timezone = pytz.timezone("Asia/Kolkata")
        utc_time = self.created_at.replace(tzinfo=pytz.utc) if self.created_at.tzinfo is None else self.created_at
        created_at_local = utc_time.astimezone(local_timezone)
        return humanize.naturaltime(created_at_local)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    def formatted_date(self):
        local_timezone = pytz.timezone("Asia/Kolkata")
        utc_time = self.created_at.replace(tzinfo=pytz.utc) if self.created_at.tzinfo is None else self.created_at
        created_at_local = utc_time.astimezone(local_timezone)
        return humanize.naturaltime(created_at_local)

with app.app_context():
    db.create_all()

# Routes
@app.route("/")
@app.route("/newhome")
def newhome():
    return render_template("newhome.html")

@app.route("/admin")
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    users = User.query.filter(User.username != 'admin').all()
    posts = Post.query.all()
    return render_template("admin.html", users=users, posts=posts)

@app.route("/home")
def home():
    if 'user_id' not in session:
        return redirect(url_for("login"))
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("home.html", username=session.get('username'), posts=posts)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if 'user_id' in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            profile_pic_url=DEFAULT_PROFILE_PIC_URL
        )
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        flash('Account created successfully!', 'success')
        return redirect(url_for("home"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user_id' in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = (user.username == 'admin')
            flash('Admin logged in!' if user.username == 'admin' else 'Logged in successfully!', 'success')
            return redirect(url_for("admin_dashboard" if user.username == 'admin' else "home"))
        else:
            flash('Invalid username or password!', 'danger')
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/admin/user/<int:user_id>")
def admin_user_profile(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).all()
    return render_template("admin_user_profile.html", user=user, posts=posts)

@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
def admin_delete_user(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    user = User.query.get_or_404(user_id)
    Post.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash("User and their posts deleted!", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete_post/<int:post_id>",methods=["POST"])
def admin_delete_post(post_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    post = Post.query.get_or_404(post_id)   
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted!", "success")
    return redirect(request.referrer or url_for("admin_dashboard"))

@app.route("/admin/delete_comment/<int:comment_id>", methods=["POST"])
def admin_delete_comment(comment_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted!", "success")
    return redirect(request.referrer or url_for("admin_dashboard"))

@app.route("/admin/post/<int:post_id>")
def admin_view_post(post_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).all()
    return render_template("admin_view_post.html", post=post, comments=comments)

@app.route("/create", methods=["GET", "POST"])
def create_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        local_timezone = pytz.timezone("Asia/Kolkata")
        created_at_local = datetime.now(local_timezone)
        created_at_utc = created_at_local.astimezone(pytz.utc)
        new_post = Post(title=title, content=content, created_at=created_at_utc, user_id=session['user_id'])
        db.session.add(new_post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for("home"))
    return render_template("create_post.html")

@app.route("/post/<int:post_id>")
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    local_timezone = pytz.timezone("Asia/Kolkata")
    post.created_at = post.created_at.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    return render_template("show_post.html", post=post)

@app.route('/user/<int:user_id>')
def view_user_profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).all()
    is_owner = (session.get('user_id') == user.id)
    
    current_user = User.query.get(session.get('user_id')) if 'user_id' in session else None

    return render_template(
        'profile.html',
        user=user,
        posts=posts,
        is_owner=is_owner,
        current_user=current_user
    )

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for("newhome"))

@app.route("/post/<int:post_id>", methods=["POST"])
def add_comment(post_id):
    if 'user_id' not in session:
        flash("Please login to comment!", "warning")
        return redirect(url_for("login"))
    content = request.form['comment']
    new_comment = Comment(content=content, post_id=post_id, user_id=session['user_id'])
    db.session.add(new_comment)
    db.session.commit()
    flash("Comment added!", "success")
    return redirect(url_for("show_post", post_id=post_id))

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if 'user_id' not in session:
        return redirect(url_for("login"))
    user_id = session['user_id']
    user = User.query.get(user_id)
    posts = Post.query.filter_by(user_id=user_id).all()
    
    return render_template(
        "profile.html",
        username=user.username,
        posts=posts,
        user=user,
        is_owner=True,
        current_user=user
    )

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.bio = request.form['bio']
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file.filename:
                upload_result = cloudinary.uploader.upload(file)
                user.profile_pic_url = upload_result['secure_url']

        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', user=user)

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    post = Post.query.get_or_404(post_id)
    if post.user_id != session['user_id']:
        abort(403)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))

    return render_template('edit_post.html', post=post)

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    post = Post.query.get_or_404(post_id)
    if post.user_id != session['user_id']:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('profile'))

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != session['user_id']:
        abort(403)

    db.session.delete(comment)
    db.session.commit()
    return redirect(request.referrer)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

if __name__ == "__main__":
    app.run(debug=True)
