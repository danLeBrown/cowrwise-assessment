from shared.repositories.user_repo import UserRepo
from shared.models.user_models import User
from sqlalchemy.orm import Session, make_transient
from shared.utils.redis_service import RedisService
import time
import logging
import json

logger = logging.getLogger(__name__)

def create_user_listener(redis_client: RedisService, admin_db: Session, frontend_db: Session):
    logger.info("create_user_listener started")
    pubsub = redis_client.client.pubsub() 
    pubsub.subscribe("user.created")
    admin_repo = UserRepo(admin_db)
    
    try:
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True)
            if message and message["type"] == "message" and message["channel"] == "user.created":
                logger.info(f"Received message: {message}")
                user_id = message["data"]

                # Fetch the user from the frontend database and add it to the admin database            
                user = frontend_db.query(User).filter(User.id == user_id).first()
                check = admin_db.query(User).filter(User.id == user_id).first()
                
                if check:
                    logger.info(f"User {user_id} already exists in admin database")
                    continue

                if not user:
                    logger.warning(f"User {user_id} not found in frontend database")
                    continue
               
                logger.info(f"User {user_id} found in frontend database")

                frontend_db.expunge(user)
                make_transient(user)

                admin_repo.create(user)
                logger.info(f"User {user_id} synced to admin database")
            
            # Add a small delay to prevent CPU overuse
            time.sleep(0.1)
    except Exception as e:
        logger.error(f"Error in user listener: {e}")