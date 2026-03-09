"""
CategoriesCatalog model for categorical time series in timeseries database.

This module defines the CategoriesCatalog model which represents a named categorical
time series that can store multiple categorical measurement values over time. Each
series has optional tags and state mapping for human-readable value interpretation.

Google Python Style Guide conventions are followed throughout.
"""

import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .base import Base


class CategoriesCatalog(Base):
    """Represents a categorical time-series catalog entry.

    A categorical series catalog is a named entity that can collect multiple categorical
    (discrete) measurements over time. It can have tags for organization and a state mapping
    to provide human-readable interpretations of numeric values.

    Attributes:
        id: Unique identifier for the categories catalog (primary key).
        name: Name of the categorical series (e.g., 'server_status', 'device_mode').
        tags: JSON object containing key-value pairs for metadata tagging.
        state_mapping: JSON object mapping numeric values to state descriptions
            (e.g., {0: "OFF", 1: "ON", 2: "ERROR"}).
        description: Optional description of what this categorical series represents.
        created_at: Timestamp when the categories catalog was created.
        measurements: Relationship to associated CategoricalMeasurement objects.
    """

    __tablename__ = "categories_catalog"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)
    tags = Column(JSONB, default=[], nullable=False)
    state_mapping = Column(JSONB, default={}, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)

    # Relationships
    measurements = relationship("CategoricalMeasurement", back_populates="series", cascade="all, delete-orphan")

    # Indexes for efficient queries
    __table_args__ = (
        Index("idx_categories_name", "name"),
    )

    def __repr__(self) -> str:
        """Return string representation of the CategoriesCatalog."""
        return f"<CategoriesCatalog(id={self.id}, name='{self.name}')>"
