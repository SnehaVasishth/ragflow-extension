
import os
from dotenv import dotenv_values, load_dotenv
from functools import lru_cache

class Config:
    _initialized = False
    _config_cache = None
    _env_file_map = {
            "production": ".env",
            "test": ".env.test", 
            "development": ".env.dev",
            "local": ".env.local"
        }
    
    @classmethod
    def _initialize_once(cls):
        """Initialize environment variables once at startup"""
        if cls._initialized:
            return
            
        ENV = os.environ.get("ENVIRONMENT", "development")
        
        env_file = cls._env_file_map.get(ENV)
        if env_file:
            load_dotenv(env_file)
            cls._config_cache = dotenv_values(env_file)
        else:
            cls._config_cache = {}
            
        cls._initialized = True
    
    @staticmethod
    @lru_cache(maxsize=1)
    def get_environment():
        Config._initialize_once()
        return Config._config_cache or {}