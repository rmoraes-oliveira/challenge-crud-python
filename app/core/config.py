import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.DATABASE_URL: str = os.getenv("DATABASE_URL")
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL not defined")
        
        self.REDIS_URL: str = os.getenv("REDIS_URL")
        self.CACHE_TTL: str = os.getenv("CACHE_TTL", "60")

settings = Settings()