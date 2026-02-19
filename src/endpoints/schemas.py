from pydantic import BaseModel, EmailStr
from fastapi import UploadFile
from typing import Optional


class User:
    class SignUp(BaseModel):
        username: str
        email: EmailStr
        password: str

class Request:
    class WithFile:
        text: str
        file: Optional[UploadFile] = None
