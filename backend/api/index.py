import sys
import os

# Add the 'app' directory to the Python path so absolute imports work
backend_dir = os.path.dirname(os.path.dirname(__file__))
app_dir = os.path.join(backend_dir, "app")
sys.path.insert(0, app_dir)

# Import the FastAPI application instance
from app.main import app
