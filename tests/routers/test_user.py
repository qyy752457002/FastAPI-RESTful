import pytest
from httpx import AsyncClient

# 定义一个异步函数，用于注册用户
async def register_user(async_client: AsyncClient, email: str, password: str):
    # 使用async_client发送POST请求，注册用户，参数为email和password
    return await async_client.post(
        "/register", json={"email": email, "password": password}
    )


# 使用pytest.mark.anyio装饰器，定义一个异步函数，用于测试注册用户
@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    # 调用register_user函数，注册用户，参数为email和password
    response = await register_user(async_client, "test@example.net", "1234")
    # 断言响应状态码为201
    assert response.status_code == 201
    # 断言响应内容中包含"User created"
    assert "User created" in response.json()["detail"]


@pytest.mark.anyio
async def test_register_user_already_exists(
    async_client: AsyncClient, registered_user: dict
):
    # 调用register_user函数，注册用户，参数为email和password
    response = await register_user(
        async_client, registered_user["email"], registered_user["password"]
    )
    # 断言响应状态码为400
    assert response.status_code == 400
    # 断言响应内容中包含"User already exists"
    assert "already exists" in response.json()["detail"]

# 使用pytest.mark.anyio标记异步测试函数
@pytest.mark.anyio 
# 定义异步测试函数，参数为AsyncClient类型的async_client
async def test_login_user_not_exists(async_client: AsyncClient):
    # 发送POST请求，请求路径为/token，请求参数为json格式，包含email和password
    response = await async_client.post(
        "/token", json={"email": "test@example.net", "password": "1234"}
    )
    # 断言响应状态码为401，表示用户不存在
    assert response.status_code == 401

# 使用pytest.mark.anyio标记异步测试函数
@pytest.mark.anyio 
# 定义异步测试函数，参数async_client为AsyncClient类型，registered_user为字典类型
async def test_login_user(async_client: AsyncClient, registered_user: dict):
    # 发送POST请求，请求路径为/token，请求参数为json格式，包含email和password
    response = await async_client.post(
        "/token", json={"email": registered_user["email"], "password": registered_user["password"]}
    )
    # 断言响应状态码为200，表示登录成功
    assert response.status_code == 200

