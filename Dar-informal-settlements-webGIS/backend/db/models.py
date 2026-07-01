"""SQLAlchemy ORM models with GeoAlchemy2 geometry columns."""

from __future__ import annotations

from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Settlement(Base):
    __tablename__ = "settlements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    settlement_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="Settlement")
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    isi_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    area_ha: Mapped[float] = mapped_column(Float, nullable=False)
    population_proxy: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ndbi: Mapped[float | None] = mapped_column(Float)
    ndvi: Mapped[float | None] = mapped_column(Float)
    bsi: Mapped[float | None] = mapped_column(Float)
    fragmentation_index: Mapped[float | None] = mapped_column(Float)
    data_source: Mapped[str | None] = mapped_column(String(64), default="geojson_import")
    geom: Mapped[object] = mapped_column(Geometry("MULTIPOLYGON", srid=4326), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class YearlyMetrics(Base):
    __tablename__ = "yearly_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    total_settlements: Mapped[int] = mapped_column(Integer, default=0)
    total_area_ha: Mapped[float] = mapped_column(Float, default=0.0)
    average_isi: Mapped[float] = mapped_column(Float, default=0.0)
    high_risk_area_ha: Mapped[float] = mapped_column(Float, default=0.0)
    medium_risk_area_ha: Mapped[float] = mapped_column(Float, default=0.0)
    low_risk_area_ha: Mapped[float] = mapped_column(Float, default=0.0)
    high_risk_count: Mapped[int] = mapped_column(Integer, default=0)
    medium_risk_count: Mapped[int] = mapped_column(Integer, default=0)
    low_risk_count: Mapped[int] = mapped_column(Integer, default=0)
    population_proxy_total: Mapped[int] = mapped_column(Integer, default=0)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ChangeDetection(Base):
    __tablename__ = "change_detection"
    __table_args__ = (
        UniqueConstraint("from_year", "to_year", "settlement_id", "change_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_year: Mapped[int] = mapped_column(Integer, nullable=False)
    to_year: Mapped[int] = mapped_column(Integer, nullable=False)
    settlement_id: Mapped[str | None] = mapped_column(String(32))
    to_settlement_id: Mapped[str | None] = mapped_column(String(32))
    name: Mapped[str | None] = mapped_column(String(255))
    change_type: Mapped[str] = mapped_column(String(20), nullable=False)
    isi_score: Mapped[float | None] = mapped_column(Float)
    to_isi_score: Mapped[float | None] = mapped_column(Float)
    area_ha: Mapped[float | None] = mapped_column(Float)
    to_area_ha: Mapped[float | None] = mapped_column(Float)
    area_change_ha: Mapped[float | None] = mapped_column(Float)
    area_change_pct: Mapped[float | None] = mapped_column(Float)
    isi_change: Mapped[float | None] = mapped_column(Float)
    overlap_ratio: Mapped[float | None] = mapped_column(Float)
    population_proxy: Mapped[int | None] = mapped_column(Integer)
    geom: Mapped[object | None] = mapped_column(Geometry("MULTIPOLYGON", srid=4326))
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ImportLog(Base):
    __tablename__ = "import_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    source_file: Mapped[str | None] = mapped_column(String(512))
    features_imported: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="success")
    message: Mapped[str | None] = mapped_column(Text)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
