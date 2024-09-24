from pydantic import BaseModel 

class User(BaseModel):
    # 用户ID，可以为空
    id: int | None = None 
    # 用户邮箱
    email: str 

class UserIn(User):
    # 用户输入密码
    password: str