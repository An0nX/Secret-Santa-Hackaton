from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel

"""
Note: This is just a basic example how to enable cookies.
This is vulnerable to CSRF attacks, and should not be used this example.
"""

app = FastAPI()

class User(BaseModel):
    email: str
    password: str

class Settings(BaseModel):
    authjwt_secret_key: str = "secret"
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False

@AuthJWT.load_config
def get_config():
    return Settings()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.post('/login')
def login(user: User, Authorize: AuthJWT = Depends()):
    if user.email != "test" or user.password != "test":
        raise HTTPException(status_code=401,detail="Bad email or password")

    access_token = Authorize.create_access_token(subject=user.email)
    if Authorize._verify_and_get_jwt_in_cookies('refresh', Authorize._request):
        Authorize.unset_jwt_cookies()
    refresh_token = Authorize.create_refresh_token(subject=user.email)

    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)
    return {"msg":"Successfully login"}

@app.post('/refresh')
def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    Authorize.set_access_cookies(new_access_token)
    return {"msg":"The token has been refresh"}

@app.delete('/logout')
def logout(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    Authorize.unset_jwt_cookies()
    return {"msg":"Successfully logout"}

@app.get('/protected')
def protected(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    return {"user": current_user}

@app.post('/register')
def register(user: User, Authorize: AuthJWT = Depends()):
    if user.email == "test":
        raise HTTPException(status_code=401,detail="User already exists")

    access_token = Authorize.create_access_token(subject=user.email)
    refresh_token = Authorize.create_refresh_token(subject=user.email)

    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)

    # Верни сообщение об успешной регистрации
    return {"msg": "Successfully registered"}
