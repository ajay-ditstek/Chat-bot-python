"""
wsgi.py — WSGI/ASGI configuration for PythonAnywhere.

This file is used by PythonAnywhere to run the FastAPI application.
"""

import os
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault("PYTHONPATH", str(BASE_DIR))

# Import the FastAPI app
from src.main import app

# PythonAnywhere uses WSGI by default, but FastAPI is ASGI.
# We need to use the ASGI interface directly.
application = app
