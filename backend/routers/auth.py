from fastapi import APIRouter, Response, HTTPException, Depends, status
from schemas import AccountLoginDto, AccountRegistrationDto
from repositories.account_repo import AccountRepository
from security import verify_password, get_password_hash, sanitize_html
import jwt
from datetime import datetime, timedelta, timezone
from config import get_settings

router = APIRouter(prefix="/api/auth", tags=["Auth"])
repo = AccountRepository()

settings = get_settings()

@router.post("/login")
async def login(response: Response, login_data: AccountLoginDto):
    user = await repo.get_by_username(login_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials!")

    if not verify_password(login_data.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials!")

    access_token_expires = timedelta(minutes=120)
    claims = {
        "sub": str(user['id']), 
        "name": user['username'], 
        "email": user['email']
    }
    claims.update({"exp": datetime.now(timezone.utc) + access_token_expires})
    
    token = jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm="HS256")

    response.set_cookie(
        key="SocialAppAuth", 
        value=token, 
        httponly=True,
        max_age=120 * 60,
        samesite="lax"
    )
    
    return {
        "message": "Login successful",
        "user": {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "full_name": user['full_name'],
            "phone_number": user['phone_number'],
            "date_of_birth": user['date_of_birth'],
            "date_of_create": user['date_of_create'],
            "profile_picture": user['profile_picture'],
            "follower_count": user['follower_count'],
            "following_count": user['following_count'],
        }
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("SocialAppAuth")
    return {"message": "Logout successful"}


@router.post("/register", status_code=201)
async def register(reg_data: AccountRegistrationDto):
    existing = await repo.get_by_username(reg_data.username)
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken!")

    safe_username = sanitize_html(reg_data.username)
    safe_email = sanitize_html(reg_data.email)

    hashed_pw = get_password_hash(reg_data.password)    
    new_id = await repo.create_account(safe_username, safe_email, hashed_pw)
    
    return {"message": "Registration successful", "accountId": new_id}