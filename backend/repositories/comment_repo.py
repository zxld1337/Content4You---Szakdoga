from database import database



class CommentRepository:
    async def get_comments_by_post(self, post_id: int):
        query = """
            SELECT c.id, c.user_id, c.post_id, c.text, c.date_of_comment, a.username
            FROM comments c 
            INNER JOIN accounts a ON c.user_id = a.id 
            WHERE c.post_id = :post_id 
            ORDER BY c.date_of_comment ASC
        """
        return await database.fetch_all(query=query, values={"post_id": post_id})


    async def create_comment(self, user_id: int, post_id: int, text: str) -> int:
        query = """
            INSERT INTO comments (user_id, post_id, text) 
            VALUES (:user_id, :post_id, :text)
        """
        return await database.execute(query=query, values={"user_id": user_id, "post_id": post_id, "text": text})


    async def get_comment_by_id(self, comment_id: int):
        query = "SELECT id, user_id, post_id, text, date_of_comment FROM comments WHERE id = :id"
        return await database.fetch_one(query=query, values={"id": comment_id})


    async def delete_comment(self, comment_id: int) -> bool:
        query = "DELETE FROM comments WHERE id = :id"
        rows = await database.execute(query=query, values={"id": comment_id})
        return rows > 0