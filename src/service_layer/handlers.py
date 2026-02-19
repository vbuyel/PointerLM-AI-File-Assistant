from src.domain.commands import Command
from src.domain.events import Event
from src.domain.model import User, Response
from src.service_layer.unit_of_work import AbstractUnitOfWork
from src.adapters.ai.ai_service import AbstractAIService
from src.adapters.security import PasswordHasher
from src.adapters import ensure

def create_user(create_data: Command.CreateUser, uow: AbstractUnitOfWork):
    with uow:
        hashed_password = PasswordHasher.hash(create_data.password)
        
        user = User(
            username=create_data.username,
            email=create_data.email,
            password=hashed_password
        )
        result = uow.user.add(user)

        if result:
            uow.commit()
    return result

def login_user(login_data: Command.LogInUser, uow: AbstractUnitOfWork):
    with uow:
        user = uow.user.find_by_email(login_data.email)
        if ensure.is_verified_user(user, login_data.password):
            uow.commit()
        else:
            user = None
    return user

def delete_user(delete_data: Command.DeleteUser, uow: AbstractUnitOfWork):
    with uow:
        user = uow.user.find_by_email(delete_data.email)
        result = uow.user.delete(user)
        uow.commit()
    return result

def generate_response(response_data: Command.GenerateResponse, uow: AbstractUnitOfWork, abs_ai_service: AbstractAIService):
    processed_file = "None"
    if response_data.file_path:
        processed_file = abs_ai_service.get_context_from_file(response_data.prompt, response_data.file_path)

    response_text = abs_ai_service.question_answering(response_data.prompt, processed_file)
    
    with uow:
        if response_data.owner_id:
            response = Response(response_text, response_data.owner_id)
            response.generate()
            
            uow.responses.events.extend(response.events)
            responses_amount = uow.responses.count(response_data.owner_id)

            if responses_amount >= 10:
                uow.responses.delete_last(response_data.owner_id)

        uow.commit()

    return response_text

def update_response_database(event: Event.ResponseGenerated, uow: AbstractUnitOfWork):
    with uow:
        result = uow.responses.add(event.response)
        uow.commit()
    return result

def get_user_response_history(cmd: Command.GetResponseHistory, uow: AbstractUnitOfWork):
    with uow:
        result = uow.responses.get_all_for_user(cmd.owner_id)
        uow.commit()
    return result

def clear_current_chat(cmd: Command.ClearChatHistory, abs_ai_service: AbstractAIService):
    abs_ai_service.clear_chat_memory()
    return


HANDLER_EVENTS = {
    Event.ResponseGenerated: [update_response_database]
}

HANDLER_COMMANDS = {
    Command.CreateUser: create_user,
    Command.LogInUser: login_user,
    Command.DeleteUser: delete_user,
    Command.GenerateResponse: generate_response,
    Command.GetResponseHistory: get_user_response_history,
    Command.ClearChatHistory: clear_current_chat,
}
