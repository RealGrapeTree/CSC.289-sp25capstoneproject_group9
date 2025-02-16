
from flask import  render_template, Blueprint, redirect, url_for, request, flash
from extensions import db, bcrypt, login_manager
from flask_login import  UserMixin, login_user, logout_user, current_user, login_required
from ..loginpage.Novel_login import Novel_login

Novel_POS = Blueprint('Novel_POS', __name__, template_folder='templates')

# Process Sale Route (Restricted to Cashiers)
@Novel_POS.route('/process_sale')
@login_required
def process_sale():
    if current_user.role != 'cashier':
        flash('Unauthorized! Only cashiers can process sales.', 'danger')
        return redirect(url_for('Novel_login.dashboard'))
    return render_template('process_sale.html')