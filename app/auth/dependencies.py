from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth.utils import SECRET_KEY, ALGORITHM

# Token source (login endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Extract and return the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exception

    return user






# --- Role-based dependencies --- #
def get_current_organizer(current_user: User = Depends(get_current_user)):
    """Allow only users with role='organizer'."""
    if current_user.role != "organizer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to event organizers only."
        )
    return current_user


def get_current_customer(current_user: User = Depends(get_current_user)):
    """Allow only users with role='customer'."""
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to customers only."
        )
    return current_user
