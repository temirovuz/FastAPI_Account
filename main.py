from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.orm import Session

from scheme import ShowUser, UserLogin
from services import authenticate_user, signJWT, get_current_user, get_db, create_user
from models import Token, User

app = FastAPI()

security = HTTPBearer()


@app.post("/signup")
def signup(user: UserLogin, db: Session = Depends(get_db)):
    return create_user(user=user, db=db)


@app.post("/login")
def user_login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(username=user.username, password=user.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password'
        )
    return signJWT(user.username, db=db)


@app.get("/me")
def user_me(current_user: ShowUser = Depends(get_current_user)):
    return current_user
