from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from fastapi.responses import JSONResponse
import pandas as pd
import io
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from .. import schemas, crud
from ..models.transaction import Transaction
from ..models.category import Category
from ..models.account import Account
from sqlalchemy import select

router = APIRouter()


@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    delimiter: str = Form(","),
    encoding: str = Form("utf-8"),
    db: AsyncSession = Depends(get_db)
):
    """CSV 文件导入交易记录"""
    try:
        # 检查文件类型
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")

        # 读取文件内容
        contents = await file.read()

        # 解析 CSV 文件
        df = pd.read_csv(io.StringIO(contents.decode(encoding)), delimiter=delimiter)

        # 验证必需的列
        required_columns = ['amount', 'description', 'category', 'account']
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            raise HTTPException(status_code=400, detail=f"Missing required columns: {missing_cols}")

        # 从数据库中获取现有分类和账户
        categories_result = await db.execute(select(Category))
        categories = {cat.name.lower(): cat.id for cat in categories_result.scalars().all()}

        accounts_result = await db.execute(select(Account))
        accounts = {acc.name.lower(): acc.id for acc in accounts_result.scalars().all()}

        # 验证并准备数据
        errors = []
        valid_transactions = []

        for idx, row in df.iterrows():
            error_msg = []

            # 验证金额
            try:
                amount = float(row['amount'])
            except (ValueError, TypeError):
                error_msg.append(f"Invalid amount: {row['amount']}")

            # 验证交易类型
            trans_type = 'expense' if amount < 0 else 'income'
            amount = abs(amount)  # 使用绝对值，正数为收入，负数为支出

            # 验证分类
            category_name = str(row['category']).lower()
            if category_name not in categories:
                error_msg.append(f"Category '{row['category']}' does not exist")

            # 验证账户
            account_name = str(row['account']).lower()
            if account_name not in accounts:
                error_msg.append(f"Account '{row['account']}' does not exist")

            if error_msg:
                errors.append({"row": idx + 1, "errors": error_msg})
            else:
                # 准备有效交易数据
                transaction_data = {
                    "amount": amount,
                    "description": str(row['description']) if pd.notna(row['description']) else "",
                    "transaction_type": trans_type,
                    "category_id": categories[category_name],
                    "account_id": accounts[account_name],
                    "user_id": user_id,
                    "date": datetime.now()
                }

                # 如果有可选字段，也包括它们
                if 'date' in df.columns and pd.notna(row['date']):
                    try:
                        transaction_data['date'] = datetime.fromisoformat(str(row['date']))
                    except ValueError:
                        transaction_data['date'] = datetime.now()

                valid_transactions.append(transaction_data)

        # 插入有效交易
        successful_count = 0
        for trans_data in valid_transactions:
            try:
                schema_data = schemas.TransactionCreate(**trans_data)
                await crud.transaction.create(db, schema_data)
                successful_count += 1
            except Exception as e:
                errors.append({"row": len(errors) + successful_count + 1, "errors": [str(e)]})

        return {
            "total_processed": len(df),
            "successful_imports": successful_count,
            "failed_imports": len(errors),
            "errors": errors
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-excel")
async def upload_excel(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    sheet_name: str = Form("Sheet1"),
    db: AsyncSession = Depends(get_db)
):
    """Excel 文件导入交易记录"""
    try:
        # 检查文件类型
        if not (file.filename.lower().endswith('.xlsx') or file.filename.lower().endswith('.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed")

        # 读取文件内容
        contents = await file.read()
        buffer = io.BytesIO(contents)

        # 解析 Excel 文件
        df = pd.read_excel(buffer, sheet_name=sheet_name)

        # 验证必需的列
        required_columns = ['amount', 'description', 'category', 'account']
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            raise HTTPException(status_code=400, detail=f"Missing required columns: {missing_cols}")

        # 从数据库中获取现有分类和账户
        categories_result = await db.execute(select(Category))
        categories = {cat.name.lower(): cat.id for cat in categories_result.scalars().all()}

        accounts_result = await db.execute(select(Account))
        accounts = {acc.name.lower(): acc.id for acc in accounts_result.scalars().all()}

        # 验证并准备数据
        errors = []
        valid_transactions = []

        for idx, row in df.iterrows():
            error_msg = []

            # 验证金额
            try:
                amount = float(row['amount'])
            except (ValueError, TypeError):
                error_msg.append(f"Invalid amount: {row['amount']}")

            # 验证交易类型
            trans_type = 'expense' if amount < 0 else 'income'
            amount = abs(amount)  # 使用绝对值，正数为收入，负数为支出

            # 验证分类
            category_name = str(row['category']).lower()
            if category_name not in categories:
                error_msg.append(f"Category '{row['category']}' does not exist")

            # 验证账户
            account_name = str(row['account']).lower()
            if account_name not in accounts:
                error_msg.append(f"Account '{row['account']}' does not exist")

            if error_msg:
                errors.append({"row": idx + 1, "errors": error_msg})
            else:
                # 准备有效交易数据
                transaction_data = {
                    "amount": amount,
                    "description": str(row['description']) if pd.notna(row['description']) else "",
                    "transaction_type": trans_type,
                    "category_id": categories[category_name],
                    "account_id": accounts[account_name],
                    "user_id": user_id,
                    "date": datetime.now()
                }

                # 如果有可选字段，也包括它们
                if 'date' in df.columns and pd.notna(row['date']):
                    try:
                        transaction_data['date'] = datetime.fromisoformat(str(row['date']))
                    except ValueError:
                        transaction_data['date'] = datetime.now()

                valid_transactions.append(transaction_data)

        # 插入有效交易
        successful_count = 0
        for trans_data in valid_transactions:
            try:
                schema_data = schemas.TransactionCreate(**trans_data)
                await crud.transaction.create(db, schema_data)
                successful_count += 1
            except Exception as e:
                errors.append({"row": len(errors) + successful_count + 1, "errors": [str(e)]})

        return {
            "total_processed": len(df),
            "successful_imports": successful_count,
            "failed_imports": len(errors),
            "errors": errors
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview-csv")
async def preview_csv(file: UploadFile = File(...), delimiter: str = Form(","), encoding: str = Form("utf-8"), rows: int = Form(10)):
    """CSV 文件导入预览"""
    try:
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")

        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode(encoding)), delimiter=delimiter)

        # 只返回前几行作为预览
        preview_data = df.head(rows).to_dict('records')

        return {
            "columns": df.columns.tolist(),
            "preview_data": preview_data,
            "total_rows": len(df)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview-excel")
async def preview_excel(file: UploadFile = File(...), sheet_name: str = Form("Sheet1"), rows: int = Form(10)):
    """Excel 文件导入预览"""
    try:
        if not (file.filename.lower().endswith('.xlsx') or file.filename.lower().endswith('.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed")

        contents = await file.read()
        buffer = io.BytesIO(contents)
        df = pd.read_excel(buffer, sheet_name=sheet_name)

        # 只返回前几行作为预览
        preview_data = df.head(rows).to_dict('records')

        return {
            "columns": df.columns.tolist(),
            "preview_data": preview_data,
            "total_rows": len(df)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))