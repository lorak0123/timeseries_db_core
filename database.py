"""
Database configuration module for SQLAlchemy.

This module provides database connection configuration and session management
for the timeseries database core. It handles connection strings, engine setup,
and session factory creation.

Google Python Style Guide conventions are followed throughout.
"""

import os
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig:
    """Database configuration management.

    This class manages database connection parameters and provides
    factory methods for creating database engines and sessions.

    Attributes:
        DATABASE_URL: Connection string for the database.
        ECHO_SQL: Flag to enable SQL query logging.
        POOL_SIZE: Number of connections to maintain in the pool.
        MAX_OVERFLOW: Maximum overflow connections beyond pool_size.
    """

    # Default database connection string from environment or fallback
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://user:password@localhost:5432/timeseries_db"
    )

    # SQL query logging flag
    ECHO_SQL: bool = os.getenv("ECHO_SQL", "False").lower() == "true"

    # Connection pool configuration
    POOL_SIZE: int = int(os.getenv("POOL_SIZE", "5"))
    MAX_OVERFLOW: int = int(os.getenv("MAX_OVERFLOW", "10"))

    @classmethod
    def get_engine(cls) -> Engine:
        """Create and return a SQLAlchemy engine.

        Returns:
            Engine: Configured SQLAlchemy engine for database connections.
        """
        return create_engine(
            cls.DATABASE_URL,
            echo=cls.ECHO_SQL,
            pool_size=cls.POOL_SIZE,
            max_overflow=cls.MAX_OVERFLOW,
        )

    @classmethod
    def get_session_factory(cls) -> sessionmaker:
        """Create and return a session factory.

        Returns:
            sessionmaker: Factory for creating database sessions.
        """
        engine = cls.get_engine()
        return sessionmaker(bind=engine, class_=Session, expire_on_commit=False)

    @classmethod
    def get_session(cls) -> Session:
        """Create and return a new database session.

        Returns:
            Session: A new SQLAlchemy session for database operations.
        """
        factory = cls.get_session_factory()
        return factory()
