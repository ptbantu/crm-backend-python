#!/usr/bin/env python3
"""
后端 API 访问测试脚本
测试 HTTPS 和 HTTP 访问后端接口
"""

import requests
import json
import sys
from urllib.parse import urljoin

# 禁用 SSL 警告（用于自签名证书）
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL_HTTPS = "https://www.bantu.sbs"
BASE_URL_HTTP = "http://www.bantu.sbs"

def test_endpoint(method, path, description, data=None, headers=None, use_https=True):
    """测试单个接口"""
    base_url = BASE_URL_HTTPS if use_https else BASE_URL_HTTP
    url = urljoin(base_url, path)
    
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"URL: {url}")
    print(f"方法: {method}")
    print(f"{'='*60}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, verify=False, headers=headers, timeout=10, allow_redirects=True)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, verify=False, headers=headers, timeout=10, allow_redirects=True)
        else:
            print(f"❌ 不支持的方法: {method}")
            return
        
        print(f"✅ HTTP Status: {response.status_code}")
        print(f"✅ 响应头 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        # 尝试解析 JSON 响应
        try:
            response_json = response.json()
            print(f"✅ 响应内容 (JSON):")
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except:
            print(f"✅ 响应内容 (文本):")
            print(response.text[:500])  # 只显示前 500 个字符
        
        return response.status_code == 200 or response.status_code == 401
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接错误: {e}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 错误: {type(e).__name__}: {e}")
        return False

def main():
    print("="*60)
    print("后端 API 访问测试")
    print("="*60)
    
    results = []
    
    # 测试 1: 健康检查 (HTTPS)
    results.append((
        "健康检查 (HTTPS)",
        test_endpoint("GET", "/health", "健康检查接口", use_https=True)
    ))
    
    # 测试 2: 健康检查 (HTTP - 应该重定向到 HTTPS)
    results.append((
        "健康检查 (HTTP)",
        test_endpoint("GET", "/health", "健康检查接口 (HTTP)", use_https=False)
    ))
    
    # 测试 3: 登录接口 (HTTPS)
    login_data = {
        "email": "admin@bantu.sbs",
        "password": "password123"
    }
    results.append((
        "登录接口 (HTTPS)",
        test_endpoint("POST", "/api/foundation/auth/login", "登录接口", 
                     data=login_data, use_https=True)
    ))
    
    # 测试 4: 登录接口 (HTTP - 应该重定向到 HTTPS)
    results.append((
        "登录接口 (HTTP)",
        test_endpoint("POST", "/api/foundation/auth/login", "登录接口 (HTTP)", 
                     data=login_data, use_https=False)
    ))
    
    # 测试 5: 组织列表 (无认证，应该返回 401)
    results.append((
        "组织列表 (无认证)",
        test_endpoint("GET", "/api/foundation/organizations?page=1&size=10", 
                     "组织列表接口 (无认证)", use_https=True)
    ))
    
    # 测试 6: 角色列表 (无认证，应该返回 401)
    results.append((
        "角色列表 (无认证)",
        test_endpoint("GET", "/api/foundation/roles", 
                     "角色列表接口 (无认证)", use_https=True)
    ))
    
    # 测试 7: Foundation Service 健康检查
    results.append((
        "Foundation Service 健康检查",
        test_endpoint("GET", "/api/foundation/health", 
                     "Foundation Service 健康检查", use_https=True)
    ))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    success_count = 0
    for name, result in results:
        status = "✅ 成功" if result else "❌ 失败"
        print(f"{status}: {name}")
        if result:
            success_count += 1
    
    print(f"\n总计: {success_count}/{len(results)} 个测试通过")
    
    if success_count == len(results):
        print("\n🎉 所有测试通过！后端可以正常访问。")
    elif success_count > 0:
        print("\n⚠️  部分测试通过。请检查失败的测试。")
        print("   注意: 返回 401 是正常的（需要认证）")
    else:
        print("\n❌ 所有测试失败。请检查后端服务状态。")
    
    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main())

