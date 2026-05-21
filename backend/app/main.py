from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, account, category, transaction, tag, budget, report, import_transactions, dashboard

app = FastAPI(title="My Wallet Butler API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由器
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(account.router, prefix="/api/v1/accounts", tags=["account"])
app.include_router(category.router, prefix="/api/v1/categories", tags=["category"])
app.include_router(transaction.router, prefix="/api/v1/transactions", tags=["transaction"])
app.include_router(tag.router, prefix="/api/v1/tags", tags=["tag"])
app.include_router(budget.router, prefix="/api/v1/budgets", tags=["budget"])
app.include_router(report.router, prefix="/api/v1/report", tags=["report"])
app.include_router(import_transactions.router, prefix="/api/v1/import", tags=["import"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])

@app.get("/")

@app.get("/")
async def root():
    return {"message": "My Wallet Butler API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}