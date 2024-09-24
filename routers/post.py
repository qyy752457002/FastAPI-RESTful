import logging
import sqlalchemy

from models.user import User
from security import get_current_user
from enum import Enum
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from database import comment_table, database, like_table, post_table
from models.post import (
    Comment,
    CommentIn,
    PostLike,
    PostLikeIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
    UserPostWithLikes
)

# 创建一个API路由器
router = APIRouter()

# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)

'''
select_post_and_likes 可能的结果如下：

+----+-----------------+-------+
| id | title           | likes |
+----+-----------------+-------+
| 1  | "First Post"    | 5     |
| 2  | "Second Post"   | 3     |
| 3  | "Third Post"    | 4     |
| 4  | "Fourth Post"   | 7     |
+----+-----------------+-------+

'''

# 从post_table和like_table中选择post_table和like_table.c.id的count，并将count命名为likes
select_post_and_likes = (
    sqlalchemy.select(post_table, sqlalchemy.func.count(like_table.c.id).label("likes"))
    # 将post_table和like_table进行外连接
    .select_from(post_table.outerjoin(like_table))
    # 按照post_table.c.id进行分组
    .group_by(post_table.c.id)
)

# 根据post_id查找帖子
async def find_post(post_id: int):
    # 记录查找帖子的日志
    logger.info(f"Finding post with id {post_id}")

    # 构建查询语句，查找id为post_id的帖子
    query = post_table.select().where(post_table.c.id == post_id)

    # 记录查询语句的日志
    logger.debug(query)

    # 执行查询语句，返回结果
    return await database.fetch_one(query)

''' 
这段代码是Python中的一个类型注解，通常用于FastAPI框架中，用于定义路由处理函数的参数类型。
具体来说，这段代码定义了两个参数：`post`和`current_user`。

1. **`post: UserPostIn`**:
   - `post`是一个参数，它的类型是`UserPostIn`。
   - `UserPostIn`通常是一个Pydantic模型，用于定义用户提交的数据结构。

      Pydantic是一个用于数据验证和设置管理的Python库，它可以帮助开发者快速构建数据模型，并确保数据的有效性和一致性。

2. **`current_user: Annotated[User, Depends(get_current_user)]`**:
   - `current_user`也是一个参数，它的类型是`Annotated[User, Depends(get_current_user)]`。

   - `Annotated`是Python的类型注解的一种扩展，用于添加额外的元数据。
      在这里，它用于将`Depends(get_current_user)`作为元数据附加到`User`类型上。

   - `Depends(get_current_user)`是一个依赖项，用于在处理请求之前执行一些操作。
      get_current_user`是一个函数，它通常用于从请求中提取当前登录的用户信息。

   - `User`是一个模型，用于定义用户的数据结构。

**用途**:
- 这段代码通常用于定义FastAPI路由处理函数的参数类型，以便进行数据验证和依赖注入。
- `post`参数用于接收用户提交的数据，`current_user`参数用于获取当前登录的用户信息。

**注意事项**:
- 确保在代码中已经导入了必要的模块和函数，例如`UserPostIn`模型和`get_current_user`函数。
- 确保在路由处理函数中正确使用这些参数，例如通过`request`对象获取`post`参数，通过依赖注入获取`current_user`参数。

'''

# 创建帖子
@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(
    post: UserPostIn, current_user: Annotated[User, Depends(get_current_user)]
):
    # 记录创建帖子的日志
    logger.info("Creating post")

    # 将post和current_user的id合并为一个字典
    data = {**post.model_dump(), "user_id": current_user.id}
    # 构建插入语句，将data插入到post_table中
    query = post_table.insert().values(data)

    # 记录插入语句的日志
    logger.debug(query)

    # 执行插入语句，返回最后一条记录的id
    last_record_id = await database.execute(query)
    # 返回插入的数据，包括id
    return {**data, "id": last_record_id}

class PostSorting(str, Enum):
    # 新建帖子排序方式
    new = "new"
    # 旧帖子排序方式
    old = "old"
    # 按点赞数排序方式
    most_likes = "most_likes"

# 获取所有帖子
@router.get("/post", response_model=list[UserPostWithLikes])
async def get_all_posts(sorting: PostSorting = PostSorting.new): #http://api.com/post?sorting=most_likes
    # 记录获取所有帖子的日志
    logger.info("Getting all posts")

    # 构建查询语句，查询帖子及其点赞数
    match sorting:
        case PostSorting.new:
            # 查询帖子及其点赞数，并按帖子id降序排列
            query = select_post_and_likes.order_by(post_table.c.id.desc())
        case PostSorting.old:
            # 查询帖子及其点赞数，并按帖子id升序排列
            query = select_post_and_likes.order_by(post_table.c.id.asc())
        case PostSorting.most_likes:
            # 按照点赞数降序排列查询结果
            query = select_post_and_likes.order_by(sqlalchemy.desc("likes"))
        case _:
            # 默认情况，可以选择抛出异常或使用默认排序
            raise ValueError(f"Unsupported sorting option: {sorting}")

    # 记录查询语句的日志
    logger.debug(query)

    # 执行查询语句，返回结果
    return await database.fetch_all(query)


# 创建评论
@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(
    comment: CommentIn, current_user: Annotated[User, Depends(get_current_user)]
):
    # 记录创建评论的日志
    logger.info("Creating comment")

    # 根据comment的post_id查找帖子
    post = await find_post(comment.post_id)
    # 如果post为空，则抛出HTTPException异常
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 将comment.model_dump()和current_user.id合并为一个字典
    data = {**comment.model_dump(), "user_id": current_user.id}
    # 将data插入到comment_table表中
    query = comment_table.insert().values(data)

    # 打印查询语句
    logger.debug(query)

    # 执行查询语句，并返回最后一条记录的id
    last_record_id = await database.execute(query)
    # 返回data和最后一条记录的id
    return {**data, "id": last_record_id}


# 获取指定post_id的评论
@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    # 打印日志
    logger.info("Getting comments on post")

    # 查询comment_table表中post_id为post_id的记录
    query = comment_table.select().where(comment_table.c.post_id == post_id)

    # 打印查询语句
    logger.debug(query)

    # 执行查询语句，并返回所有记录
    return await database.fetch_all(query)


# 获取指定post_id的post及其评论
@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    # 打印日志
    logger.info("Getting post and its comments")

    # 根据post_id查询post_table和likes_table中的数据
    query = select_post_and_likes.where(post_table.c.id == post_id)

    # 打印查询语句
    logger.debug(query)

    # 执行查询语句，获取一条数据
    post = await database.fetch_one(query)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }


# 使用装饰器定义一个POST请求的路由，路径为"/like"，返回的数据模型为PostLike，状态码为201
@router.post("/like", response_model=PostLike, status_code=201)
async def like_post(
    like: PostLikeIn, current_user: Annotated[User, Depends(get_current_user)]
):
    # 记录日志，表示正在点赞
    logger.info("Liking post")

    # 根据post_id查找帖子
    post = await find_post(like.post_id)

    # 如果帖子不存在，抛出404错误
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # 将点赞数据与当前用户id合并
    data = {**like.model_dump(), "user_id": current_user.id}

    # 构建插入数据库的查询语句
    query = like_table.insert().values(data)

    # 记录日志，表示查询语句
    logger.debug(query)

    # 执行查询语句，返回最后一条记录的id
    last_record_id = await database.execute(query)

    # 返回点赞数据，包括id
    return {**data, "id": last_record_id}