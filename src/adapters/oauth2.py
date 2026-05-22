import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from config import settings
from src.service_layer.unit_of_work import SQLAlchemyUnitOfWork

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    data_to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    data_to_encode.update({"exp": expire})

    data_encoded = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return data_encoded


def is_verified_access_token(token: str, credentials_exception):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        id: str = payload.get("id")
        email: str = payload.get("email")
        if id is None or email is None:
            return None

        token_data = id
    except InvalidTokenError:
        return None
    
    return token_data


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    
    user_id = is_verified_access_token(token, credentials_exception)
    if user_id is None:
        return None

    with SQLAlchemyUnitOfWork() as uow:
        user = uow.user.get(user_id)
    return user
