from dataclasses import dataclass
from pydantic import EmailStr
from typing import Optional


class Command:
    @dataclass
    class CreateUser:
        username: str
        email: EmailStr
        password: str

    @dataclass
    class LogInUser:
        email: EmailStr
        password: str

    @dataclass
    class DeleteUser:
        email: EmailStr

    @dataclass
    class GenerateResponse:
        prompt: str
        owner_id: Optional[int] = None
        file_path: Optional[str] = None

    @dataclass
    class ProcessFile:
        path: str

    @dataclass
    class GetResponseHistory:
        owner_id: int
    
    @dataclass
    class ClearChatHistory:
        pass
