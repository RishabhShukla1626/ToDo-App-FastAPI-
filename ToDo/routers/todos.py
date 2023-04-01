import sys

sys.path.append("../")

import models

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from db import engine, session_local
from pydantic import BaseModel, Field
from starlette import status
from starlette.responses import RedirectResponse
from typing import Optional
from sqlalchemy.orm import Session
from .auth import get_current_user, get_user_exception
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates



router = APIRouter(
    prefix='/todos',
    tags=["todos"],
    responses={404: {"description": "Not Found."}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")



def get_db():
    try:
        db = session_local()
        yield db
    finally:
        db.close()


@router.get('/', response_class=HTMLResponse)
async def get_all_by_user(request: Request, db: Session = Depends(get_db)):
    todos = db.query(models.ToDo).all()
    return templates.TemplateResponse("home.html", {"request":request, "todos": todos})


@router.get('/add-todo', response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request":request})


@router.post('/add-todo', response_class=HTMLResponse)
async def create_todo(request: Request, title: str = Form(...), description: str = Form(...),
                       priority: int = Form(...), db: Session = Depends(get_db)):
    todo_model = models.ToDo()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = 1
    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo_to_update = db.query(models.ToDo).filter(models.ToDo.id == todo_id).first()
    return templates.TemplateResponse("edit-todo.html", {"request":request, "todo": todo_to_update})


@router.post('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def edit_todo_commit(request: Request, todo_id: int, title: str = Form(...), description: str = Form(...),
                       priority: int = Form(...), db: Session = Depends(get_db)):
    todo_to_update = db.query(models.ToDo).filter(models.ToDo.id == todo_id).first()
    todo_to_update.title = title 
    todo_to_update.description = description
    todo_to_update.priority = priority
    db.add(todo_to_update)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get('/delete/{todo_id}')
async def delete_todo(request: Request, todo_id: int, 
                      db: Session = Depends(get_db)):
     todo = db.query(models.ToDo).filter(models.ToDo.id == todo_id).filter(models.ToDo.owner_id==1).first()
     if not todo:
            return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
     db.query(models.ToDo).filter(models.ToDo.id == todo_id).delete()
     db.commit()

     return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)



@router.get('/complete/{todo_id}', response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int, 
                      db: Session = Depends(get_db)):
    todo = db.query(models.ToDo).filter(models.ToDo.id == todo_id).first()
    todo.complete = not todo.complete
    db.add(todo)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

# @router.put('/update-todo/{todo_id}')
# async def update_todo(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):

#     todo_to_update = db.query(models.ToDo).filter(models.ToDo.id == todo_id).first()
#     if not todo_to_update:
#         raise HTTPException(status_code=404, detail="ToDo item not found.")
#     todo_to_update.title = todo.title 
#     todo_to_update.description = todo.description
#     todo_to_update.priority = todo.priority
#     todo_to_update.complete = todo.complete
#     db.add(todo_to_update)
#     db.commit()

#     return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


# class ToDo(BaseModel):
#     title: str
#     description: Optional[str] = Field(max_length=500)
#     priority: int = Field(gt=0, lt=6, title="The priority must be between 1-5")
#     complete: bool



# @router.get('/')
# async def get_todos(db: Session = Depends(get_db)):
#     return db.query(models.ToDo).all()


# @router.get('/user-todos')
# async def get_all_todos_by_user( user: dict = Depends(get_current_user), 
#                                  db: Session = Depends(get_db)
#                                     ):
#     if user is None:
#         raise get_user_exception()
    
#     return db.query(models.ToDo).filter(models.ToDo.owner_id == user.get("id")).all()



# @router.get('/{todo_id}')
# async def get_todo_by_id(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#     todo = db.query(models.ToDo).filter(models.ToDo.id == todo_id).filter(models.ToDo.owner_id == user.get("id")).first()
#     if todo:
#         return todo
#     raise HTTPException(status_code=404, detail="ToDo item not found.")



# @router.post('/create-todo')
# async def create_todo(todo: ToDo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
    
#     todo_model = models.ToDo()
#     todo_model.title = todo.title
#     todo_model.description = todo.description
#     todo_model.priority = todo.priority
#     todo_model.complete = todo.complete
#     todo_model.owner_id = user.get('id') 
#     db.add(todo_model)
#     db.commit()

#     return {
#         'status': 201,
#         'transaction': 'Successfull',
#     }


# @router.put('/update-todo/{todo_id}')
# async def update_todo(todo_id: int, todo: ToDo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    
#     if user is None:
#         raise get_user_exception()

#     todo_to_update = db.query(models.ToDo).filter(models.ToDo.id == todo_id).filter(models.ToDo.owner_id == user.get("id")).first()
#     if not todo_to_update:
#         raise HTTPException(status_code=404, detail="ToDo item not found.")
#     todo_to_update.title = todo.title 
#     todo_to_update.description = todo.description
#     todo_to_update.priority = todo.priority
#     todo_to_update.complete = todo.complete
#     db.add(todo_to_update)
#     db.commit()

#     return {
#         'status': 200,
#         'transaction': 'Successfull',
#     }



# @router.delete('/delete-todo/{todo_id}')
# async def delete_todo(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#     todo = db.query(models.ToDo).filter(models.ToDo.id == todo_id).filter(models.ToDo.owner_id == user.get("id")).first()
#     if not todo:
#         raise HTTPException(status_code=404, detail=f"Todo with todo_id {todo_id} not found.")
#     db.query(models.ToDo).filter(models.ToDo.id == todo_id).delete()
#     db.commit()
    
#     return {
#         'status': 201,
#         'transaction': 'Successfull',
#     }