#!/usr/bin/env python3
"""
生成测试数据并验证可视化系统
"""
import psycopg2
import random
from datetime import datetime, timedelta

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "visualization",
    "user": "visualization",
    "password": "viz2026"
}

# 测试数据
PROTOCOLS = ['Shadowsocks', 'ShadowsocksR', 'vmess', 'vless', 'trojan', 'socks5']
APP_PACKAGES = [
    'com.github.shadowsocks',
    'com.v2ray.ang',
    'com.clash.android',
    'org.torproject.android',
    'com.nicegram'
]
APP_NAMES = [
    'Shadowsocks',
    'v2rayNG',
    'Clash',
    'Tor Browser',
    'Nicegram'
]
DOMAINS = [
    'google.com', 'youtube.com', 'twitter.com', 'facebook.com',
    'instagram.com', 'telegram.org', 'whatsapp.com', 'netflix.com'
]
SERVER_IPS = [
    '103.150.128.1', '103.150.128.2', '45.32.100.1', '45.32.100.2',
    '192.168.100.1', '192.168.100.2', '172.16.50.1', '172.16.50.2'
]
# 解密内容数据（用于访问内容 Top20）
DECRYPT_CONTENTS = [
    'https://www.google.com/search?q=vpn',
    'https://www.youtube.com/watch?v=abc123',
    'https://twitter.com/user/status/123456',
    'https://www.facebook.com/profile.php?id=123',
    'https://t.me/channel/1234',
    'https://www.instagram.com/p/ABC123',
    'https://api.telegram.org/bot123/sendMessage',
    'https://www.netflix.com/title/80123456',
    'wss://ss-panel.com/link/xxx',
    'https://v2rayse.com/subscribe/xxx',
]
URLS = [
    '/search', '/watch', '/status', '/profile', '/p', '/bot', '/title', '/link', '/subscribe',
    '/api/v1/data', '/api/v2/user', '/download/file1', '/chat/message'
]
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Dalvik/2.1.0 (Linux; U; Android 13; SM-A546B Build/TP1A.220624.014)',
    'okhttp/4.12.0',
    'PostmanRuntime/7.36.0',
]

def generate_mobile():
    return f"1{random.randint(1000000000, 9999999999)}"

def generate_data():
    data = []
    base_date = datetime.now() - timedelta(days=30)

    for day in range(30):
        current_date = base_date + timedelta(days=day)

        # 每天生成不同数量的记录
        records_per_day = random.randint(50, 200)

        for _ in range(records_per_day):
            mobile = generate_mobile()
            imei = f"{random.randint(100000000000000, 999999999999999)}"
            imsi = f"460{random.randint(10000000000, 99999999999)}"

            # 随机选择数据类型
            data_type = random.choices(
                ['install_app', 'tunnel_tool', 'protocol', 'decrypt'],
                weights=[25, 25, 25, 25]  # 增加 decrypt 权重
            )[0]

            app_package = random.choice(APP_PACKAGES) if data_type == 'install_app' else None
            app_name = APP_NAMES[APP_PACKAGES.index(app_package)] if app_package else None

            proto = random.choice(PROTOCOLS) if data_type in ['tunnel_tool', 'protocol', 'decrypt'] else None
            # 解密维度数据：tunnel_proto_type IS NOT NULL AND content_s IS NOT NULL
            content = random.choice(DECRYPT_CONTENTS) if data_type == 'decrypt' else None
            domain = random.choice(DOMAINS) if random.random() > 0.3 else None
            server_ip = random.choice(SERVER_IPS) if proto else None
            # URL 主要用于访问内容
            url = f"{random.choice(URLS)}" if data_type == 'decrypt' and random.random() > 0.3 else None
            user_agent = random.choice(USER_AGENTS) if random.random() > 0.3 else None

            row = (
                current_date,  # handle_datetime
                imei,          # imei
                imsi,          # imsi
                mobile,        # mobile
                app_package,   # app_package_name
                app_name,      # app_name
                proto,         # tunnel_proto_type
                content,       # content_s
                domain,        # domain
                server_ip,     # tunnel_server_ip
                url,           # url
                user_agent,    # user_agent
                random.choice(['Android', 'iOS', 'Windows', 'MacOS']),  # terminal_type
                '192.168.1.100',  # src_ip
                random.choice(DOMAINS),  # dst_ip (using domain name)
                int(current_date.strftime('%Y%m%d')),  # handle_date
            )
            data.append(row)

    return data

def create_test_table(conn):
    with conn.cursor() as cur:
        # 删除旧表
        cur.execute("DROP TABLE IF EXISTS nb_mass_resource_all_stream CASCADE;")

        # 创建简化版测试表
        cur.execute("""
            CREATE TABLE nb_mass_resource_all_stream (
                id BIGSERIAL PRIMARY KEY,
                handle_datetime TIMESTAMP,
                imei VARCHAR(50),
                imsi VARCHAR(50),
                mobile VARCHAR(50),
                app_package_name VARCHAR(255),
                app_name VARCHAR(255),
                tunnel_proto_type VARCHAR(50),
                content_s TEXT,
                domain VARCHAR(500),
                tunnel_server_ip VARCHAR(50),
                url TEXT,
                user_agent VARCHAR(500),
                terminal_type VARCHAR(100),
                src_ip VARCHAR(50),
                dst_ip VARCHAR(500),
                handle_date INTEGER
            )
        """)

        # 创建索引
        cur.execute("""
            CREATE INDEX idx_mobile ON nb_mass_resource_all_stream(mobile);
            CREATE INDEX idx_app_package ON nb_mass_resource_all_stream(app_package_name);
            CREATE INDEX idx_tunnel_proto ON nb_mass_resource_all_stream(tunnel_proto_type);
            CREATE INDEX idx_handle_date ON nb_mass_resource_all_stream(handle_date);
        """)

        conn.commit()
        print("测试表创建成功!")

def insert_test_data(conn, data):
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO nb_mass_resource_all_stream (
                handle_datetime, imei, imsi, mobile, app_package_name, app_name,
                tunnel_proto_type, content_s, domain, tunnel_server_ip, url, user_agent,
                terminal_type, src_ip, dst_ip, handle_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, data)
        conn.commit()
        print(f"插入 {len(data)} 条测试数据成功!")

def test_queries(conn):
    with conn.cursor() as cur:
        print("\n=== 测试查询 ===\n")

        # 测试汇总统计
        cur.execute("""
            SELECT
                COUNT(DISTINCT mobile) as total_users,
                COUNT(DISTINCT app_package_name) as total_apps,
                COUNT(DISTINCT tunnel_server_ip) as total_servers,
                COUNT(*) as total_records
            FROM nb_mass_resource_all_stream
            WHERE handle_datetime >= CURRENT_DATE - INTERVAL '7 days'
        """)
        result = cur.fetchone()
        print(f"近 7 天统计：用户={result[0]}, 应用={result[1]}, 服务器={result[2]}, 记录={result[3]}")

        # 测试安装应用统计
        cur.execute("""
            SELECT
                DATE(handle_datetime) as stat_date,
                COUNT(DISTINCT mobile) as daily_users
            FROM nb_mass_resource_all_stream
            WHERE app_package_name IS NOT NULL AND app_package_name <> ''
            GROUP BY DATE(handle_datetime)
            ORDER BY stat_date DESC
            LIMIT 7
        """)
        print("\n近 7 天安装应用用户数:")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]} 用户")

if __name__ == "__main__":
    print("正在连接数据库...")
    conn = psycopg2.connect(**DB_CONFIG)

    print("创建测试表...")
    create_test_table(conn)

    print("生成测试数据...")
    data = generate_data()

    print("插入测试数据...")
    insert_test_data(conn, data)

    print("测试查询...")
    test_queries(conn)

    conn.close()
    print("\n完成!")
