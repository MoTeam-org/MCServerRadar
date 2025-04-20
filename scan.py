import asyncio
import argparse
from mc_scanner import MinecraftServerScanner
import ipaddress

def validate_ip(ip_str):
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def parse_port_range(port_range):
    try:
        start, end = map(int, port_range.split('-'))
        if 1 <= start <= 65535 and 1 <= end <= 65535 and start <= end:
            return (start, end)
    except:
        pass
    raise argparse.ArgumentTypeError('端口范围格式无效，请使用 "起始端口-结束端口" 格式，例如: "25565-25575"')

async def main():
    parser = argparse.ArgumentParser(description='Minecraft服务器扫描工具')
    parser.add_argument('--mode', choices=['single', 'multiple', 'range', 'all-ports', 'global', 'all-ipv4', 'country'],
                      required=True, help='扫描模式：single=单个服务器，multiple=多个服务器，range=IP范围，all-ports=扫描所有端口，global=扫描全球服务器，all-ipv4=扫描所有IPv4地址，country=扫描特定国家')
    
    parser.add_argument('--host', help='要扫描的服务器主机名或IP')
    parser.add_argument('--hosts-file', help='包含多个服务器地址的文件路径，每行一个地址')
    parser.add_argument('--start-ip', help='起始IP地址')
    parser.add_argument('--end-ip', help='结束IP地址')
    parser.add_argument('--port-range', type=parse_port_range, 
                      help='端口范围，格式: "起始端口-结束端口"，例如: "25565-25575"')
    parser.add_argument('--output', default='scan_results.json',
                      help='结果输出文件路径')
    parser.add_argument('--count', type=int, default=1000,
                      help='全球扫描模式下要扫描的IP数量')
    parser.add_argument('--port', type=int, default=25565,
                      help='指定扫描端口')
    parser.add_argument('--batch-size', type=int, default=1000,
                      help='批处理大小（用于全IPv4扫描模式）')
    parser.add_argument('--save-interval', type=int, default=300,
                      help='保存间隔（全IPv4扫描模式下，每扫描多少秒保存一次结果）')
    parser.add_argument('--country', help='要扫描的国家（例如：china, usa, japan等）')

    args = parser.parse_args()
    scanner = MinecraftServerScanner()

    try:
        if args.mode == 'single':
            if not args.host:
                parser.error('单服务器模式需要指定 --host 参数')
            await scanner.scan_server(args.host)

        elif args.mode == 'multiple':
            if not args.hosts_file:
                parser.error('多服务器模式需要指定 --hosts-file 参数')
            with open(args.hosts_file, 'r') as f:
                servers = [line.strip() for line in f if line.strip()]
            await scanner.scan_multiple_servers(servers)

        elif args.mode == 'range':
            if not (args.start_ip and args.end_ip):
                parser.error('IP范围模式需要指定 --start-ip 和 --end-ip 参数')
            if not (validate_ip(args.start_ip) and validate_ip(args.end_ip)):
                parser.error('请输入有效的IP地址')
            port_range = args.port_range or (25565, 25565)
            await scanner.scan_ip_range(args.start_ip, args.end_ip, port_range)

        elif args.mode == 'all-ports':
            if not args.host:
                parser.error('全端口扫描模式需要指定 --host 参数')
            port_range = args.port_range or (1, 65535)
            await scanner.scan_single_host_all_ports(args.host, port_range[0], port_range[1])

        elif args.mode == 'global':
            print(f"开始全球服务器扫描，将随机扫描 {args.count} 个IP地址")
            await scanner.scan_random_global_ips(args.count, args.port)

        elif args.mode == 'all-ipv4':
            print("警告: 扫描所有IPv4地址将耗费大量时间和资源！")
            confirmation = input("确定要继续吗？(y/N) ")
            if confirmation.lower() == 'y':
                await scanner.scan_all_ipv4(args.port, args.batch_size, args.save_interval)
            else:
                print("操作已取消")
                return

        elif args.mode == 'country':
            if not args.country:
                parser.error('请使用 --country 参数指定要扫描的国家')
            await scanner.scan_country(args.country, args.port, args.batch_size)

        scanner.save_results(args.output)

    except KeyboardInterrupt:
        print("\n扫描被用户中断")
        scanner.save_results(args.output)
    except Exception as e:
        print(f"发生错误: {str(e)}")
        scanner.save_results(args.output)

if __name__ == "__main__":
    asyncio.run(main()) 