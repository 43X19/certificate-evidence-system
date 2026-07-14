from pydantic import BaseModel


class CertificateListItem(BaseModel):
    certificate_id: int
    certificate_no: str
    student_id: int
    student_name: str
    batch_id: str | None = None
    template_id: str | None = None
    pdf_path: str | None = None
    certificate_hash: str | None = None
    qr_code_path: str | None = None
    verify_url: str | None = None
    receipt_id: str | None = None
    status: str
    credential_type: str = "CERTIFICATE"
    root_id: str | None = None