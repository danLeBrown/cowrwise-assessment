from shared.repositories.user_repo import UserRepo
from shared.models.user_models import User
from sqlalchemy.orm import Session, make_transient
from redis import client
import time
import logging

logger = logging.getLogger(__name__)

def create_user_listener(pubsub: client.PubSub, admin_db: Session, frontend_db: Session):
    logger.info("create_user_listener started")
    pubsub.subscribe("user.created")
    frontend_repo = UserRepo(frontend_db)
    admin_repo = UserRepo(admin_db)
    
    logger.info(f"frontend_repo: {frontend_repo}")
    logger.info(f"admin_repo: {admin_repo}")
    
    try:
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True)
            if message and message["channel"].decode("utf-8") == "user.created":
                logger.info(f"Received message: {message}")
                user_id = message["data"].decode("utf-8")
                logger.info(f"User {user_id} created")

                # Fetch the user from the frontend database and add it to the admin database            
                user = frontend_repo.db.query(User).filter(User.id == user_id).first()
                
                if not user:
                    logger.warning(f"User {user_id} not found in frontend database")
                    continue
               
                logger.info(f"User {user_id} found in frontend database")

                # Detach the user object from the frontend session
                frontend_db.expunge(user)
                make_transient(user)

                admin_repo.create(user)
                logger.info(f"User {user_id} synced to admin database")
            
            # Add a small delay to prevent CPU overuse
            time.sleep(0.1)
    except Exception as e:
        logger.error(f"Error in user listener: {e}")