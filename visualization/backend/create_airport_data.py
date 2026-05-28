#!/usr/bin/env python3
"""
生成机场网站测试数据
构造 tool_name='机场网站', app_type='100348246', capture_time, host, url 等数据
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

# 机场网站域名
AIRPORT_DOMAINS = [
    'sspanel.io',
    'v2rayse.com',
    'subshare.dev',
    'cloudairport.net',
    'rapidcloud.org',
    'flycat.club',
    'nexitally.com',
    'justmysocks.net',
    'dlercloud.com',
    'wgetcloud.com',
    'airport.example.com',
    'proxyhub.io',
    'fastlink.org',
    'shadowsocks.org',
    'getlantern.org'
]

# 机场网站 URL 路径
AIRPORT_URLS = [
    '/link/xxxx',
    '/subscribe/xxxx',
    '/api/v1/client/subscribe',
    '/sub/xxxx',
    '/dashboard',
    '/panel',
    '/auth/login',
    '/user',
    '/index.php?sub=xxxx',
    '/download',
    '/client/subscribe',
    '/s/xxxx'
]

# 翻墙工具/应用
VPN_APPS = [
    ('com.github.shadowsocks', 'Shadowsocks'),
    ('com.v2ray.ang', 'v2rayNG'),
    ('com.clash.android', 'Clash'),
    ('org.torproject.android', 'Tor Browser'),
    ('com.nicegram', 'Nicegram'),
]

PROTOCOLS = ['Shadowsocks', 'ShadowsocksR', 'vmess', 'vless', 'trojan', 'socks5']

SERVER_IPS = [
    '103.150.128.1', '103.150.128.2', '45.32.100.1', '45.32.100.2',
    '192.168.100.1', '192.168.100.2', '172.16.50.1', '172.16.50.2'
]

def generate_mobile():
    return f"1{random.randint(1000000000, 9999999999)}"

def generate_airport_data(num_records=500):
    """生成机场网站相关数据"""
    data = []
    base_date = datetime.now() - timedelta(days=60)

    for i in range(num_records):
        mobile = generate_mobile()
        imei = f"{random.randint(100000000000000, 999999999999999)}"
        imsi = f"460{random.randint(10000000000, 99999999999)}"

        # 随机时间（60 天内）
        days_offset = random.randint(0, 60)
        hours_offset = random.randint(0, 23)
        minutes_offset = random.randint(0, 59)
        record_time = base_date + timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)

        # 选择机场域名和 URL
        domain = random.choice(AIRPORT_DOMAINS)
        url_path = random.choice(AIRPORT_URLS)
        full_url = f"https://{domain}{url_path}"

        # 随机选择应用和协议
        app_pkg, app_name = random.choice(VPN_APPS)
        proto = random.choice(PROTOCOLS)
        server_ip = random.choice(SERVER_IPS)

        # capture_time（采集时间）
        capture_time = record_time + timedelta(seconds=random.randint(1, 3600))

        row = (
            record_time,       # handle_datetime
            imei,              # imei
            imsi,              # imsi
            mobile,            # mobile
            app_pkg,           # app_package_name
            app_name,          # app_name
            proto,             # tunnel_proto_type
            full_url,          # content_s (解密内容)
            domain,            # domain
            server_ip,         # tunnel_server_ip
            url_path,          # url
            None,              # user_agent
            random.choice(['Android', 'iOS']),  # terminal_type
            '192.168.1.100',   # src_ip
            domain,            # dst_ip
            int(record_time.strftime('%Y%m%d')),  # handle_date
            '机场网站',         # tool_name
            '100348246',       # app_type
            int(capture_time.strftime('%Y%m%d')),  # capture_time (as bigint)
        )
        data.append(row)

    return data

def add_airport_columns(conn):
    """添加机场网站相关字段到表"""
    with conn.cursor() as cur:
        # 检查并添加 tool_name 字段
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'nb_mass_resource_all_stream' AND column_name = 'tool_name'
                ) THEN
                    ALTER TABLE nb_mass_resource_all_stream ADD COLUMN tool_name VARCHAR(255);
                END IF;
            END $$;
        """)

        # 检查并添加 app_type 字段
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'nb_mass_resource_all_stream' AND column_name = 'app_type'
                ) THEN
                    ALTER TABLE nb_mass_resource_all_stream ADD COLUMN app_type VARCHAR(50);
                END IF;
            END $$;
        """)

        # 检查并添加 capture_time 字段
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'nb_mass_resource_all_stream' AND column_name = 'capture_time'
                ) THEN
                    ALTER TABLE nb_mass_resource_all_stream ADD COLUMN capture_time TIMESTAMP;
                END IF;
            END $$;
        """)

        conn.commit()
        print("表结构更新成功!")

def insert_airport_data(conn, data):
    """插入机场网站数据"""
    with conn.cursor() as cur:
        for row in data:
            cur.execute("""
                INSERT INTO nb_mass_resource_all_stream (
                    handle_datetime, imei, imsi, mobile, app_package_name, app_name,
                    tunnel_proto_type, content_s, domain, tunnel_server_ip, url, user_agent,
                    terminal_type, src_ip, dst_ip, handle_date, tool_name, app_type, capture_time
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, row)
        conn.commit()
        print(f"插入 {len(data)} 条机场网站数据成功!")

def verify_data(conn):
    """验证插入的数据"""
    with conn.cursor() as cur:
        print("\n=== 数据验证 ===\n")

        # 统计机场网站数据
        cur.execute("""
            SELECT COUNT(*) FROM nb_mass_resource_all_stream
            WHERE tool_name = '机场网站' OR app_type = '100348246'
        """)
        total = cur.fetchone()[0]
        print(f"机场网站数据总数：{total}")

        # 按域名统计
        cur.execute("""
            SELECT domain, COUNT(DISTINCT mobile) as user_count
            FROM nb_mass_resource_all_stream
            WHERE tool_name = '机场网站' OR app_type = '100348246'
            GROUP BY domain
            ORDER BY user_count DESC
            LIMIT 10
        """)
        print("\n机场网站域名 Top10:")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]} 用户")

        # 按时间范围统计
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE handle_datetime >= CURRENT_DATE - INTERVAL '7 days') as last_7_days,
                COUNT(*) FILTER (WHERE handle_datetime >= CURRENT_DATE - INTERVAL '30 days') as last_30_days,
                COUNT(*) as all_time
            FROM nb_mass_resource_all_stream
            WHERE tool_name = '机场网站' OR app_type = '100348246'
        """)
        row = cur.fetchone()
        print(f"\n时间分布：近 7 天={row[0]}, 近 30 天={row[1]}, 全部={row[2]}")

if __name__ == "__main__":
    print("正在连接数据库...")
    conn = psycopg2.connect(**DB_CONFIG)

    print("更新表结构...")
    add_airport_columns(conn)

    print("生成机场网站数据...")
    data = generate_airport_data(500)

    print("插入数据...")
    insert_airport_data(conn, data)

    print("验证数据...")
    verify_data(conn)

    conn.close()
    print("\n完成!")
