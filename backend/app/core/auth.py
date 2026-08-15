from uuid import UUID

from fastapi import Depends

from app.models.user import User
from app.db.database import get_db
from sqlalchemy.orm import Session


def get_current_user(
    db: Session = Depends(get_db),
) -> User:
    user = (
        db.query(User)
        .filter(User.username == "dev-user")
        .first()
    )

    if user is None:
        user = User(
            username="dev-user",
            role="BATMAN_OPERATOR",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    return user