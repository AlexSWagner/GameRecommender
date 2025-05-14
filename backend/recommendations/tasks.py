import logging
from celery import shared_task
from django.db import transaction

from users.models import UserProfile
from .engine import RecommendationEngine


logger = logging.getLogger(__name__)


@shared_task
def generate_recommendations_for_all_users():
    """
    Task to regenerate recommendations for all users.
    This is scheduled to run periodically to keep recommendations fresh.
    """
    logger.info("Starting recommendation generation for all users")
    
    # Get all user profiles with completed surveys
    user_profiles = UserProfile.objects.filter(survey_completed=True)
    
    for profile in user_profiles:
        # Launch a task for each user
        generate_recommendations_for_user.delay(profile.id)
    
    return f"Initiated recommendation generation for {user_profiles.count()} users"


@shared_task
def generate_recommendations_for_user(user_profile_id):
    """
    Task to generate recommendations for a specific user.
    
    Args:
        user_profile_id: ID of the UserProfile to generate recommendations for
    """
    try:
        user_profile = UserProfile.objects.get(id=user_profile_id)
        
        logger.info(f"Generating recommendations for user {user_profile.user.username}")
        
        # Initialize recommendation engine
        engine = RecommendationEngine()
        
        # Generate recommendations within a transaction
        with transaction.atomic():
            recommendations = engine.generate_recommendations(user_profile)
        
        logger.info(f"Generated {len(recommendations)} recommendations for user {user_profile.user.username}")
        return f"Successfully generated {len(recommendations)} recommendations"
    
    except UserProfile.DoesNotExist:
        logger.error(f"User profile with ID {user_profile_id} does not exist")
        return f"Error: User profile with ID {user_profile_id} does not exist"
    
    except Exception as e:
        logger.exception(f"Error generating recommendations for user {user_profile_id}: {str(e)}")
        return f"Error generating recommendations: {str(e)}" 