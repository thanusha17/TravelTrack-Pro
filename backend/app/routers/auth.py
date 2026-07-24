from fastapi import APIRouter, HTTPException, status
from app.models import User
from app.schemas import UserRegister, UserLogin, Token, UserOut
from app.utils.auth import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserRegister):
    # Check if the user email is already registered
    existing_user = await User.find_one(User.email == user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Hash the password
    hashed_pwd = get_password_hash(user_data.password)

    # Create new user document
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_pwd,
        home_currency=user_data.home_currency
    )
    await new_user.insert()

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(new_user.id), "email": new_user.email})

    # Return token & user details
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    # Find user by email
    user = await User.find_one(User.email == credentials.email)
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address or password."
        )

    # Verify password hash
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address or password."
        )

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

    # Return token & user details
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
