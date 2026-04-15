from repositories.post_repo import PostRepository
from collections import defaultdict
import time, math
from database import database
from typing import Optional, List


class Recommender:
    def __init__(self):
        self.user_profiles_cache = None
        self.cache_timestamp = 0
        self.cache_ttl = 60 
        self.repo = PostRepository()

        # hibrid ajánlórendszer súlyai
        self.coll_weight = 0.6 # collaborative filtering súlya
        self.cont_weight = 0.4 # content-based filtering súlya
        self.similarity_min = 0.1 # zajszűrés
        self.popularity_weight = 0.1 # népszerűségi bónusz súlya


    async def update_user_profile(self, user_id):
        if self.user_profiles_cache is None:
            self.user_profiles_cache = {}

        query = """
            SELECT t.name, COUNT(*) as score
            FROM liked_posts lp
            JOIN post_tags pt ON lp.post_id = pt.post_id
            JOIN tags t ON pt.tag_id = t.id
            WHERE lp.user_id = :user_id
            GROUP BY t.name
        """
        rows = await database.fetch_all(query=query, values={"user_id": user_id})

        profile = {row["name"]: row["score"] for row in rows}
        self.user_profiles_cache[user_id] = profile
        self.cache_timestamp = time.time()  


    async def _load_user_profiles(self):
        matrix_query = """
            SELECT lp.user_id, t.name AS tag, COUNT(*) AS score
            FROM liked_posts lp
            JOIN post_tags pt ON lp.post_id = pt.post_id
            JOIN tags t ON pt.tag_id = t.id
            GROUP BY lp.user_id, t.name
        """
        raw_matrix = await database.fetch_all(query=matrix_query)

        profiles = defaultdict(dict)
        for row in raw_matrix:
            profiles[row["user_id"]][row["tag"]] = row["score"]

        return profiles
    

    async def _get_user_profiles_cached(self):
        now = time.time()
        if (self.user_profiles_cache is None or now - self.cache_timestamp > self.cache_ttl):
            self.user_profiles_cache = await self._load_user_profiles()            
            self.cache_timestamp = now

        return self.user_profiles_cache
    

    # Hibrid ajánlórendszer - collaborative + content-based + népszerűségi bónusz
    async def get_recommended_posts(
        self,
        user_id: int,
        limit: int = 10,
        seen_post_ids: Optional[List[int]] = None,        
    ):          
    
        if seen_post_ids is None:
            seen_post_ids = []
    
        seen_ids_sql = ",".join(map(str, seen_post_ids)) if seen_post_ids else "-1"
    
        # User-tag cache interakciók lekérése a mátrixhoz
        user_profiles = await self._get_user_profiles_cached()
    
        # Cold-start - ha nincs interakció, vissza adja a népszerú posztokat
        if user_id not in user_profiles:
            return await self.repo.get_popular_posts(limit, seen_ids_sql, user_id)
    

        # koszinusz hasonlóság számítása, a releváns felhasználók között
        target_vector = user_profiles[user_id]  

        similar_users: list[tuple[int, float]] = []
        target_tags = set(target_vector)
        
        relevant_users = {
            uid: vec for uid, vec in user_profiles.items()
            if uid != user_id and target_tags & vec.keys()
        }
         
        sum_sq_a = sum(v**2 for v in target_vector.values())

        for other_uid, other_vector in relevant_users.items():
            sum_sq_b = sum(v**2 for v in other_vector.values())
            if sum_sq_b == 0:
                continue

            common_tags = target_tags & other_vector.keys()

            dot_product = sum(target_vector[t] * other_vector[t] for t in common_tags)

            similarity = dot_product / (math.sqrt(sum_sq_a) * math.sqrt(sum_sq_b))
            if similarity > self.similarity_min: 
                similar_users.append((other_uid, similarity))
    
        similar_users.sort(key=lambda x: x[1], reverse=True)
        top_similar = similar_users[:10]

        # collaborative score szamítás
        if top_similar:
            similar_ids_sql = ",".join(str(u[0]) for u in top_similar)
            sim_likes_query = f"""
                SELECT post_id, user_id
                FROM liked_posts
                WHERE user_id IN ({similar_ids_sql})
            """
            sim_likes_rows = await database.fetch_all(query=sim_likes_query)

            sim_score_map: dict[int, float] = {}
            sim_lookup = dict(top_similar)  
            for row in sim_likes_rows:
                pid = row["post_id"]
                uid = row["user_id"]
                sim_score_map[pid] = sim_score_map.get(pid, 0.0) + sim_lookup.get(uid, 0.0)
        else:
            sim_score_map = {}
    
        # Jelölt posztok lekérése (-látottak -lájkoltak)
        candidates_query = f"""
            SELECT
                p.id,
                p.user_id,
                p.image,
                p.text,
                p.date_of_post,
                a.username,
                GROUP_CONCAT(t.name) AS tag_list,
                (SELECT COUNT(*) FROM liked_posts l WHERE l.post_id = p.id) AS like_count,
                (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comment_count               
            FROM posts p
            JOIN accounts a ON p.user_id = a.id
            JOIN post_tags pt ON p.id = pt.post_id
            JOIN tags t ON pt.tag_id = t.id
            WHERE p.user_id != :user_id
            AND p.id NOT IN (SELECT post_id FROM liked_posts WHERE user_id = :user_id)
            AND p.id NOT IN ({seen_ids_sql})
            GROUP BY p.id
        """
        candidate_posts = await database.fetch_all(query=candidates_query, values={"user_id": user_id})
        if not candidate_posts:
            return []
            
        # content based filtering
        raw_scores = []
        for post in candidate_posts:
            post_tags = post["tag_list"].split(",") if post["tag_list"] else []
            content_score = sum(target_vector.get(tag, 0) for tag in post_tags)
            collab_score = sim_score_map.get(post["id"], 0.0)
            raw_scores.append((post, content_score, collab_score))

        # Normalizálási max
        max_content = max((s[1] for s in raw_scores), default=1) or 1
        max_collab  = max((s[2] for s in raw_scores), default=1) or 1

        # pontszámítás (collaborative + content-based + népszerűségi bónusz)
        scored_posts = []
        for post, content_score, collab_score in raw_scores:
            norm_content = content_score / max_content 
            norm_collab  = collab_score / max_collab  
            popularity_bonus = math.log1p(post["like_count"]) * self.popularity_weight 

            final_score = (
                self.coll_weight * norm_collab
                + self.cont_weight  * norm_content
                + popularity_bonus
            )
    
            if final_score > 0:
                post_dict = dict(post)
                post_dict["score"] = final_score
                post_dict["collab_score"] = norm_collab
                post_dict["content_score"] = norm_content
                scored_posts.append(post_dict)

        

        scored_posts.sort(key=lambda x: x["score"], reverse=True)
        return scored_posts[:limit]
    
    
    
