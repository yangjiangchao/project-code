from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import yaml
from datetime import datetime, timedelta

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

app = FastAPI(title="翻墙数据可视化 API")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== 配置加载 ==============

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')

def load_config():
    """加载配置文件，环境变量优先于配置文件"""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    db = cfg.get('database', {})
    server = cfg.get('server', {})
    return {
        'database': {
            'host': os.getenv('DB_HOST', db.get('host', 'localhost')),
            'port': os.getenv('DB_PORT', str(db.get('port', '5432'))),
            'database': os.getenv('DB_NAME', db.get('name', 'visualization')),
            'user': os.getenv('DB_USER', db.get('user', 'visualization')),
            'password': os.getenv('DB_PASSWORD', db.get('password', '')),
        },
        'server': {
            'host': os.getenv('SERVER_HOST', server.get('host', '0.0.0.0')),
            'port': int(os.getenv('SERVER_PORT', str(server.get('port', 8000)))),
        },
        'api': {
            'base_url': os.getenv('API_BASE_URL', cfg.get('api', {}).get('base_url', 'http://localhost:8000/api')),
        },
    }

CONFIG = load_config()

def get_db_connection():
    return psycopg2.connect(**CONFIG['database'])


def build_time_condition(time_range: str = "") -> tuple:
    """构建时间范围 SQL 条件和参数"""
    if not time_range or time_range == "all":
        return "", {}
    try:
        days = int(time_range)
        return "WHERE handle_datetime >= %(min_date)s", {"min_date": datetime.now() - timedelta(days=days)}
    except (ValueError, TypeError):
        return "", {}


def build_time_condition_and(time_range: str = "") -> tuple:
    """构建时间范围 SQL 条件（用于 AND 连接）"""
    if not time_range or time_range == "all":
        return "WHERE 1=1", {}
    try:
        days = int(time_range)
        return "WHERE handle_datetime >= %(min_date)s", {"min_date": datetime.now() - timedelta(days=days)}
    except (ValueError, TypeError):
        return "WHERE 1=1", {}


# ============== 主页统计页面 API ==============

@app.get("/api/stats/install-app")
async def get_install_app_stats():
    """
    主页展示 1: 统计安装翻墙工具、小众应用 (app_package_name 不为空) 的每天用户数、积累用户数
    统计 sql: app_package_name IS NOT NULL -- 安装维度
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            DATE(handle_datetime) as stat_date,
            COUNT(DISTINCT mobile) FILTER (WHERE mobile IS NOT NULL AND mobile <> '' AND (auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL)) as daily_users,
            SUM(COUNT(DISTINCT mobile) FILTER (WHERE mobile IS NOT NULL AND mobile <> '' AND (auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL))) OVER (ORDER BY DATE(handle_datetime)) as accumulated_users
        FROM nb_mass_resource_all_stream
        WHERE app_package_name IS NOT NULL
        GROUP BY DATE(handle_datetime)
        ORDER BY stat_date DESC
        LIMIT 30
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


@app.get("/api/stats/tunnel-tool")
async def get_tunnel_tool_stats():
    """
    主页展示 2: 使用翻墙工具的每天用户数、积累总用户数
    其中包括了协议识别数据，统计表中 app_package_name 字段为 NULL 的数据
    统计 sql: app_package_name IS NULL -- 识别维度
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            DATE(handle_datetime) as stat_date,
            COUNT(DISTINCT mobile) FILTER (WHERE mobile IS NOT NULL AND mobile <> '' AND (auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL)) as daily_users,
            SUM(COUNT(DISTINCT mobile) FILTER (WHERE mobile IS NOT NULL AND mobile <> '' AND (auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL))) OVER (ORDER BY DATE(handle_datetime)) as accumulated_users
        FROM nb_mass_resource_all_stream
        WHERE app_package_name IS NULL
        GROUP BY DATE(handle_datetime)
        ORDER BY stat_date DESC
        LIMIT 30
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


@app.get("/api/stats/tunnel-protocol")
async def get_tunnel_protocol_stats():
    """
    主页展示 3: 使用翻墙协议识别的每天用户数、积累用户总数
    只统计协议数据
    统计 sql: tunnel_proto_type IS NOT NULL AND content_s IS NULL
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            DATE(handle_datetime) as stat_date,
            COUNT(DISTINCT mobile) FILTER (WHERE mobile IS NOT NULL AND mobile <> '' AND (auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL)) as daily_users,
            SUM(COUNT(DISTINCT mobile) FILTER (WHERE mobile IS NOT NULL AND mobile <> '' AND (auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL))) OVER (ORDER BY DATE(handle_datetime)) as accumulated_users
        FROM nb_mass_resource_all_stream
        WHERE tunnel_proto_type IS NOT NULL AND content_s IS NULL
        GROUP BY DATE(handle_datetime)
        ORDER BY stat_date DESC
        LIMIT 30
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


@app.get("/api/stats/tunnel-decrypt")
async def get_tunnel_decrypt_stats():
    """
    主页展示 4: 翻墙访问应用/网站的每日用户数、积累总用户数
    包括一次和二次数据 -- 解密维度
    统计 sql: tunnel_proto_type IS NOT NULL AND content_s IS NOT NULL
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            DATE(handle_datetime) as stat_date,
            COUNT(DISTINCT mobile) FILTER (WHERE mobile IS NOT NULL AND mobile <> '' AND (auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL)) as daily_users,
            SUM(COUNT(DISTINCT mobile) FILTER (WHERE mobile IS NOT NULL AND mobile <> '' AND (auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL))) OVER (ORDER BY DATE(handle_datetime)) as accumulated_users
        FROM nb_mass_resource_all_stream
        WHERE tunnel_proto_type IS NOT NULL AND content_s IS NOT NULL
        GROUP BY DATE(handle_datetime)
        ORDER BY stat_date DESC
        LIMIT 30
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


@app.get("/api/stats/proxy-server")
async def get_proxy_server_stats():
    """
    主页展示 6: 统计代理服务器访问用户数
    统计 sql: tunnel_server_ip IS NOT NULL
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            DATE(handle_datetime) as stat_date,
            COUNT(DISTINCT mobile) FILTER (WHERE mobile IS NOT NULL AND mobile <> '' AND (auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL)) as daily_users,
            SUM(COUNT(DISTINCT mobile) FILTER (WHERE mobile IS NOT NULL AND mobile <> '' AND (auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL))) OVER (ORDER BY DATE(handle_datetime)) as accumulated_users
        FROM nb_mass_resource_all_stream
        WHERE tunnel_server_ip IS NOT NULL
        GROUP BY DATE(handle_datetime)
        ORDER BY stat_date DESC
        LIMIT 30
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


@app.get("/api/stats/airport-website")
async def get_airport_website_stats():
    """
    主页展示 5: 机场网站统计
    统计 sql: tool_name = '机场网站' OR app_type = '100348246'
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            DATE(handle_datetime) as stat_date,
            COUNT(DISTINCT mobile) FILTER (WHERE mobile IS NOT NULL AND mobile <> '' AND (auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL)) as daily_users,
            SUM(COUNT(DISTINCT mobile) FILTER (WHERE mobile IS NOT NULL AND mobile <> '' AND (auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL))) OVER (ORDER BY DATE(handle_datetime)) as accumulated_users
        FROM nb_mass_resource_all_stream
        WHERE tool_name = '机场网站' OR app_type = '100348246'
        GROUP BY DATE(handle_datetime)
        ORDER BY stat_date DESC
        LIMIT 30
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


@app.get("/api/stats/proxy-server-rank")
async def get_proxy_server_rank(time_range: str = ""):
    """
    主页展示：代理服务器排行 Top10
    time_range: 7, 30, all
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    time_condition, params = build_time_condition_and(time_range)

    cur.execute(f"""
        SELECT
            tunnel_server_ip,
            COUNT(DISTINCT mobile) FILTER (WHERE auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL) as user_count,
            COUNT(*) as access_count
        FROM nb_mass_resource_all_stream
        {time_condition}
          AND tunnel_server_ip IS NOT NULL
          AND tunnel_server_ip <> ''
        GROUP BY tunnel_server_ip
        ORDER BY user_count DESC
        LIMIT 10
    """, params if params else {})

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


@app.get("/api/stats/install-app-rank")
async def get_install_app_rank(time_range: str = ""):
    """
    主页展示：安装应用排行 Top10
    time_range: 7, 30, all
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    time_condition, params = build_time_condition_and(time_range)

    cur.execute(f"""
        SELECT
            app_package_name,
            app_name,
            COUNT(DISTINCT mobile) FILTER (WHERE auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL) as user_count,
            COUNT(*) as access_count
        FROM nb_mass_resource_all_stream
        {time_condition}
          AND app_package_name IS NOT NULL
          AND app_package_name <> ''
        GROUP BY app_package_name, app_name
        ORDER BY user_count DESC
        LIMIT 10
    """, params if params else {})

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


@app.get("/api/stats/tunnel-tool-rank")
async def get_tunnel_tool_rank(time_range: str = ""):
    """
    主页展示：翻墙工具排行 Top10
    time_range: 7, 30, all
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    time_condition, params = build_time_condition_and(time_range)

    cur.execute(f"""
        SELECT
            tool_name,
            COUNT(DISTINCT mobile) FILTER (WHERE auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL) as user_count,
            COUNT(*) as access_count
        FROM nb_mass_resource_all_stream
        {time_condition}
          AND tool_name IS NOT NULL
          AND tool_name <> ''
        GROUP BY tool_name
        ORDER BY user_count DESC
        LIMIT 10
    """, params if params else {})

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


@app.get("/api/stats/protocol-rank")
async def get_protocol_rank(time_range: str = ""):
    """
    主页展示：翻墙协议排行 Top10
    time_range: 7, 30, all
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    time_condition, params = build_time_condition_and(time_range)

    cur.execute(f"""
        SELECT
            tunnel_proto_type,
            COUNT(DISTINCT mobile) FILTER (WHERE auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL) as user_count,
            COUNT(*) as access_count
        FROM nb_mass_resource_all_stream
        {time_condition}
          AND tunnel_proto_type IS NOT NULL
          AND tunnel_proto_type <> ''
        GROUP BY tunnel_proto_type
        ORDER BY user_count DESC
        LIMIT 10
    """, params if params else {})

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


@app.get("/api/stats/decrypt-rank")
async def get_decrypt_rank(time_range: str = ""):
    """
    主页展示：翻墙解密数据排行 Top10
    time_range: 7, 30, all
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    time_condition, params = build_time_condition_and(time_range)

    cur.execute(f"""
        SELECT
            domain,
            COUNT(DISTINCT mobile) FILTER (WHERE auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL) as user_count,
            COUNT(*) as access_count
        FROM nb_mass_resource_all_stream
        {time_condition}
          AND tunnel_proto_type IS NOT NULL AND content_s IS NOT NULL
          AND domain IS NOT NULL
          AND domain <> ''
        GROUP BY domain
        ORDER BY user_count DESC
        LIMIT 10
    """, params if params else {})

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


@app.get("/api/stats/airport-website-rank")
async def get_airport_website_rank(time_range: str = ""):
    """
    主页展示：机场网站排行 Top10
    统计 sql: tool_name = '机场网站' OR app_type = '100348246'
    time_range: 7, 30, all
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    time_condition, params = build_time_condition_and(time_range)

    cur.execute(f"""
        SELECT
            domain,
            COUNT(DISTINCT mobile) FILTER (WHERE auth_account IS NOT NULL OR imei IS NOT NULL OR imsi IS NOT NULL) as user_count,
            COUNT(*) as access_count
        FROM nb_mass_resource_all_stream
        {time_condition}
          AND (tool_name = '机场网站' OR app_type = '100348246')
          AND domain IS NOT NULL
          AND domain <> ''
        GROUP BY domain
        ORDER BY user_count DESC
        LIMIT 10
    """, params if params else {})

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


@app.get("/api/stats/trend")
async def get_trend_stats():
    """
    主页展示 5(趋势图): 每天安装应用数量、每天翻墙解密数据量
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            DATE(handle_datetime) as stat_date,
            COUNT(DISTINCT CASE WHEN app_package_name IS NOT NULL AND app_package_name <> '' THEN mobile END) as install_app_count,
            COUNT(DISTINCT CASE WHEN tunnel_proto_type IS NOT NULL AND content_s IS NOT NULL THEN mobile END) as decrypt_count
        FROM nb_mass_resource_all_stream
        WHERE handle_datetime >= CURRENT_TIMESTAMP - INTERVAL '30 days'
        GROUP BY DATE(handle_datetime)
        ORDER BY stat_date DESC
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


# ============== 翻墙详情统计页面 API ==============

@app.get("/api/detail/app-top20")
async def get_app_top20():
    """
    翻墙详情 1: 安装应用 top20 排行
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            app_package_name,
            app_name,
            COUNT(DISTINCT mobile) as user_count,
            COUNT(*) as access_count
        FROM nb_mass_resource_all_stream
        WHERE app_package_name IS NOT NULL
          AND app_package_name <> ''
        GROUP BY app_package_name, app_name
        ORDER BY user_count DESC
        LIMIT 20
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


@app.get("/api/detail/app-list")
async def get_app_list(page: int = 1, page_size: int = 50):
    """
    详情展示 1: 安装应用使用详情 - 分页查看所有信息
    包括 apk 包名、应用名称
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    offset = (page - 1) * page_size

    cur.execute("""
        WITH agg AS (
            SELECT app_package_name,
                   COUNT(DISTINCT mobile) as user_count,
                   COUNT(*) as access_count
            FROM nb_mass_resource_all_stream
            WHERE app_package_name IS NOT NULL AND app_package_name <> ''
            GROUP BY app_package_name
        )
        SELECT
            s.app_package_name,
            s.app_name,
            s.mobile,
            s.imei,
            s.imsi,
            s.tunnel_proto_type,
            s.domain,
            s.handle_datetime,
            s.capture_time,
            a.user_count,
            a.access_count
        FROM nb_mass_resource_all_stream s
        JOIN agg a ON s.app_package_name = a.app_package_name
        WHERE s.app_package_name IS NOT NULL
          AND s.app_package_name <> ''
        ORDER BY s.handle_datetime DESC
        LIMIT %s OFFSET %s
    """, (page_size, offset))

    result = cur.fetchall()

    # 获取总数
    cur.execute("""
        SELECT COUNT(*) as total
        FROM nb_mass_resource_all_stream
        WHERE app_package_name IS NOT NULL
          AND app_package_name <> ''
    """)
    total = cur.fetchone()['total']

    cur.close()
    conn.close()

    return {"data": result, "total": total, "page": page, "page_size": page_size}


@app.get("/api/detail/tunnel-top20")
async def get_tunnel_top20():
    """
    翻墙详情 2: 翻墙工具使用详情 top20
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            domain,
            tunnel_proto_type,
            COUNT(DISTINCT mobile) as user_count,
            COUNT(*) as access_count
        FROM nb_mass_resource_all_stream
        WHERE domain IS NOT NULL
          AND domain <> ''
        GROUP BY domain, tunnel_proto_type
        ORDER BY user_count DESC
        LIMIT 20
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


@app.get("/api/detail/tunnel-list")
async def get_tunnel_list(page: int = 1, page_size: int = 50):
    """
    详情展示 2: 翻墙工具使用详情 - 分页查看所有信息
    包括域名、应用名称
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    offset = (page - 1) * page_size

    cur.execute("""
        WITH agg AS (
            SELECT domain, app_name,
                   COUNT(DISTINCT mobile) as user_count,
                   COUNT(*) as access_count
            FROM nb_mass_resource_all_stream
            WHERE domain IS NOT NULL AND domain <> ''
            GROUP BY domain, app_name
        )
        SELECT
            s.domain,
            s.app_name,
            s.mobile,
            s.imei,
            s.imsi,
            s.tunnel_proto_type,
            s.handle_datetime,
            s.capture_time,
            a.user_count,
            a.access_count
        FROM nb_mass_resource_all_stream s
        JOIN agg a ON s.domain = a.domain AND s.app_name IS NOT DISTINCT FROM a.app_name
        WHERE s.domain IS NOT NULL
          AND s.domain <> ''
        ORDER BY s.handle_datetime DESC
        LIMIT %s OFFSET %s
    """, (page_size, offset))

    result = cur.fetchall()

    # 获取总数
    cur.execute("""
        SELECT COUNT(*) as total
        FROM nb_mass_resource_all_stream
        WHERE domain IS NOT NULL
          AND domain <> ''
    """)
    total = cur.fetchone()['total']

    cur.close()
    conn.close()

    return {"data": result, "total": total, "page": page, "page_size": page_size}


@app.get("/api/detail/content-top20")
async def get_content_top20():
    """
    翻墙详情 3: 访问内容使用详情 top20
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            content_s,
            tunnel_proto_type,
            url,
            COUNT(DISTINCT mobile) as user_count,
            COUNT(*) as access_count
        FROM nb_mass_resource_all_stream
        WHERE content_s IS NOT NULL
          AND content_s <> ''
        GROUP BY content_s, tunnel_proto_type, url
        ORDER BY user_count DESC
        LIMIT 20
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


@app.get("/api/detail/content-list")
async def get_content_list(page: int = 1, page_size: int = 50):
    """
    详情展示 3: 访问内容使用详情 - 分页查看所有信息
    展示内容包括域名、访问 URL、USER_AGENT、协议类型、应用名称
    其他和此手机号相关的数据都隐藏到详细内容中
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    offset = (page - 1) * page_size

    cur.execute("""
        WITH agg AS (
            SELECT content_s, tunnel_proto_type, url,
                   COUNT(DISTINCT mobile) as user_count,
                   COUNT(*) as access_count
            FROM nb_mass_resource_all_stream
            WHERE content_s IS NOT NULL AND content_s <> ''
            GROUP BY content_s, tunnel_proto_type, url
        )
        SELECT
            s.id,
            s.domain,
            s.url,
            s.user_agent,
            s.tunnel_proto_type,
            s.app_name,
            s.mobile,
            s.imei,
            s.imsi,
            s.handle_datetime,
            s.capture_time,
            a.user_count,
            a.access_count
        FROM nb_mass_resource_all_stream s
        JOIN agg a ON s.content_s = a.content_s
                  AND s.tunnel_proto_type IS NOT DISTINCT FROM a.tunnel_proto_type
                  AND s.url IS NOT DISTINCT FROM a.url
        WHERE s.content_s IS NOT NULL
          AND s.content_s <> ''
        ORDER BY s.handle_datetime DESC
        LIMIT %s OFFSET %s
    """, (page_size, offset))

    result = cur.fetchall()

    # 获取总数
    cur.execute("""
        SELECT COUNT(*) as total
        FROM nb_mass_resource_all_stream
        WHERE content_s IS NOT NULL
          AND content_s <> ''
    """)
    total = cur.fetchone()['total']

    cur.close()
    conn.close()

    return {"data": result, "total": total, "page": page, "page_size": page_size}


@app.get("/api/detail/content-detail/{id}")
async def get_content_detail(id: int):
    """
    获取访问内容详细信息
    显示该手机号相关的所有数据
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            mobile, imei, imsi,
            app_package_name, app_name,
            domain, url, user_agent,
            tunnel_proto_type, tunnel_server_ip, content_s,
            terminal_type,
            handle_datetime, capture_time, src_ip, dst_ip
        FROM nb_mass_resource_all_stream
        WHERE id = %s
    """, (id,))

    result = cur.fetchone()

    cur.close()
    conn.close()

    return {"data": result}


# ============== 查询检索页面 API ==============

class SearchRequest(BaseModel):
    keyword: Optional[str] = None
    mobile: Optional[str] = None
    imei: Optional[str] = None
    imsi: Optional[str] = None
    domain: Optional[str] = None
    app_package_name: Optional[str] = None
    app_name: Optional[str] = None
    tunnel_server_ip: Optional[str] = None
    tunnel_proto_type: Optional[str] = None


@app.post("/api/search")
async def search(request: SearchRequest):
    """
    查询检索：支持按条件进行数据检索
    keyword: 跨字段模糊搜索（手机号/IMEI/IMSI/域名/包名/应用名）
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    conditions = []
    params = {}

    if request.keyword:
        conditions.append("(mobile LIKE %(kw)s OR imei LIKE %(kw)s OR imsi LIKE %(kw)s OR domain LIKE %(kw)s OR app_package_name LIKE %(kw)s OR app_name LIKE %(kw)s)")
        params["kw"] = f"%{request.keyword}%"

    if request.mobile:
        conditions.append("mobile LIKE %(mobile)s")
        params["mobile"] = f"%{request.mobile}%"

    if request.imei:
        conditions.append("imei LIKE %(imei)s")
        params["imei"] = f"%{request.imei}%"

    if request.imsi:
        conditions.append("imsi LIKE %(imsi)s")
        params["imsi"] = f"%{request.imsi}%"

    if request.domain:
        conditions.append("domain LIKE %(domain)s")
        params["domain"] = f"%{request.domain}%"

    if request.app_package_name:
        conditions.append("app_package_name LIKE %(app_package_name)s")
        params["app_package_name"] = f"%{request.app_package_name}%"

    if request.app_name:
        conditions.append("app_name LIKE %(app_name)s")
        params["app_name"] = f"%{request.app_name}%"

    if request.tunnel_server_ip:
        conditions.append("tunnel_server_ip LIKE %(tunnel_server_ip)s")
        params["tunnel_server_ip"] = f"%{request.tunnel_server_ip}%"

    if request.tunnel_proto_type:
        conditions.append("tunnel_proto_type ILIKE %(tunnel_proto_type)s")
        params["tunnel_proto_type"] = f"%{request.tunnel_proto_type}%"

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    query = f"""
        SELECT
            mobile, imei, imsi, app_package_name, app_name, domain,
            tunnel_proto_type, tunnel_server_ip, content_s, terminal_type,
            handle_datetime, src_ip, dst_ip
        FROM nb_mass_resource_all_stream
        WHERE {where_clause}
        ORDER BY handle_datetime DESC
        LIMIT 1000
    """

    cur.execute(query, params)
    result = cur.fetchall()

    cur.close()
    conn.close()

    return {"data": result, "total": len(result)}


@app.get("/api/search/detail/{mobile}")
async def search_detail(mobile: str):
    """
    查询详情：查看指定手机号的详细信息
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            mobile, imei, imsi, mac, app_package_name, app_name, domain,
            url, tunnel_proto_type, tunnel_server_ip, content_s,
            terminal_type, handle_datetime, src_ip, dst_ip
        FROM nb_mass_resource_all_stream
        WHERE mobile = %(mobile)s
        ORDER BY handle_datetime DESC
        LIMIT 500
    """, {"mobile": mobile})

    result = cur.fetchall()
    cur.close()
    conn.close()

    return {"data": result}


# ============== 汇总统计 API ==============

@app.get("/api/summary")
async def get_summary():
    """
    获取数据汇总统计
    总用户数: AUTH_ACCOUNT/IMEI/IMSI 不为空且不为空字符串的去重 mobile 数
    总应用数: tool_name 不为空的去重数量
    代理服务器数: tunnel_server_ip 不为空的去重数量
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            COUNT(DISTINCT mobile) FILTER (WHERE (auth_account IS NOT NULL AND auth_account <> '') OR (imei IS NOT NULL AND imei <> '') OR (imsi IS NOT NULL AND imsi <> '')) as total_users,
            COUNT(DISTINCT mobile) FILTER (WHERE DATE(handle_datetime) = CURRENT_DATE AND ((auth_account IS NOT NULL AND auth_account <> '') OR (imei IS NOT NULL AND imei <> '') OR (imsi IS NOT NULL AND imsi <> ''))) as today_users,
            COUNT(DISTINCT tool_name) FILTER (WHERE tool_name IS NOT NULL AND tool_name <> '') as total_apps,
            COUNT(DISTINCT tool_name) FILTER (WHERE DATE(handle_datetime) = CURRENT_DATE AND tool_name IS NOT NULL AND tool_name <> '') as today_apps,
            COUNT(DISTINCT tunnel_server_ip) FILTER (WHERE tunnel_server_ip IS NOT NULL) as total_servers,
            COUNT(DISTINCT tunnel_server_ip) FILTER (WHERE DATE(handle_datetime) = CURRENT_DATE AND tunnel_server_ip IS NOT NULL) as today_servers
        FROM nb_mass_resource_all_stream
    """)
    summary = cur.fetchone()

    cur.close()
    conn.close()

    return {"data": summary}


@app.get("/api/config")
async def get_config():
    """返回前端所需的配置信息"""
    return {"data": {"api_base_url": CONFIG['api']['base_url']}}


@app.get("/{filename:path}")
async def serve_frontend(filename: str):
    """Serve frontend HTML files"""
    filepath = os.path.join(FRONTEND_DIR, filename)
    if os.path.isfile(filepath):
        return FileResponse(filepath)
    # Default to index.html for root
    if not filename or filename == '.':
        return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'))
    raise HTTPException(status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=CONFIG['server']['host'], port=CONFIG['server']['port'])
