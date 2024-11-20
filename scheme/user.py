import uuid
from typing import Optional

from pydantic import BaseModel


class UserInfo(BaseModel):
    id: str = str(uuid.uuid4())
    platform: str
    name: str
    email: str
    image: Optional[str] = None
