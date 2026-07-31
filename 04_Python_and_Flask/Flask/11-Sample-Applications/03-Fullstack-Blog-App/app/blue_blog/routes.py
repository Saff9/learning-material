from flask import Blueprint, render_template, request, redirect, url_for, g
from app import db
from app.models import Post
from app.blue_auth.routes import login_required

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    posts = db.session.query(Post).all()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        
        post = Post(title=title, body=body, author_id=g.user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('blog.index'))
        
    return render_template('blog/create.html')
