from pydantic import BaseModel, Field


class Jobs(BaseModel):
    task: str
    price: int = Field(ge=0)
