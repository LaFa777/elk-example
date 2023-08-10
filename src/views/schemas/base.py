# thirdparty
from pydantic import BaseModel, Field


class ErrorResponseSchema(BaseModel):
    code: int
    message: str


class HelloSchema(BaseModel):
    who: str = Field(title='Строка, добавляемая в ответе "Hello {who}!"')
