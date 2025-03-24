from flask import render_template, Blueprint, redirect, url_for, request, flash, jsonify, session
from extensions import db
from flask_login import login_required, current_user
from ..POS.Novel_POS import *
from ..cart.Novel_cart import *
from models import Transaction, User, Book
import json

import datetime as dt, calendar
from datetime import timedelta
import pandas as pd


# Create the Blueprint
Novel_sales_reports = Blueprint('Novel_sales_reports', __name__, template_folder='templates')


# Functions to export reports to CSV and PDF
def export_reports_csv():
    pass
def export_reports_pdf():
    pass


# Generate sales report route
@Novel_sales_reports.route('/sales_report')
def sales_report():
    return render_template('sales_reports.html', user=current_user)


# Daily sales report route
@Novel_sales_reports.route('/sales_report/daily', methods=["GET"])
def daily_sales_report():
    # Get current date
    current_date = dt.datetime.now()
    daily_transactions = []
    
    return render_template(
        'daily_sales_report.html',
        user=current_user,
        current_date=current_date
        )

# Weekly sales report route
@Novel_sales_reports.route('/sales_report/weekly')
def weekly_sales_report():
    # Get current date and week start/end dates
    current_date = dt.datetime.now()
    week_start = current_date - timedelta(days=current_date.weekday()+ 1 % 7)
    week_end = week_start + timedelta(days=6)

    return render_template('weekly_sales_report.html', user=current_user, current_date=current_date, week_start=week_start, week_end=week_end)

# Monthly sales report route
@Novel_sales_reports.route('/sales_report/monthly')
def monthly_sales_report():
    # Get current date and month start/end dates
    current_date = dt.datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    num_days = calendar.monthrange(current_year, current_month)[1]
    month_days = [str(dt.date(current_year, current_month, day).strftime("%A, %B %d %Y")) for day in range(1, num_days + 1)]

    return render_template('monthly_sales_report.html', user=current_user, current_date=current_date, month_days=month_days)
    
# Custom sales report route
@Novel_sales_reports.route('/sales_report/custom', methods=['GET', 'POST'])
def custom_sales_report():
    # Get current date
    current_date = dt.datetime.now()

    # Get the search term from the form
    if request.method == 'POST':
        user_start, user_end = request.form['custom_start_date'], request.form['custom_end_date']

        # Convert user input dates into datetime
        custom_start_date, custom_end_date = dt.datetime.strptime(user_start, "%Y-%m-%d"), dt.datetime.strptime(user_end, "%Y-%m-%d")
        custom_range = pd.date_range(custom_start_date, custom_end_date).tolist()



    return render_template('custom_sales_report.html', current_date=current_date, custom_start_date=custom_start_date, custom_end_date=custom_end_date, custom_range=custom_range, user=current_user)