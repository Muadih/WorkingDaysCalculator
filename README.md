# WorkingDaysCalculator
Program wyliczający datę na podstawie liczby dni roboczych lub podaje liczbę dni roboczych na podstawie dat

This web service provides two main endpoints:

/api/is-working-day

Checks if a given date is a working day
Takes a date parameter in YYYY-MM-DD format
Returns whether the date is a working day or not
/api/working-days-between

Counts working days between two dates
Takes start_date and end_date parameters
Returns the number of working days in the range
To run this service, you'll need to install the required dependencies:

You can test the service using curl:

The service takes into account:

Weekends (Saturday and Sunday)
Polish national holidays (using the holidays package)

Create_db.sh
------------
To use this script:

Make the script executable:
Run the script:
The script will:

Check if PostgreSQL is installed and install it if necessary
Create a new database user
Create the database
Grant necessary privileges
Update the database URL in your models.py file
Make sure to:

Replace your_secure_password with a secure password
Run the script with appropriate permissions
Keep the database credentials secure

Admin Panel
------------
To use the admin panel:

Install the new requirements:
Run the application:
Access the admin panel at http://localhost:5000/admin
Features of the admin panel:

List all holidays with sorting and filtering
Add new holidays with date validation
Edit existing holidays
Delete holidays
Search holidays by name
Filter by date and type
Polish language labels
Bootstrap-based responsive interface
The admin panel allows you to:

View all holidays in a table format
Add new holidays using a form
Edit existing holidays by clicking the edit button
Delete holidays using the delete button
Search through holidays using the search bar
Filter holidays by date range or type
Sort holidays by any column
All changes made in the admin panel are automatically saved to the PostgreSQL database.

