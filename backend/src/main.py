from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from fastapi.responses import JSONResponse
import traceback

from .config import get_settings
from .routers import auth, users

app = FastAPI()

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-CSRF-Token",
    ],
    expose_headers=[
        "Content-Type",
        "Authorization",
        "X-CSRF-Token",
    ],
)

# include your routers
app.include_router(auth.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/csrf-token")
async def get_csrf_token(csrf_protect: CsrfProtect = Depends()):
    """Generate and set CSRF token in cookie."""
    try:
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = JSONResponse(
            status_code=200,
            content={"message": "CSRF token set successfully"}
        )
        response.set_cookie(
            key="csrf_access_token",
            value=csrf_token,
            secure=False,
            samesite="lax"
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response
    except Exception as e:
        print(f"Error in get_csrf_token: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Failed to generate CSRF token"
        )


@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})