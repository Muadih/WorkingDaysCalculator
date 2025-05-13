#!/bin/bash
set -e

echo "Creating test database..."
PGPASSWORD=your_secure_password psql -U wdc_user -h localhost -c "DROP DATABASE IF EXISTS working_days_test_db;"
PGPASSWORD=your_secure_password psql -U wdc_user -h localhost -c "CREATE DATABASE working_days_test_db;"

echo "Running tests..."
pytest tests/ -v --cov=wdc_service --cov-report=term-missing

echo "Cleaning up test database..."
PGPASSWORD=your_secure_password psql -U wdc_user -h localhost -c "DROP DATABASE IF EXISTS working_days_test_db;"