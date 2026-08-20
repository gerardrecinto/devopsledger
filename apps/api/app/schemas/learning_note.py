from pydantic import BaseModel, field_validator


class LearningNoteCreate(BaseModel):
    note: str
    author: str | None = None

    @field_validator("note")
    @classmethod
    def _note_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("note cannot be blank")
        return value
