from fastapi import Request, HTTPException, status, Depends
from typing import Optional
import jwt 
from datetime import datetime, timedelta
from config import get_settings

settings = get_settings()
ALGORITHM = "HS256"

def get_current_user_id(request: Request) -> int:
    token = request.cookies.get("SocialAppAuth") 
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")