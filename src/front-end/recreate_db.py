from database import Base, engine
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def recreate_tables():
    """Drop and recreate all database tables without prompting."""
    logger.info("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    logger.info("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    logger.info("Database tables recreated successfully!")
    return True

if __name__ == "__main__":
    print("WARNING: This will drop and recreate all tables, losing all data!")
    print("Proceeding in 3 seconds...")
    
    import time
    time.sleep(3)
    
    success = recreate_tables()
    if success:
        print("Tables recreated successfully!")
    else:
        print("Failed to recreate tables.") 