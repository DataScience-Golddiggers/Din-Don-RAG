import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    CLEANED_DATA_DIR = DATA_DIR / "cleaned"
    MODELS_DIR = BASE_DIR / "models"
    LOGS_DIR = BASE_DIR / "logs"
    
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "italian")
    USE_LEMMATIZATION = os.getenv("USE_LEMMATIZATION", "true").lower() == "true"
    REMOVE_STOPWORDS = os.getenv("REMOVE_STOPWORDS", "true").lower() == "true"
    
    TEST_SIZE = float(os.getenv("TEST_SIZE", "0.2"))
    RANDOM_STATE = int(os.getenv("RANDOM_STATE", "42"))
    MAX_FEATURES = int(os.getenv("MAX_FEATURES", "1000"))
    
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    @classmethod
    def ensure_directories(cls):
        for directory in [
            cls.DATA_DIR,
            cls.RAW_DATA_DIR,
            cls.PROCESSED_DATA_DIR,
            cls.CLEANED_DATA_DIR,
            cls.MODELS_DIR,
            cls.LOGS_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_log_file(cls, name: str = "app") -> Path:
        cls.ensure_directories()
        return cls.LOGS_DIR / f"{name}.log"


config = Config()
