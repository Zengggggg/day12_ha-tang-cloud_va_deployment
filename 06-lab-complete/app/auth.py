import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

# Fixed credentials as requested.
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "vinfast123"


def verify_api_key(credentials: HTTPBasicCredentials = Depends(security)) -> None:
    is_valid_username = secrets.compare_digest(credentials.username, DEFAULT_USERNAME)
    is_valid_password = secrets.compare_digest(credentials.password, DEFAULT_PASSWORD)

    if not (is_valid_username and is_valid_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
