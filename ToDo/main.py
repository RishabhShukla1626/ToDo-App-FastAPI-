import models

from fastapi import FastAPI, Depends
from db import engine
from routers import auth, todos
from companies import companyapis, dependencies
from starlette.staticfiles import StaticFiles



app = FastAPI()


models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(
    companyapis.router,
    prefix="/companyapis",
    tags=["Company APIs"],
    dependencies=[Depends(dependencies.get_token_header)],
    responses={408:{"description": "Internal use only."}}
    )




