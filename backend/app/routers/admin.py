from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import get_db
from .. import schemas, models
from ..services.auth import get_current_user
from ..utils.security import get_password_hash
from ..schemas.common import SuccessResponse

router = APIRouter()


async def require_admin(current_user: models.User = Depends(get_current_user)):
    """
    检查当前用户是否为管理员
    """
    if current_user.username != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can access this endpoint"
        )
    return current_user


@router.get("/users", response_model=SuccessResponse)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    获取所有用户列表（仅管理员）
    """
    from ..crud.user import user as user_crud
    users = await user_crud.get_multi(db, skip=skip, limit=limit)

    # 转换为字典列表，不包含密码哈希
    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        })

    return SuccessResponse(
        code=200,
        message="Users retrieved successfully",
        data=user_list
    )


@router.post("/users/{user_id}/reset-password", response_model=SuccessResponse)
async def reset_user_password(
    user_id: int,
    password_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    重置用户密码（仅管理员）
    """
    from ..crud.user import user as user_crud

    # 获取用户
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 获取新密码
    new_password = password_data.get("new_password")
    if not new_password or len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )

    # 更新密码
    user.hashed_password = get_password_hash(new_password)
    await db.commit()
    await db.refresh(user)

    return SuccessResponse(
        code=200,
        message=f"Password reset successfully for user '{user.username}'",
        data={"username": user.username}
    )


@router.put("/users/{user_id}/status", response_model=SuccessResponse)
async def update_user_status(
    user_id: int,
    status_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    更新用户状态（启用/禁用）（仅管理员）
    """
    from ..crud.user import user as user_crud

    # 获取用户
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 不能禁用管理员自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disable yourself"
        )

    # 更新状态
    is_active = status_data.get("is_active")
    if is_active is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="is_active field is required"
        )

    user.is_active = is_active
    await db.commit()
    await db.refresh(user)

    status_text = "enabled" if is_active else "disabled"
    return SuccessResponse(
        code=200,
        message=f"User '{user.username}' has been {status_text}",
        data={
            "id": user.id,
            "username": user.username,
            "is_active": user.is_active
        }
    )
