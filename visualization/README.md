# 翻墙数据可视化系统

## 项目结构

```
/home/jcyang/2026/visualization/
├── backend/
│   ├── main.py              # FastAPI 后端服务
│   ├── config.yaml          # 系统配置（数据库、服务、API）
│   ├── requirements.txt     # Python 依赖
│   ├── create_table.sql     # PostgreSQL 建表语句
│   └── create_test_data.py  # 测试数据生成脚本
├── frontend/
│   └── index.html           # 单页应用（统一入口，三 Tab 切换）
└── README.md                # 本文件
```

## 功能说明

### 主页统计
| 序号 | 维度 | 统计 SQL 条件 | 展示内容 |
|------|------|--------------|----------|
| ① | **安装应用** | `app_package_name IS NOT NULL` | 每天用户数、累计用户数 |
| ② | **翻墙工具** | `app_package_name IS NULL` | 每天用户数、累计用户数（含协议识别数据） |
| ③ | **翻墙协议** | `tunnel_proto_type IS NOT NULL AND content_s IS NULL` | 每天用户数、累计用户数 |
| ④ | **翻墙解密数据** | `tunnel_proto_type IS NOT NULL AND content_s IS NOT NULL` | 每天用户数、累计用户数（含一次和二次数据） |
| ⑤ | **机场网站** | `tool_name = '机场网站' OR app_type = '100348246'` | 每天用户数、累计用户数 |
| ⑥ | **代理服务器** | `tunnel_server_ip IS NOT NULL` | 每天访问用户数、累计用户数 |

### 翻墙详情
- **安装应用使用详情**: 分页列表，含手机号、IMEI、IMSI、包名、应用名称、最近使用时间
- **翻墙工具使用详情**: 分页列表，含手机号、IMEI、IMSI、域名、应用名称、最近使用时间
- **访问内容使用详情**: 分页列表，含手机号、IMEI、IMSI、域名、URL、USER_AGENT、协议、应用、最近使用时间，支持查看详情弹窗

### 智能查询
- **关键词搜索**: 顶部搜索框，支持手机号/IMEI/IMSI/域名/包名/应用名 跨字段模糊匹配，回车即查
- **筛选器**: 网站标签、应用名称、翻墙协议、代理服务器 IP 均为下拉列表，选中自动触发查询
- **结果展示**: 卡片式布局，显示手机号、IMEI、IMSI、应用、域名、协议、服务器、时间等信息
- **查看详情**: 点击"查看详情"查看该手机号的全部关联记录

## 快速开始

### 1. 配置文件

编辑 `backend/config.yaml` 修改数据库连接和服务参数：

```yaml
database:
  host: localhost
  port: 5432
  name: visualization
  user: visualization
  password: viz2026

server:
  host: 0.0.0.0
  port: 8000

api:
  base_url: http://localhost:8000/api
```

> 环境变量优先于配置文件：`DB_HOST`、`DB_PORT`、`DB_NAME`、`DB_USER`、`DB_PASSWORD`、`SERVER_HOST`、`SERVER_PORT`、`API_BASE_URL`

### 2. 安装依赖

```bash
cd /home/jcyang/2026/visualization/backend
pip3 install -r requirements.txt
```

### 3. 启动后端

```bash
python3 main.py
```

访问 http://localhost:8000/docs 查看 API 文档，访问 http://localhost:8000/ 进入前端页面。

## API 接口

### 汇总统计
| 接口 | 说明 |
|------|------|
| GET /api/summary | 汇总统计（总用户: auth_account/IMEI/IMSI 不为空，总应用: tool_name 去重，代理服务器: tunnel_server_ip 去重，含今日数） |

### 主页统计
| 接口 | 说明 | SQL 条件 |
|------|------|----------|
| GET /api/stats/install-app | 安装维度统计 | app_package_name IS NOT NULL |
| GET /api/stats/tunnel-tool | 识别维度统计 | app_package_name IS NULL |
| GET /api/stats/tunnel-protocol | 协议识别统计 | tunnel_proto_type IS NOT NULL AND content_s IS NULL |
| GET /api/stats/tunnel-decrypt | 解密维度统计 | tunnel_proto_type IS NOT NULL AND content_s IS NOT NULL |
| GET /api/stats/airport-website | 机场网站统计 | tool_name = '机场网站' OR app_type = '100348246' |
| GET /api/stats/proxy-server | 代理服务器统计 | tunnel_server_ip IS NOT NULL |
| GET /api/stats/proxy-server-rank | 代理服务器 Top20 | tunnel_server_ip IS NOT NULL |

### 翻墙详情
| 接口 | 说明 |
|------|------|
| GET /api/detail/app-list | 安装应用使用详情（分页） |
| GET /api/detail/tunnel-list | 翻墙工具使用详情（分页） |
| GET /api/detail/content-list | 访问内容使用详情（分页） |
| GET /api/detail/content-detail/{id} | 单条内容详情 |

### 查询检索
| 接口 | 说明 |
|------|------|
| POST /api/search | 多条件检索（支持 keyword 跨字段模糊匹配） |
| GET /api/search/detail/{mobile} | 手机号详情 |

## 技术栈

- **后端**: Python + FastAPI + PostgreSQL
- **前端**: Vue3 + Element Plus + ECharts

## 变更日志

### V1.7 (2026-05-23)
- 主页统计：排行榜增加时间维度选择器（近 7 天、近 30 天、全部）
- 后端 6 个排行榜接口均支持 time_range 参数（7/30/all）

### V1.6 (2026-05-23)
- 主页统计：汇总统计卡片样式优化（渐变色背景、阴影效果）
- 主页统计：图表改为排行榜展示（Top10），包括安装应用、翻墙工具、翻墙协议、翻墙解密数据、机场网站、代理服务器
- 后端新增 6 个排行榜接口：/api/stats/install-app-rank, /api/stats/tunnel-tool-rank, /api/stats/protocol-rank, /api/stats/decrypt-rank, /api/stats/airport-website-rank, /api/stats/proxy-server-rank

### V1.5 (2026-05-22)
- 翻墙详情：三个详情列表去掉用户数、访问次数列，新增最近使用时间列
- 详情弹窗新增最近使用时间字段显示
- 主页统计：卡片标题优化（安装维度→安装应用、识别维度→翻墙工具、协议识别→翻墙协议、解密维度→翻墙解密数据、代理服务器 - 每日访问→代理服务器）
- 主页统计：移除"趋势 - 安装应用 / 解密数据量"趋势图及相关接口调用
- 主页统计：新增机场网站统计图表（tool_name = '机场网站' OR app_type = '100348246'），编号为⑤，代理服务器改为⑥

### V1.4 (2026-05-21)
- 汇总统计逻辑调整：总用户数改为 auth_account/IMEI/IMSI 不为空的去重数量；总应用数改为 tool_name 不为空的去重数量；代理服务器数改为 tunnel_server_ip 不为空的去重数量
- 移除总记录数字段
- 主页统计汇总卡片布局从 4 列调整为 3 列

### V1.3 (2026-05-21)
- 配置文件解耦：数据库连接、服务端口、API 地址提取至 `backend/config.yaml`
- 新增 `/api/config` 接口，前端动态获取 API 基础地址
- 支持环境变量覆盖配置（`DB_HOST`、`SERVER_PORT`、`API_BASE_URL` 等）
- 新增 `pyyaml` 依赖

### V1.2 (2026-05-21)
- 前端重构为单页应用，参考 222.jpg 风格设计顶部导航栏，三 Tab（主页统计/翻墙详情/智能查询）切换
- 智能查询：关键词搜索支持跨字段模糊匹配（手机号/IMEI/IMSI/域名/包名/应用名），回车即查
- 智能查询：网站标签、应用名称、翻墙协议、代理服务器 IP 改为下拉列表，选中自动触发查询
- 智能查询：结果卡片式展示，支持查看详情弹窗
- 翻墙详情：移除 Top20 模块，三个详情列表均新增用户数、访问次数列
- 后端：app-list/tunnel-list/content-list 接口新增 user_count、access_count 字段

### V1.1 (2026-05-20)
- 前后端分离架构搭建
- 主页统计 5 维度图表 + 趋势图
- 翻墙详情 Top20 排行 + 分页列表
- 查询检索 多条件组合搜索

## 当前状态

系统已启动:
- 后端 API + 前端页面: http://localhost:8000/
- API 文档: http://localhost:8000/docs

测试数据：3717 条记录
