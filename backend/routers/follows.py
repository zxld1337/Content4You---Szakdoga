from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List
from dependencies import get_current_user_id
from repositories.follow_repo import FollowRepository
from schemas import FollowRequest, FollowReadDto

router = APIRouter(prefix="/api/follow", tags=["Follows"])
repo = FollowRepository()


@router.get("/{user_id}/following", response_model=List[FollowReadDto])
async def get_following(user_id: int):
    return await repo.get_following_list(user_id)


@router.get("/{user_id}/followers", response_model=List[FollowReadDto])
async def get_followers(user_id: int):
    return await repo.get_followers_list(user_id)


@router.post("", status_code=201)
async def follow_user(dto: FollowRequest, user_id: int = Depends(get_current_user_id)):
    if user_id == dto.following_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself.")

    existing_follow = await repo.get_relationship(user_id, dto.following_id)
    if existing_follow:
        raise HTTPException(status_code=409, detail="You are already following this user.")

    new_id = await repo.create_follow(user_id, dto.following_id)
    return {"message": "User followed successfully.", "followId": new_id}


@router.delete("/{following_id}")
async def unfollow_user(following_id: int, user_id: int = Depends(get_current_user_id)):
    existing_follow = await repo.get_relationship(user_id, following_id)
    
    if not existing_follow:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    success = await repo.delete_follow(user_id, following_id)
    if not success:
        raise HTTPException(status_code=500, detail="Unfollow failed")

    return Response(status_code=status.HTTP_204_NO_CONTENT)