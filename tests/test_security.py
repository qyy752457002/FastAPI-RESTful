import pytest 
import security
from jose import jwt

# 测试访问令牌过期时间
def test_access_token_expire_minutes():
    # 断言访问令牌过期时间为30分钟
    assert security.access_token_expire_minutes() == 30

# 测试创建访问令牌
def test_create_access_token():
    # 创建访问令牌，传入用户ID为"123"
    token = security.create_access_token("123")
    # 断言解码后的访问令牌中包含用户ID为"123"
    assert {"sub": "123"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()

# 定义一个测试密码哈希的函数
def test_password_hashes():
    # 定义一个密码
    password = "password"
    # 断言密码和密码哈希是否匹配
    assert security.verify_password(password, security.get_password_hash(password))

# 使用pytest.mark.anyio装饰器标记异步测试函数
@pytest.mark.anyio 
async def test_get_user(registered_user: dict):
    # 调用security模块中的get_user函数，传入注册用户的email
    user = await security.get_user(registered_user["email"])
    # 断言返回的用户email与传入的注册用户email相同
    assert user.email == registered_user["email"]

# 使用pytest.mark.anyio装饰器标记异步测试函数
@pytest.mark.anyio 
async def test_get_user_not_found():
    # 调用security模块中的get_user函数，传入一个不存在的email
    user = await security.get_user("text@example.com")
    # 断言返回的用户为None
    assert user is None

# 使用pytest.mark.anyio装饰器标记此函数为异步函数
@pytest.mark.anyio
async def test_authenticate_user(registered_user: dict):
    # 调用security.authenticate_user函数，传入注册用户的邮箱和密码，获取用户信息
    user = await security.authenticate_user(
        registered_user["email"], registered_user["password"]
    )
    # 断言用户信息中的邮箱与注册用户的邮箱相同
    assert user.email == registered_user["email"]

# 使用pytest.mark.anyio装饰器标记此函数为异步函数
@pytest.mark.anyio 
# 定义一个异步函数，用于测试用户认证
async def test_authenticate_user_not_found():
    # 使用pytest.raises装饰器，捕获security.authenticate_user函数抛出的异常
    with pytest.raises(security.HTTPException):
        # 调用security.authenticate_user函数，传入用户名和密码
        await security.authenticate_user("test@example.net", "1234")

# 使用pytest.mark.anyio标记异步测试函数
@pytest.mark.anyio 
# 定义异步测试函数，测试用户认证时输入错误密码的情况
async def test_authenticate_user_wrong_password(registered_user: dict):
    # 使用pytest.raises装饰器，捕获security.authenticate_user函数抛出的异常
    with pytest.raises(security.HTTPException):
        # 调用security.authenticate_user函数，传入用户名和错误的密码
        await security.authenticate_user(registered_user["email"], "wrong password")

# 使用pytest.mark.anyio标记异步测试函数
@pytest.mark.anyio 
# 定义一个异步函数test_get_current_user，参数为registered_user，类型为字典
async def test_get_current_user(registered_user: dict):
    # 使用security模块的create_access_token函数，传入registered_user中的email，生成token
    token = security.create_access_token(registered_user["email"])
    # 使用security模块的get_current_user函数，传入token，获取当前用户
    user = await security.get_current_user(token)
    # 断言当前用户的email与registered_user中的email相等
    assert user.email == registered_user["email"]

# 使用pytest.mark.anyio标记异步测试函数
@pytest.mark.anyio 
# 定义一个异步函数，用于测试获取当前用户时，使用无效的token
async def test_get_current_user_invalid_token():
   # 使用pytest.raises装饰器，捕获security.HTTPException异常
   with pytest.raises(security.HTTPException):
       # 调用security模块的get_current_user函数，传入无效的token
       await security.get_current_user("invalid token")