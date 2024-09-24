# Most of this taken from Redowan Delowar's post on configurations with Pydantic
# https://rednafi.github.io/digressions/python/2020/06/03/python-configs.html

# 导入BaseSettings和SettingsConfigDict类，用于定义配置类
from pydantic_settings import BaseSettings, SettingsConfigDict
# 导入Optional类，用于定义可选参数
from typing import Optional
# 导入lru_cache装饰器，用于缓存函数结果
from functools import lru_cache

# 定义基础配置类，继承自 Pydantic 的 BaseSettings
class BaseConfig(BaseSettings):
    # 可选的环境状态，默认为 None
    # # (很重要！！！) *** 如果 .env 文件中有 ENV_STATE 配置项，则使用该配置项，否则使用默认值 None ***
    ENV_STATE: Optional[str] = None

    """加载 .env 文件的配置，包含这个部分是为了让 pydantic 自动加载 .env 文件的内容。"""
    # model_config 定义了要加载的 .env 文件和忽略额外的配置项
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# 定义全局配置类，继承自 BaseConfig
class GlobalConfig(BaseConfig):
    # 可选的数据库 URL 配置项one
    # (很重要！！！) *** 如果 .env 文件中有 DATABASE_URL 配置项，则使用该配置项，否则使用默认值 None ***
    DATABASE_URL: Optional[str] = None
    # 数据库回滚的标志位，默认为 False
    # 在数据库事务执行失败时，不会强制执行回滚操作
    DB_FORCE_ROLL_BACK: bool = False
    # 可选的日志追踪 API 密钥
    # (很重要！！！) *** 如果 .env 文件中有 LOGTAIL_API_KEY 配置项，则使用该配置项，否则使用默认值 None ***
    LOGTAIL_API_KEY: Optional[str] = None
    # Sentry的DSN，用于错误追踪
    # (很重要！！！) *** 如果 .env 文件中有 SENTRY_DSN 配置项，则使用该配置项，否则使用默认值 None ***
    SENTRY_DSN: Optional[str] = None


# 定义开发环境的配置类，继承自 GlobalConfig
class DevConfig(GlobalConfig):
    # 重写开发环境下数据库 URL，使用 SQLite 的内存数据库
    DATABASE_URL: str = "sqlite:///dev.db"
    # 重写开发环境下强制回滚数据库事务
    # 在数据库事务执行失败时，会强制执行回滚操作
    DB_FORCE_ROLL_BACK: bool = True

    '''
    (很重要！！！) SettingsConfigDict 会优先读取 DEV_DATABASE_URL 的值

    如果 .env 文件中定义了：

    DATABASE_URL=sqlite:///dev.db
    DEV_DATABASE_URL=sqlite:///development.db

    那么 config.DATABASE_URL 的值将会是 "sqlite:///development.db"，因为 SettingsConfigDict 会优先读取 DEV_DATABASE_URL 的值。

    需要注意的是，SettingsConfigDict 只会读取以 DEV_ 开头的环境变量，所以如果 .env 文件中只定义了 DATABASE_URL，那么 config.DATABASE_URL 的值将会是 "sqlite:///dev.db"
    
    '''

    # 设置开发环境的环境变量前缀为 "DEV_"
    model_config = SettingsConfigDict(env_prefix="DEV_")


# 定义生产环境的配置类，继承自 GlobalConfig
class ProdConfig(GlobalConfig):
    # 重写生产环境下数据库 URL，使用 SQLite 的内存数据库
    DATABASE_URL: str = "sqlite:///prod.db"
    # 重写生产环境下强制回滚数据库事务
    # 在数据库事务执行失败时，会强制执行回滚操作
    DB_FORCE_ROLL_BACK: bool = True

    '''
    (很重要！！！) SettingsConfigDict 会优先读取 PROD_DATABASE_URL 的值

    如果 .env 文件中定义了：

    DATABASE_URL=sqlite:///prod.db
    PROD_DATABASE_URL=sqlite:///production.db

    那么 config.DATABASE_URL 的值将会是 "sqlite:///production.db"，因为 SettingsConfigDict 会优先读取 PROD_DATABASE_URL 的值。

    需要注意的是，SettingsConfigDict 只会读取以 PROD_ 开头的环境变量，所以如果 .env 文件中只定义了 DATABASE_URL，那么 config.DATABASE_URL 的值将会是 "sqlite:///prod.db"
    
    '''

    # 设置生产环境的环境变量前缀为 "PROD_"
    model_config = SettingsConfigDict(env_prefix="PROD_")


# 定义测试环境的配置类，继承自 GlobalConfig
class TestConfig(GlobalConfig):
    # 重写测试环境下数据库 URL， 使用 SQLite 的内存数据库
    DATABASE_URL: str = "sqlite:///test.db"
    # 重写测试环境下强制回滚数据库事务
    # 在数据库事务执行失败时，会强制执行回滚操作
    DB_FORCE_ROLL_BACK: bool = True

    '''
    (很重要！！！) SettingsConfigDict 会优先读取 TEST_DATABASE_URL 的值

    如果 .env 文件中定义了：

    DATABASE_URL=sqlite:///test.db
    TEST_DATABASE_URL=sqlite:///testing.db

    那么 config.DATABASE_URL 的值将会是 "sqlite:///testing.db"，因为 SettingsConfigDict 会优先读取 TEST_DATABASE_URL 的值。

    需要注意的是，SettingsConfigDict 只会读取以 TEST_ 开头的环境变量，所以如果 .env 文件中只定义了 DATABASE_URL，那么 config.DATABASE_URL 的值将会是 "sqlite:///test.db"
    
    '''

    # 设置测试环境的环境变量前缀为 "TEST_"
    model_config = SettingsConfigDict(env_prefix="TEST_")
    

# 使用 Python 的 lru_cache 装饰器缓存配置实例，避免每次调用都重新实例化
@lru_cache()
def get_config(env_state: str):
    """根据传入的环境状态实例化相应的配置类。"""
    # 定义环境与配置类的映射关系
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    # 返回根据环境状态选择的配置类的实例
    return configs[env_state]()


# 根据 BaseConfig 中的 ENV_STATE 实例化配置，默认情况下从 .env 文件中读取 ENV_STATE
config = get_config(BaseConfig().ENV_STATE)

