from database import database



class LikeRepository:
    async def get_like_by_keys(self, user_id: int, post_id: int):
        query = """
            SELECT id, user_id, post_id, date_of_like 
            FROM liked_posts
            WHERE user_id = :user_id AND post_id = :post_id
        """
        return await database.fetch_one(query=query, values={"user_id": user_id, "post_id": post_id})


    async def get_likes_by_post_id(self, post_id: int):
        query = """
            SELECT l.user_id, a.username, l.date_of_like
            FROM likes l
            INNER JOIN accounts a ON l.user_id = a.id 
            WHERE l.post_id = :post_id 
            ORDER BY l.date_of_like DESC
        """
        return await database.fetch_all(query=query, values={"post_id": post_id})


    async def create_like(self, user_id: int, post_id: int) -> int:
        query = "INSERT INTO liked_posts (user_id, post_id) VALUES (:user_id, :post_id)"
        return await database.execute(query=query, values={"user_id": user_id, "post_id": post_id})
    

    async def delete_like(self, user_id: int, post_id: int) -> bool:
        query = "DELETE FROM liked_posts WHERE user_id = :user_id AND post_id = :post_id"
        rows = await database.execute(query=query, values={"user_id": user_id, "post_id": post_id})
        return rows > 0