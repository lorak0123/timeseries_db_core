"""
Base model configuration for SQLAlchemy.

This module provides the declarative base for all SQLAlchemy models
used in the timeseries database core. All models should inherit from
the Base class defined here.

Google Python Style Guide conventions are followed throughout.
"""

from sqlalchemy.orm import declarative_base

# Create the declarative base that all models will inherit from
Base = declarative_base()
