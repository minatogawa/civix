import os
import sys
from datetime import datetime

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import create_app, db  # noqa: E402
from models import Campaign, Contact, Interaction  # noqa: E402

app = create_app()

# Import models to make them available to Flask-Migrate
with app.app_context():
    # This ensures models are registered with SQLAlchemy
    pass

if __name__ == "__main__":
    with app.app_context():
        # Create tables if they don't exist (for development)
        try:
            db.create_all()
        except Exception as e:
            print(f"Database error: {e}")

    app.run(debug=True, host="0.0.0.0", port=5000)
