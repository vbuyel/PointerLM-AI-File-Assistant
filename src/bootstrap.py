from src.service_layer.handlers import HANDLER_EVENTS, HANDLER_COMMANDS
from src.service_layer import messagebus
from src.service_layer.unit_of_work import SQLAlchemyUnitOfWork
from src.adapters.ai.transformers_service import TransformersAIService
import inspect

def bootstrap(
    uow = None,
    abs_ai_service = None
):
    if uow is None:
        uow = SQLAlchemyUnitOfWork()
    if abs_ai_service is None:
        abs_ai_service = TransformersAIService()

    dependencies = {
        "uow": uow,
        "abs_ai_service": abs_ai_service
    }

    injected_events_handler = {
        event_type: [
            injected_dependencies(handler, dependencies)
            for handler in event_handler
        ]
        for event_type, event_handler in HANDLER_EVENTS.items()
    }

    injected_commands_handler = {
        command_type: injected_dependencies(command_handler, dependencies)
        for command_type, command_handler in HANDLER_COMMANDS.items()
    }

    return messagebus.MessageBus(
        uow,
        injected_events_handler,
        injected_commands_handler
    )


def injected_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    args = {
        name: dependency
        for name, dependency in dependencies.items()
        if name in params
    }

    return lambda message: handler(message, **args)

bus = bootstrap()
