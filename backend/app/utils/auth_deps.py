from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from beanie import PydanticObjectId

from app.config import settings
from app.models import User

# OAuth2 scheme looking for 'Authorization: Bearer <token>'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Extracts and verifies JWT token from the Authorization header.
    Returns the authenticated Beanie User document.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    try:
        # Convert to PydanticObjectId for Beanie querying
        oid = PydanticObjectId(user_id)
    except Exception:
        raise credentials_exception

    # Query the user from MongoDB
    user = await User.get(oid)
    if user is None:
        raise credentials_exception
    return user
