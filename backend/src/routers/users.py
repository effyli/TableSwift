from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from ..models.user import User, TokenData
from ..services.users import get_all_users, get_user_by_email
from ..dependencies import validate_token
import traceback

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/", response_model=List[User], dependencies=[Depends(validate_token)])
async def list_users():
    """Get all users from the database. Protected by JWT validation."""
    try:
        return get_all_users()
    except Exception as e:
        print(f"Error in list_users: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching users"
        )
    
@router.get("/me", response_model=User)
async def get_user(token_data: TokenData = Depends(validate_token)):
    """Get the current user from the access token."""
    try:
        user = get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except Exception as e:
        print(f"Error in get_user: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user"
        )