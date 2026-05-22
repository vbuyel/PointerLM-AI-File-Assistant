from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings, get_postgres_url
import time


db_user = settings.db_user
db_password = settings.db_password
db_host = settings.db_host
db_port = settings.db_port
db_name = settings.db_name

Base = declarative_base()

while True:
    try:
        SQLALCHEMY_DATABASE_URL = get_postgres_url() #f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'client_encoding': 'utf8'})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        Base.metadata.create_all(bind=engine)

        print("Database connection established")
        break
    except Exception as e:
        print("Error connecting to DataBase", e)
        time.sleep(2)

