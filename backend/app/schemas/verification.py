from pydantic import BaseModel


class VerificationResult(BaseModel):
    result: str
    certificate_no: str
    student_name: str | None = None
    certificate_hash: str | None = None
    receipt_id: str | None = None
    status: str | None = None
    message: str