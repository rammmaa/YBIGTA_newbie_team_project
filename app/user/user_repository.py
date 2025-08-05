from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional, Dict

from app.user.user_schema import User

class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        query = text("SELECT email, username, password FROM users WHERE email = :email")
        result = self.db.execute(query, {"email": email}).fetchone()

        if result is None:
            return None

        return User(
            email=result[0],
            username=result[1],
            password=result[2]
        )

    def save_user(self, user: User) -> User:
        # 존재하는지 확인 후 insert or update
        existing = self.get_user_by_email(user.email)
        if existing:
            query = text("""
                UPDATE users 
                SET username = :username, password = :password 
                WHERE email = :email
            """)
        else:
            query = text("""
                INSERT INTO users (email, username, password) 
                VALUES (:email, :username, :password)
            """)

        self.db.execute(query, {
            "email": user.email,
            "username": user.username,
            "password": user.password
        })
        self.db.commit()
        return user

    def delete_user(self, user: User) -> User:
        query = text("DELETE FROM users WHERE email = :email")
        self.db.execute(query, {"email": user.email})
        self.db.commit()
        return user
