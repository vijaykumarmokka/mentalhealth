import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    
    # Azure SQL Database connection string
    SQLALCHEMY_DATABASE_URI = (
        'mssql+pyodbc://Cs4hmhiHGrT%24cwmb:helloword-server@helloword.database.windows.net/helloword-database?driver=ODBC+Driver+17+for+SQL+Server'
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
