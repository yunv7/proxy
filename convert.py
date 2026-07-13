#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import yaml
import requests
from pathlib import Path

def parse_proxy_line(line: str):
    """从一行文本中提取代理 URL (协议://主机:端口)"""
    line = line.strip()
    if not line:
        return None
    # 取第一个空格前的部分作为 URL
    url = line.split()[0]
    match = re.match(r'^(socks5|http|https)://([^:]+):(\d+)$', url)
    if match:
        protocol, host, port = match.groups()
        return protocol, host, int(port)
    return None

def main():
    source_url = "https://gh-proxy.org/https://raw.githubusercontent.com/watchttvv/free-proxy-list/refs/heads/main/proxy.txt"
    output_path = Path("proxy.yml")   # 相对路径，在 Actions 中工作目录即为仓库根目录

    try:
        print(f"正在从 {source_url} 获取代理列表...")
        response = requests.get(source_url, timeout=30)
        response.raise_for_status()
        content = response.text
    except Exception as e:
        print(f"❌ 获取远程文件失败：{e}")
        return

    proxies = []
    for raw_line in content.splitlines():
        parsed = parse_proxy_line(raw_line)
        if parsed is None:
            continue
        protocol, host, port = parsed

        proxy = {
            "name": f"{protocol}_{host}_{port}",
            "server": host,
            "port": port,
        }

        if protocol == "socks5":
            proxy["type"] = "socks5"
            proxy["udp"] = True
        elif protocol == "http":
            proxy["type"] = "http"
        elif protocol == "https":
            proxy["type"] = "http"
            proxy["tls"] = True

        proxies.append(proxy)

    config = {"proxies": proxies}

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"✅ 转换完成！共 {len(proxies)} 个代理节点已写入 {output_path}")

if __name__ == "__main__":
    main()
