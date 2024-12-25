from pydantic import BaseModel


class DocumentOutDTO(BaseModel):
    document_id: int
    name: str
    year: int | None = None
    link: str
    is_file: bool
    subject_name: str
    teacher_name: str | None = None
    category_name: str
    semester_num: int
