-- PostgreSQL 建表语句
-- 将原始 Hive/Spark SQL 转换为 PostgreSQL 语法

CREATE TABLE IF NOT EXISTS nb_mass_resource_all_stream (
    -- 基础字段
    id BIGSERIAL PRIMARY KEY,
    handle_datetime TIMESTAMP,
    upload_area_code INTEGER,
    isp_type INTEGER,
    line_id VARCHAR(255),
    pkt_time TIMESTAMP,
    capture_time BIGINT,
    rele_direction_type VARCHAR(50),
    flow_direction_type VARCHAR(50),
    netbar_number VARCHAR(100),
    data_source INTEGER,
    second_netbar_number VARCHAR(100),
    security_company_code VARCHAR(100),

    -- IP 地址
    src_ip INET,
    dst_ip INET,
    src_ipv6 INET,
    dst_ipv6 INET,
    src_ipid_s VARCHAR(100),
    dst_ipid_s VARCHAR(100),
    src_port INTEGER,
    dst_port INTEGER,
    outer_dst_ip INET,
    outer_src_ip INET,
    vlan_id VARCHAR(50),

    -- 协议类型 (关键字段)
    tunnel_proto_type INTEGER,
    net_proto_type VARCHAR(50),
    trans_proto_type VARCHAR(50),
    app_proto_type VARCHAR(100),
    main_proto_type INTEGER,
    app_type INTEGER,
    action_type INTEGER,
    entity_type INTEGER,

    -- 终端信息
    terminal_type VARCHAR(100),
    terminal_brand VARCHAR(100),
    terminal_model VARCHAR(100),
    tool_type VARCHAR(100),
    teid VARCHAR(100),
    restore_type INTEGER,
    device_id VARCHAR(100),
    tool_name VARCHAR(255),

    -- 位置信息
    rele_lat DECIMAL(10, 6),
    rele_lon DECIMAL(10, 6),
    bs_attribution_area_code VARCHAR(50),
    mobile_attribution_area_code VARCHAR(50),
    bs_id VARCHAR(100),
    bs_type VARCHAR(50),

    -- 用户标识 (关键字段)
    imei VARCHAR(50),
    mac VARCHAR(50),
    imsi VARCHAR(50),
    mobile VARCHAR(50),
    auth_account VARCHAR(255),
    auth_type VARCHAR(50),

    -- 隧道信息
    tunnel_login_username VARCHAR(255),
    tunnel_login_password VARCHAR(255),
    tunnel_server_ip INET,
    tunnel_session_id VARCHAR(255),
    tunnel_server_port INTEGER,
    tunnel_server_ipv6 INET,

    -- 应用信息 (关键字段)
    domain VARCHAR(500),
    url TEXT,
    user_agent TEXT,
    userid VARCHAR(255),
    username VARCHAR(255),
    app_imei VARCHAR(50),
    app_package_name VARCHAR(255),
    app_name VARCHAR(255),
    app_version VARCHAR(50),

    -- 内容信息 (关键字段)
    content_s TEXT,

    -- 时间戳
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    create_time TIMESTAMP,

    -- 流量统计
    up_pkt_quantity BIGINT,
    up_flow BIGINT,
    down_pkt_quantity BIGINT,
    down_flow BIGINT,

    -- 分区字段
    capture_hour INTEGER,
    capture_date INTEGER,
    handle_time BIGINT,
    handle_minute BIGINT,
    handle_hour INTEGER,
    handle_date INTEGER,

    -- 其他常用字段
    conffeature_id BIGINT,
    referer_url TEXT,
    http_request_type VARCHAR(50),
    cookie TEXT,
    request_data TEXT,
    response_data TEXT,

    -- 证书相关
    crt_user_common_name VARCHAR(255),
    ca_org_name VARCHAR(255),

    -- 扩展字段
    extend_field_s TEXT,
    other_field_s TEXT,

    -- 索引优化
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_mobile ON nb_mass_resource_all_stream(mobile) WHERE mobile IS NOT NULL AND mobile != '';
CREATE INDEX idx_imei ON nb_mass_resource_all_stream(imei) WHERE imei IS NOT NULL AND imei != '';
CREATE INDEX idx_imsi ON nb_mass_resource_all_stream(imsi) WHERE imsi IS NOT NULL AND imsi != '';
CREATE INDEX idx_app_package_name ON nb_mass_resource_all_stream(app_package_name) WHERE app_package_name IS NOT NULL AND app_package_name != '';
CREATE INDEX idx_domain ON nb_mass_resource_all_stream(domain) WHERE domain IS NOT NULL AND domain != '';
CREATE INDEX idx_tunnel_proto_type ON nb_mass_resource_all_stream(tunnel_proto_type) WHERE tunnel_proto_type IS NOT NULL;
CREATE INDEX idx_tunnel_server_ip ON nb_mass_resource_all_stream(tunnel_server_ip) WHERE tunnel_server_ip IS NOT NULL;
CREATE INDEX idx_content_s ON nb_mass_resource_all_stream(content_s) WHERE content_s IS NOT NULL;
CREATE INDEX idx_handle_datetime ON nb_mass_resource_all_stream(handle_datetime);
CREATE INDEX idx_handle_date ON nb_mass_resource_all_stream(handle_date);

-- 创建复合索引用于统计查询
CREATE INDEX idx_stats_app ON nb_mass_resource_all_stream(handle_date, app_package_name, mobile)
    WHERE app_package_name IS NOT NULL AND app_package_name != '' AND mobile IS NOT NULL AND mobile != '';

CREATE INDEX idx_stats_tunnel ON nb_mass_resource_all_stream(handle_date, tunnel_proto_type, content_s, mobile)
    WHERE tunnel_proto_type IS NOT NULL AND mobile IS NOT NULL AND mobile != '';

CREATE INDEX idx_stats_proxy ON nb_mass_resource_all_stream(tunnel_server_ip, mobile)
    WHERE tunnel_server_ip IS NOT NULL AND mobile IS NOT NULL AND mobile != '';
