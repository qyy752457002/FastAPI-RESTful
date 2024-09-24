from pydantic import BaseModel

# 定义一个用户帖子输入模型
class UserPostIn(BaseModel):
    body: str

# 定义一个用户帖子模型，继承自用户帖子输入模型
class UserPost(UserPostIn):
    id: int
    user_id: int

    # 定义一个名为Config的类
    class Config:
        # 设置orm_mode为True，表示返回的数据类型为字典
        orm_mode = True

# 定义一个包含用户帖子和点赞的模型
class UserPostWithLikes(UserPost):
    likes: int 

    # 定义一个名为Config的类
    class Config:
        # 设置orm_mode为True，表示返回的数据类型为字典
        orm_mode = True

# 定义一个评论输入模型
class CommentIn(BaseModel):
    body: str
    post_id: int

# 定义一个评论模型，继承自评论输入模型
class Comment(CommentIn):
    id: int
    user_id: int

    # 定义一个名为Config的类
    class Config:
        # 设置orm_mode为True，表示返回的数据类型为字典
        orm_mode = True

# 定义一个包含用户帖子和评论的模型
class UserPostWithComments(BaseModel):
    post: UserPostWithLikes
    comments: list[Comment]

class PostLikeIn(BaseModel):
    post_id: int

class PostLike(PostLikeIn):
    id: int 
    user_id: int

# {
#     "post": {"id": 0, "body": "My post"},
#     "comments": [{"id": 2, "post_id": 0, "body": "My comment"}],
# }
