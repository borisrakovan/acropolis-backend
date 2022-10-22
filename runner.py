from database.db import create_db_and_tables
from monitoring_service.flow import run_monitoring_flow


if __name__ == "__main__":
    create_db_and_tables()
    run_monitoring_flow()
