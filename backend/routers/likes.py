from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List
from requests import session
from dependencies import get_current_user_id
from repositories.like_repo import LikeRepository
from schemas import LikeReadDto
from services.recommender_instance import recommender_inst

router = APIRouter(prefix="/api/posts", tags=["Likes"])
repo = LikeRepository()
recommender = recommender_inst


@router.get("/{post_id}/likes", response_model=List[LikeReadDto])
async def get_likes(post_id: int):
    return await repo.get_likes_by_post_id(post_id)


@router.post("/{post_id}/like", status_code=201)
async def like_post(post_id: int, user_id: int = Depends(get_current_user_id)):
    existing_like = await repo.get_like_by_keys(user_id, post_id)
    
    if existing_like:
        raise HTTPException(status_code=409, detail="Post is already liked by this user.")
    
    new_id = await repo.create_like(user_id, post_id)

    await recommender.update_user_profile(user_id) # update cache
   
    return {"message": "Post liked successfully.", "likeId": new_id}


@router.delete("/{post_id}/like")
async def unlike_post(post_id: int, user_id: int = Depends(get_current_user_id)):
    existing_like = await repo.get_like_by_keys(user_id, post_id)
    
    if not existing_like:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    success = await repo.delete_like(user_id, post_id)
    if not success:
        raise HTTPException(status_code=500, detail="Unlike failed")
        
    await recommender.update_user_profile(user_id) # update cache
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)