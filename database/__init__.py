"""
Database management package.
"""
from .db_manager import DatabaseManager

db_manager = DatabaseManager()

__all__ = ["DatabaseManager", "db_manager"]
