"""报表相关路由"""
from datetime import datetime, date
from typing import Optional
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from app.database import get_db
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.budget import Budget
from app.models.user import User
from app.config import settings

router = APIRouter()


@router.get("/monthly-summary")
async def get_monthly_summary(
    year: int = Query(..., description="年份"),
    month: int = Query(..., description="月份"),
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """获取月度收支汇总"""
    # 使用 MySQL DATE_FORMAT 替代 PostgreSQL 的 to_char
    # 收入
    income_stmt = (
        select(
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
            func.DATE_FORMAT(Transaction.transaction_date, "%Y-%m").label("month"),
        )
        .where(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "income",
            func.YEAR(Transaction.transaction_date) == year,
            func.MONTH(Transaction.transaction_date) == month,
        )
        .group_by(func.DATE_FORMAT(Transaction.transaction_date, "%Y-%m"))
    )
    income_result = await db.execute(income_stmt)
    income_row = income_result.first()
    total_income = float(income_row[0]) if income_row else 0.0

    # 支出
    expense_stmt = (
        select(
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
            func.DATE_FORMAT(Transaction.transaction_date, "%Y-%m").label("month"),
        )
        .where(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense",
            func.YEAR(Transaction.transaction_date) == year,
            func.MONTH(Transaction.transaction_date) == month,
        )
        .group_by(func.DATE_FORMAT(Transaction.transaction_date, "%Y-%m"))
    )
    expense_result = await db.execute(expense_stmt)
    expense_row = expense_result.first()
    total_expense = float(expense_row[0]) if expense_row else 0.0

    return {
        "year": year,
        "month": month,
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "net": round(total_income - total_expense, 2),
    }


@router.get("/category-expense")
async def get_category_expense(
    year: int = Query(..., description="年份"),
    month: int = Query(..., description="月份"),
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """获取分类支出占比"""
    stmt = (
        select(
            Category.name.label("category_name"),
            func.sum(Transaction.amount).label("total"),
        )
        .join(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense",
            func.YEAR(Transaction.transaction_date) == year,
            func.MONTH(Transaction.transaction_date) == month,
        )
        .group_by(Category.name)
        .order_by(func.sum(Transaction.amount).desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    categories = [
        {"name": row[0], "amount": round(float(row[1]), 2)}
        for row in rows
    ]

    total = sum(c["amount"] for c in categories)
    for c in categories:
        c["percentage"] = round((c["amount"] / total * 100), 2) if total > 0 else 0

    return {"year": year, "month": month, "categories": categories, "total": round(total, 2)}


@router.get("/budget-execution")
async def get_budget_execution(
    year: int = Query(..., description="年份"),
    month: int = Query(..., description="月份"),
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """获取预算执行报告"""
    # 获取该月所有预算
    budget_stmt = select(Budget).where(
        Budget.user_id == user_id,
        Budget.year == year,
        Budget.month == month,
    )
    budget_result = await db.execute(budget_stmt)
    budgets = budget_result.scalars().all()

    results = []
    for budget in budgets:
        # 查询该分类的实际支出
        expense_stmt = (
            select(func.coalesce(func.sum(Transaction.amount), 0))
            .where(
                Transaction.user_id == user_id,
                Transaction.category_id == budget.category_id,
                Transaction.transaction_type == "expense",
                func.YEAR(Transaction.transaction_date) == year,
                func.MONTH(Transaction.transaction_date) == month,
            )
        )
        expense_result = await db.execute(expense_stmt)
        actual = float(expense_result.scalar() or 0)

        # 获取分类名称
        cat_stmt = select(Category.name).where(Category.id == budget.category_id)
        cat_result = await db.execute(cat_stmt)
        cat_name = cat_result.scalar() or "未知分类"

        executed_pct = round((actual / budget.amount * 100), 2) if budget.amount > 0 else 0

        results.append({
            "category_id": budget.category_id,
            "category_name": cat_name,
            "budget_amount": round(budget.amount, 2),
            "actual_amount": round(actual, 2),
            "executed_percentage": executed_pct,
            "remaining": round(budget.amount - actual, 2),
            "is_over": actual > budget.amount,
        })

    return {
        "year": year,
        "month": month,
        "budgets": results,
    }


@router.get("/daily-trend")
async def get_daily_trend(
    year: int = Query(..., description="年份"),
    month: int = Query(..., description="月份"),
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """获取每日收支趋势"""
    stmt = (
        select(
            func.DATE_FORMAT(Transaction.transaction_date, "%Y-%m-%d").label("day"),
            Transaction.transaction_type.label("type"),
            func.sum(Transaction.amount).label("total"),
        )
        .where(
            Transaction.user_id == user_id,
            func.YEAR(Transaction.transaction_date) == year,
            func.MONTH(Transaction.transaction_date) == month,
        )
        .group_by(
            func.DATE_FORMAT(Transaction.transaction_date, "%Y-%m-%d"),
            Transaction.transaction_type,
        )
        .order_by(func.DATE_FORMAT(Transaction.transaction_date, "%Y-%m-%d"))
    )
    result = await db.execute(stmt)
    rows = result.all()

    # 构建每日数据
    daily_data = {}
    for row in rows:
        day = row[0]
        if day not in daily_data:
            daily_data[day] = {"day": day, "income": 0, "expense": 0}
        if row[1] == "income":
            daily_data[day]["income"] = round(float(row[2]), 2)
        else:
            daily_data[day]["expense"] = round(float(row[2]), 2)

    # 按日期排序
    sorted_data = sorted(daily_data.values(), key=lambda x: x["day"])

    return {"year": year, "month": month, "daily_data": sorted_data}


@router.get("/yearly-summary")
async def get_yearly_summary(
    year: int = Query(..., description="年份"),
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """获取年度收支汇总"""
    stmt = (
        select(
            func.DATE_FORMAT(Transaction.transaction_date, "%Y-%m").label("month"),
            Transaction.transaction_type.label("type"),
            func.sum(Transaction.amount).label("total"),
        )
        .where(
            Transaction.user_id == user_id,
            func.YEAR(Transaction.transaction_date) == year,
        )
        .group_by(
            func.DATE_FORMAT(Transaction.transaction_date, "%Y-%m"),
            Transaction.transaction_type,
        )
        .order_by(func.DATE_FORMAT(Transaction.transaction_date, "%Y-%m"))
    )
    result = await db.execute(stmt)
    rows = result.all()

    # 构建月度数据
    monthly = {}
    for row in rows:
        m = row[0]
        if m not in monthly:
            monthly[m] = {"month": m, "income": 0, "expense": 0}
        if row[1] == "income":
            monthly[m]["income"] = round(float(row[2]), 2)
        else:
            monthly[m]["expense"] = round(float(row[2]), 2)

    sorted_monthly = sorted(monthly.values(), key=lambda x: x["month"])

    return {"year": year, "monthly_data": sorted_monthly}


# ==================== 数据导出 ====================

@router.get("/export/csv")
async def export_csv(
    year: int = Query(..., description="年份"),
    month: int = Query(..., description="月份"),
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """导出月度交易记录为 CSV"""
    stmt = (
        select(
            Transaction.transaction_date,
            Category.name.label("category_name"),
            Transaction.transaction_type,
            Transaction.amount,
            Transaction.description,
            Transaction.tags,
        )
        .join(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user_id,
            func.YEAR(Transaction.transaction_date) == year,
            func.MONTH(Transaction.transaction_date) == month,
        )
        .order_by(Transaction.transaction_date)
    )
    result = await db.execute(stmt)
    rows = result.all()

    import csv
    output = BytesIO()
    writer = csv.writer(output)
    writer.writerow(["日期", "分类", "类型", "金额", "描述", "标签"])
    for row in rows:
        writer.writerow([
            row[0].strftime("%Y-%m-%d") if row[0] else "",
            row[1] or "",
            "收入" if row[2] == "income" else "支出",
            round(float(row[3]), 2) if row[3] else 0,
            row[4] or "",
            row[5] or "",
        ])

    output.seek(0)
    filename = f"transactions_{year}_{month:02d}.csv"
    return Response(
        content=output.read(),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/excel")
async def export_excel(
    year: int = Query(..., description="年份"),
    month: int = Query(..., description="月份"),
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """导出月度交易记录为 Excel"""
    stmt = (
        select(
            Transaction.transaction_date,
            Category.name.label("category_name"),
            Transaction.transaction_type,
            Transaction.amount,
            Transaction.description,
            Transaction.tags,
        )
        .join(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user_id,
            func.YEAR(Transaction.transaction_date) == year,
            func.MONTH(Transaction.transaction_date) == month,
        )
        .order_by(Transaction.transaction_date)
    )
    result = await db.execute(stmt)
    rows = result.all()

    wb = Workbook()
    ws = wb.active
    ws.title = f"{year}年{month}月"

    # 表头
    headers = ["日期", "分类", "类型", "金额", "描述", "标签"]
    for col_idx, header in enumerate(headers, 1):
        ws.cell(row=1, column=col_idx, value=header)

    # 数据
    for row_idx, row in enumerate(rows, 2):
        ws.cell(row=row_idx, column=1, value=row[0].strftime("%Y-%m-%d") if row[0] else "")
        ws.cell(row=row_idx, column=2, value=row[1] or "")
        ws.cell(row=row_idx, column=3, value="收入" if row[2] == "income" else "支出")
        ws.cell(row=row_idx, column=4, value=round(float(row[3]), 2) if row[3] else 0)
        ws.cell(row=row_idx, column=5, value=row[4] or "")
        ws.cell(row=row_idx, column=6, value=row[5] or "")

    # 自动调整列宽
    for col in ws.columns:
        max_length = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        ws.column_dimensions[col_letter].width = max_length + 4

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f"transactions_{year}_{month:02d}.xlsx"
    return Response(
        content=output.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ==================== 数据备份与恢复 ====================

@router.post("/backup")
async def create_backup(
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """创建数据库备份"""
    import subprocess
    import os

    backup_dir = settings.BACKUP_DIR
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"wallet_butler_backup_{timestamp}.sql"
    filepath = os.path.join(backup_dir, filename)

    # 使用 mysqldump 进行备份
    db_url = settings.DATABASE_URL
    # 解析数据库连接信息
    # 格式: mysql+aiomysql://user:password@host:port/dbname
    import re
    match = re.match(r'mysql\+aiomysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
    if not match:
        raise HTTPException(status_code=500, detail="数据库连接配置错误")

    db_user, db_password, db_host, db_port, db_name = match.groups()

    try:
        env = os.environ.copy()
        env['MYSQL_PWD'] = db_password
        result = subprocess.run(
            [
                "mysqldump",
                f"--host={db_host}",
                f"--port={db_port}",
                f"--user={db_user}",
                f"--databases={db_name}",
                "--single-transaction",
                "--routines",
                "--triggers",
                "--events",
                "-r", filepath,
            ],
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"备份失败: {result.stderr}")

        file_size = os.path.getsize(filepath)
        return {
            "message": "备份成功",
            "filename": filename,
            "filepath": filepath,
            "size": file_size,
            "created_at": timestamp,
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="备份超时")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="mysqldump 命令未找到，请确保已安装 MySQL 客户端")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"备份失败: {str(e)}")


@router.get("/backups")
async def list_backups(
    user_id: int = Query(..., description="用户ID"),
):
    """列出所有备份文件"""
    import os

    backup_dir = settings.BACKUP_DIR
    if not os.path.exists(backup_dir):
        return {"backups": []}

    backups = []
    for filename in sorted(os.listdir(backup_dir), reverse=True):
        if filename.endswith(".sql"):
            filepath = os.path.join(backup_dir, filename)
            stat = os.stat(filepath)
            backups.append({
                "filename": filename,
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            })

    return {"backups": backups}


@router.delete("/backups/{filename}")
async def delete_backup(
    filename: str,
    user_id: int = Query(..., description="用户ID"),
):
    """删除指定备份"""
    import os
    import re

    # 安全检查：防止路径遍历
    if not re.match(r'^wallet_butler_backup_\d{8}_\d{6}\.sql$', filename):
        raise HTTPException(status_code=400, detail="无效的备份文件名")

    backup_dir = settings.BACKUP_DIR
    filepath = os.path.join(backup_dir, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="备份文件不存在")

    try:
        os.remove(filepath)
        return {"message": "备份已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/restore")
async def restore_backup(
    filename: str = Query(..., description="备份文件名"),
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """从备份恢复数据"""
    import subprocess
    import os
    import re

    # 安全检查
    if not re.match(r'^wallet_butler_backup_\d{8}_\d{6}\.sql$', filename):
        raise HTTPException(status_code=400, detail="无效的备份文件名")

    backup_dir = settings.BACKUP_DIR
    filepath = os.path.join(backup_dir, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="备份文件不存在")

    # 解析数据库连接信息
    db_url = settings.DATABASE_URL
    match = re.match(r'mysql\+aiomysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
    if not match:
        raise HTTPException(status_code=500, detail="数据库连接配置错误")

    db_user, db_password, db_host, db_port, db_name = match.groups()

    try:
        env = os.environ.copy()
        env['MYSQL_PWD'] = db_password
        result = subprocess.run(
            [
                "mysql",
                f"--host={db_host}",
                f"--port={db_port}",
                f"--user={db_user}",
                db_name,
            ],
            env=env,
            capture_output=True,
            text=True,
            timeout=600,
            stdin=open(filepath, "r"),
        )
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"恢复失败: {result.stderr}")

        return {"message": "数据恢复成功"}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="恢复超时")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="mysql 命令未找到，请确保已安装 MySQL 客户端")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"恢复失败: {str(e)}")
