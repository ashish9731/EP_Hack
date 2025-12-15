import os
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

# Global client instance
_supabase_client = None

def get_supabase_client() -> Client:
    """Initialize and return a Supabase client"""
    global _supabase_client
    
    if _supabase_client is not None:
        return _supabase_client
    
    logger.debug("Initializing Supabase client")
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    
    logger.debug(f"Supabase URL from env: {url}")
    logger.debug(f"Supabase KEY from env: {'*' * len(key) if key else None}")
    
    if not url or not key:
        logger.error("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    
    try:
        _supabase_client = create_client(url, key)
        logger.debug("Supabase client initialized successfully")
        return _supabase_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to initialize Supabase client: {str(e)}")