from flask import render_template, Blueprint, request, jsonify
from extensions import db
from flask_login import current_user
from models import Transaction
from ..cart.Novel_cart import NC_TAX_RATE

import datetime as dt
from datetime import timedelta, datetime, date
import calendar
import pandas as pd


# Create the Blueprint
Novel_sales_reports = Blueprint('Novel_sales_reports', __name__, template_folder='templates')


# Function to export reports to CSV
@Novel_sales_reports.route("/export_sales_csv/<string:table_to_export>", methods=["POST"])
def export_reports_csv(table_to_export):
    csv_table = pd.read_html(table_to_export)
    df = csv_table[0]
    df.to_csv(f'{table_to_export}_report.csv')

    return jsonify({"message": "Table exported to CSV file.", "success": True})


# Function to export reports to PDF
@Novel_sales_reports.route("/export_sales_pdf/<string:table_to_export>", methods=["POST"])
def export_reports_pdf(table_to_export):
    pass


# Generate sales report route
@Novel_sales_reports.route('/sales_report')
def sales_report():
    return render_template('sales_reports.html', user=current_user)


# Daily sales report route
@Novel_sales_reports.route('/sales_report/daily', methods=["GET"])
def daily_sales_report():
    subtotal = 0


    # Get current date
    current_date = datetime.today()

    # Get start and end of the day
    start_of_day = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = current_date.replace(hour=23, minute=59, second=59, microsecond=999999)

    transactions = db.session.query(Transaction).filter(
        Transaction.timestamp >= start_of_day,
        Transaction.timestamp <= end_of_day
    ).all()  

    subtotal = sum(t.amount for t in transactions)
    tax_amount = round(subtotal * NC_TAX_RATE, 2)
    total_price = round(subtotal + tax_amount, 2)

    return render_template('daily_sales_report.html',
                           user=current_user,
                           current_date=current_date,
                           transactions=transactions,
                           subtotal=subtotal / 100,  # Convert from cents to dollars
                           tax_amount=tax_amount / 100, 
                           total_price=total_price / 100,
                           NC_TAX_RATE=NC_TAX_RATE) 


# Weekly sales report route
@Novel_sales_reports.route('/sales_report/weekly')
def weekly_sales_report():
    subtotal = 0
    # Get current date
    current_date = datetime.today()

    # Get first and last dates of the week
    week_start = current_date - timedelta(days=current_date.weekday())  # Start of the week (Monday)
    week_end = week_start + timedelta(days=6)  # End of the week (Sunday)

    # Query all transactions for the week
    transactions = db.session.query(Transaction).filter(
        Transaction.timestamp >= week_start,
        Transaction.timestamp <= week_end
    ).all()  

    for t in transactions:
        subtotal += t.amount 

    # Calculate tax and total price
    tax_amount = round(subtotal * NC_TAX_RATE, 2)
    total_price = round(subtotal + tax_amount, 2)

    return render_template('weekly_sales_report.html',
                           user=current_user,
                           current_date=current_date,
                           week_start=week_start,
                           week_end=week_end,
                           transactions=transactions,
                           subtotal=subtotal / 100,  
                           tax_amount=tax_amount / 100,  
                           total_price=total_price / 100,
                           NC_TAX_RATE=NC_TAX_RATE) 



# Monthly sales report route
@Novel_sales_reports.route('/sales_report/monthly')
def monthly_sales_report():
    
    subtotal = 0

    # Get current date
    current_date = datetime.today()

    # Get first of the month
    first_of_month = current_date.replace(day=1)

    # Get the last day of the month
    last_day = calendar.monthrange(current_date.year, current_date.month)[1]

    # Create datetime object for last day of the month
    last_of_month = current_date.replace(day=last_day)

    # Query transactions within the first and last day of the month
    transactions = db.session.query(Transaction).filter(
        Transaction.timestamp >= first_of_month,
        Transaction.timestamp <= last_of_month  
    ).all()

    for t in transactions:
        subtotal += t.amount

    tax_amount = round(subtotal * NC_TAX_RATE, 2)
    total_price = round(subtotal + tax_amount, 2)

    return render_template('monthly_sales_report.html', 
                           user=current_user, 
                           current_date=current_date, 
                           first_of_month=first_of_month,
                           last_of_month=last_of_month,  
                           transactions=transactions,
                           subtotal=subtotal / 100,  # Convert cents to dollars
                           tax_amount=tax_amount / 100,
                           total_price=total_price / 100,
                           NC_TAX_RATE=NC_TAX_RATE)

    

# Custom sales report route
@Novel_sales_reports.route('/sales_report/custom', methods=['GET', 'POST'])
def custom_sales_report():
    
    subtotal = 0

    # Get current date
    current_date = datetime.today()

    # Get the search term from the form
    if request.method == 'POST':
        user_start, user_end = request.form['custom_start_date'], request.form['custom_end_date']
        # Convert user input dates into datetime
        custom_start_date, custom_end_date = dt.datetime.strptime(user_start, "%Y-%m-%d"), dt.datetime.strptime(user_end, "%Y-%m-%d")

    # Query all transactions for the custom timeframe
    transactions = db.session.query(Transaction).filter(Transaction.timestamp >= custom_start_date,\
                                                         Transaction.timestamp <= custom_end_date)
    for t in transactions:
        subtotal += t.amount
       

    tax_amount = round(subtotal * NC_TAX_RATE, 2)
    total_price = round(subtotal + tax_amount, 2)

    return render_template('custom_sales_report.html', 
                           user=current_user,
                           current_date=current_date, 
                           custom_start_date=custom_start_date, 
                           custom_end_date=custom_end_date,
                           transactions=transactions,
                           subtotal=subtotal,
                           tax_amount=tax_amount,
                           total_price=total_price,
                           NC_TAX_RATE=NC_TAX_RATE)