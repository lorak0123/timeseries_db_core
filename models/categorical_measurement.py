"""
CategoricalMeasurement model for categorical time series values in timeseries database.

This module defines the CategoricalMeasurement model which represents a single
categorical measurement point. Each measurement is associated with a categorical
series catalog and has a timestamp and categorical (small integer) value.

Google Python Style Guide conventions are followed throughout.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TIMESTAMP

from .base import Base


class CategoricalMeasurement(Base):
    """Represents a single categorical time-series measurement.

    A categorical measurement is a single discrete (small integer) value associated
    with a specific categorical series at a particular point in time. The value
    typically maps to a state via the state_mapping in the parent CategoriesCatalog.

    Attributes:
        timestamp: The time at which the measurement was taken (with timezone).
        series_id: Foreign key reference to the associated CategoriesCatalog.
        value: The categorical value as a small integer (e.g., 0, 1, 2).
        series: Relationship to the associated CategoriesCatalog object.
    """

    __tablename__ = "categorical_measurements"

    # Time column is part of composite primary key (implicit in time-series context)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, index=True, primary_key=True)
    series_id = Column(Integer, ForeignKey("categories_catalog.id", ondelete="CASCADE"), nullable=False, index=True, primary_key=True)
    value = Column(Integer, nullable=False)  # SMALLINT equivalent

    # Relationships
    series = relationship("CategoriesCatalog", back_populates="measurements")

    # Indexes for efficient time-series queries
    __table_args__ = (
        Index("idx_categorical_time", "timestamp", postgresql_using="btree"),
        Index("idx_categorical_series_id", "series_id"),
    )

    def __repr__(self) -> str:
        """Return string representation of the CategoricalMeasurement."""
        return f"<CategoricalMeasurement(time={self.timestamp}, series_id={self.series_id}, value={self.value})>"
