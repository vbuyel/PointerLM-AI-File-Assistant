'''
Entity, Object-Value, Aggregate
'''

from src.domain import events
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# User (Entity/Aggregate)
class User:
    def __init__(self, username: str, email: str, password: str):
        self.id: Optional[str] = None
        self.username = username
        self.email = email
        self.password = password
        self.created_at = datetime.now()
        self.events = []
    
    def signup(self):
        self.events.append(events.Event.UserCreated(self.email, self.password))
    

# Model (Entity/Aggregate)
class Response:
    def __init__(self, text: str, owner_id: int):
        self.id: Optional[int] = None
        self.text = text
        self.owner_id = owner_id
        self.created_at = datetime.now()
        self.events = []

    def generate(self):
        self.events.append(events.Event.ResponseGenerated(self))

# Prompt (Object-Value)
@dataclass
class Prompt:
    text: str
    language: str
