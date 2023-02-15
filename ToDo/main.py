import models

from fastapi import FastAPI, Depends, HTTPException
from db import engine, session_local
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = session_local()
        yield db
    finally:
        db.close()



class ToDo(BaseModel):
    title: str
    description: Optional[str] = Field(max_length=500)
    priority: int = Field(gt=0, lt=6, title="The priority must be between 1-5")
    complete: bool



@app.get('/')
async def get_todos(db: Session = Depends(get_db)):
    return db.query(models.ToDo).all()



@app.get('/todo/{todo_id}')
async def get_todo_by_id(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.ToDo).filter(models.ToDo.id == todo_id).first()
    if todo:
        return todo
    raise HTTPException(status_code=404, detail="ToDo item not found.")



@app.post('/create-todo')
async def create_todo(todo: ToDo, db: Session = Depends(get_db)):
    todo_model = models.ToDo()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    db.add(todo_model)
    db.commit()

    return {
        'status': 201,
        'transaction': 'Successfull',
    }


@app.put('/update-todo/{todo_id}')
async def update_todo(todo_id: int, todo: ToDo, db: Session = Depends(get_db)):
    todo_to_update = db.query(models.ToDo).filter(models.ToDo.id == todo_id).first()
    if not todo_to_update:
        raise HTTPException(status_code=404, detail="ToDo item not found.")
    todo_to_update.title = todo.title 
    todo_to_update.description = todo.description
    todo_to_update.priority = todo.priority
    todo_to_update.complete = todo.complete
    db.add(todo_to_update)
    db.commit()

    return {
        'status': 200,
        'transaction': 'Successfull',
    }



@app.delete('/delete-todo/{todo_id}')
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.ToDo).filter(models.ToDo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with todo_id {todo_id} not found.")
    db.query(models.ToDo).filter(models.ToDo.id == todo_id).delete()
    db.commit()
    
    return {
        'status': 201,
        'transaction': 'Successfull',
    }