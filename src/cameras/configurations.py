from pydantic import BaseModel, field_validator


class Configurations(BaseModel):
    id: int
    sensitivity: float
    recording: bool

    @field_validator("sensitivity")
    @classmethod
    def sensitivity(cls, sensitivity: float) -> float:
        if not 0 <= sensitivity <= 1:
            raise Exception("Sensitivity must be a number between 0 and 1")

        return sensitivity
