from app.user.user_repository import UserRepository
from app.user.user_schema import User, UserLogin, UserUpdate


class UserService:
    def __init__(self, userRepoitory: UserRepository) -> None:
        self.repo = userRepoitory

    def login(self, user_login: UserLogin) -> User:
        ## TODO
        """
        Check if the user exists and if the password matches.
        Args:
            user_login (UserLogin): The login credentials of the user.
        Returns:
            User: The user object if login is successful.
        """
        user = self.repo.get_user_by_email(user_login.email)
        if not user:
            raise ValueError("User not Found.")
        if user.password != user_login.password:   
            raise ValueError("Invalid ID/PW")
        return user
        
    def register_user(self, new_user: User) -> User:
        ## TODO
        """
        Register a new user.
        Args:
            new_user (User): The user object to be registered.
        Returns:
            User: The registered user object.
        """
        checked_user = self.repo.get_user_by_email(new_user.email)
        if checked_user:
            raise ValueError("User already Exists.")
        new_user = self.repo.save_user(new_user)
        return new_user

    def delete_user(self, email: str) -> User:
        ## TODO        
        """
        Delete a user by email.
        Args:
            email (str): The email of the user to be deleted.
        Returns:
            User: The deleted user object.
        """
        user = self.repo.get_user_by_email(email)
        if not user:
            raise ValueError("User not Found.")
        user = self.repo.delete_user(user)
        return user

    def update_user_pwd(self, user_update: UserUpdate) -> User:
        ## TODO
        """
        Update the password of a user.
        Args:
            user_update (UserUpdate): The user update object containing the new password.
        Returns:
            User: The updated user object.
        """
        updated_user = self.repo.get_user_by_email(user_update.email)
        if not updated_user:
            raise ValueError("User not Found.")
        updated_user = User(
            email=updated_user.email,
            password=user_update.new_password,
            username=updated_user.username
        )
        updated_user = self.repo.save_user(updated_user)
        return updated_user
        