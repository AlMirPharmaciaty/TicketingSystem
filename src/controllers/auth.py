from datetime import datetime
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from ..models.user import User
from ..utils.encryption import verify
from ..utils.database import get_db

auth = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = "ansoifnafo8ahwfnasnuiauhyh89rhuioashfuwaghf"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")


def get_user(email: str, db: Session):
    """
    Function to get the active user from db by email
    """
    user = db.query(User).filter(User.email == email, User.deleted == False).first()
    return user


def authenticate_user(email: str, password: str, db: Session):
    """
    Function to authenticate user by email and password
    the given password is verified using md5 encryption
    see utils/encryption
    """
    user = get_user(email=email, db=db)
    if not user:
        return False
    if not verify(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Function to create a JWT token
    - expiry time is set to provided mins from request
    - a data which is user credentials are encrypted
        - by a secret key using HS256 algorithm
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Function to get active user
    a token is retrieved from the client
    and decoded using the same secret key and algorithm as the above function
    then the user credentials are matched with the existing records in the db
    """
    credentials_exception = HTTPException(status_code=401, detail="Invalid credentials")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except InvalidTokenError as e:
        raise credentials_exception from e
    user = get_user(email=user_email, db=db)
    if user is None:
        raise credentials_exception
    return user
