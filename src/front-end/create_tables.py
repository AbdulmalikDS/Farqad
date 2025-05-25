from database import Base, engine
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def recreate_tables():
    """Drop and recreate all database tables to ensure schema is up-to-date."""
    logger.info("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    logger.info("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    logger.info("Database tables recreated successfully!")
    return True

if __name__ == "__main__":
    print("Managing database tables...")
    print("WARNING: This will drop and recreate all tables, losing all existing data!")
    choice = input("Do you want to proceed? (y/n): ").lower()
    
    if choice == 'y':
        success = recreate_tables()
        if success:
            print("Database tables have been successfully recreated.")
        else:
            print("Failed to recreate database tables.")
    else:
        print("Operation cancelled.")