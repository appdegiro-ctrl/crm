from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from .user import User
    from .restaurant import Restaurant
    from .lead import Lead
    from .message import Message
    from .campaign import Campaign
    from .product import Product
    from .whatsapp_session import WhatsAppSession
    
    Base.metadata.create_all(bind=engine)