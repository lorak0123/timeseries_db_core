"""
Measurement model for numeric time series in timeseries database.

This module defines the Measurement model which represents a single
measurement point in a numeric time-series. Each measurement is associated
with a numeric series catalog and has a timestamp and numeric value.

Google Python Style Guide conventions are followed throughout.
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TIMESTAMP

from .base import Base


class Measurement(Base):
    """Represents a single numeric time-series measurement.

    A measurement is a single numeric value associated with a specific numeric series
    at a particular point in time. The timestamp is stored with timezone awareness
    for accurate distributed system time handling.

    Attributes:
        timestamp: The time at which the measurement was taken (with timezone).
        series_id: Foreign key reference to the associated SeriesCatalog.
        value: The numeric (double precision) value of the measurement.
        series: Relationship to the associated SeriesCatalog object.
    """

    __tablename__ = "measurements"

    # Time column is part of composite primary key (implicit in time-series context)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, index=True, primary_key=True)
    series_id = Column(Integer, ForeignKey("series_catalog.id", ondelete="CASCADE"), nullable=False, index=True, primary_key=True)
    value = Column(Float, nullable=True)

    # Relationships
    series = relationship("SeriesCatalog", back_populates="measurements")

    # Indexes for efficient time-series queries
    __table_args__ = (
        Index("idx_measurements_time", "timestamp", postgresql_using="btree"),
        Index("idx_measurements_series_id", "series_id"),
    )

    def __repr__(self) -> str:
        """Return string representation of the Measurement."""
        return f"<Measurement(time={self.timestamp}, series_id={self.series_id}, value={self.value})>"
