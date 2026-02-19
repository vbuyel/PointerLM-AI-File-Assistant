from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.endpoints import responses, users
from src.adapters.orm.conn import Base
from src.adapters.orm.conn import engine
from src.adapters.orm.tables import ResponseORM, UserORM

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vbuyel.github.io/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(responses.router)

Base.metadata.create_all(bind=engine)
