from abc import ABC, abstractmethod
from src.adapters import repository
from src.adapters.orm.conn import SessionLocal

class AbstractUnitOfWork(ABC):
    user: repository.AbstractUserRepository
    responses: repository.AbstractResponseRepository

    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.rollback()
    
    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    def collect_all_events(self):
        collected_events = []
        for event in self.user.events:
            collected_events.append(event)
        
        for event in self.responses.events:
            collected_events.append(event)

        self.user.events.clear()
        self.responses.events.clear()
        return collected_events


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        super().__init__()
        self.session = SessionLocal()

    def __enter__(self):
        self.user = repository.SQLAlchemyUserRepository(self.session)
        self.responses = repository.SQLAlchemyResponseRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()
    
    def commit(self):
        self.session.commit()
    
    def rollback(self):
        self.session.rollback()
