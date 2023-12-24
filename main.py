from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

import functions.logger
from functions.suggest_gift import suggest_gift
from classes.settings import Settings
from classes.user import User, RegisterForm
from functions.db import PostgreSQLController

# Initialize the PostgreSQL database
db = PostgreSQLController(table_definition="""
CREATE TABLE IF NOT EXISTS users (
    key SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    gift_preferences VARCHAR(255) NOT NULL,
    budget INTEGER NOT NULL,
    address VARCHAR(255) NOT NULL,
    gender VARCHAR(255) NOT NULL,
    is_student BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS gifts (
    key SERIAL PRIMARY KEY,
    recipient INTEGER NOT NULL UNIQUE,
    sender INTEGER NOT NULL UNIQUE
);
""")

# Initialize the FastAPI app
app = FastAPI()

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
def login(user: User, authorize: AuthJWT = Depends()):
    """
    Login endpoint for user authentication.
    
    Parameters:
    - user (User): The user object containing the email and password for authentication.
    - authorize (AuthJWT): The instance of the AuthJWT class used for token generation and cookie setting.
    
    Returns:
    - dict: A dictionary containing a success message upon successful login.
    
    Raises:
    - HTTPException: If the email or password is incorrect, a 401 status code with a corresponding detail message is raised.
    """
    query = f"SELECT * FROM users WHERE email = '{user.email}' AND password = '{user.password}'"
    result = db.execute_query(query)

    if len(result) == 0:
        raise HTTPException(status_code=401,detail="Bad email or password or user doesn't exist")

    access_token = authorize.create_access_token(subject=user.email)
    refresh_token = authorize.create_refresh_token(subject=user.email)
    
    authorize.set_refresh_cookies(refresh_token)
    authorize.set_access_cookies(access_token)
    return {"msg":"Successfully login"}

@app.post('/refresh')
def refresh(authorize: AuthJWT = Depends()):
    """
        A function to refresh the access token.

        Parameters:
            authorize (AuthJWT): An instance of the AuthJWT class for JWT authorization.
        
        Returns:
            dict: A dictionary containing a success message.
    """
    authorize.jwt_refresh_token_required()

    current_user = authorize.get_jwt_subject()
    new_access_token = authorize.create_access_token(subject=current_user)
    authorize.set_access_cookies(new_access_token)
    return {"msg":"The token has been refresh"}

@app.post('/logout')
def logout(authorize: AuthJWT = Depends()):
    """
    Logout the user by invalidating their JWT token and removing the token cookies.
    
    Parameters:
        authorize (AuthJWT): An instance of the AuthJWT class that handles JWT authorization.
    
    Returns:
        dict: A dictionary with a success message indicating that the logout was successful.
    """
    authorize.jwt_required()

    authorize.unset_jwt_cookies()
    return {"msg":"Successfully logout"}

@app.get('/protected')
def protected(authorize: AuthJWT = Depends()):
    """
    A decorator to create a route for a protected endpoint.

    Parameters:
    - authorize (AuthJWT): An instance of the AuthJWT class that handles JWT authorization.
    - db (PostgreSQLController): An instance of the PostgreSQLController class to interact with the database.

    Returns:
    - dict: A dictionary containing the user name and other information fetched from the database.
    """
    authorize.jwt_required()

    current_user = authorize.get_jwt_subject()
    query = f"SELECT * FROM users WHERE email = '{current_user}'"
    result = db.execute_query(query)

    if len(result) == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"user": result[0]}

@app.post('/register')
def register(user: RegisterForm, authorize: AuthJWT = Depends()):
    result = db.execute_query(f"SELECT * FROM users WHERE email = '{user.email}'")
    if len(result) > 0:
        raise HTTPException(status_code=401,detail="User already exists")

    register_data = user.dict()

    db.write("users", ", ".join(register_data.keys()), ", ".join([f"'{register_data[key]}'" for key in register_data]))

    access_token = authorize.create_access_token(subject=user.email)
    refresh_token = authorize.create_refresh_token(subject=user.email)

    authorize.set_access_cookies(access_token)
    authorize.set_refresh_cookies(refresh_token)

    # Верни сообщение об успешной регистрации
    return {"msg": "Successfully registered"}

@app.post('/active')
def is_cookies_active(authorize: AuthJWT = Depends()):
    """
    Validates if cookies are active.

    Parameters:
        authorize (AuthJWT): An instance of the AuthJWT class.

    Returns:
        dict: A dictionary with a message indicating if cookies are active.
    """
    authorize.jwt_required()
    return {"msg": "Cookies are active"}

@app.post('/suggest')
async def suggest_gift_handler(authorize: AuthJWT = Depends()):
    """
    A function to suggest a gift based on user preferences and budget.

    Parameters:
    - preferences (str): The user's preferences for the gift.
    - budget (int, optional): The budget for the gift. Defaults to 10.
    - authorize (AuthJWT): An instance of the AuthJWT class that handles JWT authorization.

    Returns:
    - None
    """
    authorize.jwt_required()
    email = authorize.get_jwt_subject()

    gift_preferences = db.execute_query(f"SELECT gift_preferences FROM users WHERE email = '{email}'")
    budget = db.execute_query(f"SELECT budget FROM users WHERE email = '{email}'")

    
    return suggest_gift(preferences=gift_preferences, budget=budget)

@app.delete('/delete')
def delete_account(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    email = authorize.get_jwt_subject()
    db.execute_query(f"DELETE FROM users WHERE email = '{email}'")
    authorize.unset_jwt_cookies()
    return {"msg": "Account deleted"}
