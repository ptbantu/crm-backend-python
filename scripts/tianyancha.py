#coding=utf-8
#!/usr/bin/python

# 接口请求示例为：http://open.api.tianyancha.com/services/open/ic/baseinfo/2.0?keyword=中航重机股份有限公司

# pip install requests
import requests
import time
import hashlib
import json
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

#  token可以从 数据中心 -> 我的接口 中获取
token = os.getenv("TIANYANCHA_API_KEY")
if not token:
    print("错误: TIANYANCHA_API_KEY 环境变量未设置")
    print("请在 .env 文件中配置 TIANYANCHA_API_KEY")
    print("参考 .env.example 文件获取配置说明")
    sys.exit(1)

encode = 'utf-8'

url = "http://open.api.tianyancha.com/services/open/ic/baseinfo/2.0?keyword=中航重机股份有限公司"
headers={'Authorization': token}
response = requests.get(url, headers=headers)

#结果打印
print(response.status_code)
print(response.text)