#!/usr/bin/env python3
"""
Database initialization script.

Usage:
    python scripts/init_db.py

This script initializes the database with:
- All required tables
- Default admin user
- Sample hotel and rooms
- Staff users for testing
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.seed import seed_database

if __name__ == "__main__":
    seed_database()
