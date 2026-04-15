from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response, status
from typing import List, Optional, Union
from dependencies import get_current_user_id
from repositories.account_repo import AccountRepository
from schemas import AccountPublicDto, AccountPrivateDto
from security import sanitize_html
from services.recommender_instance import recommender_inst

router = APIRouter(prefix="/api/users", tags=["Users"])
repo = AccountRepository()
recommender = recommender_inst



@router.get("/interests")
async def get_user_interests(current_user_id: int = Depends(get_current_user_id)):
    user_profiles = await recommender._get_user_profiles_cached()
    return user_profiles.get(current_user_id, {})


@router.get("", response_model=List[AccountPublicDto])
async def get_all_users():
    return await repo.get_all()


@router.get("/{id}", response_model=Union[AccountPrivateDto, AccountPublicDto])
async def get_user_by_id(id: int, current_user_id: int = Depends(get_current_user_id)):
    account = await repo.get_by_id(id)
    if not account:
        raise HTTPException(status_code=404, detail="User not found")

    is_owner = id == current_user_id
    base_data = {
        "id": account['id'],
        "username": account['username'],
        "email": account['email'],
        "full_name": account['full_name'],
        "date_of_create": account['date_of_create'],
        "profile_picture": account['profile_picture'],
        "follower_count": account['follower_count'],
        "following_count": account['following_count']
    }

    if is_owner:
        return AccountPrivateDto(
            **base_data,
            phone_number=account['phone_number'],
            date_of_birth=account['date_of_birth']
        )

    return AccountPublicDto(**base_data)


@router.put("/{id}")
async def update_profile(
    id: int,
    email: Optional[str] = Form(None),
    full_name: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    date_of_birth: Optional[str] = Form(None),
    profile_picture_file: Optional[UploadFile] = File(None),
    current_user_id: int = Depends(get_current_user_id)
):
    # Auth check
    if id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    profile_picture_data = None
    if profile_picture_file:
        if profile_picture_file.size > 5242880: # 5 MB limit
             raise HTTPException(status_code=400, detail="Profile picture size exceeds limit.")
        profile_picture_data = await profile_picture_file.read()

    sanitized_email = sanitize_html(email) if email else None
    sanitized_full_name = sanitize_html(full_name) if full_name else None
    sanitized_phone = sanitize_html(phone_number) if phone_number else None
    sanitized_dob = sanitize_html(date_of_birth) if date_of_birth else None

    success = await repo.update_account(
        id, 
        sanitized_email, 
        sanitized_full_name, 
        sanitized_phone, 
        sanitized_dob, 
        profile_picture_data
    )

    if not success:
        raise HTTPException(status_code=400, detail="Could not update profile.")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{id}")
async def delete_user(id: int, response: Response, current_user_id: int = Depends(get_current_user_id)):
    if id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    response.delete_cookie("SocialAppAuth")

    success = await repo.delete_account(id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Account successfully deleted."}


