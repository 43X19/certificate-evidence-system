from pydantic import BaseModel


class StudentListItem(BaseModel):
    student_id: int
    student_no: str
    student_name: str
    college: str | None = None
    class_name: str | None = None
    major_name: str | None = None


class ImportFailure(BaseModel):
    row: int
    reason: str


class ImportResult(BaseModel):
    success_count: int
    failed_count: int
    failures: list[ImportFailure] = []
