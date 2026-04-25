from functools import wraps
from fastapi import Response
from typing import Any
from ..schemas.common import SuccessResponse


def unified_response_format(func):
    """
    装饰器：统一API响应格式
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)

        # 如果结果已经是SuccessResponse格式，则直接返回
        if hasattr(result, 'code'):
            return result

        # 否则包装为SuccessResponse格式
        return SuccessResponse(code=200, message="success", data=result)

    return wrapper