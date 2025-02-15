from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and login manager
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Function to ensure the manager account exists
def create_default_manager():
    with app.app_context():
        db.create_all()  # Ensure database tables are created
        if not User.query.filter_by(username="admin").first():
            manager = User(username="admin", role="manager")
            manager.set_password("admin123")
            db.session.add(manager)
            db.session.commit()
            print("Default manager account created: admin/admin123")

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    users = User.query.all() if current_user.role == 'manager' else None
    return render_template('dashboard.html', user=current_user, users=users)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Process Sale Route (Restricted to Cashiers)
@app.route('/process_sale')
@login_required
def process_sale():
    if current_user.role != 'cashier':
        flash('Unauthorized! Only cashiers can process sales.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('process_sale.html')

# Add User Route (Restricted to Managers)
@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'manager':
        flash('Unauthorized! Only managers can add users.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        if not username or not password or not role:
            flash('All fields are required!', 'warning')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
        else:
            new_user = User(username=username, role=role)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('User created successfully!', 'success')
            return redirect(url_for('dashboard'))

    return render_template('add_user.html')

# Delete User Route (Restricted to Managers)
@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'manager':
        flash('Unauthorized! Only managers can delete users.', 'danger')
        return redirect(url_for('dashboard'))

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    else:
        flash('User not found!', 'danger')

    return redirect(url_for('dashboard'))

# Ensure database tables and default manager are created before app starts
if __name__ == '__main__':
    create_default_manager()
    app.run(debug=True)
