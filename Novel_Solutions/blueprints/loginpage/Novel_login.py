
# Imports the required libraries
from flask import  render_template, Blueprint, redirect, url_for, request, jsonify
from extensions import db, bcrypt, login_manager

# Imports for Login
from flask_login import login_user, logout_user, current_user, login_required



# Imports for the Models
from models import User

# Create a Blueprint object 
Novel_login = Blueprint('Novel_login', __name__,)

# Set up flask-login
login_manager.login_view = "Novel_login.login"


# Create a UserLoader for flask-login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


#basic home route can move to a home or iventory blueprint if needed
@Novel_login.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Home'}), 200

# login page route
@Novel_login.route('/login', methods=['POST'])
def login():
    
    # check if the user is already logged in
    if current_user.is_authenticated:
        return jsonify({'message': 'User already logged in.'}), 200
    

    # get the username and password from the request
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")


    user = User.query.filter_by(username=username).first()

    # check if the user exists and the password is correct
    if user:
        if bcrypt.check_password_hash(user.password, password):
            # Log in the user after successful login
            login_user(user)
            return jsonify({'message': 'Login successful.'}), 200
       
    return jsonify({'message': 'Invalid username or password.'}), 401
    

@Novel_login.route('/logout', methods=['POST'])
@login_required
def logout():
    # logout the user
    logout_user()
    
    return jsonify({'message': 'Logout successful.'}), 200


# register page route
@Novel_login.route('/add_user', methods=['POST'])
def add_user():
    
    if not current_user.is_authenticated or current_user.role != 'manager':
        return jsonify({'message': 'Unauthorized! Only managers can add users.'}), 403
    # create a new instance of the registration form
    data = request.get_json()
        
    # hash the password
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode('utf-8')

        # create a new user object
    user = User(username= data["username"], 
                firstname= data["firstname"], 
                lastname=data["lastname"], 
                email=data["email"], 
                password=hashed_password, 
                role=data["role"])

    # add the new user to the database
    db.session.add(user)
    # commit the changes
    db.session.commit()

    return jsonify({'message': 'User created successfully.'}), 201




# Delete User Route
@Novel_login.route('/delete_user/<string:username>', methods=['DELETE'])
@login_required
def delete_user(username):
    if current_user.role != 'manager':
        return jsonify({'message': 'Unauthorized! Only managers can delete users.'}), 403

    user = User.query.get(username)  

    if user:
        db.session.delete(user)
        db.session.commit()
       
    else:
        return jsonify({'message': 'User not found.'}), 404

    return jsonify({'message': 'User deleted successfully.'}), 200

# Dashboard route
@Novel_login.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if current_user.role == "manager":
        users = [{"username": user.username, "role": user.role} for user in User.query.all()]
        return jsonify({"user": {"username": current_user.username, "role": current_user.role}, "users": users})

    return jsonify({"user": {"username": current_user.username, "role": current_user.role}}), 200



