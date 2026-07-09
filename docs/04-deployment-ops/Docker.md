# Docker 容器化部署教程

> 本文档面向 Docker 新手，从零开始讲解 Docker 的概念、本项目的容器化方案，以及如何部署到腾讯云。

---
AppSecret 获取方式：微信 MP 后台 → 设置 → 开发设置 → 开发者密码(AppSecret)：
0e9a69b03f45330a46ecf42e73f85217

{
  "DB_TYPE": "mysql",
  "DB_HOST": "sh-cynosdbmysql-grp-kz0y0ejc.sql.tencentcdb.com",
  "DB_PORT": "22860",
  "DB_USER": "chem_user",
  "DB_PASSWORD": "Test123456",
  "DB_NAME": "cloud1-d5gls7mdgf0e5f907",
  "DEBUG": "false",
  "SWAGGER_ENABLED": "false",
  "JWT_SECRET_KEY": "RandomKey2026ForCloudDeploy!",
  "CORS_ORIGINS": "*",
  "UPLOAD_DIR": "./uploads",
  "EXPORT_DIR": "./exports"
}
## 目录

1. [Docker 是什么](#1-docker-是什么)
2. [为什么本项目要用 Docker](#2-为什么本项目要用-docker)
3. [安装 Docker Desktop](#3-安装-docker-desktop)
4. [Docker 核心概念](#4-docker-核心概念)
5. [本项目的容器化架构](#5-本项目的容器化架构)
6. [本地开发环境（一键启动）](#6-本地开发环境一键启动)
7. [常用 Docker 命令速查](#7-常用-docker-命令速查)
8. [腾讯云容器镜像服务（TCR）](#8-腾讯云容器镜像服务tcr)
9. [微信云开发 - 云数据库（MySQL）](#9-微信云开发---云数据库mysql)
10. [微信云开发 - 云后台（云托管）](#10-微信云开发---云后台云托管)
11. [完整部署流程](#11-完整部署流程)
12. [常见问题排查](#12-常见问题排查)

---

## 1. Docker 是什么

### 一句话理解

Docker 是一个"**软件集装箱**"——把你的程序和它运行需要的所有东西（Python、MySQL、依赖库、配置文件）打包成一个标准的"箱子"（镜像），这个箱子可以在任何装了 Docker 的电脑上一键运行。

### 用生活类比

| 没有 Docker | 有了 Docker |
|------------|------------|
| 搬家时家具散装，容易磕碰 | 搬家公司用标准集装箱，家具打包即走 |
| 换电脑要重新装环境 | 一条命令，环境原样搬过去 |
| "我电脑上能跑啊" | 在任何电脑上都能跑 |

### 没有 Docker 的痛苦

```
新同事入职，想跑项目：
1. 装 Python 3.11  → "我电脑上是 3.9 行不行？"  → 不行
2. pip install 一堆包 → "这个包编译失败了"  → 百度半天
3. 装 MySQL 8.0   → "端口被占用了"  → 又百度半天
4. 建库建表       → "SQL 文件在哪？"  → 找了半天
5. 终于跑起来了   → "我电脑上怎么不行？"  → 版本不一样
```

### 有了 Docker

```
新同事入职：
1. 安装 Docker Desktop
2. docker compose up -d  → 喝杯咖啡
3. 项目跑起来了 ✅
```

---

## 2. 为什么本项目要用 Docker

### 2.1 一键启动完整环境

本项目需要两个服务配合工作：

```
┌─────────────────────────────────┐
│       docker-compose.yml        │
│                                 │
│  ┌───────────┐  ┌────────────┐ │
│  │  MySQL    │  │  FastAPI   │ │
│  │  数据库    │◄─│  后端服务   │ │
│  │  端口3306 │  │  端口8000  │ │
│  └───────────┘  └────────────┘ │
│                                 │
│  init.sql → 自动建表+预置数据    │
└─────────────────────────────────┘
```

不用 Docker，你需要：分别安装 Python 和 MySQL，手动配置版本兼容性。
用 Docker，只需要：`docker compose up -d`，两个服务同时启动。

### 2.2 数据库自动初始化

本项目参考了 [学之思 xzs](https://github.com/mindskip/xzs-mysql) 的部署方案：

```yaml
# docker-compose.yml 关键片段
volumes:
  - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
```

MySQL 容器首次启动时，会**自动执行** `init.sql` 建库建表、插入测试数据。无需手动操作。

### 2.3 生产环境一致性

本地测试和线上部署使用**同一套 Docker 镜像**，不存在"本地能跑线上不行"的问题。

---

## 3. 安装 Docker Desktop

### 下载地址

https://www.docker.com/products/docker-desktop/

- Windows 10/11：下载 Windows 版
- 安装后需要**重启电脑**
- 重启后打开 Docker Desktop，等左下角显示绿色 "Engine running"

### 常见问题

**Q: 安装后提示需要开启 WSL2？**

A: 打开 PowerShell（管理员），执行：
```powershell
wsl --install
```
重启电脑即可。

**Q: Docker Desktop 启动很慢？**

A: 正常现象，首次启动需要初始化 WSL2 虚拟机，约 1-2 分钟。

---

## 4. Docker 核心概念

### 4.1 镜像（Image）vs 容器（Container）

| 概念 | 类比 | 说明 |
|------|------|------|
| **镜像 (Image)** | 安装光盘/系统模板 | 只读的，包含程序+环境+依赖 |
| **容器 (Container)** | 运行中的电脑 | 镜像跑起来就是容器，可以有多个 |
| **仓库 (Registry)** | 应用商店 | 存放镜像的地方，如 Docker Hub、腾讯云 TCR |

```
镜像 (Image)                容器 (Container)
┌──────────────┐           ┌──────────────┐
│ Python 3.11  │  docker   │ Python 3.11  │  ← 运行中的实例1
│ FastAPI      │ ──run──►  │ FastAPI      │
│ 你的代码     │           │ 你的代码     │
│ 依赖库       │           │ 依赖库       │
└──────────────┘           └──────────────┘
     一份                     可以运行多个
```

### 4.2 Dockerfile

**Dockerfile** 是"制作镜像的配方"——告诉 Docker 怎么一步步搭建环境。

```dockerfile
# 本项目的 Dockerfile（简化版）
FROM python:3.11-slim          # 基础镜像：Python 3.11
WORKDIR /app                   # 工作目录
COPY requirements.txt .        # 复制依赖文件
RUN pip install -r requirements.txt  # 安装依赖
COPY . .                       # 复制源码
CMD ["uvicorn", "app.main:app"] # 启动命令
```

### 4.3 docker-compose.yml

**docker-compose.yml** 是"编排剧本"——告诉 Docker 怎么同时启动多个容器。

```yaml
# 本项目的 docker-compose.yml（简化版）
services:
  mysql:                        # 服务1：MySQL 数据库
    image: mysql:8.0
    ports: ["3306:3306"]
    volumes:
      - ./sql/init.sql:/docker-entrypoint-initdb.d/  # 自动初始化

  backend:                      # 服务2：FastAPI 后端
    build: .                    # 从 Dockerfile 构建
    ports: ["8000:8080"]
    depends_on: [mysql]         # 等 MySQL 先启动
    env_file: .env.docker       # 环境变量
```

### 4.4 Volume（数据卷）

容器删除后，里面的数据会丢失。Volume 用于**持久化数据**：

```yaml
volumes:
  - mysql_data:/var/lib/mysql   # MySQL 数据持久化
```

---

## 5. 本项目的容器化架构

### 5.1 文件结构

```
backend/
├── Dockerfile              # 镜像构建配方
├── docker-compose.yml      # 多容器编排
├── .dockerignore           # 构建时排除的文件
├── .env.docker             # Docker 本地测试环境变量
├── .env.cloud.example      # 云托管生产环境变量模板
├── requirements.txt        # Python 依赖
├── sql/
│   └── init.sql            # MySQL 初始化脚本（建表+测试数据）
└── app/                    # FastAPI 源码
```

### 5.2 两个容器的职责

| 容器 | 镜像 | 端口 | 职责 |
|------|------|------|------|
| `chem-mysql` | `mysql:8.0` | 3306 | 数据存储，执行 init.sql 建表 |
| `chem-backend` | 自己构建 | 8000→8080 | FastAPI 后端，处理 API 请求 |

### 5.3 通信方式

```
小程序 → http://127.0.0.1:8000/api/...  → chem-backend 容器
                                              │
                                              ▼ (内网)
                                        chem-mysql 容器 (172.17.0.x:3306)
```

同一个 docker-compose 网络内的容器，可以通过**服务名**（如 `mysql`）或**内网 IP** 互相访问。

---

## 6. 本地开发环境（一键启动）

### 6.1 启动

推荐（含 init.sql 种子数据、admin-console）：

```bash
cd F:\project\rr_teacher\backend
node ../admin-web/scripts/build.mjs
docker compose up -d --build
```

仓库根目录也提供 MySQL + Redis + Backend 最小栈（需先编译 admin-console）：

```bash
cd F:\project\rr_teacher
node admin-web/scripts/build.mjs
docker compose up -d --build
```

首次启动需要：
- 下载 MySQL 镜像（约 600MB）—— 只需一次
- 构建后端镜像（约 200MB）—— 代码修改后需重新构建

启动后：
- MySQL 自动建表 + 插入测试数据（约 10 秒）
- 后端自动连接 MySQL 并启动（约 5 秒）

### 6.2 验证

```bash
# 检查容器状态
docker ps

# 测试 API
curl http://127.0.0.1:8000/
# 返回: {"name":"高中化学教学辅助系统","version":"1.0.0"}

# 测试登录
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"teacher1","password":"123456"}'
```

### 6.3 测试账号

| 账号 | 密码 | 角色 |
|------|------|------|
| teacher1 | 123456 | 老师 |
| student1 | 123456 | 学生 |

### 6.4 修改代码后重新构建

```bash
docker compose up -d --build
```

Docker 会利用缓存，只重新构建变化的层，通常几秒到几十秒。

### 6.5 重置数据库

```bash
# 删除所有容器和数据卷，重新开始
docker compose down -v
docker compose up -d
```

---

## 7. 常用 Docker 命令速查

### 容器管理

```bash
docker compose up -d              # 启动（后台运行）
docker compose down               # 停止并删除容器
docker compose down -v            # 停止并删除容器+数据卷（清空数据）
docker compose ps                 # 查看运行状态
docker compose logs -f backend    # 实时查看后端日志
docker compose logs -f mysql      # 实时查看 MySQL 日志
```

### 镜像管理

```bash
docker images                     # 列出本地镜像
docker rmi <image_id>             # 删除镜像
docker system df                  # 查看 Docker 占用磁盘空间
docker system prune               # 清理无用镜像和缓存
```

### 进入容器

```bash
docker exec -it chem-mysql bash   # 进入 MySQL 容器终端
docker exec -it chem-backend bash # 进入后端容器终端
```

进入 MySQL 容器后可以连数据库：
```bash
mysql -u root -proot123456
SHOW DATABASES;
USE cloud1_d5gls7mdgf0e5f907;
SHOW TABLES;
```

### 查看容器详情

```bash
docker inspect chem-backend       # 查看容器配置（网络、环境变量等）
docker stats                      # 实时查看 CPU/内存使用
```

---

## 8. 腾讯云容器镜像服务（TCR）

### 8.1 是什么

TCR（Tencent Container Registry）是腾讯云的**Docker 镜像仓库**，相当于自己私有的"Docker Hub"。

```
你的电脑                    腾讯云 TCR                    云托管
┌──────────┐  docker push   ┌──────────┐  docker pull   ┌──────────┐
│ 构建镜像  │ ──────────►   │ 存放镜像  │ ◄──────────   │ 拉取运行  │
│ backend:v1│              │ backend:v1│               │ 容器      │
└──────────┘              └──────────┘               └──────────┘
```

### 8.2 开通和使用

#### 第一步：开通

1. 打开 https://console.cloud.tencent.com/tcr
2. 点「免费开通」→ 选「个人版」
3. 完成初始化（设置密码）

#### 第二步：创建命名空间和仓库

1. 左侧「命名空间」→ 新建 → 名称 `chem-teacher` → 公开
2. 左侧「镜像仓库」→ 新建 → 名称 `backend` → 命名空间选 `chem-teacher`

#### 第三步：登录、构建、推送

```bash
# 登录（输入用户名和密码）
docker login ccr.ccs.tencentyun.com
# 用户名: 你的腾讯云账号ID
# 密码: TCR 个人版密码

# 构建镜像（需先在仓库根目录编译 admin-console）
cd F:\project\rr_teacher
node admin-web/scripts/build.mjs
docker build -f backend/Dockerfile -t ccr.ccs.tencentyun.com/chem-teacher/backend:v1 .

# 或使用一键脚本（Windows）
powershell -File scripts/build_backend_image.ps1 ccr.ccs.tencentyun.com/chem-teacher/backend:v1

# 推送
docker push ccr.ccs.tencentyun.com/chem-teacher/backend:v1
```

### 8.3 镜像版本管理

在仓库根目录执行（先编译 admin-console，再构建镜像）：

```bash
cd F:\project\rr_teacher
node admin-web/scripts/build.mjs
docker build -f backend/Dockerfile -t ccr.ccs.tencentyun.com/chem-teacher/backend:dev .
docker push ccr.ccs.tencentyun.com/chem-teacher/backend:dev

docker build -f backend/Dockerfile -t ccr.ccs.tencentyun.com/chem-teacher/backend:v1 .
docker push ccr.ccs.tencentyun.com/chem-teacher/backend:v1

docker build -f backend/Dockerfile -t ccr.ccs.tencentyun.com/chem-teacher/backend:latest .
docker push ccr.ccs.tencentyun.com/chem-teacher/backend:latest
```

Windows 一键构建：

```powershell
powershell -File scripts/build_backend_image.ps1 ccr.ccs.tencentyun.com/chem-teacher/backend:v1
```

---

## 9. 微信云开发 - 云数据库（MySQL）

### 9.1 云开发自带 MySQL vs 独立腾讯云 MySQL

| 对比项 | 云开发自带 MySQL | 独立腾讯云 MySQL |
|--------|----------------|-----------------|
| 开通方式 | 云开发控制台直接开通 | 腾讯云控制台单独购买 |
| 费用 | 免费额度内 | 按量计费（最低约 ¥30/月） |
| 网络 | 和云托管同内网，零延迟 | 同区域也走内网 |
| 连接方式 | 内网地址（如 172.17.0.8） | 内网地址（如 gz-cdb-xxx.sql.tencentcdb.com） |
| 适合场景 | 开发测试、小规模应用 | 正式上线、大规模应用 |

### 9.2 初始化步骤

1. 微信开发者工具 → 云开发控制台 → 左侧「数据库」→ 选「SQL 型数据库」
2. 点「初始化」，等待创建完成
3. 点「数据库设置」查看连接信息：
   - 内网地址：`172.17.0.8`
   - 端口：`3306`
   - 数据库名：`cloud1-d5gls7mdgf0e5f907`

### 9.3 创建账号

1. 「账号管理」→「新建账号」
2. 填写：
   - 账号名：`chem_user`
   - 主机：`%`（允许任意 IP）
   - 权限：全选
   - 密码：自定义

### 9.4 连接配置

在云托管的环境变量中配置：

```
DB_TYPE=mysql
DB_HOST=172.17.0.8
DB_PORT=3306
DB_USER=chem_user
DB_PASSWORD=你的密码
DB_NAME=cloud1-d5gls7mdgf0e5f907
```

### 9.5 注意事项

- **自动暂停**：30 分钟无请求会自动暂停，首次访问需要等待冷启动（约 5-10 秒）
- **迁移自由**：MySQL 是标准协议，随时可以迁移到独立 MySQL 实例
- **初始化脚本**：首次建表使用 `backend/sql/init.sql`，在云托管的容器内会自动执行 `init_db()` 建表

---

## 10. 微信云开发 - 云后台（云托管）

### 10.1 是什么

云托管（CloudBase Run）是腾讯云的**容器化部署平台**——你把 Docker 镜像推上去，它帮你跑起来，自动分配公网域名。

```
你推镜像 ──► 云托管拉取镜像 ──► 启动容器 ──► 分配公网域名
                                         │
                                         ▼
                                   小程序可以直接访问
```

### 10.2 核心优势

| 优势 | 说明 |
|------|------|
| **免服务器** | 不需要自己买 ECS 服务器 |
| **自动扩缩** | 没请求时缩容到 0（省钱），有请求时自动扩容 |
| **公网域名** | 自动分配 HTTPS 域名，小程序可直接访问 |
| **内网通信** | 和云数据库同一内网，延迟极低 |
| **免费额度** | 个人版每月有一定免费调用次数 |

### 10.3 部署步骤

1. 云开发控制台 → 左侧「云后台」→「新建服务」
2. 选择「自定义部署」
3. 镜像来源：腾讯云容器镜像 → 选择推送的镜像
4. 配置环境变量（DB_TYPE, DB_HOST, DB_PASSWORD 等）
5. 端口：`8080`（Dockerfile 中 EXPOSE 的端口）
6. 创建 → 等待部署完成 → 获得公网域名

### 10.4 环境变量配置

在云托管的服务设置中，逐个添加：

```bash
# 数据库
DB_TYPE=mysql
DB_HOST=172.17.0.8
DB_PORT=3306
DB_USER=chem_user
DB_PASSWORD=你的MySQL密码
DB_NAME=cloud1-d5gls7mdgf0e5f907

# 安全（生产环境）
DEBUG=false
SWAGGER_ENABLED=false
JWT_SECRET_KEY=自定义随机字符串
CORS_ORIGINS=*
RATE_LIMIT_PER_MINUTE=120
LOGIN_RATE_LIMIT=5

# 文件上传
UPLOAD_DIR=./uploads
EXPORT_DIR=./exports
```

### 10.5 云托管 vs 云函数

| 对比项 | 云托管 | 云函数 |
|--------|--------|--------|
| 运行方式 | 长期运行的容器 | 事件触发的函数 |
| 适合场景 | Web API（如 FastAPI） | 短任务（如图片处理） |
| 冷启动 | 无（容器一直运行） | 有（首次调用需初始化） |
| 本项目适用 | ✅ FastAPI 后端 | ⚠️ OCR 服务可考虑 |

---

## 11. 完整部署流程

### 概览

```
                    你的电脑                          腾讯云
    ┌─────────────────────────┐     ┌──────────────────────────┐
    │                         │     │                          │
    │  1. docker build        │     │  4. 云托管拉取镜像         │
    │     ↓                   │     │     ↓                    │
    │  2. docker push ────────┼────►│  5. 启动容器              │
    │                         │     │     ↓                    │
    │                         │     │  6. 分配公网域名           │
    │                         │     │     ↓                    │
    │  3. 修改 api.js         │     │  7. 小程序访问公网域名      │
    │     API_BASE=新域名     │◄────┼──────                    │
    └─────────────────────────┘     └──────────────────────────┘
```

### 步骤清单

| 步骤 | 操作 | 在哪做 |
|------|------|--------|
| 1 | 构建 Docker 镜像 | 本地终端 |
| 2 | 推送镜像到 TCR | 本地终端 |
| 3 | 创建云托管服务 | 云开发控制台 |
| 4 | 配置环境变量 | 云开发控制台 |
| 5 | 获取公网域名 | 云开发控制台 |
| 6 | 修改前端 API_BASE | 编辑器 |
| 7 | 测试 | 微信开发者工具 |

### 前端切换到云托管

镜像推送成功并部署后，修改 `frontend/src/utils/api.js`：

```javascript
// 切换到云托管域名（部署后获得）
export const API_BASE = 'https://你的云托管域名'
```

重新编译小程序即可访问云端后端。

---

## 12. 常见问题排查

### Q: docker compose up 报错 "port is already allocated"

某个端口被占用（可能是之前没停干净）：

```bash
# 查看占用端口的进程
netstat -ano | findstr :8000

# 停掉所有相关容器
docker compose down
```

### Q: MySQL 容器启动后立即退出

查看日志找原因：

```bash
docker logs chem-mysql
```

常见原因：
- 端口 3306 被本机 MySQL 占用 → 先停本机 MySQL 服务
- 数据卷损坏 → `docker compose down -v` 删除重来

### Q: 后端报 "连接 MySQL 失败"

1. 检查 MySQL 是否启动：`docker ps`
2. 检查连接信息是否正确（环境变量）
3. 等 MySQL 初始化完成（首次启动需 10-15 秒）

### Q: Docker 镜像拉取很慢

配置 Docker 镜像加速器：

1. Docker Desktop → Settings → Docker Engine
2. 添加：
```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://dockerhub.icu"
  ]
}
```
3. Apply & Restart

### Q: 云托管容器启动失败

查看云托管日志：

1. 云开发控制台 → 云后台 → 点击服务名 → 日志
2. 查看启动日志中的报错信息
3. 常见原因：环境变量配置错误、MySQL 连接不上

### Q: 云数据库自动暂停后首次访问很慢

这是正常现象（冷启动）。解决方案：
- 保持最小实例数为 1（会增加少量费用）
- 或接受首次请求 5-10 秒延迟

---

## 附录：本项目 Docker 相关文件说明

| 文件 | 用途 | 何时修改 |
|------|------|---------|
| `backend/Dockerfile` | 构建后端镜像的配方 | 添加新的系统依赖时 |
| `backend/docker-compose.yml` | 本地编排 MySQL + 后端 | 添加新服务时 |
| `backend/.env.docker` | 本地测试环境变量 | 修改数据库密码时 |
| `backend/.env.cloud.example` | 云托管环境变量模板 | 参考用 |
| `backend/.dockerignore` | 构建时排除文件 | 一般不需要改 |
| `backend/sql/init.sql` | MySQL 初始化脚本 | 新增/修改表结构时 |
| `backend/requirements.txt` | Python 依赖 | 添加新的 Python 包时 |
| `frontend/cloudfunctions/` | 云函数代码 | 开发新云函数时 |
| `frontend/src/utils/cloud.js` | 云存储工具函数 | 云存储相关改动时 |
