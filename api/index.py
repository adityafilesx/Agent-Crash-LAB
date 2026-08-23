import sys
import os

# Set up ephemeral database for Vercel
os.environ["DATABASE_URL"] = "sqlite:////tmp/test.db"

# Add the backend directory to the Python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

from app.main import app
from app.core.database import Base, engine

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Try to seed if empty
try:
    from app.seed import seed
    seed()
except Exception as e:
    print("Seed failed:", e)
