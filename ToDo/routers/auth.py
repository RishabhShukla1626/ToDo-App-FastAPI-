import sys



sys.path.append('../')

import models

from fastapi import Depends, HTTPException, Request, status, APIRouter, Response, Form
from typing import Optional
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from db import session_local, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette.responses import RedirectResponse
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


class LoginForm:

    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


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


async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if not token:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if not username or not user_id:
            logout(request)
        return {"username": username, "user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="Not Found")



def get_db():
    try:
        db = session_local()
        yield db
    finally:
        db.close()



@router.get("/", response_class=HTMLResponse)
async def authentication_page(request:Request):
    return templates.TemplateResponse("login.html", {"request":request})


@router.post('/', response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request=request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            message = "Invalid username or password."
            return templates.TemplateResponse("login.html", {"request":request, "message": message})

        return response

    except HTTPException:
        message = "unknown error"
        return templates.TemplateResponse("login.html", {"request": request, "message": message})


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    message = "Logged Out Successfully"
    response = templates.TemplateResponse("login.html", {"request": request, "message": message})
    response.delete_cookie(key="access_token")
    return response


@router.get("/register", response_class=HTMLResponse)
async def register(request:Request):
    return templates.TemplateResponse("register.html", {"request":request})


@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, email: str = Form(...), username: str = Form(...), firstname: str = Form(...),
                   lastname: str = Form(...), password: str = Form(...), password2: str = Form(...),
                   db: Session= Depends(get_db)):
    validation1 = db.query(models.Users).filter(models.Users.username == username).first()

    validation2 = db.query(models.Users).filter(models.Users.email == email).first()

    if password != password2 or validation1 is not None or validation2 is not None:
        message = "Invalid Registration Request."
        return templates.TemplateResponse("register.html", {"request":request, "message": message})

    user_model = models.Users()
    user_model.username = username
    user_model.email = email
    user_model.first_name = firstname
    user_model.last_name = lastname
    user_model.hashed_password = get_hashed_password(password)

    message = "User Created Successfully"

    return templates.TemplateResponse("login.html", {"request":request, "message":message})


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
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):

    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return False
    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)

    response.set_cookie(key="access_token", value=token, httponly=True)

    return True


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
