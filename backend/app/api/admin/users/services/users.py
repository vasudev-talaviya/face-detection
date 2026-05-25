from app.core.base import APIResponse, BaseService
from app.core.exceptions import BadRequestError, NotFoundError
from app.core.logging import get_logger
from app.api.admin.users.repositories.users import UserRepository

logger = get_logger(__name__)


class UserService(BaseService):
    def __init__(self, repository: UserRepository) -> None:
        super().__init__(repository)
        self.repository = repository
        logger.info("UserService initialized")

    def register(self, name: str, embedding: list[float]) -> dict:
        try:
            success, existing_user, template_added = self.repository.save_embedding(name, embedding)
            if not success:
                logger.error(f"Failed to save user profile for {name}")
                raise RuntimeError("Failed to save user profile.")
            
            if existing_user and not template_added:
                logger.info(f"Face profile already exists for {name}")
                return APIResponse.success(
                    message=f"Face profile already exists for '{name}'."
                )
            
            action = "Added face profile to existing user" if existing_user else "Registered user"
            logger.info(f"{action} '{name}' successfully")
            return APIResponse.success(
                message=f"{action} '{name}' successfully."
            )
        except Exception as e:
            logger.error(f"Error registering user {name}: {e}")
            raise

    def list_users(self) -> dict:
        try:
            users = self.repository.list_users()
            logger.info(f"Retrieved {len(users)} users")
            return APIResponse.success(
                data=users,
                message="Users retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise

    def delete_user(self, user_id: str) -> dict:
        try:
            deleted = self.repository.delete_user(user_id)
        except ValueError as exc:
            logger.warning(f"Invalid user ID: {user_id}")
            raise BadRequestError("Invalid user ID.") from exc
        
        if not deleted:
            logger.warning(f"User not found: {user_id}")
            raise NotFoundError("User not found.")
        
        logger.info(f"User {user_id} deleted successfully")
        return APIResponse.success(
            message="User deleted successfully."
        )

    def update_user(self, user_id: str, new_name: str, embedding: list[float] | None = None) -> dict:
        if not new_name or not new_name.strip():
            raise BadRequestError("Name cannot be empty.")
            
        try:
            updated = self.repository.update(user_id, {"name": new_name.strip()}, embedding)
        except ValueError as exc:
            logger.warning(f"Invalid user ID: {user_id}")
            raise BadRequestError("Invalid user ID.") from exc
            
        if not updated:
            logger.warning(f"User not found or no changes made: {user_id}")
            raise NotFoundError("User not found.")
            
        logger.info(f"User {user_id} updated successfully to '{new_name}'")
        msg = f"User renamed to '{new_name}' successfully."
        if embedding:
            msg = f"User '{new_name}' updated with new face template."
        return APIResponse.success(message=msg)
