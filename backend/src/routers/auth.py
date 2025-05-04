from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import Response
from typing import Annotated
from ..models.user import UserCreate, User
from ..services.auth import authenticate_user, create_access_token
from ..services.user import create_user
from ..config import get_settings
from ..dependencies import validate_csrf_token
import traceback

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

settings = get_settings()

@router.post("/register", response_model=User, dependencies=[Depends(validate_csrf_token)])
async def register(user_create: UserCreate):
    """Register a new user."""
    try:
        return create_user(user_create)
    except ValueError as e:
        print(f"Error in list_users: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=User, dependencies=[Depends(validate_csrf_token)])
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    response.set_cookie(
        key="access_token",
        value=f"{access_token}",
        httponly=True,
        secure=False, #TODO make true in production
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 12
    )
    
    return user


@router.post("/logout", dependencies=[Depends(validate_csrf_token)])
async def logout(response: Response):
    """Clear the access token cookie."""
    response.delete_cookie(key="access_token", httponly=True, secure=True)
    return {"message": "Logged out successfully"}
