from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from ..POS.Novel_POS import get_transactions
from models import Transaction, User

import datetime as dt
from datetime import date, timedelta


# Create the Blueprint
Novel_sales_reports = Blueprint('sales_report', __name__, template_folder='templates')


# Function to get dates
def get_dates():
    # Get the current day and month
    current_date = date.today()
    current_month = current_date.month

    # Get the current week's start and end dates
    week_start = current_date - timedelta(days=current_date.weekday()+ 1 % 7)
    week_end = week_start + timedelta(days=6)

    # Custom timeframe based off user input
    startDateEntry = input("Enter the start date in MM-DD-YYYY format: ")
    endDateEntry = input("Enter the end date in MM-DD-YYYY format: ")
    userStartDate, userEndDate = dt.datetime.strptime(startDateEntry, "%m-%d-%Y"), dt.datetime.strptime(endDateEntry, "%m-%d-%Y")

# Function to export reports to CSV and PDF
def export_reports():
    pass


# Generate sales report route
@Novel_sales_reports.route('/sales_report')
def generate_sales_report():
    return render_template('sales_reports.html', user=current_user)


# Daily sales report route
@Novel_sales_reports.route('/sales_report/daily')
def daily_sales_report():
    return render_template('daily_sales_report.html', user=current_user)

# Weekly sales report route
@Novel_sales_reports.route('/sales_report/weekly')
def weekly_sales_report():
    return render_template('weekly_sales_report.html', user=current_user)

# Monthly sales report route
@Novel_sales_reports.route('/sales_report/monthly')
def monthly_sales_report():
    return render_template('monthly_sales_report.html', user=current_user)
    
# Custom sales report route
@Novel_sales_reports.route('/sales_report/custom')
def custom_sales_report():
    return render_template('custom_sales_report.html', user=current_user)