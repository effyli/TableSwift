import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext

from ..database import get_db
from ..config import get_settings
from ..models.user import User


settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)
    

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        content = payload.get("sub")
        if content is None:
            raise InvalidTokenError("Invalid token")
        return content
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Token has expired")
    except jwt.JWTError:
        raise InvalidTokenError("Invalid token")


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    with get_db() as conn:
        result = conn.execute(
            "SELECT id, email, hashed_password FROM users WHERE email = ?",
            [email]
        ).fetchone()
        
        if not result:
            return None
        
        if not verify_password(password, result[2]):
            return None
        
        return User(
            id=result[0],
            email=result[1],
        )
