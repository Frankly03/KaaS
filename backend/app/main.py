import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .api import ingestion, query
from .db import init_db
from .services.vectorstore import init_vectorstore
from .config import settings
