import logging
from fastapi import APIRouter, HTTPException, status
from models.user import UserIn
from security import get_password_hash, get_user, authenticate_user, create_access_token
from database import database, user_table

# 获取当前模块的logger对象
logger = logging.getLogger(__name__)

# 创建一个APIRouter对象
router = APIRouter()

# 定义一个POST请求的路由，路径为/register，状态码为201
@router.post("/register", status_code=201)
async def register(user: UserIn):
    # 检查数据库中是否存在该邮箱的用户
    if await get_user(user.email):
        # 如果存在，抛出HTTPException异常，状态码为400，错误信息为"A user with that email already exists"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that email already exists",
        )
    
    # 获取用户输入的密码，并对其进行哈希处理
    hashed_password = get_password_hash(user.password)
    # 创建一个插入数据库的查询语句，插入用户的邮箱和密码
    query = user_table.insert().values(
        email=user.email, password=hashed_password
    ) 

    # 记录debug级别的日志
    logger.debug(query)

    # 执行查询语句，将用户信息插入数据库
    await database.execute(query)
    # 返回用户创建成功的提示信息
    return {"detail": "User created."}

# 定义一个路由，当用户发送POST请求到"/token"时，调用login函数
@router.post("/token")
# 定义一个异步函数login，接收一个UserIn类型的参数user
async def login(user: UserIn):
    # 调用authenticate_user函数，传入user的email和password，返回一个用户对象
    user = await authenticate_user(user.email, user.password)
    # 调用create_access_token函数，传入用户的email，返回一个access_token
    access_token = create_access_token(user.email)
    # 返回一个包含access_token和token_type的字典
    return {"access_token": access_token, "token_type": "bearer"}