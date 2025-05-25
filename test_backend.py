import sys
import os
import traceback

# Add src directory to Python path to find modules
src_path = os.path.join(os.getcwd(), "src")
sys.path.append(src_path)
print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Added to path:", src_path)
print("\nTesting imports for backend dependencies...\n")

try:
    print("Testing FastAPI import...")
    from fastapi import FastAPI
    print("✓ FastAPI imported successfully")
except Exception as e:
    print("✗ Error importing FastAPI:", str(e))
    traceback.print_exc()

try:
    print("\nTesting motor import...")
    from motor.motor_asyncio import AsyncIOMotorClient
    print("✓ motor imported successfully")
except Exception as e:
    print("✗ Error importing motor:", str(e))
    traceback.print_exc()

try:
    print("\nTesting helpers.config import...")
    from helpers.config import get_settings
    print("✓ helpers.config imported successfully")
    
    # Try to get settings
    try:
        settings = get_settings()
        print("✓ get_settings() called successfully")
        print("  - MONGODB_URL:", settings.MONGODB_URL if hasattr(settings, "MONGODB_URL") else "Not defined")
        print("  - MONGODB_DATABASE:", settings.MONGODB_DATABASE if hasattr(settings, "MONGODB_DATABASE") else "Not defined")
        print("  - GENERATION_BACKEND:", settings.GENERATION_BACKEND if hasattr(settings, "GENERATION_BACKEND") else "Not defined")
    except Exception as e:
        print("✗ Error calling get_settings():", str(e))
        traceback.print_exc()
except Exception as e:
    print("✗ Error importing helpers.config:", str(e))
    traceback.print_exc()

try:
    print("\nTesting routes imports...")
    from routes import base, data, nlp
    print("✓ routes imported successfully")
except Exception as e:
    print("✗ Error importing routes:", str(e))
    traceback.print_exc()

try:
    print("\nTesting LLM factories import...")
    from stores.llm.LLMProviderFactory import LLMProviderFactory
    from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
    print("✓ LLM factories imported successfully")
except Exception as e:
    print("✗ Error importing LLM factories:", str(e))
    traceback.print_exc()

print("\nImport test completed.") 