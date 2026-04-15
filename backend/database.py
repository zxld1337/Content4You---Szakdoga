from databases import Database
from config import get_settings


database = Database(get_settings().DATABASE_URL)
