from database import database
from typing import Optional, List
import math
from collections import defaultdict



class PostRepository:
    async def get_all_posts(self, user_id: int):
        query = """
            SELECT p.id, p.user_id, p.image, p.text, p.date_of_post, a.username,
                   (SELECT COUNT(*) FROM liked_posts l WHERE l.post_id = p.id) AS like_count,
                   (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comment_count,
                   EXISTS(SELECT 1 FROM liked_posts l WHERE l.post_id = p.id AND l.user_id = :user_id) AS is_liked
            FROM posts p 
            INNER JOIN accounts a ON p.user_id = a.id 
            ORDER BY p.date_of_post DESC
        """
        return await database.fetch_all(query=query, values={"user_id": user_id})
    

    async def get_liked_posts(self, user_id: int):
        query = """
                SELECT p.id, p.user_id, p.image, p.text, p.date_of_post, a.username,
                (SELECT COUNT(*) FROM liked_posts l WHERE l.post_id = p.id) AS like_count,
                (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comment_count,
                EXISTS(SELECT 1 FROM liked_posts l WHERE l.post_id = p.id AND l.user_id = :user_id) AS is_liked
                FROM posts p
                INNER JOIN accounts a ON p.user_id = a.id
                INNER JOIN liked_posts lp ON lp.post_id = p.id
                WHERE lp.user_id = :user_id
                ORDER BY p.date_of_post DESC
        """
        return await database.fetch_all(query=query, values={"user_id": user_id})


    async def get_post_by_id(self, id: int):
        query = """
            SELECT p.id, p.user_id, p.image, p.text, p.date_of_post, a.username,
                   (SELECT COUNT(*) FROM liked_posts l WHERE l.post_id = p.id) AS like_count,
                   (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comment_count
            FROM posts p 
            INNER JOIN accounts a ON p.user_id = a.id 
            WHERE p.id = :id
        """
        return await database.fetch_one(query=query, values={"id": id})


    async def create_post(self, user_id: int, image_path: Optional[str], text: Optional[str]) -> int:
        query = """
            INSERT INTO posts (user_id, image, text) 
            VALUES (:user_id, :image, :text)
        """
        values = {"user_id": user_id, "image": image_path, "text": text}
        return await database.execute(query=query, values=values)


    async def update_post(self, post_id: int, text: Optional[str], image_path: Optional[str]) -> bool:
        updates = []
        values = {"id": post_id}

        if text is not None:
            updates.append("text = :text")
            values["text"] = text
        
        if image_path is not None:
            updates.append("image = :image")
            values["image"] = image_path

        if not updates:
            return False

        query = f"UPDATE posts SET {', '.join(updates)} WHERE id = :id"
        rows = await database.execute(query=query, values=values)
        return rows > 0

    
    async def delete_post(self, id: int) -> bool:
        query = "DELETE FROM posts WHERE id = :id"
        rows = await database.execute(query=query, values={"id": id})
        return rows > 0
    

    async def add_tags_to_post(self, post_id: int, tags: List[str]):
        for tag in tags:
            await database.execute(
                "INSERT INTO tags (name) VALUES (:name) ON DUPLICATE KEY UPDATE id=id", 
                values={"name": tag}
            )

            tag_record = await database.fetch_one(
                "SELECT id FROM tags WHERE name = :name", 
                values={"name": tag}
            )
            tag_id = tag_record['id']
            
            try:
                await database.execute(
                    "INSERT INTO post_tags (post_id, tag_id) VALUES (:post_id, :tag_id)",
                    values={"post_id": post_id, "tag_id": tag_id}
                )
            except:
                pass 


    # friss posztok (kizárja a látottakat)
    async def get_fresh_posts(self, limit: int = 10, exclude_ids: List[int] = None):
        if exclude_ids is None:
            exclude_ids = []
            
        exclude_sql = ",".join(map(str, exclude_ids)) if exclude_ids else "-1"
        
        query = f"""
            SELECT p.id, p.user_id, p.image, p.text, p.date_of_post, a.username,
                   (SELECT COUNT(*) FROM liked_posts l WHERE l.post_id = p.id) AS like_count,
                   (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comment_count
            FROM posts p 
            INNER JOIN accounts a ON p.user_id = a.id 
            WHERE p.id NOT IN ({exclude_sql})
            ORDER BY p.date_of_post DESC
            LIMIT :limit
        """
        return await database.fetch_all(query=query, values={"limit": limit})    
    
    
    # Cold-start fallback - legnépszerűbb posztokat adja vissza 
    async def get_popular_posts(self, limit: int, seen_ids_sql: str, user_id: int):
        popular_query = f"""
            SELECT
                p.id, p.user_id, p.image, p.text, p.date_of_post, a.username,
                GROUP_CONCAT(DISTINCT t.name) AS tag_list,
                COUNT(DISTINCT lp.id) AS like_count,
                (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comment_count,
                0 AS is_liked
            FROM posts p
            JOIN accounts a ON p.user_id = a.id
            LEFT JOIN liked_posts lp ON p.id = lp.post_id
            JOIN post_tags pt ON p.id = pt.post_id
            JOIN tags t ON pt.tag_id = t.id
            WHERE p.user_id != :user_id
            AND p.id NOT IN ({seen_ids_sql})
            GROUP BY p.id
            ORDER BY like_count DESC, p.date_of_post DESC
            LIMIT :limit
        """

        return await database.fetch_all(query=popular_query, values={"user_id": user_id, "limit": limit})
    