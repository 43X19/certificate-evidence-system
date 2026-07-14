from fastapi import APIRouter

from app.api.routes.certificates import MOCK_CERTIFICATES
from app.core.responses import ApiResponse
from app.schemas.verification import VerificationResult


router = APIRouter(prefix="/verification")


@router.get("/{certificate_no}", response_model=ApiResponse[VerificationResult])
def verify_certificate(certificate_no: str) -> ApiResponse[VerificationResult]:
    certificate = next(
        (
            item
            for item in MOCK_CERTIFICATES
            if item.certificate_no == certificate_no
        ),
        None,
    )

    if certificate_no == "CERT-HASH-MISMATCH":
        return ApiResponse.success(
            VerificationResult(
                result="HASH_MISMATCH",
                certificate_no=certificate_no,
                student_name="Test Student C",
                certificate_hash="c" * 64,
                receipt_id="RCPT-20260714-0003",
                status="VALID",
                message="Certificate exists, but uploaded PDF hash does not match.",
            )
        )

    if certificate is None:
        return ApiResponse.success(
            VerificationResult(
                result="NOT_FOUND",
                certificate_no=certificate_no,
                message="Certificate number does not exist.",
            )
        )

    if certificate.status == "REVOKED":
        return ApiResponse.success(
            VerificationResult(
                result="REVOKED",
                certificate_no=certificate.certificate_no,
                student_name=certificate.student_name,
                certificate_hash=certificate.certificate_hash,
                receipt_id=certificate.receipt_id,
                status=certificate.status,
                message="Certificate has been revoked.",
            )
        )

    return ApiResponse.success(
        VerificationResult(
            result="PASS",
            certificate_no=certificate.certificate_no,
            student_name=certificate.student_name,
            certificate_hash=certificate.certificate_hash,
            receipt_id=certificate.receipt_id,
            status=certificate.status,
            message="Certificate is valid.",
        )
    )