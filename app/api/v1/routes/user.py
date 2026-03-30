import json
import logging
import uuid
from math import ceil

from app.api.v1.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.core.config import settings
from app.core.redis import redis_client
from app.db.session import get_db
from app.models.user import User
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def find_user_by_id(user_id: uuid.UUID, db: Session):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def find_user_by_email(email: str, db: Session, user_id: uuid.UUID | None = None):
    user = db.query(User).filter(User.email == email).first()
    if user and user.id != user_id:
        raise HTTPException(status_code=409, detail="Email existing")


def invalidate_user_cache(user_id: int | None = None):
    list_keys = redis_client.keys("users:list:*")

    if list_keys:
        redis_client.delete(*list_keys)
        logger.info("CACHE INVALIDATE LIST - keys=%s", list_keys)

    if user_id is not None:
        redis_client.delete(f"users:detail:{user_id}")
        logger.info("CACHE INVALIDATE DETAIL - key=%s", user_id)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    find_user_by_email(payload.email, db)

    # Criação do usuário
    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("USER CREATED - id=%s cache invalidated", user.id)
    invalidate_user_cache()
    return user


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    size: int = Query(10, ge=1, le=100, description="Number of records per page"),
    db: Session = Depends(get_db),
):
    cache_key = f"users:list:page={page}:size={size}"

    cached = redis_client.get(cache_key)
    if cached:
        logger.info("CACHE HIT - key=%s", cache_key)
        return UserListResponse.model_validate_json(cached)

    logger.info("CACHE MISS - key=%s", cache_key)

    skip = (page - 1) * size
    total = db.query(User).count()
    users = db.query(User).offset(skip).limit(size).all()

    items = [UserResponse.model_validate(user, from_attributes=True) for user in users]

    response = UserListResponse(
        items=items, page=page, size=size, total=total, pages=ceil(total / size) if total > 0 else 1
    )

    redis_client.setex(cache_key, settings.CACHE_TTL, response.model_dump_json())
    logger.info("CACHE SET - key=%s ttl=%s", cache_key, settings.CACHE_TTL)
    return response


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    cache_key = f"users:detail:{user_id}"

    cached = redis_client.get(cache_key)
    if cached:
        logger.info("CACHE HIT - key=%s", cache_key)
        return json.loads(cached)

    logger.info("CACHE MISS - key=%s", cache_key)
    user = find_user_by_id(user_id, db)

    response = UserResponse.model_validate(user, from_attributes=True)

    redis_client.setex(cache_key, settings.CACHE_TTL, response.model_dump_json())
    logger.info("CACHE SET - key=%s ttl=%s", cache_key, settings.CACHE_TTL)
    return response


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user = find_user_by_id(user_id, db)
    db.delete(user)
    db.commit()

    invalidate_user_cache(user_id)
    logger.info("USER DELETED - id=%s cache invalidated", user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: uuid.UUID, payload: UserUpdate, db: Session = Depends(get_db)):
    user = find_user_by_id(user_id, db)
    find_user_by_email(payload.email, db, user_id)

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    invalidate_user_cache(user.id)
    logger.info("USER UPDATED - id=%s cache invalidated", user.id)

    return user
