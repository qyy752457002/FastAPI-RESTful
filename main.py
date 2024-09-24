# 导入 logging模块
import logging
# 导入sentry_sdk模块
import sentry_sdk

# 导入 asgi_correlation_id 模块
from asgi_correlation_id import CorrelationIdMiddleware
# 导入FastAPI模块
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

# 导入数据库模块
from database import database
# 从config模块中导入config变量
from config import config
# 导入路由模块
from routers.post import router as post_router
from routers.user import router as user_router
# 导入 configure_logging 模块
from logging_conf import configure_logging
# 导入asynccontextmanager模块
from contextlib import asynccontextmanager

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

sentry_sdk.init(
    dsn=config.SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)

# 定义一个异步上下文管理器，用于管理数据库连接
@asynccontextmanager
async def lifespan(app: FastAPI):   
    # 配置日志
    configure_logging()     

    # 连接数据库
    await database.connect()
    # 上下文管理器开始
    yield
    # 上下文管理器结束，断开数据库连接
    await database.disconnect()

# 创建一个FastAPI实例
app = FastAPI(lifespan=lifespan)
# 添加一个中间件，用于添加一个关联ID
app.add_middleware(CorrelationIdMiddleware)

# 将post_router路由器添加到app中
app.include_router(post_router)
# 将user_router路由器添加到app中
app.include_router(user_router)

# 定义一个全局异常处理函数
@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    # 记录异常信息
    logger.error(f"HTTP Exception: {exc.status_code} {exc.detail}")
    # 返回异常信息
    return await http_exception_handler(request, exc)