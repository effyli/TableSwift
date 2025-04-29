from datetime import datetime, timedelta
from typing import Optional
import uuid
from passlib.context import CryptContext
from jose import JWTError, jwt

from ..database import get_db
from ..config import get_settings
from ..models.user import UserCreate, User, TokenData

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_user(user_create: UserCreate) -> User:
    """Create a new user in the database."""
    with get_db() as conn:
        # Check if user already exists
        result = conn.execute(
            "SELECT email FROM users WHERE email = ?",
            [user_create.email]
        ).fetchone()
        
        if result:
            raise ValueError("Email already registered")
        
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user_create.password)
        
        conn.execute("""
            INSERT INTO users (id, email, hashed_password)
            VALUES (?, ?, ?)
        """, [user_id, user_create.email, hashed_password])
        
        # Fetch the created user
        result = conn.execute(
            "SELECT id, email, created_at FROM users WHERE id = ?",
            [user_id]
        ).fetchone()
        
        return User(
            id=result[0],
            email=result[1],
            created_at=result[2]
        )


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    with get_db() as conn:
        result = conn.execute(
            "SELECT id, email, hashed_password, created_at FROM users WHERE email = ?",
            [email]
        ).fetchone()
        
        if not result:
            return None
        
        if not verify_password(password, result[2]):
            return None
        
        return User(
            id=result[0],
            email=result[1],
            created_at=result[3]
        )


def get_all_users() -> list[User]:
    """Get all users from the database."""
    with get_db() as conn:
        results = conn.execute(
            "SELECT id, email, created_at FROM users"
        ).fetchall()
        
        return [
            User(
                id=result[0],
                email=result[1],
                created_at=result[2]
            )
            for result in results
        ]
