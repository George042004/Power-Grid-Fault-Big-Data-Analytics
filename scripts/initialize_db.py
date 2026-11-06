"""
Database Initialization Script.
Creates tables and seeds default grid substations into SQLite.
"""
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db_manager import db_manager


def main():
    print("=" * 70)
    print("Initializing Power-Grid Database...")
    print("=" * 70)
    success = db_manager.initialize_database()
    if success:
        stations = db_manager.get_all_stations()
        print(f"Database schema initialized successfully with {len(stations)} substations:")
        for st in stations:
            print(f" - [{st['station_id']}] {st['station_name']} ({st['region']}) | {st['capacity_mva']} MVA")
    else:
        print("[ERROR] Database initialization failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
