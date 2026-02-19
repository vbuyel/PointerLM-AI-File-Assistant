from abc import ABC, abstractmethod
from src.domain.model import User, Response
from typing import Optional
from src.adapters.orm.tables import UserORM, ResponseORM
from sqlalchemy import desc


class AbstractUserRepository(ABC):
    def __init__(self):
        self.events = []

    @abstractmethod
    def add(self, user: User) -> User:
        pass

    @abstractmethod
    def get(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def delete(self, user_id: int):
        pass


class SQLAlchemyUserRepository(AbstractUserRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session
    
    def _to_domain(self, orm_user: UserORM):
        user = User(
            username=orm_user.username,
            email=orm_user.email,
            password=orm_user.password
        )
        user.id = orm_user.id
        user.created_at = orm_user.created_at
        return user
    
    def _to_orm(self, user: User):
        return UserORM(
            id=user.id,
            username=user.username,
            email=user.email,
            password=user.password,
            created_at=user.created_at
        )

    def add(self, user: User) -> User:
        self.events.extend(user.events)

        try:
            user_orm = UserORM(
                username=user.username,
                email=user.email,
                password=user.password
            )
            self.session.add(user_orm)

            self.session.commit()
            self.session.refresh(user_orm)
            
            user.id = user_orm.id
            user.created_at = user_orm.created_at
            return self._to_domain(user_orm)
        except Exception:
            self.session.rollback()
            return None
    
    def get(self, user_id: int) -> Optional[User]:
        orm_user = self.session.query(UserORM).filter_by(id=user_id).first()
        return self._to_domain(orm_user) if orm_user else None
    
    def find_by_email(self, user_email: str) -> Optional[User]:
        orm_user = self.session.query(UserORM).filter_by(email = user_email).first()
        return self._to_domain(orm_user) if orm_user else None
    
    def delete(self, user: User):
        orm_user = self._to_orm(user)
        user = self.session.query(UserORM).filter_by(id=orm_user.id).first()
        self.session.delete(user)
        self.session.commit()



class AbstractResponseRepository(ABC):
    def __init__(self):
        self.events = []

    @abstractmethod
    def add(self, response: Response) -> str:
        pass

    @abstractmethod
    def get(self, text_id: int) -> Optional[Response]:
        pass

    @abstractmethod
    def get_all_for_user(self, owner_id: int):
        pass

    @abstractmethod
    def count(self, owner_id: int) -> int:
        pass

    @abstractmethod
    def delete_last(self, owner_id: int):
        pass


class SQLAlchemyResponseRepository(AbstractResponseRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session
    
    def _to_domain(self, orm_response: ResponseORM) -> Response:
        """ORM -> Domain"""
        response = Response(
            text=orm_response.response_text,
            owner_id=orm_response.owner_id
        )
        response.id = orm_response.id
        response.created_at = orm_response.created_at
        return response
    
    def _to_orm(self, response: Response) -> ResponseORM:
        """Domain -> ORM"""
        return ResponseORM(
            id=response.id,
            response_text=response.text,
            owner_id=response.owner_id,
            created_at=response.created_at
        )
    
    def _delete(self, response_id: int):
        self.session.query(ResponseORM).filter_by(id = response_id).delete()
        self.session.commit()

    def add(self, response: Response) -> str:

        response_orm = ResponseORM(
            response_text=response.text,
            owner_id=response.owner_id
        )
        self.session.add(response_orm)
        self.session.commit()
        self.session.refresh(response_orm)
        
        response.id = response_orm.id
        response.created_at = response_orm.created_at
        return response.text
    
    def get(self, text_id: int) -> Optional[Response]:
        orm_response = self.session.query(ResponseORM).filter_by(id=text_id).first()
        return self._to_domain(orm_response) if orm_response else None
    
    def get_all_for_user(self, owner_id: int):
        response = self.session.query(ResponseORM).filter_by(owner_id=owner_id).order_by(desc(ResponseORM.created_at)).all()
        return [self._to_domain(orm_response).text for orm_response in response]

    def count(self, owner_id: int) -> int:
        return self.session.query(ResponseORM).filter_by(owner_id = owner_id).count()
    
    def delete_last(self, owner_id: int):
        last_response = self.session.query(ResponseORM).filter_by(owner_id = owner_id).order_by(ResponseORM.created_at).first()
        self._delete(last_response.id)
        self.session.commit()
