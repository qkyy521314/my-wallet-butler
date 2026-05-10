from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..database import get_db
from .. import schemas, crud, models
from ..services.auth import get_current_user
from ..schemas.common import SuccessResponse
from ..utils.exceptions import InsufficientPermissions

router = APIRouter()


@router.get("")
@router.get("/", response_model=List[schemas.Tag])
async def get_tags(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    tags = await crud.tag.get_multi(db, skip=skip, limit=limit)
    return tags


@router.get("/{tag_id}", response_model=schemas.Tag)
async def get_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    tag = await crud.tag.get(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.post("/")
@router.post("")
async def create_tag(
    tag: schemas.TagCreate,
    db: AsyncSession = Depends(get_db)
):
    db_tag = await crud.tag.create(db, tag)
    return db_tag


@router.put("/{tag_id}", response_model=schemas.Tag)
async def update_tag(
    tag_id: int,
    tag_update: schemas.TagUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_tag = await crud.tag.get(db, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    updated_tag = await crud.tag.update(db, db_tag, tag_update)
    return updated_tag


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    tag = await crud.tag.get(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    await crud.tag.remove(db, tag_id)
    return {"success": True, "message": "Tag deleted successfully"}


@router.get("/{tag_id}/transactions", response_model=List[schemas.Transaction])
async def get_transactions_by_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """获取带有指定标签的交易列表"""
    from ..models.transaction import Transaction
    from sqlalchemy import select, and_
    from sqlalchemy.orm import selectinload

    # 先检查标签是否存在
    tag = await crud.tag.get(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # 需要先将 Transaction 导入
    from ..models.transaction_tag import TransactionTag

    # 查询带有所选标签的交易
    result = await db.execute(
        select(Transaction)
        .join(TransactionTag)
        .where(and_(TransactionTag.tag_id == tag_id, Transaction.user_id == tag.user_id))  # 确保权限控制
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/{transaction_id}/tags/{tag_id}")
async def add_tag_to_transaction(
    transaction_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db)
):
    """为交易添加标签"""
    # 检查交易和标签是否存在
    from ..models.transaction import Transaction
    transaction = await crud.transaction.get(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    tag = await crud.tag.get(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # 检查用户权限
    if transaction.user_id != tag.user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # 创建关联
    await crud.transaction_tag.create(db, transaction_id, tag_id)
    return {"success": True, "message": "Tag added to transaction successfully"}


@router.delete("/{transaction_id}/tags/{tag_id}")
async def remove_tag_from_transaction(
    transaction_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db)
):
    """从交易移除标签"""
    # 检查交易和标签是否存在
    from ..models.transaction import Transaction
    transaction = await crud.transaction.get(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    tag = await crud.tag.get(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # 检查用户权限
    if transaction.user_id != tag.user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    success = await crud.transaction_tag.remove_by_transaction_and_tag(db, transaction_id, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag association not found")

    return {"success": True, "message": "Tag removed from transaction successfully"}