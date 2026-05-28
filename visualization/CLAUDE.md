# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

翻墙数据可视化系统 — a single-page web application for visualizing VPN/proxy traffic data from a PostgreSQL database. Built with FastAPI backend serving both API and static frontend, Vue3 + Element Plus + ECharts for the UI.

**Single entry point**: `frontend/index.html` is served by the FastAPI backend at `http://localhost:8000/`. The three modules (主页统计 / 翻墙详情 / 智能查询) are implemented as tabs within one SPA, not separate pages.

## Development Commands

```bash
# Edit config: backend/config.yaml (db, server, api base_url)
# Env vars override config: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, SERVER_HOST, SERVER_PORT, API_BASE_URL

# Start backend (serves API + frontend at port 8000)
cd /home/jcyang/2026/visualization/backend
python3 main.py

# API documentation: http://localhost:8000/docs
# Frontend: http://localhost:8000/
```

No separate frontend dev server needed — the backend serves static files via the `/{filename:path}` route.

## Architecture

### Backend (`backend/main.py`)

- **Framework**: FastAPI with uvicorn
- **Database**: PostgreSQL, `nb_mass_resource_all_stream` table (~3717 records)
- **DB config**: localhost:5432, db=visualization, user=visualization, password=viz2026 (overridable via env vars `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`)
- **All routes defined in a single file** — no blueprint/module separation

**Route groups**:
1. `/api/summary` — aggregate stats (total users, apps, servers, records)
2. `/api/stats/*` — 6 dimension stats (install-app, tunnel-tool, tunnel-protocol, tunnel-decrypt, airport-website, proxy-server, proxy-server-rank, trend)
3. `/api/detail/*` — list endpoints with pagination (app-list, tunnel-list, content-list) + content-detail/{id}
4. `/api/search` — POST multi-condition search, supports `keyword` cross-field fuzzy matching + individual field filters
5. `/api/search/detail/{mobile}` — all records for a specific mobile number
6. `/{filename:path}` — serves static files from `../frontend/`

**Key pattern**: list endpoints (`app-list`, `tunnel-list`, `content-list`) return paginated results with `user_count` and `access_count` computed via CTE aggregation on the group-by key (package name / domain / content).

### Frontend (`frontend/index.html`)

Single HTML file with inline CSS and JS. Uses Vue3 global build + Element Plus + ECharts from CDN.

**Three tabs** controlled by `currentTab` state:
- **主页统计** (`stats`): Summary cards + 5 ECharts bar/line combo charts + proxy server rank table + trend chart
- **翻墙详情** (`detail`): Three paginated tables (app list, tunnel list, content list) with user_count/access_count columns + detail dialog
- **智能查询** (`search`): Keyword search bar + 4 filter dropdowns (domain, app name, protocol, server IP) that auto-trigger search on selection + card-style result display

**Chart rendering**: Charts are lazily initialized in `renderAllCharts()` and disposed/recreated on tab switch via `createOrGetChart()`.

### Database Schema

Table `nb_mass_resource_all_stream` — wide table with ~100 columns. Key fields used by the app:

| Field | Description |
|-------|-------------|
| `mobile`, `imei`, `imsi` | User identifiers |
| `app_package_name`, `app_name` | Installed app info |
| `domain`, `url`, `user_agent` | Network activity |
| `tunnel_proto_type` | VPN protocol (Shadowsocks, Vmess, Trojan, Vless) |
| `tunnel_server_ip` | Proxy server address |
| `content_s` | Decrypted content |
| `handle_datetime` | Record timestamp (used for daily stats) |
| `terminal_type` | Device type (Windows, etc.) |

5 indexes on key query fields (`mobile`, `imei`, `imsi`, `app_package_name`, `domain`, `tunnel_proto_type`, `tunnel_server_ip`, `content_s`, `handle_datetime`).

## Change Log

### V1.7 (2026-05-23)
- 主页统计：排行榜增加时间维度选择器（近 7 天、近 30 天、全部）
- 后端 6 个排行榜接口均支持 time_range 参数（7/30/all）

### V1.6 (2026-05-23)
- 主页统计：汇总统计卡片样式优化（渐变色背景、阴影效果）
- 主页统计：图表改为排行榜展示（Top10），包括安装应用、翻墙工具、翻墙协议、翻墙解密数据、机场网站、代理服务器
- 后端新增 6 个排行榜接口

### V1.5 (2026-05-22)
- 翻墙详情：三个详情列表去掉用户数、访问次数列，新增最近使用时间列
- 详情弹窗新增最近使用时间字段显示
- 主页统计：卡片标题优化（安装维度→安装应用、识别维度→翻墙工具、协议识别→翻墙协议、解密维度→翻墙解密数据、代理服务器 - 每日访问→代理服务器）
- 主页统计：移除"趋势 - 安装应用 / 解密数据量"趋势图
- 主页统计：新增机场网站统计图表（tool_name = '机场网站' OR app_type = '100348246'），编号为⑤

### V1.4 (2026-05-21)
- `/api/summary` 逻辑调整：total_users = auth_account/imei/imsi 不为空的去重 mobile 数；total_apps = tool_name 不为空的去重数；total_servers = tunnel_server_ip 不为空的去重数；移除 total_records
- 主页统计卡片从 4 列改为 3 列

### V1.3 (2026-05-21)
- 配置解耦：数据库连接、服务端口、API 地址提取至 `backend/config.yaml`
- 新增 `/api/config` 接口，前端动态获取 API 基础地址
- 环境变量优先于配置文件覆盖

### V1.2 (2026-05-21)
- Frontend refactored to single-page app with top tab navigation (参考 222.jpg 风格)
- Smart search: keyword cross-field fuzzy matching (mobile/IMEI/IMSI/domain/package/app name), Enter to search
- Smart search: filter dropdowns (domain, app, protocol, server IP) auto-trigger search on selection
- Smart search: card-style results with detail dialog
- Detail page: removed Top20 modules, added user_count/access_count columns to all three list tables
- Backend: list endpoints use CTE aggregation for user_count/access_count

### V1.1 (2026-05-20)
- Initial architecture: backend API + separate frontend pages (stats.html, detail.html, search.html)
