from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CertificateStatus(str, Enum):
    VALID = "VALID"
    REVOKED = "REVOKED"


class Certificate(Base):
    __tablename__ = "certificates"

    certificate_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    certificate_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.student_id"))
    student_name: Mapped[str] = mapped_column(String(64))
    batch_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    template_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    certificate_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    qr_code_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verify_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    receipt_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default=CertificateStatus.VALID.value)
    credential_type: Mapped[str] = mapped_column(String(32), default="CERTIFICATE")
    root_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)