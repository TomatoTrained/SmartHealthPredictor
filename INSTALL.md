# Installation Guide for Healthcare Prediction System

## System Requirements

1. Python 3.11
2. PostgreSQL Database Server (version 12 or higher)
3. 2GB RAM minimum
4. 1GB free disk space

## Files to Transfer

Copy these files and folders to your flash drive:
```
├── .streamlit/          # Streamlit configuration
├── data/               # Data files (symptoms.csv, doctors.json)
│   ├── symptoms.csv    # Disease prediction data
│   ├── doctors.json    # Doctor information
│   └── users.json      # Initial user data
├── pages/             # Application pages
├── styles/            # CSS styles
├── utils/             # Utility functions
└── Home.py            # Main application file
```

## Step-by-Step Installation

### 1. Install Python 3.11
- Windows: Download from [Python.org](https://www.python.org/downloads/release/python-3110/)
- Linux: `sudo apt-get install python3.11`
- Mac: `brew install python@3.11`

### 2. Install PostgreSQL
- Windows: Download installer from [PostgreSQL Website](https://www.postgresql.org/download/windows/)
- Linux: `sudo apt-get install postgresql`
- Mac: `brew install postgresql`

### 3. Install Required Python Packages
```bash
pip install streamlit plotly sqlalchemy psycopg2-binary
```

### 4. Database Setup
1. Create a new PostgreSQL database:
```sql
CREATE DATABASE healthcare_prediction;
```

2. Set up environment variables:
Create a `.env` file in the project root with:
```
DATABASE_URL=postgresql://username:password@localhost:5432/healthcare_prediction
PGUSER=your_postgres_username
PGPASSWORD=your_postgres_password
PGDATABASE=healthcare_prediction
PGHOST=localhost
PGPORT=5432
```

### 5. Running the Application

1. Initialize the database:
```python
from utils.database import init_db
init_db()
```

2. Start the application:
```bash
streamlit run Home.py
```

3. Access the application:
Open your web browser and navigate to `http://localhost:5000`

## Default Test Account
You can use these credentials for testing:
- Regular User:
  - Username: demo_user
  - Password: demo123
- Doctor:
  - Username: dr_smith
  - Password: doctor123

## Troubleshooting

1. If you see database connection errors:
   - Verify PostgreSQL is running
   - Check your database credentials in `.env`
   - Ensure the database exists

2. If you see missing package errors:
   - Run pip install command again
   - Verify Python 3.11 is in your PATH

3. If the web interface doesn't load:
   - Check if port 5000 is available
   - Verify Streamlit is installed correctly

## Security Notes

1. Never share your `.env` file
2. Change default passwords
3. Keep your Python packages updated
4. Regularly backup your database

For additional help, contact technical support or refer to the documentation.