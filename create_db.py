from repository import AttendanceManager
from models import Base  # Make sure this import is from the correct module where `Base` is defined

# Initialize the AttendanceManager
db_manager = AttendanceManager()

# Create all tables in the database
Base.metadata.create_all(db_manager.engine)

print("Database tables created successfully.")
