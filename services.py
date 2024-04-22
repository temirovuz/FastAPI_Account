import os
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from db import SessionLocal
from hashing import Hasher
from models import User, Token

SECRET_KEY = '2d2bff71da1410bba67dd68834a285f333e047882f7f31fd'
ALGORITHM = 'HS256'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def token_response(token: str):
    return {
        "access_token": token,
        "token_type": "Bearer"
    }


def signJWT(user_id: int, db: Session = Depends(get_db)):
    u_id = get_user(user_id, db)
    get_token_user = get_token(user_id=u_id, db=db)
    if get_token_user:
        return token_response(get_token_user.token)
    else:
        payload = {
            "user_id": user_id,
            "expires": time.time() + 3600
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        if get_token_user:
            get_token_user.token = token
            db.commit()
            db.refresh(get_token_user)
            return token_response(token)
        else:
            token_ = Token(token=token, user_id=u_id.id)
            db.add(token_)
            db.commit()
            db.refresh(token_)
            return token_response(token)


def create_user(user: User, db: Session = Depends(get_db)) -> object:
    user = User(username=user.username,
                password=Hasher.get_password_hash(user.password),
                is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    payload = {
        "user_id": user.id,
        "expires": time.time() + 3600
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    t = Token(token=token, user_id=user.id)
    db.add(t)
    db.commit()
    db.refresh(t)
    return user


def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return user


def get_token(user_id: int, db: Session = Depends(get_db)):
    token = db.query(Token).filter(Token.user_id == user_id).first()
    return token


def authenticate_user(user_id: int, password: str, db: Session = Depends(get_db)):
    user = get_user(user_id, db)
    if not user:
        return False
    if not Hasher.verify_password(password, user.password):
        return False
    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user = db.query(User).filter(User.id == decoded_token.get('user_id')).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user
