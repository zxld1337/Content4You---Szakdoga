from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from dependencies import get_current_user_id
from repositories.comment_repo import CommentRepository
from schemas import CommentCreateDto, CommentReadDto
from security import sanitize_html

router = APIRouter(tags=["Comments"])
repo = CommentRepository()


@router.get("/api/posts/{post_id}/comments", response_model=List[CommentReadDto])
async def get_comments_by_post(post_id: int):
    comments = await repo.get_comments_by_post(post_id)
    return comments 


@router.post("/api/posts/{post_id}/comments", status_code=201)
async def create_comment(
    post_id: int, 
    dto: CommentCreateDto, 
    user_id: int = Depends(get_current_user_id)
):
    sanitized_text = sanitize_html(dto.text)
    
    new_id = await repo.create_comment(user_id, post_id, sanitized_text)    
    return {"message": "Comment created successfully.", "commentId": new_id}


@router.delete("/api/comments/{comment_id}")
async def delete_comment(comment_id: int, user_id: int = Depends(get_current_user_id)):
    existing_comment = await repo.get_comment_by_id(comment_id)
    
    if not existing_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if existing_comment['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    success = await repo.delete_comment(comment_id)
    if not success:
        raise HTTPException(status_code=500, detail="Delete failed")

    return {"message": "Comment successfully deleted."}