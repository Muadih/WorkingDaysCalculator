#!/bin/bash

# Database configuration
DB_NAME="working_days_db"
DB_USER="wdc_user"
DB_PASSWORD="your_secure_password"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Setting up PostgreSQL database for Working Days Calculator..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}PostgreSQL is not installed. Installing...${NC}"
    sudo apt-get update
    sudo apt-get install -y postgresql postgresql-contrib
fi

# Create database and user
sudo -u postgres psql << EOF
-- Create user if not exists
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$DB_USER') THEN
    CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
  END IF;
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE $DB_NAME'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME');

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

# Check if database creation was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Database setup completed successfully!${NC}"
    
    # Update the database URL in the configuration
    echo "Updating database configuration..."
    sed -i "s|postgresql://username:password@localhost:5432/working_days_db|postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME|g" models.py
    
    echo -e "${GREEN}Configuration updated successfully!${NC}"
    echo "Database URL: postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
else
    echo -e "${RED}Error setting up the database${NC}"
    exit 1
fi
