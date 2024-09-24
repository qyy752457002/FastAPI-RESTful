import pytest
import security
from httpx import AsyncClient

# 定义一个异步函数，用于创建帖子
async def create_post(
    body: str, async_client: AsyncClient, logged_in_token: str
) -> dict:
    # 使用async_client发送POST请求，创建帖子
    response = await async_client.post(
        "/post",
        json={"body": body},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    # 返回响应的JSON数据
    return response.json()


# 定义一个异步函数，用于创建评论
async def create_comment(
    body: str, post_id: int, async_client: AsyncClient, logged_in_token: str
) -> dict:
    # 使用async_client发送POST请求，创建评论
    response = await async_client.post(
        "/comment",
        json={"body": body, "post_id": post_id},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    # 返回响应的JSON数据
    return response.json()


# 定义一个异步函数，用于点赞帖子
async def like_post(
    post_id: int, async_client: AsyncClient, logged_in_token: str
) -> dict:
    # 使用async_client发送POST请求，点赞帖子
    response = await async_client.post(
        "/like",
        json={"post_id": post_id},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    # 返回响应的JSON数据
    return response.json()


# 定义一个pytest的fixture，用于创建帖子
@pytest.fixture()
async def created_post(async_client: AsyncClient, logged_in_token: str):
    # 调用create_post函数，创建帖子
    return await create_post("Test Post", async_client, logged_in_token)


# 定义一个异步的fixture，用于创建一个评论
@pytest.fixture()
async def created_comment(
    async_client: AsyncClient, created_post: dict, logged_in_token: str
):
    # 调用create_comment函数，传入评论内容、帖子id、异步客户端和登录令牌，返回创建的评论
    return await create_comment(
        "Test Comment", created_post["id"], async_client, logged_in_token
    )


# 定义一个异步的测试函数，用于测试创建帖子
@pytest.mark.anyio
async def test_create_post(
    async_client: AsyncClient, registered_user: dict, logged_in_token: str
):
    # 定义帖子内容
    body = "Test Post"

    # 发送post请求，创建帖子
    response = await async_client.post(
        "/post",
        json={"body": body},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    # 断言响应状态码为201
    assert response.status_code == 201
    # 断言响应内容与预期一致
    assert {
        "id": 1,
        "body": body,
        "user_id": registered_user["id"],
    }.items() <= response.json().items()


# 定义一个异步的测试函数，用于测试过期令牌创建帖子
@pytest.mark.anyio
async def test_create_post_expired_token(
    async_client: AsyncClient, registered_user: dict, mocker
):
    # 模拟令牌过期时间
    mocker.patch("security.access_token_expire_minutes", return_value=-1)
    # 创建令牌
    token = security.create_access_token(registered_user["email"])
    # 发送post请求，创建帖子
    response = await async_client.post(
        "/post",
        json={"body": "Test Post"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # 断言响应状态码为401
    assert response.status_code == 401
    # 断言响应内容包含"Token has expired"
    assert "Token has expired" in response.json()["detail"]


# 定义一个异步的测试函数，用于测试缺少数据创建帖子
@pytest.mark.anyio
async def test_create_post_missing_data(
    async_client: AsyncClient, logged_in_token: str
):
    # 发送post请求，创建帖子，不传入数据
    response = await async_client.post(
        "/post", json={}, headers={"Authorization": f"Bearer {logged_in_token}"}
    )

    # 断言响应状态码为422
    assert response.status_code == 422


# 定义一个异步的测试函数，用于测试点赞帖子
@pytest.mark.anyio
async def test_like_post(
    async_client: AsyncClient, created_post: dict, logged_in_token: str
):
    # 发送post请求，点赞帖子
    response = await async_client.post(
        "/like",
        json={"post_id": created_post["id"]},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    # 断言响应状态码为201
    assert response.status_code == 201


# 定义一个异步的测试函数，用于测试获取所有帖子
@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient, created_post: dict):
    # 发送get请求，获取所有帖子
    response = await async_client.get("/post")

    # 断言响应状态码为200
    assert response.status_code == 200
    # 断言响应内容与预期一致
    assert created_post.items() <= response.json()[0].items()

''' 
`@pytest.mark.parametrize` 是一个装饰器，用于在测试函数中参数化测试数据。

它允许你为测试函数提供多个输入参数，并运行测试函数多次，每次使用不同的参数组合。

在你的代码中，`@pytest.mark.parametrize` 装饰器用于参数化测试函数的 `sorting` 和 `expected_order` 参数。

- `sorting` 是一个字符串参数，用于指定排序方式，可以是 `"new"` 或 `"old"`。
- `expected_order` 是一个列表，用于指定排序后的预期顺序。

测试函数将会被运行两次，每次使用不同的参数组合：

1. 第一次运行时，`sorting` 参数为 `"new"`，`expected_order` 参数为 `[2, 1]`。
2. 第二次运行时，`sorting` 参数为 `"old"`，`expected_order` 参数为 `[1, 2]`。

这样，你就可以通过参数化测试来验证你的代码在不同排序方式下的行为是否正确。
'''
# 定义一个异步的测试函数，用于测试获取所有帖子排序
@pytest.mark.anyio
@pytest.mark.parametrize(
    "sorting, expected_order",
    [
        ("new", [2, 1]),
        ("old", [1, 2]),
    ],
)
async def test_get_all_posts_sorting(
    async_client: AsyncClient,
    logged_in_token: str,
    sorting: str,
    expected_order: list[int],
):
    # 创建两个帖子
    await create_post("Test Post 1", async_client, logged_in_token)
    await create_post("Test Post 2", async_client, logged_in_token)
    # 发送get请求，获取所有帖子，并按指定排序
    response = await async_client.get("/post", params={"sorting": sorting})
    # 断言响应状态码为200
    assert response.status_code == 200

    data = response.json()
    # 从响应中获取数据，并将其转换为json格式
    post_ids = [post["id"] for post in data]
    # 从数据中提取每个帖子的id，并存储在post_ids列表中
    assert post_ids == expected_order


@pytest.mark.anyio
# 使用anyio库进行异步测试
async def test_get_all_posts_sort_likes(
    async_client: AsyncClient, logged_in_token: str
):
    # 创建两个帖子
    await create_post("Test Post 1", async_client, logged_in_token)
    await create_post("Test Post 2", async_client, logged_in_token)
    # 对第二个帖子进行点赞
    await like_post(2, async_client, logged_in_token)
    # 获取所有帖子，并按照点赞数进行排序
    response = await async_client.get("/post", params={"sorting": "most_likes"})
    assert response.status_code == 200
    # 从响应中获取数据，并将其转换为json格式
    data = response.json()
    # 断言返回的帖子id列表按照点赞数排序
    assert [post["id"] for post in data] == [2, 1]


@pytest.mark.anyio
# 使用anyio库进行异步测试
async def test_get_all_post_wrong_sorting(async_client: AsyncClient):
    # 获取所有帖子，并按照错误的排序方式进行排序
    response = await async_client.get("/post", params={"sorting": "wrong"})
    # 断言返回的状态码为422
    assert response.status_code == 422


@pytest.mark.anyio
# 使用anyio库进行异步测试
async def test_create_comment(
    async_client: AsyncClient,
    created_post: dict,
    registered_user: dict,
    logged_in_token: str,
):
    # 创建一个评论
    body = "Test Comment"

    response = await async_client.post(
        "/comment",
        json={"body": body, "post_id": created_post["id"]},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    # 断言返回的状态码为201
    assert response.status_code == 201
    # 断言返回的评论数据与预期一致
    assert {
        "id": 1,
        "body": body,
        "post_id": created_post["id"],
        "user_id": registered_user["id"],
    }.items() <= response.json().items()


@pytest.mark.anyio
# 使用anyio库进行异步测试
async def test_get_comments_on_post(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    # 获取指定帖子的评论
    response = await async_client.get(f"/post/{created_post['id']}/comment")

    # 断言返回的状态码为200
    assert response.status_code == 200
    # 断言返回的评论数据与预期一致
    assert response.json() == [created_comment]


@pytest.mark.anyio
# 使用anyio库进行异步测试
async def test_get_comments_on_post_empty(
    async_client: AsyncClient, created_post: dict
):
    # 获取指定帖子的评论
    response = await async_client.get(f"/post/{created_post['id']}/comment")

    # 断言返回的状态码为200
    assert response.status_code == 200
    # 断言返回的评论数据为空
    assert response.json() == []


# 使用pytest.mark.anyio装饰器标记此函数为异步函数
@pytest.mark.anyio
async def test_get_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    # 使用async_client发送GET请求，获取创建的帖子
    response = await async_client.get(f"/post/{created_post['id']}")

    # 断言响应状态码为200
    assert response.status_code == 200
    # 断言响应内容与预期一致
    assert response.json() == {
        "post": {
            **created_post,
            "likes": 0,
        },
        "comments": [created_comment],
    }


# 使用pytest.mark.anyio装饰器标记此函数为异步函数
@pytest.mark.anyio
async def test_get_missing_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    # 使用async_client发送GET请求，获取不存在的帖子
    response = await async_client.get("/post/2")
    # 断言响应状态码为404
    assert response.status_code == 404
