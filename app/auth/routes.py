from fastapi import APIRouter, HTTPException, status, Depends , Request
from fastapi.responses import JSONResponse
from jose import jwt,JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth.utils import hash_password, verify_password, create_access_token , create_refresh_token
from app.auth.schemas import UserCreate, UserLogin
import os
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "myrefreshsecretkey")
ALGORITHM = "HS256"

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# --- REGISTER ROUTE ---
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Hash password and include role
    hashed_password = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"msg": f"User '{new_user.username}' created successfully "}


# --- LOGIN ROUTE ---
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=7*24*60*60,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )

    return response




@router.post("/refresh")
def refresh_token(request: Request):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = jwt.decode(
            refresh_token,
            REFRESH_SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        username = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = create_access_token({"sub": username})

    return {"access_token": new_access_token, "token_type": "bearer"}







