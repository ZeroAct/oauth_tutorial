from pydantic import BaseModel


class UserInfo(BaseModel):
    name: str
    email: str
