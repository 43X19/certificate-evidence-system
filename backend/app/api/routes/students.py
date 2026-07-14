from fastapi import APIRouter

from app.core.responses import ApiResponse
from app.schemas.student import StudentListItem


router = APIRouter(prefix="/students")


MOCK_STUDENTS = [
    StudentListItem(
        student_id=1,
        student_no="20260001",
        student_name="Test Student A",
        class_name="Training Class 1",
        major_name="Computer Science",
    ),
    StudentListItem(
        student_id=2,
        student_no="20260002",
        student_name="Test Student B",
        class_name="Training Class 1",
        major_name="Computer Science",
    ),
]


@router.get("", response_model=ApiResponse[list[StudentListItem]])
def list_students() -> ApiResponse[list[StudentListItem]]:
    return ApiResponse.success(MOCK_STUDENTS)
