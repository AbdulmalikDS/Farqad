from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import DATABASE_URL
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create engine with echo=True for debugging
# Include check_same_thread=False for SQLite to allow multiple threads
connect_args = {}
if DATABASE_URL.startswith('sqlite'):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    echo=True,  # This will print SQL statements
    pool_pre_ping=True,  # This will test the connection before using it
    connect_args=connect_args
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    userID = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    type = Column(String(50))

    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user")
    budgets = relationship("Budget", back_populates="user")
    upload_documents = relationship("UploadDocument", back_populates="user")
    chat_messages = relationship("ChatMessages", back_populates="user")

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': 'type'
    }

class Admin(User):
    __tablename__ = "admins"
    userID = Column(String, ForeignKey('users.userID'), primary_key=True)

    # Admin-specific methods (as per diagram)
    def approveData(self):
        pass
    def monitorUsage(self):
        pass
    def manageUsers(self):
        pass

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

class Organization(User):
    __tablename__ = "organizations"
    userID = Column(String, ForeignKey('users.userID'), primary_key=True)
    organizationName = Column(String)
    organizationEmail = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'organization',
    }

class Individual(User):
    __tablename__ = "individuals"
    userID = Column(String, ForeignKey('users.userID'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'individual',
    }

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    sessionID = Column(String, primary_key=True, index=True)
    userID = Column(String, ForeignKey('users.userID'))
    startTime = Column(DateTime)
    endTime = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    chat_messages = relationship("ChatMessages", back_populates="session")

class ChatMessages(Base):
    __tablename__ = "chat_messages"

    messageID = Column(String, primary_key=True, index=True)
    sessionID = Column(String, ForeignKey('chat_sessions.sessionID'))
    userID = Column(String, ForeignKey('users.userID'))
    content = Column(String)
    timestamp = Column(DateTime)
    senderType = Column(String)

    # Relationships
    session = relationship("ChatSession", back_populates="chat_messages")
    user = relationship("User", back_populates="chat_messages")

class Budget(Base):
    __tablename__ = "budgets"

    budgetID = Column(String, primary_key=True, index=True)
    userID = Column(String, ForeignKey('users.userID'))
    period = Column(String)
    totalAmount = Column(String)
    categories = Column(String)

    # Relationships
    user = relationship("User", back_populates="budgets")

class UploadDocument(Base):
    __tablename__ = "upload_documents"

    documentID = Column(String, primary_key=True, index=True)
    userID = Column(String, ForeignKey('users.userID'))
    documentType = Column(String)
    content = Column(String)
    uploadDate = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="upload_documents")

# Create all tables
def create_tables():
    try:
        logger.info("Attempting to connect to database...")
        logger.info(f"Database URL type: {DATABASE_URL.split(':')[0]}")
        Base.metadata.create_all(bind=engine)
        logger.info("Successfully created all tables!")
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        return False

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
def init_db():
    return create_tables()
