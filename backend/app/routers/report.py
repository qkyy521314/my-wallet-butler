"""报表相关路由 - Phase 5"""
from datetime import datetime, timedelta, date as date_type
from typing import Optional
from io import BytesIO, StringIO
import csv
import json
import os

from fastapi import APIRouter, Depends, HTTPException, Query, Response, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.budget import Budget
from app.models.account import Account
from app.models.user import User
from app.models.tag import Tag
from app.services.auth import get_current_user
from app import crud

router = APIRouter()


def _get_user_id(current_user: User) -> int:
    return current_user.id


# ============================================================
# 报表查询
# ============================================================

@router.get("/summary")
async def get_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
):
    """收支概览统计（总收入、总支出、净收入）"""
    user_id = _get_user_id(current_user)
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

    income_stmt = select(func.sum(Transaction.amount)).where(
        and_(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "income",
            Transaction.date >= start_dt,
            Transaction.date <= end_dt,
            Transaction.is_active == True,
        )
    )
    income_result = await db.execute(income_stmt)
    total_income = income_result.scalar() or 0

    expense_stmt = select(func.sum(Transaction.amount)).where(
        and_(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense",
            Transaction.date >= start_dt,
            Transaction.date <= end_dt,
            Transaction.is_active == True,
        )
    )
    expense_result = await db.execute(expense_stmt)
    total_expense = expense_result.scalar() or 0

    net_income = total_income - total_expense

    return {
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "net_income": float(net_income),
        "date_range": {"start": start_date, "end": end_date},
    }


@router.get("/category-analysis")
async def get_category_analysis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    transaction_type: str = Query("expense", description="income or expense"),
):
    """分类支出/收入占比（饼图数据）"""
    user_id = _get_user_id(current_user)
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

    stmt = (
        select(
            func.sum(Transaction.amount).label("total"),
            Transaction.category_id,
            Category.name.label("category_name"),
        )
        .join(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user_id,
            Transaction.transaction_type == transaction_type,
            Transaction.date >= start_dt,
            Transaction.date <= end_dt,
            Transaction.is_active == True,
        )
        .group_by(Transaction.category_id, Category.name)
    )
    result = await db.execute(stmt)
    rows = result.fetchall()

    total_amount = sum(float(row[0] or 0) for row in rows)

    categories = []
    for row in rows:
        total = float(row[0] or 0)
        categories.append({
            "category_id": row[1],
            "category_name": row[2],
            "amount": total,
            "percentage": round((total / total_amount * 100) if total_amount > 0 else 0, 2),
        })

    return {
        "total_amount": total_amount,
        "categories": categories,
        "date_range": {"start": start_date, "end": end_date},
        "transaction_type": transaction_type,
    }


@router.get("/trend-analysis")
async def get_trend_analysis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    group_by: str = Query("day", description="day, week, or month"),
):
    """收支趋势（折线图数据）- MySQL DATE_FORMAT"""
    user_id = _get_user_id(current_user)
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

    fmt_map = {"day": "%Y-%m-%d", "week": "%Y-%u", "month": "%Y-%m"}
    fmt = fmt_map.get(group_by, "%Y-%m-%d")

    def _trend_stmt(tx_type):
        return (
            select(
                func.DATE_FORMAT(Transaction.date, fmt).label("date_group"),
                func.sum(Transaction.amount).label("total"),
            )
            .where(
                Transaction.user_id == user_id,
                Transaction.transaction_type == tx_type,
                Transaction.date >= start_dt,
                Transaction.date <= end_dt,
                Transaction.is_active == True,
            )
            .group_by(func.DATE_FORMAT(Transaction.date, fmt))
            .order_by(func.DATE_FORMAT(Transaction.date, fmt))
        )

    income_rows = (await db.execute(_trend_stmt("income"))).fetchall()
    expense_rows = (await db.execute(_trend_stmt("expense"))).fetchall()

    income_dict = {str(r.date_group): float(r.total or 0) for r in income_rows}
    expense_dict = {str(r.date_group): float(r.total or 0) for r in expense_rows}

    trend_data = []
    current = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)

    if group_by == "day":
        while current <= end_dt:
            key = current.strftime("%Y-%m-%d")
            inc = income_dict.get(key, 0)
            exp = expense_dict.get(key, 0)
            trend_data.append({"date": key, "income": inc, "expense": exp, "net": inc - exp})
            current += timedelta(days=1)
    elif group_by == "week":
        current = current - timedelta(days=current.weekday())
        while current <= end_dt:
            key = current.strftime("%Y-%u")
            inc = income_dict.get(key, 0)
            exp = expense_dict.get(key, 0)
            trend_data.append({"date": key, "income": inc, "expense": exp, "net": inc - exp})
            current += timedelta(weeks=1)
    else:
        while (current.year < end_dt.year) or (current.year == end_dt.year and current.month <= end_dt.month):
            key = current.strftime("%Y-%m")
            inc = income_dict.get(key, 0)
            exp = expense_dict.get(key, 0)
            trend_data.append({"date": key, "income": inc, "expense": exp, "net": inc - exp})
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

    return {
        "trend_data": trend_data,
        "group_by": group_by,
        "date_range": {"start": start_date, "end": end_date},
    }


@router.get("/monthly-report")
async def get_monthly_report(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    year: int = Query(..., description="Year"),
    month: int = Query(..., description="Month"),
):
    """月度报表汇总"""
    import calendar
    user_id = _get_user_id(current_user)
    start_date = datetime(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    end_date = datetime(year, month, last_day, 23, 59, 59)

    s, e = start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    # 复用 summary 和 category-analysis 逻辑
    summary = await get_summary(current_user, db, s, e)
    category_analysis = await get_category_analysis(current_user, db, s, e, "expense")

    # 预算执行
    budgets = await crud.budget.get_monthly_budgets(db, user_id, year, month)
    budget_performance = []
    for b in budgets:
        ub = await crud.budget.update_budget_spent_amount(db, b.id)
        budget_performance.append({
            "id": ub.id,
            "name": ub.name,
            "category_name": ub.category.name if ub.category else "Unknown",
            "budget_amount": float(ub.amount),
            "spent_amount": float(ub.spent_amount),
            "percentage_used": ub.spent_percentage,
            "is_over_spent": ub.is_over_spent,
        })

    return {
        "summary": summary,
        "category_analysis": category_analysis,
        "budget_performance": budget_performance,
        "report_period": {"year": year, "month": month},
    }


@router.get("/budget-performance")
async def get_budget_performance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
):
    """预算执行情况详细分析"""
    user_id = _get_user_id(current_user)
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

    stmt = select(Budget).where(
        and_(
            Budget.user_id == user_id,
            Budget.period_start <= end_dt,
            Budget.period_end >= start_dt,
            Budget.is_active == True,
        )
    )
    budgets = (await db.execute(stmt)).scalars().all()

    details = []
    for b in budgets:
        ub = await crud.budget.update_budget_spent_amount(db, b.id)
        details.append({
            "id": ub.id,
            "name": ub.name,
            "category_name": ub.category.name if ub.category else "Unknown",
            "budget_amount": float(ub.amount),
            "spent_amount": float(ub.spent_amount),
            "percentage_used": ub.spent_percentage,
            "is_over_spent": ub.is_over_spent,
            "period_start": ub.period_start.isoformat() if ub.period_start else None,
            "period_end": ub.period_end.isoformat() if ub.period_end else None,
        })

    return {
        "budgets": details,
        "date_range": {"start": start_date, "end": end_date},
    }


# ============================================================
# 数据导出 CSV / Excel
# ============================================================

def _build_transaction_query(user_id: int, start_date: Optional[str], end_date: Optional[str], transaction_type: Optional[str]):
    """构建交易查询（含分类、账户、标签）"""
    from sqlalchemy import text as sql_text
    stmt = (
        select(
            Transaction.id,
            Transaction.date,
            Transaction.amount,
            Transaction.transaction_type,
            Transaction.description,
            Category.name.label("category_name"),
            Account.name.label("account_name"),
            func.GROUP_CONCAT(Tag.name).label("tag_names"),
        )
        .outerjoin(Category, Transaction.category_id == Category.id)
        .outerjoin(Account, Transaction.account_id == Account.id)
        .outerjoin(Transaction.tags)
        .where(Transaction.user_id == user_id)
    )
    if start_date:
        stmt = stmt.where(Transaction.date >= datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        stmt = stmt.where(Transaction.date <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    if transaction_type:
        stmt = stmt.where(Transaction.transaction_type == transaction_type)
    stmt = stmt.group_by(Transaction.id).order_by(Transaction.date.desc())
    return stmt


@router.get("/export/csv")
async def export_csv(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None),
):
    """导出交易记录为 CSV"""
    user_id = _get_user_id(current_user)
    stmt = _build_transaction_query(user_id, start_date, end_date, transaction_type)
    rows = (await db.execute(stmt)).fetchall()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "日期", "金额", "类型", "描述", "分类", "账户", "标签"])
    for r in rows:
        writer.writerow([
            r[0],
            r[1].strftime("%Y-%m-%d %H:%M:%S") if r[1] else "",
            float(r[2]) if r[2] else 0,
            r[3],
            r[4] or "",
            r[5] or "",
            r[6] or "",
            r[7] or "",
        ])

    return Response(
        content=output.getvalue().encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="transactions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'},
    )


@router.get("/export/excel")
async def export_excel(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None),
):
    """导出交易记录为 Excel"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

    user_id = _get_user_id(current_user)
    stmt = _build_transaction_query(user_id, start_date, end_date, transaction_type)
    rows = (await db.execute(stmt)).fetchall()

    summary = await get_summary(current_user, db, start_date or "2020-01-01", end_date or datetime.now().strftime("%Y-%m-%d"))

    wb = Workbook()
    ws = wb.active
    ws.title = "交易记录"

    hf = Font(bold=True, color="FFFFFF", size=11)
    hfill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    ha = Alignment(horizontal="center", vertical="center")
    tb = Border(left=Side(style="thin"), right=Side(style="thin"), top=Side(style="thin"), bottom=Side(style="thin"))

    headers = ["ID", "日期", "金额", "类型", "描述", "分类", "账户", "标签"]
    for ci, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=ci, value=h)
        c.font, c.fill, c.alignment, c.border = hf, hfill, ha, tb

    for ri, r in enumerate(rows, 2):
        ws.cell(row=ri, column=1, value=r[0]).border = tb
        c2 = ws.cell(row=ri, column=2, value=r[1].strftime("%Y-%m-%d %H:%M:%S") if r[1] else "")
        c2.border = tb
        c3 = ws.cell(row=ri, column=3, value=float(r[2]) if r[2] else 0)
        c3.border, c3.number_format = tb, "#,##0.00"
        ws.cell(row=ri, column=4, value=r[3]).border = tb
        ws.cell(row=ri, column=5, value=r[4] or "").border = tb
        ws.cell(row=ri, column=6, value=r[5] or "").border = tb
        ws.cell(row=ri, column=7, value=r[6] or "").border = tb
        ws.cell(row=ri, column=8, value=r[7] or "").border = tb

    for col in ws.columns:
        ml = 0
        cl = col[0].column_letter
        for cell in col:
            try:
                if cell.value:
                    ml = max(ml, len(str(cell.value)))
            except Exception:
                pass
        ws.column_dimensions[cl].width = min(ml + 4, 40)

    ws2 = wb.create_sheet(title="汇总")
    ws2.cell(row=1, column=1, value="总收入").font = Font(bold=True)
    ws2.cell(row=1, column=2, value=summary["total_income"]).number_format = "#,##0.00"
    ws2.cell(row=2, column=1, value="总支出").font = Font(bold=True)
    ws2.cell(row=2, column=2, value=summary["total_expense"]).number_format = "#,##0.00"
    ws2.cell(row=3, column=1, value="净收入").font = Font(bold=True)
    ws2.cell(row=3, column=2, value=summary["net_income"]).number_format = "#,##0.00"

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="transactions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'},
    )


# ============================================================
# 数据备份与恢复（JSON 格式）
# ============================================================

BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups")


def _ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


@router.post("/backup")
async def create_backup(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建用户数据备份（JSON 格式）"""
    user_id = _get_user_id(current_user)
    _ensure_backup_dir()

    # 账户
    accounts = (await db.execute(select(Account).where(Account.user_id == user_id))).scalars().all()
    accounts_data = [{
        "id": a.id, "name": a.name, "account_type": a.account_type,
        "balance": float(a.balance), "currency": a.currency,
        "description": a.description, "is_active": a.is_active,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    } for a in accounts]

    # 分类
    categories = (await db.execute(select(Category).where(Category.user_id == user_id))).scalars().all()
    categories_data = [{
        "id": c.id, "name": c.name, "category_type": c.category_type,
        "description": c.description, "is_active": c.is_active,
        "parent_id": c.parent_id,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    } for c in categories]

    # 标签
    tags = (await db.execute(select(Tag).where(Tag.user_id == user_id))).scalars().all()
    tags_data = [{
        "id": t.id, "name": t.name, "color": t.color,
        "description": t.description, "is_active": t.is_active,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    } for t in tags]

    # 交易
    transactions = (await db.execute(
        select(Transaction).where(Transaction.user_id == user_id).order_by(Transaction.date)
    )).scalars().all()
    transactions_data = []
    for t in transactions:
        transactions_data.append({
            "id": t.id, "amount": float(t.amount), "description": t.description,
            "transaction_type": t.transaction_type,
            "category_id": t.category_id, "account_id": t.account_id,
            "from_account_id": t.from_account_id, "to_account_id": t.to_account_id,
            "date": t.date.isoformat() if t.date else None,
            "is_active": t.is_active,
            "tag_ids": [tag.id for tag in t.tags] if t.tags else [],
            "created_at": t.created_at.isoformat() if t.created_at else None,
        })

    # 预算
    budgets = (await db.execute(select(Budget).where(Budget.user_id == user_id))).scalars().all()
    budgets_data = [{
        "id": b.id, "name": b.name, "category_id": b.category_id,
        "amount": float(b.amount),
        "period_start": b.period_start.isoformat() if b.period_start else None,
        "period_end": b.period_end.isoformat() if b.period_end else None,
        "description": b.description, "is_active": b.is_active,
        "created_at": b.created_at.isoformat() if b.created_at else None,
    } for b in budgets]

    backup_data = {
        "version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "user_id": user_id,
        "accounts": accounts_data,
        "categories": categories_data,
        "tags": tags_data,
        "transactions": transactions_data,
        "budgets": budgets_data,
    }

    filename = f"backup_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(BACKUP_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)

    return {
        "message": "备份创建成功",
        "filename": filename,
        "record_counts": {
            "accounts": len(accounts_data),
            "categories": len(categories_data),
            "tags": len(tags_data),
            "transactions": len(transactions_data),
            "budgets": len(budgets_data),
        },
    }


@router.get("/backup/list")
async def list_backups(
    current_user: User = Depends(get_current_user),
):
    """列出用户的所有备份文件"""
    user_id = _get_user_id(current_user)
    _ensure_backup_dir()

    backups = []
    if os.path.exists(BACKUP_DIR):
        for fname in sorted(os.listdir(BACKUP_DIR), reverse=True):
            if fname.startswith(f"backup_{user_id}_") and fname.endswith(".json"):
                fpath = os.path.join(BACKUP_DIR, fname)
                stat = os.stat(fpath)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    backups.append({
                        "filename": fname,
                        "size_bytes": stat.st_size,
                        "created_at": stat.st_ctime,
                        "exported_at": data.get("exported_at", ""),
                        "record_counts": {
                            "accounts": len(data.get("accounts", [])),
                            "categories": len(data.get("categories", [])),
                            "tags": len(data.get("tags", [])),
                            "transactions": len(data.get("transactions", [])),
                            "budgets": len(data.get("budgets", [])),
                        },
                    })
                except Exception:
                    backups.append({
                        "filename": fname,
                        "size_bytes": stat.st_size,
                        "created_at": stat.st_ctime,
                        "exported_at": "",
                        "record_counts": {},
                    })

    return {"backups": backups}


@router.get("/backup/download/{filename}")
async def download_backup(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    """下载备份文件"""
    user_id = _get_user_id(current_user)
    _ensure_backup_dir()

    safe_filename = os.path.basename(filename)
    if not safe_filename.startswith(f"backup_{user_id}_"):
        raise HTTPException(status_code=403, detail="无权访问此备份文件")

    filepath = os.path.join(BACKUP_DIR, safe_filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="备份文件不存在")

    return FileResponse(path=filepath, media_type="application/json", filename=safe_filename)


@router.delete("/backup/delete/{filename}")
async def delete_backup(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    """删除备份文件"""
    user_id = _get_user_id(current_user)
    _ensure_backup_dir()

    safe_filename = os.path.basename(filename)
    if not safe_filename.startswith(f"backup_{user_id}_"):
        raise HTTPException(status_code=403, detail="无权删除此备份文件")

    filepath = os.path.join(BACKUP_DIR, safe_filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="备份文件不存在")

    os.remove(filepath)
    return {"message": f"备份文件 {safe_filename} 已删除"}


@router.post("/restore")
async def restore_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    backup_file: str = Query(..., description="备份文件名"),
    mode: str = Query("merge", description="merge(合并) 或 replace(替换)"),
):
    """从备份文件恢复数据"""
    user_id = _get_user_id(current_user)
    _ensure_backup_dir()

    safe_filename = os.path.basename(backup_file)
    if not safe_filename.startswith(f"backup_{user_id}_"):
        raise HTTPException(status_code=403, detail="无权访问此备份文件")

    filepath = os.path.join(BACKUP_DIR, safe_filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="备份文件不存在")

    with open(filepath, "r", encoding="utf-8") as f:
        backup_data = json.load(f)

    if backup_data.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="备份文件与当前用户不匹配")

    restored = {"accounts": 0, "categories": 0, "tags": 0, "transactions": 0, "budgets": 0}

    try:
        if mode == "replace":
            await db.execute(Transaction.__table__.delete().where(Transaction.user_id == user_id))
            await db.execute(Budget.__table__.delete().where(Budget.user_id == user_id))
            await db.execute(Tag.__table__.delete().where(Tag.user_id == user_id))
            await db.execute(Category.__table__.delete().where(Category.user_id == user_id))
            await db.execute(Account.__table__.delete().where(Account.user_id == user_id))
            await db.commit()

        id_map: dict = {"accounts": {}, "categories": {}, "tags": {}}

        # 恢复分类
        for cd in backup_data.get("categories", []):
            old_id = cd.pop("id", None)
            cat = Category(
                name=cd["name"], category_type=cd["category_type"],
                description=cd.get("description"), is_active=cd.get("is_active", True),
                parent_id=cd.get("parent_id"), user_id=user_id,
            )
            db.add(cat)
            await db.flush()
            if old_id:
                id_map["categories"][old_id] = cat.id
            restored["categories"] += 1

        # 恢复标签
        for td in backup_data.get("tags", []):
            old_id = td.pop("id", None)
            tag = Tag(
                name=td["name"], color=td.get("color"),
                description=td.get("description"), is_active=td.get("is_active", True),
                user_id=user_id,
            )
            db.add(tag)
            await db.flush()
            if old_id:
                id_map["tags"][old_id] = tag.id
            restored["tags"] += 1

        # 恢复账户
        for ad in backup_data.get("accounts", []):
            old_id = ad.pop("id", None)
            acc = Account(
                name=ad["name"], account_type=ad["account_type"],
                balance=ad.get("balance", 0), currency=ad.get("currency", "CNY"),
                description=ad.get("description"), is_active=ad.get("is_active", True),
                user_id=user_id,
            )
            db.add(acc)
            await db.flush()
            if old_id:
                id_map["accounts"][old_id] = acc.id
            restored["accounts"] += 1

        # 恢复交易
        for trd in backup_data.get("transactions", []):
            trd.pop("id", None)
            trd.pop("tag_ids", None)
            trd.pop("created_at", None)

            for field, map_key in [
                ("category_id", "categories"), ("account_id", "accounts"),
                ("from_account_id", "accounts"), ("to_account_id", "accounts"),
            ]:
                old = trd.get(field)
                if old and old in id_map[map_key]:
                    trd[field] = id_map[map_key][old]

            trd["user_id"] = user_id
            db.add(Transaction(**trd))
            await db.flush()
            restored["transactions"] += 1

        # 恢复预算
        for bd in backup_data.get("budgets", []):
            bd.pop("id", None)
            bd.pop("created_at", None)
            old_cat = bd.get("category_id")
            if old_cat and old_cat in id_map["categories"]:
                bd["category_id"] = id_map["categories"][old_cat]
            bd["user_id"] = user_id
            bd["spent_amount"] = 0
            db.add(Budget(**bd))
            restored["budgets"] += 1

        await db.commit()
        return {"message": "数据恢复成功", "mode": mode, "restored_counts": restored}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"恢复失败: {str(e)}")


@router.post("/restore/upload")
async def restore_data_upload(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(..., description="备份 JSON 文件"),
    mode: str = Query("merge", description="merge(合并) 或 replace(替换)"),
):
    """从上传的备份文件恢复数据"""
    user_id = _get_user_id(current_user)
    _ensure_backup_dir()

    content = await file.read()
    try:
        backup_data = json.loads(content)
    except Exception:
        raise HTTPException(status_code=400, detail="无效的 JSON 文件")

    if backup_data.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="备份文件与当前用户不匹配")

    # 保存到备份目录
    safe_filename = f"backup_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_upload.json"
    filepath = os.path.join(BACKUP_DIR, safe_filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)

    restored = {"accounts": 0, "categories": 0, "tags": 0, "transactions": 0, "budgets": 0}

    try:
        if mode == "replace":
            await db.execute(Transaction.__table__.delete().where(Transaction.user_id == user_id))
            await db.execute(Budget.__table__.delete().where(Budget.user_id == user_id))
            await db.execute(Tag.__table__.delete().where(Tag.user_id == user_id))
            await db.execute(Category.__table__.delete().where(Category.user_id == user_id))
            await db.execute(Account.__table__.delete().where(Account.user_id == user_id))
            await db.commit()

        # 恢复分类
        for cd in backup_data.get("categories", []):
            cd.pop("id", None)
            cd.pop("created_at", None)
            cd["user_id"] = user_id
            db.add(Category(**cd))
            await db.flush()
            restored["categories"] += 1

        # 恢复标签
        for td in backup_data.get("tags", []):
            td.pop("id", None)
            td.pop("created_at", None)
            td["user_id"] = user_id
            db.add(Tag(**td))
            await db.flush()
            restored["tags"] += 1

        # 恢复账户
        for ad in backup_data.get("accounts", []):
            ad.pop("id", None)
            ad.pop("created_at", None)
            ad["user_id"] = user_id
            db.add(Account(**ad))
            await db.flush()
            restored["accounts"] += 1

        # 恢复交易
        for trd in backup_data.get("transactions", []):
            trd.pop("id", None)
            trd.pop("tag_ids", None)
            trd.pop("created_at", None)
            trd["user_id"] = user_id
            db.add(Transaction(**trd))
            await db.flush()
            restored["transactions"] += 1

        # 恢复预算
        for bd in backup_data.get("budgets", []):
            bd.pop("id", None)
            bd.pop("created_at", None)
            bd["user_id"] = user_id
            bd["spent_amount"] = 0
            db.add(Budget(**bd))
            restored["budgets"] += 1

        await db.commit()
        return {"message": "数据恢复成功", "mode": mode, "restored_counts": restored}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"恢复失败: {str(e)}")
