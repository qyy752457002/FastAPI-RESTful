#!/bin/sh 

alembic upgrade head

# exec：在 shell 脚本中，exec 命令用于执行指定的命令，并用它来替换当前的 shell 进程，而不是打开一个新的进程。
# 这意味着 uvicorn 将接管当前的 shell，当 uvicorn 停止时，容器也会停止。
# 这儿的80是容器的端口，不是主机的端口
exec uvicorn main:app --port 80 --reload