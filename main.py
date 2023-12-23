from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from classes.user import User, RegisterForm
from functions.suggest_gift import suggest_gift

"""
Note: This is just a basic example how to enable cookies.
This is vulnerable to CSRF attacks, and should not be used this example.
"""

app = FastAPI()

class Settings(BaseModel):
    authjwt_secret_key: str = "secret"
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False

@AuthJWT.load_config
def get_config():
    """
    Load the configuration for the authentication JWT.
    
    Returns:
        Settings: An instance of the Settings class representing the configuration.
    """
    return Settings()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    """
    An exception handler for AuthJWTException.

    Args:
        request (Request): The incoming request object.
        exc (AuthJWTException): The instance of the AuthJWTException that was raised.

    Returns:
        JSONResponse: The JSON response with the appropriate status code and content.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.post('/login')
def login(user: User, Authorize: AuthJWT = Depends()):
    """
    Login endpoint for user authentication.
    
    Parameters:
    - user (User): The user object containing the email and password for authentication.
    - Authorize (AuthJWT): The instance of the AuthJWT class used for token generation and cookie setting.
    
    Returns:
    - dict: A dictionary containing a success message upon successful login.
    
    Raises:
    - HTTPException: If the email or password is incorrect, a 401 status code with a corresponding detail message is raised.
    """
    if user.email != "test" or user.password != "test":
        raise HTTPException(status_code=401,detail="Bad email or password")

    access_token = Authorize.create_access_token(subject=user.email)
    refresh_token = Authorize.create_refresh_token(subject=user.email)
    
    Authorize.set_refresh_cookies(refresh_token)
    Authorize.set_access_cookies(access_token)
    return {"msg":"Successfully login"}

@app.post('/refresh')
def refresh(Authorize: AuthJWT = Depends()):
    """
        A function to refresh the access token.

        Parameters:
            Authorize (AuthJWT): An instance of the AuthJWT class for JWT authorization.
        
        Returns:
            dict: A dictionary containing a success message.
    """
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    Authorize.set_access_cookies(new_access_token)
    return {"msg":"The token has been refresh"}

@app.delete('/logout')
def logout(Authorize: AuthJWT = Depends()):
    """
    Logout the user by invalidating their JWT token and removing the token cookies.
    
    Parameters:
        Authorize (AuthJWT): An instance of the AuthJWT class that handles JWT authorization.
    
    Returns:
        dict: A dictionary with a success message indicating that the logout was successful.
    """
    Authorize.jwt_required()

    Authorize.unset_jwt_cookies()
    return {"msg":"Successfully logout"}

@app.get('/protected')
def protected(Authorize: AuthJWT = Depends()):
    """
    A decorator to create a route for a protected endpoint.

    Parameters:
    - Authorize (AuthJWT): An instance of the AuthJWT class that handles JWT authorization.

    Returns:
    - dict: A dictionary containing the user name of the current user.
    """
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    return {"user": current_user}

@app.post('/register')
def register(user: RegisterForm, Authorize: AuthJWT = Depends()):
    if user.email == "test":
        raise HTTPException(status_code=401,detail="User already exists")

    register_data = user.dict()

    access_token = Authorize.create_access_token(subject=user.email)
    refresh_token = Authorize.create_refresh_token(subject=user.email)

    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)

    # Верни сообщение об успешной регистрации
    return {"msg": "Successfully registered"}

@app.post('/active')
def is_cookies_active(Authorize: AuthJWT = Depends()):
    """
    Validates if cookies are active.

    Parameters:
        Authorize (AuthJWT): An instance of the AuthJWT class.

    Returns:
        dict: A dictionary with a message indicating if cookies are active.
    """
    Authorize.jwt_required()
    return {"msg": "Cookies are active"}

@app.post('/suggest')
def suggest_gift_handler(Authorize: AuthJWT = Depends()):
    """
    A function to suggest a gift based on user preferences and budget.

    Parameters:
    - preferences (str): The user's preferences for the gift.
    - budget (int, optional): The budget for the gift. Defaults to 10.
    - Authorize (AuthJWT): An instance of the AuthJWT class that handles JWT authorization.

    Returns:
    - None
    """
    preferences = 'cooking food'
    budget = 10

    Authorize.jwt_required()
    return suggest_gift(preferences=preferences, budget=budget)
