from flask import  render_template, Blueprint, redirect, url_for, request, flash, jsonify
from extensions import db, bcrypt, login_manager
from flask_login import  UserMixin, login_user, logout_user, current_user, login_required
from ..loginpage.Novel_login import Novel_login
from ..cart.Novel_cart import Novel_cart, get_cart_total  # Import cart total function
import stripe 
import os
from datetime import date, timedelta
from cart import book, quantity, item_total, tax_amount, total_price


# Create the Blueprint
sales_reports = Blueprint('sales_reports', __name__, template_folder='templates')

# Generate Sales Report Route (Restricted to Managers)
@sales_reports.route('/generate_sales_report')
@login_required
def generate_sales_report():
    if current_user.role != 'manager':
        flash('Unauthorized! Only managers can generate sales reports.', 'danger')
        return redirect(url_for('Novel_login.dashboard'))
    return render_template('sales_reports.html', user=current_user)


# Get current date & week start/end dates
current_date = date.today()
week_start = current_date - timedelta(days=current_date.weekday())
week_end = current_date + timedelta(days=6)

data_list = []

# Generate report data
def daily_report():
    data_list.append({'ISBN':book.id, 'Title':book.title, 'Price':book.price, 
                      'Quantity':quantity, 'Subtotal':item_total, 'Tax':tax_amount, 'Total':total_price})
    print(data_list)

def weekly_report():
    for each in range(week_start, week_end):
        data_list.append({'ISBN':book.id, 'Title':book.title, 'Price':book.price, 
                      'Quantity':quantity, 'Subtotal':item_total, 'Tax':tax_amount, 'Total':total_price})
    print(data_list)

def custom_timeframe():
    pass


# Export data to CSV, PDF