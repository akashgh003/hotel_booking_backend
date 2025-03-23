from fastapi import FastAPI
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

# Import FastAPI app
from src.api.main import app

export_app = app