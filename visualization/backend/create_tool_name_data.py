#!/usr/bin/env python3
"""
生成 1000 条包含 tool_name（各种 VPN 应用）的测试数据
"""
import psycopg2
import random
from datetime import datetime, timedelta

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "visualization",
    "user": "visualization",
    "password": "viz2026"
}

TOOL_NAMES = [
    'Shadowsocks', 'ShadowsocksR', 'v2rayNG', 'Clash', 'Clash for Android',
    'Trojan', 'Surfboard', 'Quantumult X', 'Loon', 'Surge',
    'Potatso', 'Lantern', 'Psiphon', 'FreeGate', 'Tor Browser',
    'Windscribe', 'ExpressVPN', 'NordVPN', 'ProtonVPN', 'OpenVPN',
]

PROTOCOLS = ['Shadowsocks', 'ShadowsocksR', 'vmess', 'vless', 'trojan', 'socks5']
DOMAINS = ['google.com', 'youtube.com', 'twitter.com', 'facebook.com',
           'instagram.com', 'telegram.org', 'whatsapp.com', 'netflix.com',
           'github.com', 'reddit.com']
SERVER_IPS = ['103.150.128.1', '103.150.128.2', '45.32.100.1', '45.32.100.2',
              '192.168.100.1', '192.168.100.2', '172.16.50.1', '172.16.50.2']
TERMINAL_TYPES = ['Android', 'iOS', 'Windows', 'MacOS']


def generate_mobile():
    return f"1{random.randint(1000000000, 9999999999)}"


def generate_data(count=1000):
    data = []
    base_date = datetime.now() - timedelta(days=30)

    for _ in range(count):
        days_offset = random.randint(0, 29)
        h, m, s = random.randint(0, 23), random.randint(0, 59), random.randint(0, 59)
        handle_dt = base_date + timedelta(days=days_offset, hours=h, minutes=m, seconds=s)
        capture_ts = int(handle_dt.timestamp() * 1000)

        tool_name = random.choice(TOOL_NAMES)
        proto = random.choice(PROTOCOLS)
        domain = random.choice(DOMAINS)
        server_ip = random.choice(SERVER_IPS)
        mobile = generate_mobile()
        imei = f"{random.randint(100000000000000, 999999999999999)}"
        imsi = f"460{random.randint(10000000000, 99999999999)}"
        auth_account = mobile if random.random() > 0.2 else None

        row = (
            handle_dt,    # handle_datetime
            imei,         # imei
            imsi,         # imsi
            mobile,       # mobile
            None,         # app_package_name
            None,         # app_name
            proto,        # tunnel_proto_type
            None,         # content_s
            domain,       # domain
            server_ip,    # tunnel_server_ip
            f"https://{domain}/api/v{random.randint(1,3)}/data",  # url
            f"Mozilla/5.0 (Linux; Android 14) Chrome/120.0",     # user_agent
            random.choice(TERMINAL_TYPES),  # terminal_type
            '192.168.1.100',  # src_ip
            random.choice(['8.8.8.8', '1.1.1.1']),  # dst_ip
            int(handle_dt.strftime('%Y%m%d')),  # handle_date
            auth_account,  # auth_account
            tool_name,     # tool_name
            handle_dt,     # capture_time (timestamp type)
        )
        data.append(row)
    return data


if __name__ == "__main__":
    print("正在连接数据库...")
    conn = psycopg2.connect(**DB_CONFIG)

    print("生成 1000 条 tool_name 数据...")
    data = generate_data(1000)

    print("插入数据...")
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO nb_mass_resource_all_stream (
                handle_datetime, imei, imsi, mobile, app_package_name, app_name,
                tunnel_proto_type, content_s, domain, tunnel_server_ip, url, user_agent,
                terminal_type, src_ip, dst_ip, handle_date, auth_account, tool_name,
                capture_time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, data)
        conn.commit()
        print(f"插入 {len(data)} 条数据成功!")

    with conn.cursor() as cur:
        cur.execute("""
            SELECT tool_name, COUNT(*) as cnt
            FROM nb_mass_resource_all_stream
            WHERE tool_name IS NOT NULL AND tool_name <> ''
            GROUP BY tool_name ORDER BY cnt DESC
        """)
        print("\ntool_name 分布:")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]} 条")

        cur.execute("SELECT COUNT(*) FROM nb_mass_resource_all_stream")
        print(f"\n表总记录数: {cur.fetchone()[0]}")

    conn.close()
    print("\n完成!")
