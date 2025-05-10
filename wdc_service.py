from flask import Flask, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import holidays
from flasgger import Swagger  # New: Import Flasgger
from models import db, Holiday, init_db
from admin import init_admin
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://wdc_user:your_secure_password@localhost:5432/working_days_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# New: Swagger configuration for API documentation, with versioned documentation path.
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,  # include all endpoints
            "model_filter": lambda tag: True,  # include all models
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/v1/swagger"  # Swagger UI available at /api/v1/swagger
}
swagger = Swagger(app, config=swagger_config)

# Initialize extensions
db.init_app(app)
admin = init_admin(app, db)

@app.route('/')
def index():
    """
    Redirects to the Admin Panel.
    ---
    responses:
      302:
        description: Redirecting to admin panel
    """
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

@app.route('/api/v1/is-working-day', methods=['GET'])
def check_working_day():
    """
    Check if a given date is a working day.
    ---
    parameters:
      - name: date
        in: query
        type: string
        required: true
        description: Date in format YYYY-MM-DD
    responses:
      200:
        description: Returns if the date is a working day
        schema:
          type: object
          properties:
            date:
              type: string
            is_working_day:
              type: boolean
      400:
        description: Invalid date format or missing parameters
    """
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

@app.route('/api/v1/working-days-between', methods=['GET'])
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

@app.route('/api/v1/working-days-count', methods=['GET'])
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

@app.route('/api/v1/holidays', methods=['POST'])
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

@app.route('/api/v1/holidays', methods=['GET'])
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

@app.route('/api/v1/health')
def health_check():
    """
    Liveness probe - just checks if application is running
    """
    return jsonify({'status': 'alive'}), 200

@app.route('/api/v1/ready')
def readiness_check():
    """
    Readiness probe - checks if application can handle traffic
    """
    status = {
        'database': False,
        'holidays_service': False,
        'overall': False
    }
    
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        status['database'] = True
        
        # Check holidays service
        test_date = datetime.now()
        _ = holidays.PL().get(test_date)
        status['holidays_service'] = True
        
        # If all checks pass, set overall status to True
        if all([status['database'], status['holidays_service']]):
            status['overall'] = True
            return jsonify({
                'status': 'ready',
                'checks': status
            }), 200
        else:
            return jsonify({
                'status': 'not ready',
                'checks': status
            }), 503
            
    except Exception as e:
        return jsonify({
            'status': 'not ready',
            'checks': status,
            'error': str(e)
        }), 503

@app.route('/api/v1/calc-end-date', methods=['GET'])
def calc_end_date():
    """
    Calculate end date based on a start date and a number of working days.
    Expects query parameters:
      - start_date (format: YYYY-MM-DD)
      - working_days (integer)
    """
    start_date_str = request.args.get('start_date')
    working_days_str = request.args.get('working_days')

    if not start_date_str or not working_days_str:
        return jsonify({'error': 'start_date and working_days parameters are required'}), 400

    try:
        working_days = int(working_days_str)
    except ValueError:
        return jsonify({'error': 'working_days must be an integer'}), 400

    try:
        current_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400

    days_counted = 0
    while days_counted < working_days:
        current_date += timedelta(days=1)
        if is_working_day(current_date):
            days_counted += 1

    return jsonify({
        'start_date': start_date_str,
        'working_days': working_days,
        'end_date': current_date.strftime('%Y-%m-%d')
    }), 200

@app.route('/api/v1/calc-start-date', methods=['GET'])
def calc_start_date():
    """
    Calculate start date based on an end date and a number of working days.
    Expects query parameters:
      - end_date (format: YYYY-MM-DD)
      - working_days (integer)
    """
    end_date_str = request.args.get('end_date')
    working_days_str = request.args.get('working_days')

    if not end_date_str or not working_days_str:
        return jsonify({'error': 'end_date and working_days parameters are required'}), 400

    try:
        working_days = int(working_days_str)
    except ValueError:
        return jsonify({'error': 'working_days must be an integer'}), 400

    try:
        current_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400

    days_counted = 0
    while days_counted < working_days:
        current_date -= timedelta(days=1)
        if is_working_day(current_date):
            days_counted += 1

    return jsonify({
        'end_date': end_date_str,
        'working_days': working_days,
        'start_date': current_date.strftime('%Y-%m-%d')
    }), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)