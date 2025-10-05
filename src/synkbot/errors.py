from pydantic import BaseModel, Field


class Error(BaseModel):
    """
    An error. The action that threw the error should not be retried.
    """

    message: str = Field(description="The reason for the error.")
