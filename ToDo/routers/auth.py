import sys

sys.path.append('../')

import models

from fastapi import Depends, HTTPException, Request, status, APIRouter
from typing import Optional
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from db import session_local, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates



templates = Jinja2Templates(directory="templates")


SECRET_KEY = 'KgR5DAXPnZU57wivecYC'

ALGORITHM = 'HS256'


class CreateUser(BaseModel):
    
    username : str
    email : Optional[str]
    first_name : str
    last_name : str
    password : str


router = APIRouter(
    prefix='/auth',
    tags=["auth"],
    responses={401: {"User": "Not Authorized."}}
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated='auto')

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='token')


def get_hashed_password(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, 
                        expires_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    encode.update({'exp': expire})
    return  jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if not username or not user_id:
            raise get_user_exception()
        return {"username": username, "user_id": user_id}
    except JWTError:
        raise get_user_exception()



def get_db():
    try:
        db = session_local()
        yield db
    finally:
        db.close()



@router.get("/", response_class=HTMLResponse)
async def authentication_page(request:Request):
    return templates.TemplateResponse("login.html", {"request":request})


@router.get("/register", response_class=HTMLResponse)
async def register(request:Request):
    return templates.TemplateResponse("register.html", {"request":request})


@router.post('/create/user')
async def create_new_user(user: CreateUser, db: Session = Depends(get_db)):

    user_model = models.Users()
    user_model.email = user.email
    user_model.first_name = user.first_name
    user_model.last_name = user.last_name
    user_model.username = user.username
    user_model.hashed_password = get_hashed_password(user.password)
    user_model.is_active = True

    db.add(user_model)
    db.commit()

    return user_model


@router.post('/token')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), 
                                 db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise get_token_exception()
    token_expires = timedelta(minutes=20)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)

    return {'token': token}


# Exceptions
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    return credentials_exception


def get_token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password.",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return token_exception_response
