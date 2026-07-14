import asyncio

import httpx

from app.main import app


async def get_json(path: str) -> dict:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get(path)

    assert response.status_code == 200
    return response.json()


def test_students_endpoint_returns_mock_students() -> None:
    data = asyncio.run(get_json("/api/students"))

    assert data["code"] == 0
    assert data["data"][0]["student_no"] == "20260001"


def test_certificates_endpoint_returns_required_fields() -> None:
    data = asyncio.run(get_json("/api/certificates"))
    certificate = data["data"][0]

    assert certificate["certificate_no"] == "CERT-20260714-0001"
    assert certificate["student_name"] == "Test Student A"
    assert len(certificate["certificate_hash"]) == 64
    assert certificate["receipt_id"] == "RCPT-20260714-0001"
    assert certificate["status"] == "VALID"


def test_verification_endpoint_returns_pass_result() -> None:
    data = asyncio.run(get_json("/api/verification/CERT-20260714-0001"))

    assert data["code"] == 0
    assert data["data"]["result"] == "PASS"


def test_verification_endpoint_returns_hash_mismatch_result() -> None:
    data = asyncio.run(get_json("/api/verification/CERT-HASH-MISMATCH"))

    assert data["code"] == 0
    assert data["data"]["result"] == "HASH_MISMATCH"
