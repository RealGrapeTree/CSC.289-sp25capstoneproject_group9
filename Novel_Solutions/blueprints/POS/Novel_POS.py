
from flask import  render_template, Blueprint, redirect, url_for, request, jsonify
from extensions import db, bcrypt, login_manager
from flask_login import  UserMixin, login_user, logout_user, current_user, login_required
from ..loginpage.Novel_login import Novel_login

Novel_POS = Blueprint('Novel_POS', __name__, template_folder='templates')

# Process Sale Route (Restricted to Cashiers)
@Novel_POS.route('/process_sale' , methods=['GET'])
@login_required
def process_sale():
    if current_user.role != 'cashier':
        return jsonify({'message': 'Unauthorized! Only cashiers can process sales.'}), 403
    return jsonify({'message': 'Process Sale'}), 200