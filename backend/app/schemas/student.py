from pydantic import BaseModel


class StudentListItem(BaseModel):
    student_id: int
    student_no: str
    student_name: str
    class_name: str | None = None
    major_name: str | None = None
