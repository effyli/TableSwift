from fastapi import Request, Depends
from fastapi_csrf_protect import CsrfProtect

async def validate_csrf_token(
    request: Request,
    csrf_protect: CsrfProtect = Depends()
) -> None:
    """
    Dependency function to validate CSRF token for non-GET requests.
    Skip validation for GET requests as they are considered safe.
    """
    if request.method.upper() != "GET":
        await csrf_protect.validate_csrf(request)
    return None
