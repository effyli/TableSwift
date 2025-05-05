import uuid
from typing import Optional
from ..database import get_db
from ..config import get_settings
from ..models.user import UserCreate, User
from .auth import get_password_hash


settings = get_settings()


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
        user_id = uuid.uuid4()
        hashed_password = get_password_hash(user_create.password)
        
        conn.execute("""
            INSERT INTO users (id, email, hashed_password)
            VALUES (?, ?, ?)
        """, [user_id, user_create.email, hashed_password])
        
        # Fetch the created user
        result = conn.execute(
            "SELECT id, email FROM users WHERE id = ?",
            [user_id]
        ).fetchone()
        
        return User(
            id=result[0],
            email=result[1],
        )
    

def get_all_users() -> list[User]:
    """Get all users from the database."""
    with get_db() as conn:
        results = conn.execute(
            "SELECT id, email FROM users"
        ).fetchall()
        
        return [
            User(
                id=result[0],
                email=result[1],
            )
            for result in results
        ]
    

def get_user_by_email(email: str) -> Optional[User]:
    """Get a user by email."""
    with get_db() as conn:
        result = conn.execute(
            "SELECT id, email FROM users WHERE email = ?",
            [email]
        ).fetchone()
        
        if not result:
            return None
        
        return User(
            id=result[0],
            email=result[1],
        )