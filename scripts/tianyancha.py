#coding=utf-8
#!/usr/bin/python

# 接口请求示例为：http://open.api.tianyancha.com/services/open/ic/baseinfo/2.0?keyword=中航重机股份有限公司

# pip install requests
import requests
import time
import hashlib
import json
 
#  token可以从 数据中心 -> 我的接口 中获取
token = "59d10b88-95e5-4baa-9221-6b02ba61aea6"
encode = 'utf-8'

url = "http://open.api.tianyancha.com/services/open/ic/baseinfo/2.0?keyword=中航重机股份有限公司"
headers={'Authorization': token}
response = requests.get(url, headers=headers)

#结果打印
print(response.status_code)
print(response.text)