"""
SeriesCatalog model for numeric time series in timeseries database.

This module defines the SeriesCatalog model which represents a named numeric
time series that can store multiple measurement points over time. Each series
has optional tags and aggregation method specification.

Google Python Style Guide conventions are followed throughout.
"""

import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .base import Base


class SeriesCatalog(Base):
    """Represents a numeric time-series catalog entry.

    A series catalog is a named entity that can collect multiple numeric measurements
    over time. It can have tags for organization, filtering, and an aggregation method
    for data aggregation operations.

    Attributes:
        id: Unique identifier for the series catalog (primary key).
        name: Name of the numeric series (e.g., 'cpu_usage', 'memory_consumption').
        tags: JSON object containing key-value pairs for metadata tagging.
        description: Optional description of what this series measures.
        aggregation_method: Method for aggregating data ('mean', 'sum', 'max', etc).
        created_at: Timestamp when the series catalog was created.
        measurements: Relationship to associated Measurement objects.
    """

    __tablename__ = "series_catalog"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)
    tags = Column(JSONB, default=[], nullable=False)
    description = Column(Text, nullable=True)
    aggregation_method = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)

    # Relationships
    measurements = relationship("Measurement", back_populates="series", cascade="all, delete-orphan")

    # Indexes for efficient queries
    __table_args__ = (
        Index("idx_series_name", "name"),
    )

    def __repr__(self) -> str:
        """Return string representation of the SeriesCatalog."""
        return f"<SeriesCatalog(id={self.id}, name='{self.name}', aggregation='{self.aggregation_method}')>"
