"""
天眼查服务
集成天眼查API进行企业信息查询
"""
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import requests
import asyncio
import json
import socket
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter

from foundation_service.config import settings
from foundation_service.schemas.tianyancha import (
    EnterpriseInfo, 
    ShareholderInfo, 
    EnterpriseQueryResponse,
    EnterpriseListItem,
    EnterpriseSearchResponse,
    EnterpriseDetailResponse
)
from common.utils.logger import get_logger

logger = get_logger(__name__)


class TianyanchaService:
    """天眼查服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_url = settings.TIANYANCHA_API_URL
        self.api_key = settings.TIANYANCHA_API_KEY
        self.timeout = settings.TIANYANCHA_TIMEOUT
    
    def _resolve_ipv4(self, hostname: str) -> str:
        """
        解析域名到 IPv4 地址
        强制使用 IPv4，避免 IPv6 解析问题
        """
        try:
            # 强制使用 IPv4 (AF_INET)
            addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM)
            if addr_info:
                return addr_info[0][4][0]  # 返回第一个 IPv4 地址
        except Exception as e:
            logger.warning(f"无法解析 {hostname} 到 IPv4，使用原始域名: {e}")
        return hostname
    
    def _get_api_url_with_ipv4(self, api_url: str) -> Tuple[str, dict]:
        """
        将 API URL 转换为使用 IPv4 地址
        注意：天眼查 API 可能不接受 IP + Host 头的形式，所以直接使用域名
        但通过 socket 配置强制使用 IPv4
        返回: (实际请求URL, headers字典)
        """
        # 直接返回原始 URL，不替换为 IP
        # 因为天眼查 API 可能检测 Host 头，使用 IP 会被拒绝
        # 我们通过 requests 的适配器配置来强制 IPv4
        return api_url, {}
    
    async def query_enterprise(self, keyword: str) -> EnterpriseQueryResponse:
        """
        查询企业信息
        
        Args:
            keyword: 查询关键词（企业名称/统一社会信用代码/注册号）
            
        Returns:
            企业信息查询响应
        """
        if not self.api_key:
            logger.warning("天眼查API密钥未配置")
            return EnterpriseQueryResponse(
                success=False,
                message="天眼查API密钥未配置，请联系管理员",
                data=None,
                raw_data=None
            )
        
        try:
            # 构建请求头
            # 根据天眼查API文档，使用 Authorization 头
            headers = {
                "Authorization": self.api_key
            }
            
            # 构建请求参数
            # 根据天眼查API示例代码，参数名为 keyword
            params = {
                "keyword": keyword,
                "pageNum": 1,
                "pageSize": 1
            }
            
            # 调用天眼查搜索接口
            # 使用 requests 库（同步），在线程池中执行避免阻塞事件循环
            api_url = f"{self.api_url}/services/open/search/2.0"
            
            # 解析域名到 IPv4 地址（避免 IPv6 解析问题）
            parsed = urlparse(api_url)
            hostname = parsed.hostname
            
            # 使用 gethostbyname 获取 IPv4（更可靠）
            try:
                ipv4 = socket.gethostbyname(hostname)
                # 如果解析成功且不是 localhost，使用 IP + Host 头
                if ipv4 and ipv4 != "127.0.0.1":
                    ip_url = api_url.replace(hostname, ipv4)
                    headers_with_host = headers.copy()
                    headers_with_host['Host'] = hostname
                    api_url = ip_url
                    headers = headers_with_host
            except Exception as e:
                logger.warning(f"IPv4解析失败，使用原始URL: {e}")
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(
                    api_url,
                    headers=headers,
                    params=params,
                    timeout=self.timeout
                )
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 解析响应数据
            if result.get("error_code") == 0 and result.get("result"):
                enterprise_data = result.get("result", {})
                enterprise_info = self._parse_enterprise_data(enterprise_data)
                
                return EnterpriseQueryResponse(
                    success=True,
                    message="查询成功",
                    data=enterprise_info,
                    raw_data=result
                )
            else:
                error_msg = result.get("reason", "查询失败")
                logger.warning(f"天眼查API返回错误: {error_msg}")
                return EnterpriseQueryResponse(
                    success=False,
                    message=f"查询失败: {error_msg}",
                    data=None,
                    raw_data=result
                )
                    
        except requests.Timeout:
            logger.error(f"天眼查API请求超时: {keyword}")
            return EnterpriseQueryResponse(
                success=False,
                message="请求超时，请稍后重试",
                data=None,
                raw_data=None
            )
        except requests.ConnectionError as e:
            logger.error(f"天眼查API连接失败: {self.api_url}, 错误: {str(e)}")
            return EnterpriseQueryResponse(
                success=False,
                message=f"无法连接到天眼查API服务器，请检查网络连接或API地址配置",
                data=None,
                raw_data=None
            )
        except requests.HTTPError as e:
            logger.error(f"天眼查API请求失败: {e.response.status_code if hasattr(e, 'response') else 'N/A'} - {str(e)}")
            return EnterpriseQueryResponse(
                success=False,
                message=f"API请求失败: {e.response.status_code if hasattr(e, 'response') else '未知错误'}",
                data=None,
                raw_data=None
            )
        except Exception as e:
            logger.error(f"天眼查查询异常: {str(e)}", exc_info=True)
            return EnterpriseQueryResponse(
                success=False,
                message=f"查询异常: {str(e)}",
                data=None,
                raw_data=None
            )
    
    def _parse_enterprise_data(self, data: Dict[str, Any]) -> EnterpriseInfo:
        """
        解析天眼查返回的企业数据
        
        Args:
            data: 天眼查API返回的原始数据
            
        Returns:
            解析后的企业信息
        """
        # 解析股东信息
        shareholders = []
        if data.get("stockList"):
            for stock in data.get("stockList", []):
                shareholders.append(ShareholderInfo(
                    name=stock.get("stockName"),
                    type=stock.get("stockType"),
                    capital=stock.get("shouldCapi"),
                    capital_actual=stock.get("realCapi"),
                    ratio=stock.get("percent")
                ))
        
        # 构建企业信息
        enterprise_info = EnterpriseInfo(
            name=data.get("name"),
            credit_code=data.get("creditCode"),
            registration_number=data.get("regNumber"),
            legal_representative=data.get("legalPersonName"),
            registered_capital=data.get("regCapital"),
            establishment_date=data.get("estiblishTime"),
            business_status=data.get("regStatus"),
            company_type=data.get("companyOrgType"),
            industry=data.get("industry"),
            address=data.get("regLocation"),
            business_scope=data.get("scope"),
            shareholders=shareholders if shareholders else None,
            extra_data=data  # 保存原始数据以便后续使用
        )
        
        return enterprise_info
    
    async def search_enterprises(self, keyword: str, page_num: int = 1, page_size: int = 10) -> EnterpriseSearchResponse:
        """
        搜索企业列表（816接口）
        
        Args:
            keyword: 搜索关键词（企业名称/统一社会信用代码/注册号）
            page_num: 页码，从1开始
            page_size: 每页数量
            
        Returns:
            企业搜索响应
        """
        if not self.api_key:
            logger.warning("天眼查API密钥未配置")
            return EnterpriseSearchResponse(
                success=False,
                message="天眼查API密钥未配置，请联系管理员",
                data=None,
                total=0,
                page_num=page_num,
                page_size=page_size,
                raw_data=None
            )
        
        try:
            # 构建请求头
            # 根据天眼查API文档，使用 Authorization 头，值为 token
            headers = {
                "Authorization": self.api_key
            }
            
            # 构建请求参数
            # 根据天眼查API示例代码，参数名为 keyword，pageSize 最大20
            params = {
                "keyword": keyword,
                "pageNum": page_num,
                "pageSize": min(page_size, 20)  # 限制最大20条
            }
            
            # 调用天眼查搜索接口
            # API路径：/services/open/search/2.0
            # 使用 requests 库（同步），在线程池中执行避免阻塞事件循环
            api_url = f"{self.api_url}/services/open/search/2.0"
            
            # 添加 User-Agent 头，避免被防护系统拦截
            headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            
            logger.info(f"调用天眼查API: {api_url}, 参数: keyword={keyword}, pageNum={page_num}, pageSize={page_size}")
            
            # 创建一个强制使用 IPv4 的请求函数
            # 使用已知的 IPv4 地址，避免 DNS 解析问题
            def make_request():
                parsed = urlparse(api_url)
                hostname = parsed.hostname
                tianyancha_ip = "124.70.125.226"
                port = parsed.port or 80
                
                # 强制 socket 解析到已知的 IPv4 地址
                original_getaddrinfo = socket.getaddrinfo
                def force_ipv4(*args):
                    if len(args) > 0 and args[0] == hostname:
                        # 返回已知的 IPv4 地址
                        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (tianyancha_ip, port))]
                    return original_getaddrinfo(*args)
                
                socket.getaddrinfo = force_ipv4
                try:
                    return requests.get(api_url, headers=headers, params=params, timeout=self.timeout)
                finally:
                    socket.getaddrinfo = original_getaddrinfo
            
            # 在线程池中执行同步的 requests 调用
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, make_request)
            
            logger.info(f"天眼查API响应状态: {response.status_code}, 响应长度: {len(response.text)}")
            
            # 如果状态码不是 200，记录响应内容以便调试
            if response.status_code != 200:
                logger.warning(f"天眼查API非200响应: {response.status_code}, 响应内容: {response.text[:500]}")
            
            # 尝试解析 JSON，即使状态码不是 200
            try:
                result = response.json()
            except Exception as e:
                logger.error(f"无法解析天眼查API响应为JSON: {e}, 响应内容: {response.text[:500]}")
                raise
            
            # 检查状态码，如果不是 200 且有错误信息，返回错误响应
            if response.status_code != 200:
                error_msg = result.get("reason") or result.get("message") or result.get("error_msg") or f"API返回错误状态码: {response.status_code}"
                logger.error(f"天眼查API错误: {error_msg}, 完整响应: {result}")
                return EnterpriseSearchResponse(
                    success=False,
                    message=f"API请求失败: {error_msg}",
                    data=None,
                    total=0,
                    page_num=page_num,
                    page_size=page_size,
                    raw_data=result
                )
            
            response.raise_for_status()
            
            # 解析响应数据
            # 根据天眼查API文档，响应格式可能不同，需要根据实际返回调整
            # 可能的格式：{"result": {...}, "error_code": 0} 或直接返回数据数组
            error_code = result.get("error_code") or result.get("errorCode") or 0
            
            if error_code == 0:
                # 尝试多种响应格式
                result_data = result.get("result") or result.get("data") or result
                enterprise_list = []
                
                # 解析企业列表（可能是数组或对象中的items）
                items = []
                if isinstance(result_data, list):
                    items = result_data
                elif isinstance(result_data, dict):
                    items = result_data.get("items", []) or result_data.get("list", [])
                
                for item in items:
                    enterprise_list.append(EnterpriseListItem(
                        id=str(item.get("id") or item.get("companyId") or ""),
                        name=item.get("name") or item.get("companyName"),
                        credit_code=item.get("creditCode") or item.get("credit_code"),
                        registration_number=item.get("regNumber") or item.get("reg_number"),
                        legal_representative=item.get("legalPersonName") or item.get("legal_person_name"),
                        registered_capital=item.get("regCapital") or item.get("reg_capital"),
                        establishment_date=item.get("estiblishTime") or item.get("establishment_date"),
                        business_status=item.get("regStatus") or item.get("business_status"),
                        address=item.get("regLocation") or item.get("address")
                    ))
                
                # 获取总数
                if isinstance(result_data, dict):
                    total = result_data.get("total", len(enterprise_list))
                else:
                    total = len(enterprise_list)
                
                return EnterpriseSearchResponse(
                    success=True,
                    message="搜索成功",
                    data=enterprise_list,
                    total=total,
                    page_num=page_num,
                    page_size=page_size,
                    raw_data=result
                )
            else:
                # 处理错误响应
                error_msg = result.get("reason") or result.get("message") or result.get("error_msg") or "搜索失败"
                error_code_val = result.get("error_code") or result.get("errorCode") or -1
                logger.warning(f"天眼查API返回错误 [code={error_code_val}]: {error_msg}, 响应: {result}")
                return EnterpriseSearchResponse(
                    success=False,
                    message=f"搜索失败: {error_msg}",
                    data=None,
                    total=0,
                    page_num=page_num,
                    page_size=page_size,
                    raw_data=result
                )
                    
        except requests.Timeout as e:
            logger.error(f"天眼查API请求超时: {keyword}, 错误: {str(e)}")
            return EnterpriseSearchResponse(
                success=False,
                message="请求超时，请稍后重试",
                data=None,
                total=0,
                page_num=page_num,
                page_size=page_size,
                raw_data=None
            )
        except requests.ConnectionError as e:
            logger.error(f"天眼查API连接失败: {self.api_url}, 错误: {str(e)}")
            return EnterpriseSearchResponse(
                success=False,
                message=f"无法连接到天眼查API服务器，请检查网络连接或API地址配置",
                data=None,
                total=0,
                page_num=page_num,
                page_size=page_size,
                raw_data=None
            )
        except requests.HTTPError as e:
            logger.error(f"天眼查API请求失败: {e.response.status_code if hasattr(e, 'response') else 'N/A'} - {str(e)}")
            return EnterpriseSearchResponse(
                success=False,
                message=f"API请求失败: {e.response.status_code if hasattr(e, 'response') else '未知错误'}",
                data=None,
                total=0,
                page_num=page_num,
                page_size=page_size,
                raw_data=None
            )
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"天眼查搜索异常 [{error_type}]: {str(e)}", exc_info=True)
            return EnterpriseSearchResponse(
                success=False,
                message=f"搜索异常: {str(e)}",
                data=None,
                total=0,
                page_num=page_num,
                page_size=page_size,
                raw_data=None
            )
    
    async def get_enterprise_detail(self, enterprise_id: str) -> EnterpriseDetailResponse:
        """
        获取企业详细信息（818接口）
        
        Args:
            enterprise_id: 企业ID
            
        Returns:
            企业详情响应
        """
        if not self.api_key:
            logger.warning("天眼查API密钥未配置")
            return EnterpriseDetailResponse(
                success=False,
                message="天眼查API密钥未配置，请联系管理员",
                data=None,
                raw_data=None
            )
        
        try:
            # 构建请求头
            # 根据天眼查API文档，使用 Authorization 头
            headers = {
                "Authorization": self.api_key
            }
            
            # 构建请求参数
            params = {
                "id": enterprise_id
            }
            
            # 调用天眼查818接口获取企业详细信息
            # API路径：/services/open/ic/baseinfoV2
            # 使用 requests 库（同步），在线程池中执行避免阻塞事件循环
            api_url = f"{self.api_url}/services/open/ic/baseinfoV2"
            
            # 添加 User-Agent 头，避免被防护系统拦截
            headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            
            logger.info(f"调用天眼查详情API: {api_url}, 参数: id={enterprise_id}")
            
            # 创建一个强制使用 IPv4 的请求函数
            def make_request():
                parsed = urlparse(api_url)
                hostname = parsed.hostname
                tianyancha_ip = "124.70.125.226"
                port = parsed.port or 80
                
                # 强制 socket 解析到已知的 IPv4 地址
                original_getaddrinfo = socket.getaddrinfo
                def force_ipv4(*args):
                    if len(args) > 0 and args[0] == hostname:
                        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (tianyancha_ip, port))]
                    return original_getaddrinfo(*args)
                
                socket.getaddrinfo = force_ipv4
                try:
                    return requests.get(api_url, headers=headers, params=params, timeout=self.timeout)
                finally:
                    socket.getaddrinfo = original_getaddrinfo
            
            # 在线程池中执行同步的 requests 调用
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, make_request)
            
            logger.info(f"天眼查详情API响应状态: {response.status_code}, 响应长度: {len(response.text)}")
            
            # 尝试解析 JSON，即使状态码不是 200
            try:
                result = response.json()
            except Exception as e:
                logger.error(f"无法解析天眼查详情API响应为JSON: {e}, 响应内容: {response.text[:500]}")
                return EnterpriseDetailResponse(
                    success=False,
                    message=f"API响应格式错误: {str(e)}",
                    data=None,
                    raw_data={"raw_text": response.text[:500]}
                )
            
            # 检查状态码，418 通常表示认证失败或请求被拒绝
            if response.status_code == 418:
                error_msg = result.get("reason") or result.get("message") or result.get("error_msg") or "请求被拒绝（418），可能是API密钥无效或IP未在白名单中"
                logger.error(f"天眼查详情API返回418错误: {error_msg}, 完整响应: {result}")
                return EnterpriseDetailResponse(
                    success=False,
                    message=f"API认证失败: {error_msg}。请检查API密钥是否正确，或联系管理员确认IP白名单配置",
                    data=None,
                    raw_data=result
                )
            
            # 检查其他非200状态码
            if response.status_code != 200:
                error_msg = result.get("reason") or result.get("message") or result.get("error_msg") or f"API返回错误状态码: {response.status_code}"
                logger.error(f"天眼查详情API错误 [{response.status_code}]: {error_msg}, 完整响应: {result}")
                return EnterpriseDetailResponse(
                    success=False,
                    message=f"API请求失败 ({response.status_code}): {error_msg}",
                    data=None,
                    raw_data=result
                )
            
            # 解析响应数据
            if result.get("error_code") == 0 and result.get("result"):
                enterprise_data = result.get("result", {})
                enterprise_info = self._parse_enterprise_data(enterprise_data)
                
                return EnterpriseDetailResponse(
                    success=True,
                    message="查询成功",
                    data=enterprise_info,
                    raw_data=result
                )
            else:
                error_msg = result.get("reason", "查询失败")
                logger.warning(f"天眼查API返回错误: {error_msg}")
                return EnterpriseDetailResponse(
                    success=False,
                    message=f"查询失败: {error_msg}",
                    data=None,
                    raw_data=result
                )
                    
        except requests.Timeout as e:
            logger.error(f"天眼查API请求超时: {enterprise_id}, 错误: {str(e)}")
            return EnterpriseDetailResponse(
                success=False,
                message="请求超时，请稍后重试",
                data=None,
                raw_data=None
            )
        except requests.ConnectionError as e:
            logger.error(f"天眼查API连接失败: {self.api_url}, 错误: {str(e)}")
            return EnterpriseDetailResponse(
                success=False,
                message=f"无法连接到天眼查API服务器，请检查网络连接或API地址配置",
                data=None,
                raw_data=None
            )
        except requests.HTTPError as e:
            logger.error(f"天眼查API请求失败: {e.response.status_code if hasattr(e, 'response') else 'N/A'} - {str(e)}")
            return EnterpriseDetailResponse(
                success=False,
                message=f"API请求失败: {e.response.status_code if hasattr(e, 'response') else '未知错误'}",
                data=None,
                raw_data=None
            )
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"天眼查查询异常 [{error_type}]: {str(e)}", exc_info=True)
            return EnterpriseDetailResponse(
                success=False,
                message=f"查询异常: {str(e)}",
                data=None,
                raw_data=None
            )
