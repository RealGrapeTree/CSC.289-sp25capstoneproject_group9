from flask import render_template, Blueprint, request, jsonify, send_file
from extensions import db
from flask_login import current_user
from models import Transaction
from ..cart.Novel_cart import NC_TAX_RATE

import datetime as dt
from datetime import timedelta, datetime, date
import calendar
import pandas as pd
import io


# Create the Blueprint
Novel_sales_reports = Blueprint('Novel_sales_reports', __name__, template_folder='templates')


# Function to export reports to CSV
@Novel_sales_reports.route("/export_sales_csv/<string:reportType>", methods=["GET"])
def export_reports_csv(reportType):
    now = datetime.today()

    # Initialize variables for transactions
    transactions = []
    subtotal = 0  # Initialize subtotal variable

    # Determine start and end times based on report type
    if reportType == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif reportType == "weekly":
        start = now - timedelta(days=now.weekday())
        end = start + timedelta(days=6)
    elif reportType == "monthly":
        start = now.replace(day=1)
        last_day = calendar.monthrange(now.year, now.month)[1]
        end = now.replace(day=last_day)
    elif reportType == "custom":
        start_str = request.args.get("start")
        end_str = request.args.get("end")
        if not start_str or not end_str:
            flash("Custom report dates not specified.")
            return redirect(url_for("Novel_sales_reports.sales_report"))
        
        # Ensure both start and end are in correct date format before adding time
        if " " not in start_str:  # Check if no time part is already present
            start_str += " 00:00:00"  # Add default time
        if " " not in end_str:  # Check if no time part is already present
            end_str += " 23:59:59"  # Add default time
        
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
            end_date = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")  # End date inclusive
        except ValueError as e:
            flash(f"Invalid date format: {str(e)}")
            return redirect(url_for("Novel_sales_reports.sales_report"))
        
        transactions = db.session.query(Transaction).filter(
            Transaction.timestamp >= start_date,
            Transaction.timestamp <= end_date
        ).all()
    else:
        return jsonify({"message": "Unsupported report type", "success": False}), 400

    # If the report type is not custom, fetch transactions accordingly
    if reportType != "custom":
        transactions = db.session.query(Transaction).filter(
            Transaction.timestamp >= start,
            Transaction.timestamp <= end
        ).all()

    # Prepare data for CSV export
    data = []
    for t in transactions:
        for item in t.items:
            line_total = item.unit_price * item.quantity  # Calculate line total in cents
            subtotal += line_total  # Add to subtotal
            data.append({
                "Transaction ID": t.id,
                "Timestamp": t.timestamp,
                "Item": item.book.title,
                "Quantity": item.quantity,
                "Unit Price": item.unit_price / 100,
                "Line Total": (item.unit_price * item.quantity) / 100
            })

    # Calculate totals
    subtotal_dollars = subtotal / 100
    tax_amount = round(subtotal_dollars * NC_TAX_RATE, 2)
    total_price = round(subtotal_dollars + tax_amount, 2)

    # Define labels for different report types
    if reportType == "daily":
        sales_label = "Daily Sales Amount"
        tax_label = "Daily Sales Tax (7.25%)"
        total_label = "Daily Sales Total"
    elif reportType == "weekly":
        sales_label = "Weekly Sales Amount"
        tax_label = "Weekly Sales Tax (7.25%)"
        total_label = "Weekly Sales Total"
    elif reportType == "monthly":
        sales_label = "Monthly Sales Amount"
        tax_label = "Monthly Sales Tax (7.25%)"
        total_label = "Monthly Sales Total"
    elif reportType == "custom":
        sales_label = "Custom Sales Amount"
        tax_label = "Custom Sales Tax (7.25%)"
        total_label = "Custom Sales Total"

    # Add totals to the data
    data.append({
        "Transaction ID": "TOTAL",
        "Timestamp": "",
        "Item": sales_label,
        "Quantity": "",
        "Unit Price": "",
        "Total": round(subtotal_dollars, 2)  # Use the calculated subtotal
    })
    data.append({
        "Transaction ID": "TOTAL",
        "Timestamp": "",
        "Item": tax_label,
        "Quantity": "",
        "Unit Price": "",
        "Total": round(tax_amount, 2)  # Use the calculated tax amount
    })
    data.append({
        "Transaction ID": "TOTAL",
        "Timestamp": "",
        "Item": total_label,
        "Quantity": "",
        "Unit Price": "",
        "Total": round(total_price, 2)  # Use the calculated total price
    })

    # Convert data to DataFrame
    df = pd.DataFrame(data)

    # Save to in-memory buffer
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    return send_file(
        io.BytesIO(buffer.getvalue().encode()),
        mimetype='text/csv',
        download_name=f"{reportType}_sales_report.csv",
        as_attachment=True
    )



# # Function to export reports to PDF
# @Novel_sales_reports.route("/export_sales_pdf/<string:table_to_export>", methods=["POST"])
# def export_reports_pdf(table_to_export):
#     pass


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

    for t in transactions:
        for item in t.items:
            line_total = item.unit_price * item.quantity  # Still in cents
            subtotal += line_total

        # Convert subtotal to dollars
        subtotal_dollars = subtotal / 100
        tax_amount = round(subtotal_dollars * NC_TAX_RATE, 2)
        total_price = round(subtotal_dollars + tax_amount, 2)
    return render_template('daily_sales_report.html',
                           user=current_user,
                           current_date=current_date,
                           transactions=transactions,
                           subtotal=subtotal_dollars,
                           tax_amount=tax_amount,
                           total_price=total_price,
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
        for item in t.items:
            line_total = item.unit_price * item.quantity  # Still in cents
            subtotal += line_total

    # Convert subtotal to dollars
    subtotal_dollars = subtotal / 100
    tax_amount = round(subtotal_dollars * NC_TAX_RATE, 2)
    total_price = round(subtotal_dollars + tax_amount, 2)

    return render_template('weekly_sales_report.html',
                           user=current_user,
                           current_date=current_date,
                           week_start=week_start,
                           week_end=week_end,
                           transactions=transactions,
                           subtotal=subtotal_dollars, 
                           tax_amount=tax_amount,
                           total_price=total_price,
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
        for item in t.items:
            line_total = item.unit_price * item.quantity  # Still in cents
            subtotal += line_total

    # Convert subtotal to dollars
    subtotal_dollars = subtotal / 100
    tax_amount = round(subtotal_dollars * NC_TAX_RATE, 2)
    total_price = round(subtotal_dollars + tax_amount, 2)

    return render_template('monthly_sales_report.html', 
                           user=current_user, 
                           current_date=current_date, 
                           first_of_month=first_of_month,
                           last_of_month=last_of_month,  
                           transactions=transactions,
                           subtotal=subtotal_dollars, 
                           tax_amount=tax_amount ,
                           total_price=total_price,
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
        for item in t.items:
            line_total = item.unit_price * item.quantity  # Still in cents
            subtotal += line_total

    # Convert subtotal to dollars
    subtotal_dollars = subtotal / 100
    tax_amount = round(subtotal_dollars * NC_TAX_RATE, 2)
    total_price = round(subtotal_dollars + tax_amount, 2)

    return render_template('custom_sales_report.html', 
                           user=current_user,
                           current_date=current_date, 
                           custom_start_date=custom_start_date, 
                           custom_end_date=custom_end_date,
                           transactions=transactions,
                           subtotal=subtotal_dollars,
                           tax_amount=tax_amount,
                           total_price=total_price,
                           NC_TAX_RATE=NC_TAX_RATE)