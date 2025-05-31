from flask import Flask, render_template, redirect, request, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///golinks.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    links = db.relationship('GoLink', backref='creator', lazy=True)

class GoLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_path = db.Column(db.String(50), unique=True, nullable=False)
    target_url = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('view_links'))
    return redirect(url_for('login'))

@app.route('/<path:short_path>')
def redirect_link(short_path):
    link = GoLink.query.filter_by(short_path=short_path).first()
    if link:
        return redirect(link.target_url)
    return redirect(url_for('create_link', shortlink=short_path))

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_link():
    # Get short_path from query parameter or form data
    short_path = request.args.get('shortlink') or request.form.get('short_path')
    
    if request.method == 'POST':
        target_url = request.form.get('target_url')
        
        if not short_path or not target_url:
            flash('Both short path and target URL are required')
            return render_template('create_link.html', short_path=short_path, target_url=target_url)
        
        if not is_valid_url(target_url):
            flash('Please enter a valid URL (including http:// or https://)')
            return render_template('create_link.html', short_path=short_path, target_url=target_url)
        
        # Check if short path already exists
        existing_link = GoLink.query.filter_by(short_path=short_path).first()
        if existing_link:
            flash('This short path is already taken')
            return render_template('create_link.html', short_path=short_path, target_url=target_url)
        
        # Create new link
        link = GoLink(short_path=short_path, target_url=target_url, user_id=current_user.id)
        db.session.add(link)
        db.session.commit()
        flash('Link created successfully')
        return redirect(url_for('view_links'))
    
    return render_template('create_link.html', short_path=short_path)

@app.route('/edit/<path:short_path>', methods=['GET', 'POST'])
@login_required
def edit_link(short_path):
    existing_link = GoLink.query.filter_by(short_path=short_path).first()
    
    if not existing_link:
        flash('Link not found')
        return redirect(url_for('view_links'))
    
    if existing_link.user_id != current_user.id:
        flash('You can only edit your own links')
        return redirect(url_for('view_links'))
    
    if request.method == 'POST':
        target_url = request.form.get('target_url')
        if not target_url:
            flash('Target URL is required')
            return render_template('edit_link.html', short_path=short_path, target_url=target_url)
        
        if not is_valid_url(target_url):
            flash('Please enter a valid URL (including http:// or https://)')
            return render_template('edit_link.html', short_path=short_path, target_url=target_url)
        
        existing_link.target_url = target_url
        db.session.commit()
        flash('Link updated successfully')
        return redirect(url_for('view_links'))
    
    return render_template('edit_link.html', 
                         short_path=short_path,
                         target_url=existing_link.target_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('view_links'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('view_links'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/links')
@login_required
def view_links():
    user_only = request.args.get('user_only', 'true').lower() == 'true'
    if user_only:
        links = GoLink.query.filter_by(user_id=current_user.id).all()
    else:
        links = GoLink.query.all()
    return render_template('links.html', links=links, user_only=user_only)

@app.route('/links/<path:short_path>/delete', methods=['POST'])
@login_required
def delete_link(short_path):
    link = GoLink.query.filter_by(short_path=short_path).first()
    if not link:
        flash('Link not found')
        return redirect(url_for('view_links'))
    
    if link.user_id != current_user.id:
        flash('You can only delete your own links')
        return redirect(url_for('view_links'))
    
    db.session.delete(link)
    db.session.commit()
    flash('Link deleted successfully')
    return redirect(url_for('view_links'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 