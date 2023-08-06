from pydantic import BaseModel


class RegisterCore(BaseModel):
    partition: str
    name: str


class RemoveCore(BaseModel):
    urn: str
