import os
from datetime import datetime, timedelta
from typing import Dict, Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from loguru import logger

load_dotenv()

logger.add("log/auth.log")

SECRET_KEY = os.getenv("GEMINI_SECRET_KEY", "secret key to connect the llm")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# advanced user management with roles
users_db = {
    "user": {"password": "user", "role": "user"},
    "admin": {"password": "admin", "role": "admin"},
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token with optional expiration

    Args:
        data (dict): _description_
        expires_delta (Optional[timedelta], optional): _description_. Defaults to None.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """Verify JWT token and return user info

    Args:
        token (str, optional): _description_. Defaults to Depends(oauth2_scheme).

    Returns:
        Dict: _description_
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"username": username, "role": role}
    except JWTError:
        logger.error("Invalid JWT token attempt")
        raise HTTPException(status_code=401, detail="Invalid token")
