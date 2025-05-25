from database import engine, Base, SessionLocal
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_db():
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Test database connection
        db = SessionLocal()
        try:
            # Try to execute a simple query to verify connection
            db.execute("SELECT 1")
            logger.info("Database connection successful!")
        except Exception as conn_err:
            logger.error(f"Database connection test failed: {str(conn_err)}")
        finally:
            db.close()
            
        logger.info("Database tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_db()
    if success:
        print("✅ Database initialization complete!")
    else:
        print("❌ Database initialization failed, check the logs for details.") 