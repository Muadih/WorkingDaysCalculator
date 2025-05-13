import pytest
from datetime import datetime
from wdc_service import app, is_working_day

def test_is_working_day_endpoint(client):
    """Test the is-working-day endpoint"""
    response = client.get('/api/v1/is-working-day?date=2025-05-10')
    assert response.status_code == 200
    data = response.get_json()
    assert 'date' in data
    assert 'is_working_day' in data

def test_working_days_between(client):
    """Test the working-days-between endpoint"""
    response = client.get('/api/v1/working-days-between?start_date=2025-05-01&end_date=2025-05-31')
    assert response.status_code == 200
    data = response.get_json()
    assert 'working_days' in data
    assert isinstance(data['working_days'], int)

def test_add_holiday(client, sample_holiday):
    """Test adding a holiday"""
    response = client.post('/api/v1/holidays', 
                         json=sample_holiday)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Holiday added successfully'

def test_list_holidays(client, sample_holiday):
    """Test listing holidays"""
    # First add a holiday
    client.post('/api/v1/holidays', json=sample_holiday)
    
    # Then list holidays
    response = client.get('/api/v1/holidays')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_calc_end_date(client):
    """Test calculating end date from start date and working days"""
    response = client.get('/api/v1/calc-end-date?start_date=2025-05-01&working_days=10')
    assert response.status_code == 200
    data = response.get_json()
    assert 'end_date' in data
    assert 'working_days' in data
    assert data['working_days'] == 10

def test_calc_start_date(client):
    """Test calculating start date from end date and working days"""
    response = client.get('/api/v1/calc-start-date?end_date=2025-05-15&working_days=10')
    assert response.status_code == 200
    data = response.get_json()
    assert 'start_date' in data
    assert 'working_days' in data
    assert data['working_days'] == 10

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'alive'

def test_readiness_check(client):
    """Test readiness check endpoint"""
    response = client.get('/api/v1/ready')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert 'checks' in data