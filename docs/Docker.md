**Docker 本地测试**
✅ MySQL 启动 + 自动建表 + 预置数据
✅ FastAPI 后端运行在 8000 端口
✅ 登录接口正常返回 JWT Token
✅ 数据库连接正常（MySQL 8.0）
✅ 两个容器正常通信

## 你现在拥有的环境

|服务|状态|访问地址|
|---|---|---|
|**后端 API**|✅ 运行中|`http://127.0.0.1:8000`|
|**MySQL**|✅ 运行中|`127.0.0.1:3306`|
|**API 文档**|✅ 可用|`http://127.0.0.1:8000/docs`|

### 测试账号

|账号|密码|角色|
|---|---|---|
|teacher1|123456|老师|
|student1|123456|学生|

### 常用 Docker 命令

启动
cd F:\project\rr_teacher\backend
docker compose up -d

停止
docker compose down

停止并删除数据
docker compose down -v

查看日志
docker logs -f chem-backend

重建（代码修改后）
docker compose up -d --build