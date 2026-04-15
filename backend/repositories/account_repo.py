from database import database
from typing import Optional, List



class AccountRepository:
    async def is_username_taken(self, username: str) -> bool:
        query = "SELECT COUNT(1) FROM accounts WHERE username = :username"
        count = await database.fetch_val(query=query, values={"username": username})
        return count > 0


    async def create_account(self, username: str, email: str, password_hash: str) -> int:
        query = """
            INSERT INTO accounts (username, email, password) 
            VALUES (:username, :email, :password)
        """
        values = {"username": username, "email": email, "password": password_hash}
        return await database.execute(query=query, values=values)


    async def get_by_username(self, username: str):
        query = """
            SELECT a.id, a.username, a.password, a.full_name, a.email, a.phone_number, 
                   a.date_of_birth, a.date_of_create, a.profile_picture,
                   (SELECT COUNT(*) FROM follows f WHERE f.following_id = a.id) AS follower_count,
                   (SELECT COUNT(*) FROM follows f WHERE f.follower_id = a.id) AS following_count
            FROM accounts a 
            WHERE a.username = :username
        """
        return await database.fetch_one(query=query, values={"username": username})


    async def get_all(self):
        query = """
            SELECT id, username, full_name, email, phone_number, date_of_birth, 
                   date_of_create, profile_picture 
            FROM accounts
        """
        return await database.fetch_all(query=query)


    async def get_by_id(self, id: int):
        query = """
            SELECT a.id, a.username, a.full_name, a.email, a.phone_number, 
                   a.date_of_birth, a.date_of_create, a.profile_picture,
                   (SELECT COUNT(*) FROM follows f WHERE f.following_id = a.id) AS follower_count,
                   (SELECT COUNT(*) FROM follows f WHERE f.follower_id = a.id) AS following_count
            FROM accounts a 
            WHERE a.id = :id
        """
        return await database.fetch_one(query=query, values={"id": id})


    async def update_account(self, id: int, email: Optional[str] = None, 
                             full_name: Optional[str] = None, phone: Optional[str] = None, 
                             dob: Optional[str] = None, profile_picture: Optional[bytes] = None) -> bool:
        
        updates = []
        values = {"id": id}

        if email:
            updates.append("email = :email")
            values["email"] = email
        if full_name:
            updates.append("full_name = :full_name")
            values["full_name"] = full_name
        if phone:
            updates.append("phone_number = :phone")
            values["phone"] = phone
        if dob:
            updates.append("date_of_birth = :dob")
            values["dob"] = dob
        if profile_picture:
            updates.append("profile_picture = :profile_picture")
            values["profile_picture"] = profile_picture

        if not updates:
            return False

        query = f"UPDATE accounts SET {', '.join(updates)} WHERE id = :id"
        
        rows_affected = await database.execute(query=query, values=values)
        return rows_affected > 0


    async def delete_account(self, id: int) -> bool:
        query = "DELETE FROM accounts WHERE id = :id"
        rows = await database.execute(query=query, values={"id": id})
        return rows > 0
    

    async def get_user_interests(self, user_id: int):
        user_likes_query = """
            SELECT t.name, COUNT(*) as weight
            FROM liked_posts lp
            JOIN post_tags pt ON lp.post_id = pt.post_id
            JOIN tags t ON pt.tag_id = t.id
            WHERE lp.user_id = :user_id
            GROUP BY t.name
        """
        user_tags = await database.fetch_all(query=user_likes_query, values={"user_id": user_id})
        tag_weights = {record['name']: record['weight'] for record in user_tags}   

        return tag_weights