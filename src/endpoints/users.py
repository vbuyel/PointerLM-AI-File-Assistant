from fastapi import status, APIRouter, Depends, Body
from src.endpoints.schemas import User
from src.domain.commands import Command
from fastapi.security import OAuth2PasswordRequestForm
from src.adapters.oauth2 import create_access_token
from src.adapters.oauth2 import get_current_user
from src.bootstrap import bus
from src.adapters import ensure
import asyncio

router = APIRouter(
    prefix="/user",
    tags=["users"]
)


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup_user_endpoint(user: User.SignUp = Body(...)):
    command = Command.CreateUser(**user.model_dump())

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, bus.handle, command)

    user = bus.result.pop(-1)

    if user:
        access_token = create_access_token({"id": user.id, "email": user.email})
        return {'access_token': access_token, 'token_type': 'Bearer'}
    else:
        raise ensure.UserAlreadyExisted()

@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user_endpoint(inputed_data: OAuth2PasswordRequestForm = Depends()):
    command = Command.LogInUser(inputed_data.username, inputed_data.password)

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, bus.handle, command)

    user = bus.result.pop(-1)

    if user:
        access_token = create_access_token({"id": user.id, "email": user.email})
        return {'access_token': access_token, 'token_type': 'Bearer'}
    else:
        raise ensure.UserIsNotVerified()

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(current_user=Depends(get_current_user)):
    if current_user is None:
        raise ensure.UserSessionIsOut()

    command = Command.DeleteUser(current_user.email)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, bus.handle, command)
    return bus.result

@router.get("/info", status_code=status.HTTP_200_OK)
async def get_user_info(current_user=Depends(get_current_user)):
    if current_user is None:
        raise ensure.UserSessionIsOut
    
    return current_user
