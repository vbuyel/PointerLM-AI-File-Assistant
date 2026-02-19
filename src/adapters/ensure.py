from src.domain.model import User
from src.adapters.security import PasswordHasher
from fastapi import status, HTTPException

class UserIsNotVerified(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password. Try again"
        )

class UserAlreadyExisted(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

class FailedResponse(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="[ERROR 500] Please try later"
        )

class UserSessionIsOut(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

class FailedToDelete(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete chat history"
        )


def is_verified_user(user: User, inputed_password: str):
    if not user or not PasswordHasher.is_verified_password(inputed_password, user.password):
        return False
    return True
