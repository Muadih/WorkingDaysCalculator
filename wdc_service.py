from flask import Flask, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import holidays
from models import db, Holiday, init_db
from admin import init_admin
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://wdc_user:your_secure_password@localhost:5432/working_days_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
admin = init_admin(app, db)

@app.route('/')
def index():
    return redirect('/admin')

# Polish holidays
pl_holidays = holidays.PL()

def get_all_holidays():
    """Get all holidays from database and Polish holidays package"""
    db_session = db.session
    try:
        # Get custom holidays from database
        custom_holidays = db_session.query(Holiday).all()
        # Convert to set of dates for efficient lookup
        custom_holiday_dates = {holiday.date for holiday in custom_holidays}
        return custom_holiday_dates
    finally:
        db_session.close()

def is_working_day(date):
    """Check if given date is a working day."""
    custom_holidays = get_all_holidays()
    return (date.weekday() < 5 and 
            date not in pl_holidays and 
            date.date() not in custom_holidays)

@app.route('/api/is-working-day', methods=['GET'])
def check_working_day():
    try:
        date_str = request.args.get('date')
        if not date_str:
            return jsonify({'error': 'Date parameter is required'}), 400
        
        date = datetime.strptime(date_str, '%Y-%m-%d')
        result = is_working_day(date)
        
        return jsonify({
            'date': date_str,
            'is_working_day': result
        })
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

@app.route('/api/working-days-between', methods=['GET'])
def count_working_days():
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            return jsonify({'error': 'Both start_date and end_date are required'}), 400
            
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        working_days = sum(1 for date in (start_date + timedelta(x) 
                          for x in range((end_date - start_date).days + 1)) 
                          if is_working_day(date))
        
        return jsonify({
            'start_date': start_date_str,
            'end_date': end_date_str,
            'working_days': working_days
        })
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

@app.route('/api/working-days-count', methods=['GET'])
def get_working_days_count():
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            return jsonify({'error': 'Both start_date and end_date are required'}), 400
            
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        if end_date < start_date:
            return jsonify({'error': 'End date must be after start date'}), 400
        
        working_days = sum(1 for date in (start_date + timedelta(x) 
                          for x in range((end_date - start_date).days + 1)) 
                          if is_working_day(date))
        
        return jsonify({
            'start_date': start_date_str,
            'end_date': end_date_str,
            'working_days_count': working_days,
            'total_days': (end_date - start_date).days + 1
        })
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

@app.route('/api/holidays', methods=['POST'])
def add_holiday():
    try:
        data = request.get_json()
        date_str = data.get('date')
        name = data.get('name')
        
        if not date_str or not name:
            return jsonify({'error': 'Date and name are required'}), 400
            
        date = datetime.strptime(date_str, '%Y-%m-%d')
        
        db_session = db.session
        try:
            holiday = Holiday(
                date=date.date(),
                name=name,
                type='CUSTOM'
            )
            db_session.add(holiday)
            db_session.commit()
            
            return jsonify({
                'message': 'Holiday added successfully',
                'date': date_str,
                'name': name
            })
        finally:
            db_session.close()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

@app.route('/api/holidays', methods=['GET'])
def list_holidays():
    db_session = db.session
    try:
        holidays = db_session.query(Holiday).all()
        return jsonify([{
            'date': holiday.date.strftime('%Y-%m-%d'),
            'name': holiday.name,
            'type': holiday.type
        } for holiday in holidays])
    finally:
        db_session.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)