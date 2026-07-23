import asyncio

import httpx
from pwdlib import PasswordHash

from app.main import app
from app.models.student import Student
from app.models.user import User


async def request(method: str, path: str, **kwargs) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.request(method, path, **kwargs)


def login_headers(username: str, password: str) -> dict[str, str]:
    response = asyncio.run(request("POST", "/api/auth/login", json={"username": username, "password": password}))
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['token']}"}


def test_admin_can_provision_reset_and_revoke_student_account_sessions(db_session) -> None:
    admin_password = "administrator-test-password"
    admin = User(
        username="account-admin",
        display_name="Account Admin",
        password_hash=PasswordHash.recommended().hash(admin_password),
        role="ADMIN",
    )
    student = Student(student_no="S20269999", student_name="测试学生")
    db_session.add_all([admin, student])
    db_session.commit()
    admin_headers = login_headers(admin.username, admin_password)

    provisioned = asyncio.run(
        request(
            "POST",
            "/api/admin/students/accounts/provision",
            headers=admin_headers,
            json={"student_ids": [student.student_id]},
        )
    )
    assert provisioned.status_code == 200
    credential = provisioned.json()["data"]["created"][0]
    assert credential["student_no"] == student.student_no
    assert credential["initial_password"]

    student_login = asyncio.run(
        request(
            "POST",
            "/api/auth/login",
            json={"username": student.student_no, "password": credential["initial_password"]},
        )
    )
    assert student_login.status_code == 200
    assert student_login.json()["data"]["role"] == "STUDENT"
    assert student_login.json()["data"]["must_change_password"] is True
    student_headers = {"Authorization": f"Bearer {student_login.json()['data']['token']}"}
    assert asyncio.run(request("GET", "/api/student/certificates", headers=student_headers)).status_code == 403

    changed = asyncio.run(
        request(
            "POST",
            "/api/auth/change-password",
            headers=student_headers,
            json={"current_password": credential["initial_password"], "new_password": "student-new-password"},
        )
    )
    assert changed.status_code == 200
    assert asyncio.run(request("GET", "/api/student/certificates", headers=student_headers)).status_code == 200

    reset = asyncio.run(
        request(
            "POST",
            f"/api/admin/students/{student.student_id}/account/reset-password",
            headers=admin_headers,
        )
    )
    assert reset.status_code == 200
    assert asyncio.run(request("GET", "/api/student/certificates", headers=student_headers)).status_code == 401

    repeated = asyncio.run(
        request(
            "POST",
            "/api/admin/students/accounts/provision",
            headers=admin_headers,
            json={"student_ids": [student.student_id]},
        )
    )
    assert repeated.status_code == 200
    assert repeated.json()["data"]["created"] == []
    assert repeated.json()["data"]["skipped"][0]["reason"] == "学生账号已开通"


def test_first_password_change_revokes_other_initial_password_sessions(db_session) -> None:
    admin_password = "administrator-test-password"
    admin = User(
        username="session-admin",
        display_name="Session Admin",
        password_hash=PasswordHash.recommended().hash(admin_password),
        role="ADMIN",
    )
    student = Student(student_no="S20268888", student_name="会话测试学生")
    db_session.add_all([admin, student])
    db_session.commit()

    provisioned = asyncio.run(
        request(
            "POST",
            "/api/admin/students/accounts/provision",
            headers=login_headers(admin.username, admin_password),
            json={"student_ids": [student.student_id]},
        )
    )
    initial_password = provisioned.json()["data"]["created"][0]["initial_password"]
    first_session = login_headers(student.student_no, initial_password)
    other_session = login_headers(student.student_no, initial_password)

    changed = asyncio.run(
        request(
            "POST",
            "/api/auth/change-password",
            headers=first_session,
            json={"current_password": initial_password, "new_password": "student-new-password"},
        )
    )
    assert changed.status_code == 200
    assert asyncio.run(request("GET", "/api/student/certificates", headers=first_session)).status_code == 200
    assert asyncio.run(request("GET", "/api/student/certificates", headers=other_session)).status_code == 401


def test_teacher_cannot_distribute_student_initial_passwords(db_session) -> None:
    teacher_password = "teacher-test-password"
    teacher = User(
        username="student-account-teacher",
        display_name="Student Account Teacher",
        password_hash=PasswordHash.recommended().hash(teacher_password),
        role="TEACHER",
    )
    student = Student(student_no="S20267777", student_name="权限测试学生")
    db_session.add_all([teacher, student])
    db_session.commit()

    response = asyncio.run(
        request(
            "POST",
            "/api/admin/students/accounts/provision",
            headers=login_headers(teacher.username, teacher_password),
            json={"student_ids": [student.student_id]},
        )
    )
    assert response.status_code == 403
    assert db_session.query(User).filter(User.student_id == student.student_id).one_or_none() is None


def test_account_bound_student_cannot_change_student_no_or_be_deleted(db_session) -> None:
    student = Student(student_no="S20266666", student_name="绑定测试学生")
    db_session.add(student)
    db_session.commit()
    db_session.add(
        User(
            username=student.student_no,
            display_name=student.student_name,
            password_hash=PasswordHash.recommended().hash("student-test-password"),
            role="STUDENT",
            student_id=student.student_id,
            must_change_password=True,
        )
    )
    db_session.commit()
    admin_headers = {"Authorization": "Bearer demo-admin-token"}

    changed_no = asyncio.run(
        request(
            "PUT",
            f"/api/admin/students/{student.student_id}",
            headers=admin_headers,
            json={"student_no": "S20260000"},
        )
    )
    deleted = asyncio.run(
        request("DELETE", f"/api/admin/students/{student.student_id}", headers=admin_headers)
    )

    assert changed_no.status_code == 409
    assert deleted.status_code == 409
    assert db_session.get(Student, student.student_id).student_no == "S20266666"
