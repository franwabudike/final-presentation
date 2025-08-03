from flask import Flask, render_template, url_for, flash, redirect, request
from reg_form import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy
from models import User, db
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vibeRoom.db'
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit for images

# Create folder for uploads if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db.init_app(app)
# Create tables
with app.app_context():
    db.create_all()
#create login manager
login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# when a user visits the root URL
@app.route('/')
def index():
    return render_template('index.html')

# will be called when a user visits the /playlists URL
@app.route('/playlists')
def playlists():
    return render_template('playlists.html')

# will be called when a user visits the /contact URL
@app.route('/contact')
def contact():
    return render_template('contact.html')

# placeholder for the About page
@app.route('/about')
def about():
    return render_template('about.html')
# choose to login or register (account page)
@app.route('/account')
def account():
    return render_template('account.html')

# a new route for the login page ("/login")
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first() #find user by email
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid Creditials')    
    return render_template('login.html')

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Handle profile picture upload
        picture_file = request.files['picture']
        if picture_file and picture_file.filename != '':
            filename = secure_filename(picture_file.filename)
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            picture_file.save(picture_path)
        else:
            filename = "default_pfp.jpeg"

        hashed_password = generate_password_hash(form.password.data, method='sha256')

        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            picture=filename
        )
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('index'))

    return render_template('register.html', title='Register', form=form)
#logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)