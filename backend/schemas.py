from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Auth DTOs 
class AccountLoginDto(BaseModel):
    username: str
    password: str

class AccountRegistrationDto(BaseModel):
    username: str
    email: EmailStr
    password: str

# Account DTOs
# public modell
class AccountPublicDto(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    date_of_create: Optional[datetime] = None
    profile_picture: Optional[bytes] = None 
    follower_count: int = 0
    following_count: int = 0

# private modell
class AccountPrivateDto(AccountPublicDto):
    phone_number: Optional[str] = None
    date_of_birth: Optional[str] = None


# Post DTOs
class PostReadDto(BaseModel):
    id: int
    user_id: int
    username: str
    image: Optional[bytes]
    text: Optional[str]
    like_count: int
    comment_count: int
    date_of_post: Optional[datetime]
    is_liked: bool = False 
    tag_list: Optional[str] = None

# comment DTOs
class CommentCreateDto(BaseModel):
    text: str

class CommentReadDto(BaseModel):
    id: int
    user_id: int
    post_id: int
    username: str
    text: str
    date_of_comment: Optional[datetime] = None


# like DTOs
class LikeReadDto(BaseModel):
    user_id: int
    username: str
    date_of_like: Optional[datetime] = None


# follow DTOs
class FollowRequest(BaseModel):
    following_id: int

class FollowReadDto(BaseModel):
    user_id: int
    username: str
    date_of_follow: Optional[datetime] = None