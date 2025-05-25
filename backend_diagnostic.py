import sys
import os
import traceback

# Add src directory to Python path to find modules
src_path = os.path.join(os.getcwd(), "src")
sys.path.append(src_path)
print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Added to path:", src_path)
print("\nRunning backend diagnostics...\n")

# Test MongoDB connection
try:
    print("Testing MongoDB connection...")
    from motor.motor_asyncio import AsyncIOMotorClient
    from helpers.config import get_settings
    
    settings = get_settings()
    print(f"MongoDB URL: {settings.MONGODB_URL}")
    print(f"MongoDB Database: {settings.MONGODB_DATABASE}")
    
    # Try to connect to MongoDB
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        print("MongoDB client created")
        # Check server info to verify connection
        server_info = client.server_info()  # This will raise an exception if connection fails
        print("✓ MongoDB connection successful")
    except Exception as e:
        print(f"✗ MongoDB connection failed: {str(e)}")
        print("This is likely causing the backend server to fail")
        print("Consider updating the MONGODB_URL in src/helpers/config.py to use a mock or in-memory database for testing")
except Exception as e:
    print(f"✗ Error setting up MongoDB test: {str(e)}")
    traceback.print_exc()

# Test LLM Provider Factory
try:
    print("\nTesting LLM Provider Factory...")
    from stores.llm.LLMProviderFactory import LLMProviderFactory
    
    settings = get_settings()
    try:
        llm_provider_factory = LLMProviderFactory(settings)
        print("✓ LLM Provider Factory created successfully")
        
        # Try to create a provider
        try:
            provider = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
            print(f"✓ Created provider for backend: {settings.GENERATION_BACKEND}")
        except Exception as e:
            print(f"✗ Error creating provider: {str(e)}")
    except Exception as e:
        print(f"✗ Error initializing LLM Provider Factory: {str(e)}")
except Exception as e:
    print(f"✗ Error importing LLM Provider Factory: {str(e)}")
    traceback.print_exc()

# Test Vector DB Provider Factory
try:
    print("\nTesting Vector DB Provider Factory...")
    from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
    
    settings = get_settings()
    try:
        vectordb_provider_factory = VectorDBProviderFactory(settings)
        print("✓ Vector DB Provider Factory created successfully")
        
        # Try to create a provider
        try:
            provider = vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
            print(f"✓ Created provider for backend: {settings.VECTOR_DB_BACKEND}")
            
            # Try to connect
            try:
                provider.connect()
                print("✓ Vector DB connection successful")
                provider.disconnect()
            except Exception as e:
                print(f"✗ Error connecting to Vector DB: {str(e)}")
        except Exception as e:
            print(f"✗ Error creating Vector DB provider: {str(e)}")
    except Exception as e:
        print(f"✗ Error initializing Vector DB Provider Factory: {str(e)}")
except Exception as e:
    print(f"✗ Error importing Vector DB Provider Factory: {str(e)}")
    traceback.print_exc()

# Test Template Parser
try:
    print("\nTesting Template Parser...")
    from stores.llm.templates.template_parser import TemplateParser
    
    settings = get_settings()
    try:
        template_parser = TemplateParser(
            language=settings.PRIMARY_LANG,
            default_language=settings.DEFAULT_LANG
        )
        print("✓ Template Parser created successfully")
    except Exception as e:
        print(f"✗ Error initializing Template Parser: {str(e)}")
except Exception as e:
    print(f"✗ Error importing Template Parser: {str(e)}")
    traceback.print_exc()

# Test routes
try:
    print("\nTesting routes import...")
    from routes import base, data, nlp
    print("✓ Routes imported successfully")
except Exception as e:
    print(f"✗ Error importing routes: {str(e)}")
    traceback.print_exc()

print("\nDiagnostic test completed.")
print("\nSummary of likely issues:")
print("1. MongoDB connection - The backend is trying to connect to MongoDB at startup")
print("   If MongoDB is not running or accessible, this will cause the server to fail")
print("   Solution: Either install and run MongoDB, or modify the config to use a mock")
print("\n2. Vector DB - The backend is trying to connect to a vector database")
print("   If the vector DB path doesn't exist or is not accessible, this will cause issues")
print("   Solution: Check if the vector DB path exists and is writable")
print("\n3. API Keys - The backend may be trying to connect to external APIs")
print("   If API keys are invalid, this could cause authentication failures")
print("   Solution: Provide valid API keys or modify the code to use mock services") 