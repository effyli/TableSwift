from fastapi import Request, HTTPException, status
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
        user_email = verify_access_token(token)
        return TokenData(email=user_email)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )