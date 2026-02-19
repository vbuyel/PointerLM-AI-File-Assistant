from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.model import Response, User

class Event:
    @dataclass
    class ResponseGenerated:
        response: 'Response'
    
    @dataclass
    class UserCreated:
        user: 'User'
