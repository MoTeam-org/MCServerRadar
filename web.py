from flask import Flask, render_template, jsonify, request
import json
import geoip2.database
from collections import defaultdict
from datetime import datetime
import os
from mc_scanner import MinecraftServerScanner

app = Flask(__name__)

# GeoIP数据库路径
GEOIP_DB = "GeoLite2-Country.mmdb"

def load_scan_results():
    """加载扫描结果"""
    try:
        with open("scan_results.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_country_info(ip):
    """获取IP的国家信息"""
    try:
        with geoip2.database.Reader(GEOIP_DB) as reader:
            response = reader.country(ip)
            return {
                "code": response.country.iso_code,
                "name": response.country.name,
                "name_zh": response.country.names.get("zh-CN", response.country.name)
            }
    except:
        return {
            "code": "UN",
            "name": "Unknown",
            "name_zh": "未知"
        }

def process_results():
    """处理扫描结果，按国家分组"""
    results = load_scan_results()
    servers_by_country = defaultdict(list)
    
    for server in results:
        country_info = get_country_info(server["host"])
        server["country"] = country_info
        servers_by_country[country_info["code"]].append(server)
    
    # 统计信息
    stats = {
        "total_servers": len(results),
        "total_countries": len(servers_by_country),
        "total_players": sum(s["players_online"] for s in results),
        "max_players": sum(s["players_max"] for s in results),
        "countries": {
            code: {
                "name": servers[0]["country"]["name"],
                "name_zh": servers[0]["country"]["name_zh"],
                "count": len(servers),
                "players": sum(s["players_online"] for s in servers),
                "max_players": sum(s["players_max"] for s in servers)
            }
            for code, servers in servers_by_country.items()
        }
    }
    
    return servers_by_country, stats

@app.route('/')
def index():
    """主页"""
    # 从查询参数获取 CDN 选择，默认不使用 JSDelivr
    use_jsdelivr = request.args.get('use_jsdelivr', '').lower() == 'true'
    servers_by_country, stats = process_results()
    return render_template('index.html', 
                         servers_by_country=servers_by_country,
                         stats=stats,
                         now=datetime.now,
                         use_jsdelivr=use_jsdelivr)

@app.route('/api/servers')
def get_servers():
    """API端点：获取所有服务器信息"""
    servers_by_country, stats = process_results()
    return jsonify({
        "stats": stats,
        "servers": servers_by_country
    })

if __name__ == '__main__':
    # 确保模板目录存在
    os.makedirs('templates', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True) 