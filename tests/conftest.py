import pytest
from datetime import datetime
from wdc_service import app, db
from models import Holiday

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://wdc_user:your_secure_password@localhost:5432/working_days_test_db'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def sample_holiday():
    return {
        'date': '2025-12-24',
        'name': 'Christmas Eve'
    }