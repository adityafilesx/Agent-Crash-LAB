import os
import sys

# Add backend to path so we can import from app
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.core.database import SessionLocal
from app.models.agent_version import AgentVersion

def fix_db():
    db = SessionLocal()
    try:
        versions = db.query(AgentVersion).all()
        for v in versions:
            if v.model_provider == 'gemini':
                print(f"Updating AgentVersion {v.id} from {v.model_provider} to groq")
                v.model_provider = 'groq'
                v.model_name = 'llama3-70b-8192'
        db.commit()
        print("Done fixing db.")
    finally:
        db.close()

if __name__ == "__main__":
    fix_db()
