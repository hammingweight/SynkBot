from pydantic import BaseModel, Field


class Power(BaseModel):
    power: int = Field(description="Power in Watts")
    direction: str = Field(description="")
