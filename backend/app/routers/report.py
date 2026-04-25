from fastapi import APIRouter
from .. import schemas

router = APIRouter()


@router.get("/summary")
async def get_summary():
    # 返回概要信息
    return {"message": "Summary report endpoint"}


@router.get("/transaction-statistics")
async def get_transaction_statistics():
    # 返回交易统计信息
    return {"message": "Transaction statistics endpoint"}


@router.get("/category-analysis")
async def get_category_analysis():
    # 返回分类分析
    return {"message": "Category analysis endpoint"}


@router.get("/budget-performance")
async def get_budget_performance():
    # 返回预算执行情况
    return {"message": "Budget performance endpoint"}