# 导入os模块，用于操作操作系统
import os
# 导入AsyncGenerator和Generator类型，用于定义异步生成器和生成器类型
from typing import AsyncGenerator, Generator 

# 导入pytest模块，用于编写和运行测试
import pytest
# 导入TestClient类，用于测试FastAPI应用程序
from fastapi.testclient import TestClient
# 导入AsyncClient类，用于测试异步FastAPI应用程序
from httpx import AsyncClient 

# 设置环境变量ENV_STATE为test
os.environ["ENV_STATE"] = "test"

# 从database模块中导入database对象
from database import database, user_table # noqa: E402
# 从main模块中导入app对象
from main import app # noqa: E402

# 定义一个名为anyio_backend的fixture，作用域为session
@pytest.fixture(scope="session")
def anyio_backend():
    # 返回字符串"asyncio"
    return "asyncio"

# 定义一个名为client的fixture，返回一个TestClient实例
@pytest.fixture()
def client() -> Generator:
    # 返回一个TestClient实例
    yield TestClient(app)

# 定义一个名为db的fixture，返回一个AsyncGenerator实例
@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    # 连接数据库
    await database.connect()
    # 生成器函数的代码块
    yield
    # 断开数据库连接
    await database.disconnect()

# 定义一个异步的fixture，用于创建一个异步的客户端
@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    # 使用AsyncClient创建一个异步的客户端，并设置app和base_url
    async with AsyncClient(app=app, base_url=client.base_url) as ac:
        # 返回异步的客户端
        yield ac

# 定义一个异步的fixture，用于创建一个异步的客户端
@pytest.fixture()
# 定义一个异步函数，用于注册用户
async def registered_user(async_client: AsyncClient) -> dict:
    # 定义用户详情，包括邮箱和密码
    user_details = {"email": "test@example.net", "password": "1234"}
    # 使用异步客户端发送POST请求，将用户详情作为json数据发送到"/register"路径
    await async_client.post("/register", json=user_details)
    # 从数据库中查询邮箱为user_details["email"]的用户
    query = user_table.select().where(user_table.c.email == user_details["email"])
    # 使用数据库客户端获取查询结果
    user = await database.fetch_one(query)
    # 将查询结果中的id添加到user_details中
    user_details["id"] = user.id
    # 返回用户详情
    return user_details

# 定义一个异步的fixture，用于获取登录用户的token
@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, registered_user: dict) -> str:
    # 使用async_client发送post请求，获取登录用户的token
    response = await async_client.post("/token", json=registered_user)
    # 返回获取到的token
    return response.json()["access_token"]

