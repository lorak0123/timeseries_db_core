# timeseries_db_core

A robust Python library for managing time-series data with both numeric and categorical measurements. This core database module provides a scalable foundation for storing and retrieving time-series data using PostgreSQL and SQLAlchemy ORM.

## Features

- **Numeric Time Series**: Store and manage numeric measurements with timestamps
- **Categorical Time Series**: Handle discrete categorical values with state mappings
- **Flexible Tagging**: Organize series with JSON-based tags and metadata
- **Timezone Support**: All timestamps include timezone awareness for distributed systems
- **Data Aggregation**: Built-in support for aggregation methods (mean, sum, max, etc.)
- **Efficient Indexing**: Optimized database indexes for fast time-series queries
- **Database Migrations**: Alembic integration for schema versioning and management

## Requirements

- Python >= 3.10
- PostgreSQL database
- SQLAlchemy >= 2.0.0

## Installation

1. **Clone the repository** (or extract the package):
```bash
git clone <repository-url>
cd timeseries_db_core
```

2. **Create a Python virtual environment**:
```bash
python -m venv venv
```

3. **Activate the virtual environment**:
   - On Windows:
   ```bash
   venv\Scripts\activate
   ```
   - On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install the package with dependencies**:
```bash
pip install -e .
```

5. **Install development dependencies** (optional, for testing and linting):
```bash
pip install -e ".[dev]"
```

## Setting Up the Test Database

### 1. Prerequisites

Ensure PostgreSQL is installed and running on your system.

### 2. Create a Database

```bash
psql -U postgres
```

Then in the PostgreSQL prompt:
```sql
CREATE DATABASE timeseries_db;
\q
```

### 3. Configure Environment Variables

Create a `.env` file in the project root with your database connection details:

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/timeseries_db
ECHO_SQL=False
POOL_SIZE=5
MAX_OVERFLOW=10
```

Replace `user` and `password` with your PostgreSQL credentials.

### 4. Verify Database Connection

Test the connection by running a Python script:
```python
from database import DatabaseConfig

engine = DatabaseConfig.get_engine()
print("Database connection successful!")
```

## Running Database Migrations

Database migrations are managed using Alembic. This ensures your schema stays in sync with your models.

### Apply All Pending Migrations

```bash
alembic upgrade head
```

### Create a New Migration

After modifying models, create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

Then review the generated migration file in `alembic/versions/` and apply it:

```bash
alembic upgrade head
```

### Downgrade to Previous Schema Version

```bash
alembic downgrade -1
```

### View Migration History

```bash
alembic current
alembic history
```

## Working with Models

The package provides four main models for managing time-series data:

### 1. SeriesCatalog - Numeric Series Registry

Represents a named numeric time-series that can collect multiple measurement points.

```python
from models import SeriesCatalog
from database import DatabaseConfig

Session = DatabaseConfig.get_session_factory()
session = Session()

# Create a new numeric series
series = SeriesCatalog(
    name="cpu_usage",
    tags={"host": "server1", "location": "datacenter1"},
    description="CPU usage percentage for server1",
    aggregation_method="mean"
)

session.add(series)
session.commit()
```

**Key Attributes:**
- `id`: Primary key (auto-generated)
- `name`: Name of the series (e.g., 'temperature', 'pressure')
- `tags`: JSON metadata for filtering and organization
- `description`: Optional human-readable description
- `aggregation_method`: Data aggregation strategy (e.g., 'mean', 'sum', 'max')
- `created_at`: Timestamp when the series was created

### 2. Measurement - Numeric Data Points

Stores individual numeric measurements for a numeric series.

```python
from models import SeriesCatalog, Measurement
from database import DatabaseConfig
from datetime import datetime, timezone

Session = DatabaseConfig.get_session_factory()
session = Session()

# Get the series
series = session.query(SeriesCatalog).filter_by(name="cpu_usage").first()

# Add measurements
measurement = Measurement(
    timestamp=datetime.now(timezone.utc),
    series_id=series.id,
    value=45.5
)

session.add(measurement)
session.commit()
```

**Key Attributes:**
- `timestamp`: Measurement time with timezone (primary key component)
- `series_id`: Foreign key to SeriesCatalog
- `value`: Numeric (double precision) value
- `series`: Relationship to SeriesCatalog object

### 3. CategoriesCatalog - Categorical Series Registry

Represents a named categorical time-series with discrete value states.

```python
from models import CategoriesCatalog
from database import DatabaseConfig

Session = DatabaseConfig.get_session_factory()
session = Session()

# Create a categorical series
categories = CategoriesCatalog(
    name="server_status",
    tags={"host": "server1"},
    state_mapping={"0": "offline", "1": "online", "2": "error"},
    description="Server operational status"
)

session.add(categories)
session.commit()
```

**Key Attributes:**
- `id`: Primary key (auto-generated)
- `name`: Name of the categorical series
- `tags`: JSON metadata for filtering
- `state_mapping`: JSON mapping of numeric values to state names
- `description`: Optional description
- `created_at`: Creation timestamp

### 4. CategoricalMeasurement - Categorical Data Points

Stores individual categorical measurements for a categorical series.

```python
from models import CategoriesCatalog, CategoricalMeasurement
from database import DatabaseConfig
from datetime import datetime, timezone

Session = DatabaseConfig.get_session_factory()
session = Session()

# Get the categorical series
categories = session.query(CategoriesCatalog).filter_by(
    name="server_status"
).first()

# Add categorical measurements
measurement = CategoricalMeasurement(
    timestamp=datetime.now(timezone.utc),
    series_id=categories.id,
    value=1  # Corresponds to "online" in state_mapping
)

session.add(measurement)
session.commit()
```

**Key Attributes:**
- `timestamp`: Measurement time with timezone (primary key component)
- `series_id`: Foreign key to CategoriesCatalog
- `value`: Numeric state value
- `series`: Relationship to CategoriesCatalog object

## Basic Usage Example

Here's a complete example demonstrating the workflow:

```python
from models import SeriesCatalog, Measurement
from database import DatabaseConfig
from datetime import datetime, timezone, timedelta

# Get database session
SessionLocal = DatabaseConfig.get_session_factory()
session = SessionLocal()

try:
    # 1. Create a numeric series
    series = SeriesCatalog(
        name="temperature",
        tags={"location": "room1", "unit": "celsius"},
        description="Room temperature readings",
        aggregation_method="mean"
    )
    session.add(series)
    session.flush()  # Get the auto-generated ID
    
    # 2. Add measurements
    now = datetime.now(timezone.utc)
    for i in range(10):
        measurement = Measurement(
            timestamp=now - timedelta(minutes=i),
            series_id=series.id,
            value=20.5 + i * 0.1
        )
        session.add(measurement)
    
    # 3. Commit all changes
    session.commit()
    
    # 4. Query the data
    measurements = session.query(Measurement)\
        .filter_by(series_id=series.id)\
        .order_by(Measurement.timestamp.desc())\
        .limit(5)\
        .all()
    
    print(f"Latest 5 measurements:")
    for m in measurements:
        print(f"  {m.timestamp}: {m.value}")

finally:
    session.close()
```

## Database Schema Overview

### series_catalog table
- Stores numeric time-series metadata
- Indexed on: `name`, `id`
- Foreign key relationships: one-to-many with `measurements`

### measurements table
- Stores individual numeric data points
- Primary key: composite of `timestamp` and implicit ordering
- Indexed on: `timestamp`, `series_id`
- Foreign key: `series_id` → `series_catalog.id`

### categories_catalog table
- Stores categorical time-series metadata
- Indexed on: `name`, `id`
- Foreign key relationships: one-to-many with `categorical_measurements`

### categorical_measurements table
- Stores individual categorical data points
- Primary key: composite of `timestamp` and implicit ordering
- Indexed on: `timestamp`, `series_id`
- Foreign key: `series_id` → `categories_catalog.id`

## Code Quality

This project follows the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) conventions.

### Code Linting and Formatting

```bash
# Check code with Ruff
ruff check .

# Format code with Black
black .

# Type checking with mypy
mypy .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=models
```

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running: `psql --version`
- Check `.env` file has correct credentials
- Ensure database exists: `psql -l`

### Migration Errors
- Check migration history: `alembic history`
- View current schema: `alembic current`
- Review migration files in `alembic/versions/`

### Import Errors
- Ensure virtual environment is activated
- Verify package is installed: `pip list | grep timeseries`
- Check Python path: `python -c "import sys; print(sys.path)"`

## License

MIT License - See LICENSE file for details

## Authors

Karol Pilot - [GitHub](https://github.com/lorak0123)

