#!/usr/bin/env python3
"""
HTTPS 登录接口测试脚本
"""
import ssl
import socket
import requests
import json
import urllib3

# 禁用 SSL 警告（用于自签名证书）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("=" * 50)
print("HTTPS 登录接口测试")
print("=" * 50)
print()

# 测试 1: 检查证书
print("1. 检查 HTTPS 证书信息:")
print("-" * 50)
try:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    with socket.create_connection(('www.bantu.sbs', 443), timeout=5) as sock:
        with context.wrap_socket(sock, server_hostname='www.bantu.sbs') as ssock:
            cert = ssock.getpeercert()
            subject = dict(x[0] for x in cert.get('subject', []))
            issuer = dict(x[0] for x in cert.get('issuer', []))
            
            print(f"   证书主题 (CN): {subject.get('commonName', 'N/A')}")
            print(f"   证书颁发者: {issuer.get('organizationName', 'N/A')}")
            print(f"   有效期: {cert.get('notBefore', 'N/A')} 到 {cert.get('notAfter', 'N/A')}")
            print("   ✅ HTTPS 连接正常")
except Exception as e:
    print(f"   ⚠️  证书检查失败: {str(e)}")

print()

# 测试 2: 登录接口
print("2. 测试登录接口 (POST /api/foundation/auth/login):")
print("-" * 50)
try:
    response = requests.post(
        'https://www.bantu.sbs/api/foundation/auth/login',
        json={'email': 'admin@bantu.sbs', 'password': 'password123'},
        verify=False,  # 跳过证书验证
        timeout=10,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   HTTP 状态码: {response.status_code}")
    print(f"   响应头 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    
    try:
        response_data = response.json()
        print(f"   响应内容: {json.dumps(response_data, indent=2, ensure_ascii=False)[:500]}")
        
        if response.status_code == 200:
            if 'data' in response_data and 'token' in response_data.get('data', {}):
                print("   ✅ 登录成功！HTTPS 访问正常")
            else:
                print("   ⚠️  登录接口可访问，但返回数据格式异常")
        elif response.status_code == 40001:
            print("   ⚠️  用户不存在（这是正常的，说明接口可访问）")
        elif response.status_code == 40002:
            print("   ⚠️  密码错误（这是正常的，说明接口可访问）")
        else:
            print(f"   ⚠️  返回状态码: {response.status_code}")
    except json.JSONDecodeError:
        print(f"   响应内容（非JSON）: {response.text[:200]}")
        
except requests.exceptions.SSLError as e:
    print(f"   ❌ SSL 错误: {str(e)}")
    print("   💡 提示: 证书可能是自签名证书，需要使用 verify=False")
except requests.exceptions.ConnectionError as e:
    print(f"   ❌ 连接错误: {str(e)}")
    print("   💡 提示: 无法连接到服务器，请检查网络和 DNS")
except Exception as e:
    print(f"   ❌ 错误: {str(e)}")

print()

# 测试 3: 健康检查
print("3. 测试健康检查接口 (GET /health):")
print("-" * 50)
try:
    response = requests.get(
        'https://www.bantu.sbs/health',
        verify=False,
        timeout=10
    )
    print(f"   HTTP 状态码: {response.status_code}")
    print(f"   响应内容: {response.text}")
    if response.status_code == 200:
        print("   ✅ 健康检查接口正常")
    else:
        print(f"   ⚠️  返回状态码: {response.status_code}")
except Exception as e:
    print(f"   ❌ 错误: {str(e)}")

print()

# 测试 4: 测试不使用 verify=False（验证证书）
print("4. 测试不使用 verify=False（验证证书）:")
print("-" * 50)
try:
    response = requests.post(
        'https://www.bantu.sbs/api/foundation/auth/login',
        json={'email': 'admin@bantu.sbs', 'password': 'password123'},
        verify=True,  # 验证证书
        timeout=10
    )
    print(f"   HTTP 状态码: {response.status_code}")
    print("   ✅ 证书验证通过（可能是 Let's Encrypt 证书）")
except requests.exceptions.SSLError as e:
    print(f"   ⚠️  SSL 证书验证失败: {str(e)[:100]}")
    print("   💡 这是正常的，说明使用的是自签名证书")
    print("   💡 前端可以使用 verify=False 或配置信任证书")
except Exception as e:
    print(f"   ❌ 错误: {str(e)}")

print()
print("=" * 50)
print("测试完成")
print("=" * 50)
print()
print("📋 总结:")
print("  - 如果测试 2 和 3 都返回 200，说明 HTTPS 访问正常")
print("  - 如果测试 4 失败，说明使用的是自签名证书")
print("  - 如果配置了 Let's Encrypt，测试 4 应该成功")
print()

