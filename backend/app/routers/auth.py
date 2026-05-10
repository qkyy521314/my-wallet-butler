from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from .. import schemas, crud, models, utils
from ..services.auth import create_access_token, authenticate_user, get_current_user
from ..schemas.common import SuccessResponse


router = APIRouter()


@router.post("/register", response_model=SuccessResponse)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # 检查用户名或邮箱是否已存在
    existing_user = await crud.user.get_by_username_or_email(db, user.username, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    # 创建新用户
    user_data = user.model_dump()
    user_data['hashed_password'] = utils.security.get_password_hash(user.password)
    db_user = await crud.user.create(db, user_data)
    user_out = schemas.User.model_validate(db_user)
    return SuccessResponse(code=200, message="User registered successfully", data=user_out.model_dump())


@router.post("/login", response_model=SuccessResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    token_data = {"access_token": access_token, "token_type": "bearer"}
    return SuccessResponse(code=200, message="Login successful", data=token_data)


@router.get("/me", response_model=SuccessResponse)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    user_out = schemas.User.model_validate(current_user)
    return SuccessResponse(code=200, message="User information retrieved", data=user_out.model_dump())


@router.put("/profile", response_model=SuccessResponse)
async def update_profile(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户个人信息
    """
    updated_user = await crud.user.update(db, db_obj=current_user, obj_in=user_update)
    user_out = schemas.User.model_validate(updated_user)
    return SuccessResponse(code=200, message="Profile updated successfully", data=user_out.model_dump())