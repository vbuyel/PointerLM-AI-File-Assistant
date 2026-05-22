from fastapi import status, APIRouter, UploadFile, File, Form, Depends
from typing import Optional
from src.domain.commands import Command
from src.adapters.oauth2 import get_current_user
from src.bootstrap import bus
from src.adapters import ensure
import asyncio
import os


router = APIRouter(
    prefix="/response",
    tags=["responses"]
)


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_response_endpoint(text: str = Form(...), file: Optional[UploadFile] = File(None), current_user = Depends(get_current_user)):
    temp_file_path = None

    try:
        if file:
            content = await file.read()

            temp_file_path = f"temp_{file.filename}"
            with open(temp_file_path, "wb") as f:
                f.write(content)

        if current_user:
            command = Command.GenerateResponse(prompt=text, file_path=temp_file_path, owner_id=current_user.id)
        else:
            command = Command.GenerateResponse(prompt=text, file_path=temp_file_path)
        bus.result.clear()

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, bus.handle, command)
        
    except Exception as e:
        print("[DEBUG] Exception:", e)
        raise ensure.FailedResponse()
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    result = bus.result.pop(-1)
    return {"response": result, "current_user": current_user}


@router.get("/history", status_code=status.HTTP_200_OK)
async def get_response_history_endpoint(current_user=Depends(get_current_user)):
    if current_user is None:
        raise ensure.UserSessionIsOut()

    bus.result.clear()
    command = Command.GetResponseHistory(owner_id=current_user.id)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, bus.handle, command)
    history = bus.result.pop(-1) if bus.result else []
    return {"history": history}

@router.get("/clear_chat", status_code=status.HTTP_200_OK)
async def clear_chat_history():
    command = Command.ClearChatHistory()
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, bus.handle, command)
    except:
        raise ensure.FailedToDelete
    return {"deleted": "successfully"}

