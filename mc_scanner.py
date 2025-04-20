import asyncio
import json
from datetime import datetime
from mcstatus import JavaServer
import aiohttp
from typing import Dict, Optional, List, Generator, Set, Tuple
import ipaddress
import socket
import random
import time
import geoip2.database
import os
from pathlib import Path

class MinecraftServerScanner:
    def __init__(self):
        self.results = []
        self.default_port_range = (25565, 25565)
        self.default_timeout = 2  # 超时时间（秒）
        self.scan_count = 0
        self.start_time = None
        self.last_save_time = time.time()
        self.last_status = ""
        self.semaphore = asyncio.Semaphore(1000)  # 限制并发连接数
        
        # IP数据库路径
        self.db_path = "GeoLite2-Country.mmdb"
        
        # 国家代码映射
        self.country_codes = {
            "china": "CN",
            "usa": "US",
            "japan": "JP",
            "korea": "KR",
            "russia": "RU",
            "germany": "DE",
            "france": "FR",
            "uk": "GB",
        }

        # 排除的私有IP范围
        self.excluded_networks = [
            ipaddress.ip_network("10.0.0.0/8"),
            ipaddress.ip_network("172.16.0.0/12"),
            ipaddress.ip_network("192.168.0.0/16"),
            ipaddress.ip_network("127.0.0.0/8"),
            ipaddress.ip_network("169.254.0.0/16"),  # 链路本地地址
            ipaddress.ip_network("224.0.0.0/4"),     # 多播地址
            ipaddress.ip_network("240.0.0.0/4"),     # 保留地址
        ]

    def download_geoip_db(self):
        """下载GeoIP数据库（这里需要你自己获取数据库文件）"""
        if not os.path.exists(self.db_path):
            self.update_status("请下载 GeoLite2-Country.mmdb 数据库文件")
            self.update_status("你可以从 https://dev.maxmind.com/geoip/geolite2-free-geolocation-data 获取")
            raise FileNotFoundError("缺少GeoIP数据库文件")

    def is_ip_in_country(self, ip: str, country_code: str) -> bool:
        """检查IP是否属于指定国家"""
        try:
            with geoip2.database.Reader(self.db_path) as reader:
                response = reader.country(ip)
                return response.country.iso_code == country_code.upper()
        except:
            return False

    def get_country_ip_count(self, country_code: str) -> Tuple[int, List[str]]:
        """获取指定国家的IP数量和IP范围"""
        ip_ranges = []
        total_ips = 0
        
        try:
            with geoip2.database.Reader(self.db_path) as reader:
                # 遍历所有可能的IP（按照/8网段）
                for first_octet in range(1, 256):
                    try:
                        # 检查每个/8网段的第一个IP
                        ip = f"{first_octet}.0.0.0"
                        response = reader.country(ip)
                        if response.country.iso_code == country_code:
                            network = f"{first_octet}.0.0.0/8"
                            # 排除私有IP范围
                            if not any(ipaddress.ip_network(network).overlaps(excluded) for excluded in self.excluded_networks):
                                ip_ranges.append(network)
                                total_ips += 2**24  # 一个/8网段包含2^24个IP
                    except:
                        continue
        except Exception as e:
            print(f"获取国家IP信息时出错: {str(e)}")
            return 0, []
            
        return total_ips, ip_ranges

    async def scan_country(self, country: str, port: int = 25565, batch_size: int = 1000):
        """扫描指定国家的服务器"""
        self.start_time = time.time()
        self.scan_count = 0
        
        # 确保GeoIP数据库存在
        self.download_geoip_db()
        
        country_code = self.country_codes.get(country.lower())
        if not country_code:
            raise ValueError(f"不支持的国家: {country}. 支持的国家: {', '.join(self.country_codes.keys())}")
        
        # 获取国家的IP数量和范围
        total_ips, ip_ranges = self.get_country_ip_count(country_code)
        
        if total_ips == 0:
            raise ValueError(f"无法获取{country}的IP信息")
        
        print(f"开始扫描{country}的Minecraft服务器")
        print(f"IP范围数量: {len(ip_ranges)}")
        print(f"总IP数量: {total_ips:,}")
        print(f"使用端口: {port}")
        print(f"批处理大小: {batch_size}")
        print(f"并发连接数: {self.semaphore._value}")
        print(f"超时设置: {self.default_timeout}秒")
        print("按 Ctrl+C 可以随时中断扫描，已扫描的结果会被保存\n")
        
        try:
            for ip_range in ip_ranges:
                network = ipaddress.ip_network(ip_range)
                tasks = []
                
                for ip in network.hosts():
                    ip_str = str(ip)
                    tasks.append(self.scan_server(ip_str, port))
                    
                    if len(tasks) >= batch_size:
                        await asyncio.gather(*tasks)
                        current_time = time.time()
                        if current_time - self.last_save_time >= 300:  # 每5分钟保存一次
                            self.save_results()
                            self.last_save_time = current_time
                        tasks = []
                    
                    self.print_progress(total_ips)
                
                # 处理剩余的任务
                if tasks:
                    await asyncio.gather(*tasks)
                    
        except KeyboardInterrupt:
            print("\n\n扫描被用户中断")
        finally:
            end_time = time.time()
            duration = end_time - self.start_time
            print(f"\n\n扫描完成!")
            print(f"总扫描IP数: {self.scan_count:,}")
            print(f"发现服务器数: {len(self.results):,}")
            print(f"总耗时: {duration/3600:.2f} 小时")
            print(f"平均速度: {self.scan_count/duration:.2f} IP/秒")
            print(f"服务器密度: {len(self.results)/self.scan_count*100:.4f}%")
            
            # 最后保存一次结果
            self.save_results()

    def update_status(self, message: str):
        """更新状态信息"""
        # 移除消息中的换行符并限制长度
        self.last_status = message.replace('\n', ' ').replace('\r', '').strip()
        if len(self.last_status) > 100:  # 限制状态消息长度
            self.last_status = self.last_status[:97] + "..."
        self.print_progress()

    def generate_all_ips(self) -> Generator[str, None, None]:
        """生成所有IPv4地址的生成器"""
        current = 0
        while current < 2**32:
            ip = ipaddress.IPv4Address(current)
            if not any(ip in network for network in self.excluded_networks):
                yield str(ip)
            current += 1

    def print_progress(self, total_ips: int = None):
        """打印扫描进度"""
        if not self.start_time:
            return
        
        elapsed_time = time.time() - self.start_time
        speed = self.scan_count / elapsed_time if elapsed_time > 0 else 0
        
        # 构建进度信息
        progress_parts = [
            f"已扫描: {self.scan_count:,} IP",
            f"速度: {speed:.2f} IP/秒",
            f"发现服务器: {len(self.results)}"
        ]
        
        if total_ips:
            percentage = (self.scan_count / total_ips) * 100
            remaining_time = (total_ips - self.scan_count) / speed if speed > 0 else 0
            progress_parts.insert(1, f"{percentage:.2f}%")
            progress_parts.insert(2, f"预计剩余: {remaining_time/3600:.1f}h")
        
        if self.last_status:
            progress_parts.append(f"状态: {self.last_status}")
        
        # 使用固定的分隔符连接所有部分
        progress_info = " | ".join(progress_parts)
        
        # 确保输出不会换行，使用\r回到行首
        print(f"\r{' ' * 150}\r{progress_info}", end="", flush=True)
        
    def is_public_ip(self, ip: str) -> bool:
        """检查是否是公网IP"""
        ip_obj = ipaddress.ip_address(ip)
        return not any(ip_obj in network for network in self.excluded_networks)

    async def scan_server(self, host: str, port: int = 25565) -> Optional[Dict]:
        """扫描单个Minecraft服务器并获取信息"""
        async with self.semaphore:  # 使用信号量控制并发
            try:
                server = JavaServer(host, port)
                status = await asyncio.wait_for(server.async_status(), timeout=self.default_timeout)
                
                server_info = {
                    "host": host,
                    "port": port,
                    "online": True,
                    "version": status.version.name,
                    "protocol": status.version.protocol,
                    "players_online": status.players.online,
                    "players_max": status.players.max,
                    "latency": status.latency,
                    "description": status.description,
                    "timestamp": datetime.now().isoformat()
                }
                
                if hasattr(status.players, 'sample') and status.players.sample:
                    server_info["player_list"] = [
                        player.name for player in status.players.sample
                    ]
                
                self.update_status(f"✅ {host}:{port}")
                self.results.append(server_info)
                return server_info
                
            except asyncio.TimeoutError:
                self.update_status(f"⚠️ {host}:{port} 超时")
                return None
            except Exception as e:
                error_msg = str(e)
                if len(error_msg) > 50:
                    error_msg = error_msg[:47] + "..."
                self.update_status(f"❌ {host}:{port} - {error_msg}")
                return None
            finally:
                self.scan_count += 1

    async def scan_all_ipv4(self, port: int = 25565, batch_size: int = 1000, save_interval: int = 300):
        """扫描所有IPv4地址"""
        self.start_time = time.time()
        self.scan_count = 0
        total_ips = 2**32 - sum(network.num_addresses for network in self.excluded_networks)
        
        print(f"开始扫描所有IPv4地址（排除私有地址范围）")
        print(f"预计总共需要扫描 {total_ips:,} 个IP地址")
        print(f"使用端口: {port}")
        print(f"批处理大小: {batch_size}")
        print("按 Ctrl+C 可以随时中断扫描，已扫描的结果会被保存\n")
        
        ip_generator = self.generate_all_ips()
        current_batch = []
        
        try:
            for ip in ip_generator:
                current_batch.append(self.scan_server(ip, port))
                
                if len(current_batch) >= batch_size:
                    await asyncio.gather(*current_batch)
                    
                    # 每隔一定时间保存一次结果
                    current_time = time.time()
                    if current_time - self.last_save_time >= save_interval:
                        self.save_results()
                        self.last_save_time = current_time
                    
                    current_batch = []
            
            # 处理最后一批
            if current_batch:
                await asyncio.gather(*current_batch)
                
        except KeyboardInterrupt:
            print("\n\n扫描被用户中断")
        finally:
            end_time = time.time()
            duration = end_time - self.start_time
            print(f"\n\n扫描完成!")
            print(f"总扫描IP数: {self.scan_count:,}")
            print(f"发现服务器数: {len(self.results):,}")
            print(f"总耗时: {duration/3600:.2f} 小时")
            print(f"平均速度: {self.scan_count/duration:.2f} IP/秒")

    async def scan_random_global_ips(self, count: int = 1000, port: int = 25565) -> List[Dict]:
        """随机扫描全球公网IP"""
        self.start_time = time.time()
        self.scan_count = 0
        tasks = []
        scanned_ips = set()
        
        print(f"开始随机扫描 {count} 个全球IP地址，端口: {port}")
        
        while len(tasks) < count:
            while True:
                ip = str(ipaddress.IPv4Address(random.randint(1, 2**32 - 1)))
                if ip not in scanned_ips and self.is_public_ip(ip):
                    scanned_ips.add(ip)
                    break
            
            tasks.append(self.scan_server(ip, port))
            if len(tasks) % 100 == 0:
                self.print_progress(count)
        
        await asyncio.gather(*tasks)
        return self.results

    async def scan_ip_range(self, start_ip: str, end_ip: str, port_range: tuple = None) -> List[Dict]:
        """扫描IP范围内的所有服务器"""
        if port_range is None:
            port_range = self.default_port_range

        start = int(ipaddress.IPv4Address(start_ip))
        end = int(ipaddress.IPv4Address(end_ip))
        
        all_tasks = []
        for ip in range(start, end + 1):
            ip_addr = str(ipaddress.IPv4Address(ip))
            if self.is_public_ip(ip_addr):
                for port in range(port_range[0], port_range[1] + 1):
                    all_tasks.append(self.scan_server(ip_addr, port))
                    
        print(f"开始扫描IP范围 {start_ip} 到 {end_ip}，端口范围 {port_range[0]} 到 {port_range[1]}")
        results = await asyncio.gather(*all_tasks)
        valid_results = [r for r in results if r]
        self.results.extend(valid_results)
        return valid_results

    async def scan_multiple_servers(self, servers: list):
        """并发扫描多个指定服务器"""
        tasks = []
        for server in servers:
            if isinstance(server, str):
                host = server
                port = 25565
            else:
                host, port = server
            
            tasks.append(self.scan_server(host, port))
        
        await asyncio.gather(*tasks)
        return self.results

    async def scan_single_host_all_ports(self, host: str, start_port: int = 1, end_port: int = 65535) -> List[Dict]:
        """扫描单个主机的所有端口"""
        print(f"开始扫描主机 {host} 的端口范围 {start_port} 到 {end_port}")
        tasks = []
        for port in range(start_port, end_port + 1):
            tasks.append(self.scan_server(host, port))
        
        await asyncio.gather(*tasks)
        return self.results
    
    def save_results(self, filename: str = "scan_results.json"):
        """保存扫描结果到JSON文件"""
        try:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_results = json.load(f)
                    if isinstance(existing_results, list):
                        seen_servers = {(r['host'], r['port']) for r in existing_results}
                        for result in self.results:
                            if (result['host'], result['port']) not in seen_servers:
                                existing_results.append(result)
                                seen_servers.add((result['host'], result['port']))
                        self.results = existing_results
            except (FileNotFoundError, json.JSONDecodeError):
                pass

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=4)
            self.update_status(f"已保存 {len(self.results)} 个服务器到 {filename}")
        except Exception as e:
            self.update_status(f"保存结果出错: {str(e)}")

async def main():
    # 示例服务器列表
    servers_to_scan = [
        "mc.hypixel.net",
        "2b2t.org",
        ("play.pixelmonrealms.com", 25565),
        # 在这里添加更多服务器
    ]
    
    scanner = MinecraftServerScanner()
    await scanner.scan_multiple_servers(servers_to_scan)
    scanner.save_results()

if __name__ == "__main__":
    asyncio.run(main()) 