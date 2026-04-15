import random
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from typing import List, Optional
from dependencies import get_current_user_id
from repositories.post_repo import PostRepository
from services.ai_service import generate_tags_from_image
from schemas import PostReadDto 
from security import sanitize_html
from services.recommender_instance import recommender_inst
    

router = APIRouter(prefix="/api/posts", tags=["Posts"])
repo = PostRepository()
recommender = recommender_inst

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("", response_model=List[PostReadDto])
async def get_all_posts(user_id: int = Depends(get_current_user_id)):
    return await repo.get_all_posts(user_id)

@router.get("/liked", response_model=List[PostReadDto])
async def get_liked_posts(user_id: int = Depends(get_current_user_id)):
    return await repo.get_liked_posts(user_id)



@router.post("", status_code=201)
async def create_post(
    text: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None),
    user_id: int = Depends(get_current_user_id)
):
    image_path = None
    tags = []

    if image_file:
        image_bytes = await image_file.read()

        try:
            tags = await generate_tags_from_image(image_bytes)
        except Exception as e:
            print(f"AI Error: {e}")

        # Fájl mentése
        file_extension = os.path.splitext(image_file.filename)[1] 
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_location = f"{UPLOAD_DIR}/{unique_filename}"
        
        with open(file_location, "wb") as buffer:
            buffer.write(image_bytes)
            
        image_path = f"uploads/{unique_filename}"

    sanitized_text = sanitize_html(text) if text else ""
    new_id = await repo.create_post(user_id, image_path, sanitized_text)
    
    if tags:
        await repo.add_tags_to_post(new_id, tags)
    
    return {"message": "Post created", "postId": new_id, "tags": tags, "image_url": image_path}



@router.get("/recommendations", response_model=List[PostReadDto])
async def get_recommendations(
    user_id: int = Depends(get_current_user_id),
    limit: int = 10,
    seen_ids: List[int] = Query(default=[])
):
    # Hibrid algoritmus 
    posts = await recommender.get_recommended_posts(user_id, limit, seen_ids)

    # h nincs eleg poszt
    if len(posts) < limit:
        needed = limit - len(posts)
        
        current_seen = seen_ids + [p['id'] for p in posts]
        fallback_posts = await repo.get_fresh_posts(needed, current_seen)
        posts.extend(fallback_posts)
            
    random.shuffle(posts)
    return posts 



@router.get("/{id}", response_model=PostReadDto)
async def get_post(id: int):
    post = await repo.get_post_by_id(id)
    if not post: 
        raise HTTPException(404, "Not found")
    return post



@router.delete("/{id}")
async def delete_post(id: int, user_id: int = Depends(get_current_user_id)):
    post = await repo.get_post_by_id(id)
    if not post:
        raise HTTPException(404, "Not found")
        
    if post['user_id'] != user_id:
        raise HTTPException(403, "Forbidden")

    await repo.delete_post(id)
    return {"message": "Deleted successfully"}

