from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.core.security import get_password_hash


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalars(select(User).where(User.email == email)).first()


def count_users(db: Session) -> int:
    n = db.scalar(select(func.count()).select_from(User))
    return int(n or 0)


def create(
    db: Session,
    *,
    email: str,
    full_name: str,
    password: str,
    role: UserRole,
) -> User:
    u = User(
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        role=role,
        is_active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def update(
    db: Session,
    user: User,
    *,
    full_name: str | None = None,
    is_active: bool | None = None,
) -> User:
    if full_name is not None:
        user.full_name = full_name
    if is_active is not None:
        user.is_active = is_active
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_password(db: Session, user: User, new_password: str) -> None:
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
