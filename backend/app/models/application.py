import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    vendor: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    app_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )
    annual_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    cost_per_license: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_licenses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active_users: Mapped[int | None] = mapped_column(Integer, nullable=True)
    adoption_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_login_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    contract_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    contract_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    data_source: Mapped[str] = mapped_column(
        String(100), nullable=False, default="manual"
    )
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    compliance_status: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], lazy="selectin")
    recommendations = relationship(
        "Recommendation", back_populates="application", cascade="all, delete-orphan"
    )
    decisions = relationship(
        "Decision", back_populates="application", cascade="all, delete-orphan"
    )
    submissions = relationship(
        "Submission",
        back_populates="matched_application",
        foreign_keys="Submission.matched_application_id",
    )
