# 导入数据库模块
import databases
# 导入SQLAlchemy模块
import sqlalchemy
# 从config模块中导入config变量
from config import config

# 创建一个SQLAlchemy的MetaData对象
metadata = sqlalchemy.MetaData()

# 定义一个名为posts的表，包含id和body两个字段，id为主键
post_table = sqlalchemy.Table(
    "posts",
    metadata,
    # 定义一个名为id的列，类型为Integer，并设置为主键
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    # 定义一个名为body的列，类型为String
    sqlalchemy.Column("body", sqlalchemy.String),
    # 定义一个名为user_id的列，类型为ForeignKey，关联到users表的id列，且不能为空
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False)
)

# 创建一个名为users的表，包含id、email和password三个字段
user_table = sqlalchemy.Table(
    "users",
    metadata,
    # 定义一个名为id的列，数据类型为Integer，并设置为主键
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),  
    # 定义一个名为email的列，数据类型为String，并设置唯一性约束
    sqlalchemy.Column("email", sqlalchemy.String, unique=True), 
    # 定义一个名为password的列，数据类型为String
    sqlalchemy.Column("password", sqlalchemy.String)  
)

# 定义一个名为comments的表，包含id、body和post_id三个字段，id为主键，post_id为外键，关联到posts表的id字段
comment_table = sqlalchemy.Table(
    "comments",
    metadata,
    # 定义一个名为"id"的列，数据类型为Integer，并设置为主键
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    # 定义一个名为"body"的列，数据类型为String
    sqlalchemy.Column("body", sqlalchemy.String),
    # 定义一个名为"post_id"的列，数据类型为ForeignKey，关联到"posts"表的"id"列，且不能为空
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("posts.id"), nullable=False),
    # 定义一个名为user_id的列，类型为ForeignKey，关联到users表的id列，且不能为空
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False)
)

# 定义一个名为likes的表，包含三个列：id、post_id和user_id
like_table = sqlalchemy.Table(
    "likes",
    metadata,
    # 定义一个名为"id"的列，数据类型为Integer，并设置为主键
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    # 定义一个名为"post_id"的列，数据类型为ForeignKey，关联到"posts"表的"id"列，且不能为空
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("posts.id"), nullable=False),
    # 定义一个名为user_id的列，类型为ForeignKey，关联到users表的id列，且不能为空
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False)
)

# 创建一个SQLAlchemy的Engine对象，连接到数据库
engine = sqlalchemy.create_engine(
    # 配置数据库连接URL，并设置参数check_same_thread为False，表示可以跨线程连接数据库
    config.DATABASE_URL, connect_args={"check_same_thread": False}
)

# 使用MetaData对象创建所有表
metadata.create_all(engine)

# 创建一个Databases的Database对象，连接到数据库
database = databases.Database(
    # 配置数据库URL，并强制回滚
    config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK
)
