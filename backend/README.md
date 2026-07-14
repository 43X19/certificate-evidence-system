# FastAPI 后端

本目录是证书存证系统的 FastAPI 后端工程，负责基础业务接口、MySQL 连接、统一返回格式、公共验真 mock 接口，以及后续证书存证业务对接。

## 已完成内容

- FastAPI 项目骨架
- MySQL 连接配置
- `.env.example` 示例配置
- 统一返回格式
- CORS 配置
- 全局异常处理初版
- 核心表结构草案
- 学生列表接口
- 证书列表接口
- 公共验真 mock 接口
- 接口自动化测试

## 本地启动方式

以下命令都在 `backend` 目录执行。

先启动 MySQL：

```powershell
"D:\Software\MySQL\8.4\bin\mysqld.exe" --defaults-file="D:\code\_mysql_certificate_evidence\my.ini" --console
```

再启动 FastAPI：

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Swagger 接口文档地址：

```text
http://127.0.0.1:8000/docs
```

## 数据库表

本机数据库表已经创建。其他成员首次运行时，可在 `backend` 目录执行：

```powershell
.\.venv\Scripts\python.exe -m scripts.create_tables
```

当前表结构草案：

- `students`
- `certificates`
- `certificate_templates`
- `certificate_batches`
- `evidence_receipts`
- `revocation_records`
- `audit_logs`

## 当前接口

- `GET /api/health`
- `GET /api/health/db`
- `GET /api/students`
- `GET /api/certificates`
- `GET /api/verification/{certificate_no}`

公共验真 mock 示例：

- `CERT-20260714-0001` -> `PASS`
- `CERT-20260714-0002` -> `REVOKED`
- `CERT-HASH-MISMATCH` -> `HASH_MISMATCH`
- `CERT-NOT-EXIST` -> `NOT_FOUND`

## 测试

在 `backend` 目录执行：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

当前测试结果：

```text
5 passed
```

## 安全说明

不要提交以下内容：

- `.env`
- 数据库真实密码
- JWT 密钥
- API key
- 私钥、助记词
- 真实学生数据

只能提交 `.env.example`。当前 mock 数据使用测试学生和测试证书编号，不包含真实个人信息。
