# Practice 7 - PhoneBook with PostgreSQL

In this practice I built a console-based PhoneBook application using Python and PostgreSQL.

# What I did
- Connected Python to PostgreSQL database using psycopg2
- Created a phonebook table with id, name and phone fields
- Implemented adding contacts manually from console
- Implemented loading contacts from a CSV file
- Implemented searching contacts by name or phone prefix
- Implemented updating contact name or phone number
- Implemented deleting contacts by name or phone number

# Files
- `phonebook.py` - main application with all CRUD functions
- `connect.py` - database connection
- `config.py` - database settings
- `contacts.csv` - sample contacts data

# How to run
1. Install psycopg2: `pip install psycopg2-binary`
2. Set your database password in `config.py`
3. Run: `python phonebook.py`
