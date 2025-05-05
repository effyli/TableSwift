from fastapi import Request, HTTPException, status
from uuid import UUID
from ..services.auth import verify_access_token
from ..models.user import TokenData


def validate_token(request: Request) -> TokenData:
    """Validate the access token from the request."""
    try: 
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Verify and decode the token
        data = verify_access_token(token)
        
        # Extract user data from the token payload
        if not data.get("id") or not data.get("email"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token data",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Convert string id back to UUID
        return TokenData(user_id=UUID(data["id"]), email=data["email"])
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )