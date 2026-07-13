#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import base64
import requests
from pathlib import Path

def parse_proxy_line(line: str):
    """从一行文本中提取代理 URL (协议://主机:端口)"""
    line = line.strip()
    if not line:
        return None
    url = line.split()[0]
    match = re.match(r'^(socks5|http|https)://([^:]+):(\d+)$', url)
    if match:
        protocol, host, port = match.groups()
        return protocol, host, int(port)
    return None

def main():
    source_url = "https://gh-proxy.org/https://raw.githubusercontent.com/watchttvv/free-proxy-list/refs/heads/main/proxy.txt"
    # 输出文件：未编码的原始列表（便于查看）和 Base64 编码后的订阅文件
    output_raw = Path("proxy_list.txt")      # 明文列表
    output_base64 = Path("proxy_sub.txt")    # Base64 编码（用于 v2rayN）

    try:
        print(f"正在从 {source_url} 获取代理列表...")
        response = requests.get(source_url, timeout=30)
        response.raise_for_status()
        content = response.text
    except Exception as e:
        print(f"❌ 获取远程文件失败：{e}")
        return

    lines = []
    for raw_line in content.splitlines():
        parsed = parse_proxy_line(raw_line)
        if parsed is None:
            continue
        protocol, host, port = parsed

        # 生成 URI（v2rayN 支持 socks5:// 和 http://）
        # 对于 https:// 协议，统一转为 http://（因为 v2rayN 对 https 代理支持有限）
        if protocol == "socks5":
            uri = f"socks5://{host}:{port}"
        else:   # http 或 https
            uri = f"http://{host}:{port}"
        lines.append(uri)

    # 明文列表
    plain_text = "\n".join(lines)
    output_raw.write_text(plain_text, encoding="utf-8")
    print(f"✅ 明文列表已保存至 {output_raw}，共 {len(lines)} 个节点")

    # Base64 编码（v2rayN 订阅需要）
    base64_bytes = base64.b64encode(plain_text.encode("utf-8"))
    base64_text = base64_bytes.decode("ascii")
    output_base64.write_text(base64_text, encoding="utf-8")
    print(f"✅ Base64 订阅文件已保存至 {output_base64}")

if __name__ == "__main__":
    main()
