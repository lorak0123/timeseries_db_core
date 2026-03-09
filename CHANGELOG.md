# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Updated project structure to fit new requirements and best practices

## [0.1.0] - 2026-03-09

### Added
- Created `models/` directory structure for data models
- Added `models/__init__.py` with package documentation and imports
- All code documentation follows Google Python Style Guide conventions with English language

#### Step 2: SQLAlchemy Models (Numeric and Categorical Time Series)
- Created `models/base.py` with declarative base configuration
- Created `models/series_catalog.py` - SeriesCatalog model for numeric time series
  - Attributes: id, name, tags (JSON), description, aggregation_method, created_at
  - Relationships: measurements (Measurement objects)
  - Indexes for efficient queries by name and creation time
- Created `models/measurement.py` - Measurement model for numeric time series values
  - Attributes: time (TIMESTAMPTZ), series_id (FK), value (DOUBLE PRECISION)
  - Relationships: series (SeriesCatalog object)
  - Indexes: idx_measurements_time, idx_measurements_series_id
- Created `models/categories_catalog.py` - CategoriesCatalog model for categorical time series
  - Attributes: id, name, tags (JSON), state_mapping (JSON), description, created_at
  - Relationships: measurements (CategoricalMeasurement objects)
  - Indexes for efficient queries by name and creation time
- Created `models/categorical_measurement.py` - CategoricalMeasurement model for categorical values
  - Attributes: time (TIMESTAMPTZ), series_id (FK), value (SMALLINT)
  - Relationships: series (CategoriesCatalog object)
  - Indexes: idx_categorical_time, idx_categorical_series_id

#### Step 3: Project Configuration (pyproject.toml)
- Created `pyproject.toml` with comprehensive project configuration
  - Build system configuration using setuptools
  - Project metadata: name, version, description, dependencies
  - Dependencies: SQLAlchemy>=2.0.0, psycopg2-binary>=2.9.0, python-dotenv>=0.21.0
  - Development dependencies: ruff, pytest, pytest-cov, black, mypy
  - Ruff configuration:
    - Target Python 3.10+
    - Line length: 88 characters
    - Enabled rule sets: E, W, F, I, C, B, D, UP, A, S, SIM
    - Google style docstrings
    - Import sorting with isort profile
  - pytest configuration with coverage reporting
  - mypy configuration for type checking

#### Step 4: SQLAlchemy and Alembic Configuration
- Created `database.py` in root directory for database configuration
  - DatabaseConfig class for connection management
  - Reads DATABASE_URL, ECHO_SQL, POOL_SIZE, MAX_OVERFLOW from environment
  - Methods: get_engine(), get_session_factory(), get_session()
- Created `alembic/` directory for database migrations
  - `alembic/env.py` - Alembic environment configuration for online/offline migrations
  - Integrated with DatabaseConfig for consistent connection management
  - `alembic/script.py.mako` - Template for generated migration files
  - `alembic/versions/` - Directory for migration scripts
  - `alembic.ini` - Alembic configuration file
- Updated `pyproject.toml` to include alembic>=1.12.0 as dependency
- Removed `sqlalchemy/` directory (moved config to root as `database.py`)

