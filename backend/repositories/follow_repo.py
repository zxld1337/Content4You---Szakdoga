from database import database



class FollowRepository:
    async def get_following_list(self, user_id: int):
        query = """
            SELECT f.following_id as user_id, a.username, f.date_of_follow
            FROM follows f
            INNER JOIN accounts a ON a.id = f.following_id
            WHERE f.follower_id = :user_id
        """
        return await database.fetch_all(query=query, values={"user_id": user_id})


    async def get_followers_list(self, user_id: int):
        query = """
            SELECT f.follower_id as user_id, a.username, f.date_of_follow
            FROM follows f
            INNER JOIN accounts a ON a.id = f.follower_id
            WHERE f.following_id = :user_id
        """
        return await database.fetch_all(query=query, values={"user_id": user_id})


    async def get_relationship(self, follower_id: int, following_id: int):
        query = """
            SELECT id, following_id, follower_id, date_of_follow 
            FROM follows
            WHERE follower_id = :follower_id AND following_id = :following_id
        """
        return await database.fetch_one(query=query, values={"follower_id": follower_id, "following_id": following_id})


    async def create_follow(self, follower_id: int, following_id: int) -> int:
        query = "INSERT INTO follows (follower_id, following_id) VALUES (:follower_id, :following_id)"
        return await database.execute(query=query, values={"follower_id": follower_id, "following_id": following_id})


    async def delete_follow(self, follower_id: int, following_id: int) -> bool:
        query = "DELETE FROM follows WHERE follower_id = :follower_id AND following_id = :following_id"
        rows = await database.execute(query=query, values={"follower_id": follower_id, "following_id": following_id})
        return rows > 0