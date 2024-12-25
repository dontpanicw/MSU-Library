from pydantic import BaseModel


class MaterialAddDTO(BaseModel):
    name: str
    year: int | None = None
    link: str
    is_file: bool = False
    teacher_name: str | None = None
    subject_name: str
    category_name: str
    semester_num: int
