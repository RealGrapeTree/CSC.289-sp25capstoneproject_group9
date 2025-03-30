from flask import render_template, Blueprint, request, jsonify
from extensions import db
from flask_login import current_user
from models import Transaction

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
    # Get current date
    current_date = datetime.today()

    # Query all transactions for the day
    transactions = db.session.query(Transaction).filter(Transaction.timestamp == current_date)
    daily_transactions = [
        {
            "id": t.id,
            "amount": t.amount / 100,  # Convert from cents to dollars
            "timestamp": t.timestamp
        }
        for t in transactions
    ]

    return render_template('daily_sales_report.html',
        user=current_user,
        current_date=current_date,
        transactions=transactions,
        daily_transactions=daily_transactions
        )


# Weekly sales report route
@Novel_sales_reports.route('/sales_report/weekly')
def weekly_sales_report():
    # Get current date
    current_date = datetime.today()
    # Get first and last dates of the week
    week_start = current_date - timedelta(days=current_date.weekday()+ 1 % 7)
    week_end = week_start + timedelta(days=6)

    # Query all transactions for the week
    transactions = db.session.query(Transaction).filter(Transaction.timestamp >= week_start,\
                                                         Transaction.timestamp <= week_end)
    weekly_transactions = [
        {
            "id": t.id,
            "amount": t.amount / 100,  # Convert from cents to dollars
            "timestamp": t.timestamp
        }
        for t in transactions
    ]

    return render_template('weekly_sales_report.html', 
                           user=current_user, 
                           current_date=current_date, 
                           week_start=week_start, 
                           week_end=week_end,
                           transactions=transactions,
                           weekly_transactions=weekly_transactions)


# Monthly sales report route
@Novel_sales_reports.route('/sales_report/monthly')
def monthly_sales_report():
    # Get current date
    current_date = datetime.today()
    # Get first of month
    first_of_month = current_date.replace(day=1)
    # Get last of month and format it into a %Y-%m-%d string
    last_day = calendar.monthrange(current_date.year, current_date.month)[1]
    last_of_month = f"{current_date.year}-{current_date.month}-{last_day}"

    # Convert first of month's datetime to timestamp
    month_first_timestamp = dt.datetime.timestamp(first_of_month)
    # Convert last of month's string into datetime and then into timestamp
    month_last_datetime = dt.datetime.strptime(last_of_month, "%Y-%m-%d")
    month_last_timestamp = dt.datetime.timestamp(month_last_datetime)

    # Query all transactions for the month
    transactions = db.session.query(Transaction).filter(Transaction.timestamp >= month_first_timestamp,\
                                                         Transaction.timestamp <= month_last_timestamp)
    monthly_transactions = [
        {
            "id": t.id,
            "amount": t.amount / 100,  # Convert from cents to dollars
            "timestamp": t.timestamp
        }
        for t in transactions
    ]

    return render_template('monthly_sales_report.html', 
                           user=current_user, 
                           current_date=current_date, 
                           first_of_month=first_of_month,
                           month_last_datetime=month_last_datetime,
                           transactions=transactions,
                           monthly_transactions=monthly_transactions)
    

# Custom sales report route
@Novel_sales_reports.route('/sales_report/custom', methods=['GET', 'POST'])
def custom_sales_report():
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
    custom_transactions = [
        {
            "id": t.id,
            "amount": t.amount / 100,  # Convert from cents to dollars
            "timestamp": t.timestamp
        }
        for t in transactions
    ]

    return render_template('custom_sales_report.html', 
                           user=current_user,
                           current_date=current_date, 
                           custom_start_date=custom_start_date, 
                           custom_end_date=custom_end_date,
                           transactions=transactions,
                           custom_transactions=custom_transactions)