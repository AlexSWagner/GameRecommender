from celery import shared_task
import logging
from games.utils.image_cache import verify_all_game_images

logger = logging.getLogger(__name__)

@shared_task
def cache_game_images(batch_size=20, limit=None):
    """
    Celery task to cache game images.
    
    Args:
        batch_size: Number of games to process in each batch
        limit: Optional limit to total number of games to process
    
    Returns:
        str: Summary of the caching process
    """
    try:
        logger.info(f"Starting game image caching task with batch size {batch_size}")
        
        success_count, failure_count = verify_all_game_images(limit or batch_size)
        
        summary = f"Image caching completed. Success: {success_count}, Failure: {failure_count}"
        logger.info(summary)
        
        return summary
    except Exception as e:
        logger.error(f"Error in game image caching task: {str(e)}")
        return f"Error: {str(e)}" 