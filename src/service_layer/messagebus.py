from src.domain import commands, events
from src.service_layer.unit_of_work import AbstractUnitOfWork
from typing import Union, Dict, List, Type, Callable

Message = Union[commands.Command, events.Event]

class MessageBus:
    def __init__(self,
        uow: AbstractUnitOfWork,
        handler_events: Dict[Type[events.Event], List[Callable]],
        handler_commands: Dict[Type[commands.Command], Callable]
    ):
        self.uow = uow
        self.handler_events = handler_events
        self.handler_commands = handler_commands
        self.query = []
        self.result = []

    def handle(self, message: Message):
        self.query.append(message)

        while self.query:
            message = self.query.pop(0)

            if type(message) in self.handler_events:
                self.handle_event(message)
            elif type(message) in self.handler_commands:
                self.handle_command(message)
            else:
                raise Exception(f"{message} was not an Event or Command")


    def handle_event(self, event: events.Event):
        try:
            handlers = self.handler_events[type(event)]
            for handler in handlers:
                handler(event)
            self.query.extend(self.uow.collect_all_events())
        except Exception as e:
            raise Exception(f"Error handling event {event}: {str(e)}")
    

    def handle_command(self, command: commands.Command):
        try:
            handler = self.handler_commands[type(command)]
            result = handler(command)
            
            self.result.append(result)
            self.query.extend(self.uow.collect_all_events())

        except Exception as e:
            raise Exception(f"Error handling command {command}: {str(e)}")
