import mysql.connector
from faker import Faker
import random
import uuid
import os
import requests 
import time     


DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'ai_recommender_db'
}

UPLOAD_DIR = "../backend/uploads"

# Kategóriák és kulcsszavak a képekhez
CATEGORIES = {
    "cars": ["car", "bmw", "audi", "ferrari", "drift", "racing", "wheel", "engine", "street", "vintage", "supercar", "luxury", "convertible", "muscle car"], 
    "nature": ["nature", "sunset", "forest", "mountain", "river", "sky", "hiking", "beach", "flower", "wildlife", "landscape", "waterfall", "autumn", "spring"],
    "tech": ["computer", "programming", "technology", "robot", "cyberpunk", "code", "gadget", "ai", "vr", "futuristic", "electronics", "innovation", "hacker", "startup"],
    "food": ["food", "pizza", "burger", "sushi", "coffee", "cake", "meal", "dessert", "cuisine", "gourmet", "healthy food", "street food", "breakfast", "dinner"], 
    "cats": ["cat", "kitten", "cute cat", "sleeping cat", "cat playing", "cat portrait", "cat in nature", "cat with toy", "funny cat", "cat close-up", "cat and human", "cat and dog", "cat on furniture", "cat silhouette"] 
}

fake = Faker()
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

def ensure_upload_dir():
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    
    print("Régi képek törlése")
    for f in os.listdir(UPLOAD_DIR):
        if f.startswith("mock_"):
            try:
                os.remove(os.path.join(UPLOAD_DIR, f))
            except:
                pass


def download_real_image(filename, category):
    """Letölt egy képet a LoremFlickr-ről a kategória alapján"""
    width, height = 640, 480
    
    # URL felépítése: https://loremflickr.com/640/480/car/random=12345
    url = f"https://loremflickr.com/{width}/{height}/{category}?random={random.randint(1, 10000)}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(os.path.join(UPLOAD_DIR, filename), 'wb') as f:
                f.write(response.content)
            return True
        
    except Exception as e:
        print(f"Hiba a kép letöltésekor ({category}): {e}")
        return False


def clean_db():
    print("Adatbázis ürítése")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    tables = ["liked_posts", "comments", "post_tags", "tags", "posts", "follows", "accounts"]
    
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table};")
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conn.commit()


def create_users(count=500):
    print(f"{count} felhasználó létrehozása...")
    sql = "INSERT INTO accounts (username, email, password, full_name) VALUES (%s, %s, %s, %s)"
    default_hash = "$2b$12$u.x.x.x..." 
    
    for _ in range(count):
        cursor.execute(sql, (fake.unique.user_name(), fake.unique.email(), default_hash, fake.name()))
    conn.commit()
    
    cursor.execute("SELECT id FROM accounts")
    return [item[0] for item in cursor.fetchall()]


def create_content(user_ids, posts_per_category=200):
    print("IGAZI képek letöltése és posztolás")
    post_ids_by_category = {cat: [] for cat in CATEGORIES.keys()}
    
    # Tagek feltöltése
    tag_map = {}
    for cat, tags in CATEGORIES.items():
        for tag_name in tags:
            cursor.execute("INSERT INTO tags (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=id", (tag_name,))
            cursor.execute("SELECT id FROM tags WHERE name = %s", (tag_name,))
            tag_map[tag_name] = cursor.fetchone()[0]

    insert_post_sql = "INSERT INTO posts (user_id, image, text, date_of_post) VALUES (%s, %s, %s, %s)"
    insert_post_tag_sql = "INSERT INTO post_tags (post_id, tag_id) VALUES (%s, %s)"

    total_posts = len(CATEGORIES) * posts_per_category
    processed = 0

    for cat, tags in CATEGORIES.items():
        print(f"Kategória feldolgozása: {cat.upper()}")
        for _ in range(posts_per_category):
            user = random.choice(user_ids)
            
            # kép letöltése 
            filename = f"mock_{cat}_{uuid.uuid4().hex[:6]}.jpg"
            success = download_real_image(filename, cat)
            
            if not success:
                continue
                
            image_path = f"uploads/{filename}"

            text = fake.sentence()
            date = fake.date_time_this_year()
            
            cursor.execute(insert_post_sql, (user, image_path, text, date))
            post_id = cursor.lastrowid
            post_ids_by_category[cat].append(post_id)
            
            # Tagek hozzárendelése
            chosen_tags = random.sample(tags, k=random.randint(2, 4))
            for tag in chosen_tags:
                cursor.execute(insert_post_tag_sql, (post_id, tag_map[tag]))
            
            processed += 1
            print(f"{processed}/{total_posts} kép letöltve ({cat})")
            
            
            time.sleep(0.5) 
    
    conn.commit()
    return post_ids_by_category


def generate_smart_interactions(user_ids, post_ids_by_category):
    print("Intelligens interakciók, Mátrix építés...")
    like_sql = "INSERT IGNORE INTO liked_posts (user_id, post_id, date_of_like) VALUES (%s, %s, %s)"
    
    for user_id in user_ids:
        favorites = random.sample(list(CATEGORIES.keys()), k=random.randint(1, 2))
        
        # Kedvenc kategóriák 60% esély like-ra
        for cat in favorites:
            posts = post_ids_by_category[cat]
            if not posts: continue
            to_like = random.sample(posts, k=int(len(posts) * 0.6))
            for pid in to_like:
                cursor.execute(like_sql, (user_id, pid, fake.date_time_this_year()))
        
        # Egyéb kategóriák 5% esély
        others = [c for c in CATEGORIES.keys() if c not in favorites]
        for cat in others:
            posts = post_ids_by_category[cat]
            if not posts: continue
            to_like = random.sample(posts, k=int(len(posts) * 0.05))
            for pid in to_like:
                cursor.execute(like_sql, (user_id, pid, fake.date_time_this_year()))

    conn.commit()


try:
    #ensure_upload_dir()
    #clean_db()
    users = create_users(500) 
    posts_map = create_content(users, posts_per_category=200) 
    
    generate_smart_interactions(users, posts_map)
    print("\nKÉSZ! Valódi fotók letöltve az 'uploads' mappába.")
except Exception as e:
    print(f"\nHIBA TÖRTÉNT: {e}")
finally:
    if cursor: cursor.close()
    if conn: conn.close()