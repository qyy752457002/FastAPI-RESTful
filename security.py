import os

import logging 

from typing import Annotated

from jose import jwt, ExpiredSignatureError, JWTError

import datetime

from passlib.context import CryptContext

from fastapi.security import OAuth2PasswordBearer

from fastapi import Depends, HTTPException, status

from database import database, user_table

# 获取logger对象
logger = logging.getLogger(__name__)

# 定义一个常量，用于存储JWT密钥，encode()函数将字符串转换为字节串
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "").encode()
# 定义一个常量，用于存储JWT算法
ALGORITHM = "HS256"
# 定义一个常量，用于存储JWT令牌的URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # noqa: F821
# 创建一个密码上下文对象，使用bcrypt算法
pwd_context = CryptContext(schemes=["bcrypt"])

# 定义一个HTTPException异常，状态码为401，详细信息为“Could not validate credentials”，头部信息为“WWW-Authenticate: Bearer”
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, 
    detail="Could not validate credentials", 
    headers={"WWW-Authenticate": "Bearer"}
)

# 定义一个函数，用于获取access token的过期时间，单位为分钟
def access_token_expire_minutes() -> int:
    # 返回access token的过期时间为30分钟
    return 30

# 定义一个函数，用于创建访问令牌
def create_access_token(email: str):
    # 记录创建访问令牌的日志
    logger.debug("Creating access token", extra={"email": email})
    # 设置令牌过期时间为30分钟
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=access_token_expire_minutes())
    # 创建JWT数据，包含用户邮箱和过期时间
    jwt_data = {"sub": email, "exp": expire}
    # 使用密钥和算法对JWT数据进行编码
    encoded_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    # 返回编码后的JWT数据
    return encoded_jwt

# 定义一个函数，用于获取密码的哈希值
def get_password_hash(password: str) -> str:
    # 使用pwd_context.hash()方法获取密码的哈希值
    return pwd_context.hash(password)

# 定义一个函数，用于验证密码是否正确
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 使用pwd_context.verify()方法验证密码是否正确
    return pwd_context.verify(plain_password, hashed_password)

# 定义一个异步函数，用于从数据库中获取用户信息
async def get_user(email: str):
    # 记录调试信息，表示正在从数据库中获取用户信息，并传入email参数
    logger.debug("Fetching usr from the database", extra={"email": email})
    # 构造查询语句，查询user_table表中email字段等于传入的email参数的记录
    query = user_table.select().where(user_table.c.email == email)
    # 异步执行查询语句，获取结果
    result = await database.fetch_one(query)

    # 如果查询结果不为空，则返回结果
    if result:
        return result 
    
# 定义一个异步函数，用于验证用户
async def authenticate_user(email: str, password: str):
    # 记录调试信息，记录用户邮箱
    logger.debug("Authenticating user", extra={"email": email})
    # 调用get_user函数，根据邮箱获取用户信息
    user = await get_user(email)
    # 如果用户不存在，则抛出凭证异常
    if not user:
        raise credentials_exception
    # 如果密码验证失败，则抛出凭证异常
    if not verify_password(password, user.password):
        raise credentials_exception
    # 如果用户存在且密码验证成功，则返回用户信息
    return user

# 异步函数，用于获取当前用户
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    # 尝试解码token
    try:
        # 解码JWT令牌
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        # 从payload中获取email
        email = payload.get("sub")
        # 如果email不存在，则抛出异常
        if email is None:
            # 抛出凭证异常
            raise credentials_exception
    # 如果token过期，抛出HTTPException异常
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token has expired", 
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    # 如果token无效，抛出credentials_exception异常
    except JWTError as e:
         # 抛出凭证异常，并附带原始异常信息
        raise credentials_exception from e  
    # 根据邮箱获取用户信息
    user = await get_user(email=email)  
    # 如果用户不存在
    if user is None: 
        # 抛出凭证异常
        raise credentials_exception   
    # 返回用户信息
    return user                  